import difflib
import re
import time
import unicodedata

import requests

from services.concorrente_site.base import ProductPrice, SiteFetcher


class PremocilFetcher(SiteFetcher):
    BASE_URL = "https://www.premocil.com.br"
    SEARCH_URL = "https://www.premocil.com.br/loja/busca.php?loja=1338870"
    FONTE = "Premocil"

    # Mínimo de similaridade (SequenceMatcher + tokens) para aceitar um match.
    MATCH_THRESHOLD = 0.55
    # Margem mínima entre o melhor e o segundo melhor para confiar sem ajuda do LLM.
    CONFIDENCE_MARGIN = 0.10

    def __init__(self, delay: float = 0.4, llm=None):
        self.delay = delay
        self.llm = llm
        self._session = None

    def _get_session(self) -> requests.Session:
        if self._session is None:
            print(f"[Premocil] inicializando sessao para {self.BASE_URL}")
            session = requests.Session()
            session.headers.update(
                {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/json,*/*",
                    "Accept-Language": "pt-BR,pt;q=0.9",
                }
            )
            # Warm up to acquire any cookies the store expects.
            try:
                warm = session.get(self.BASE_URL, timeout=15)
                print(f"[Premocil] warmup GET {self.BASE_URL} -> {warm.status_code}")
            except Exception as e:
                print(f"[Premocil] warmup GET {self.BASE_URL} -> ERRO: {e}")
            self._session = session
        return self._session

    def fetch_by_name(self, descricao: str, gtin: str | None = None) -> ProductPrice | None:
        raw = (descricao or "").strip()
        print(
            f"[Premocil] fetch_by_name -> descricao='{raw or '(vazia)'}'"
            + (f" gtin={gtin}" if gtin else "")
        )

        reference = self._normalize(raw)
        if not reference:
            print("[Premocil] descricao vazia, nada a fazer")
            return None

        if self.delay:
            print(f"[Premocil] aguardando {self.delay}s entre requisicoes")
            time.sleep(self.delay)

        try:
            session = self._get_session()

            queries = []
            meaningful = self._meaningful_query(reference)
            if meaningful and meaningful != reference:
                queries.append(meaningful)
            queries.append(reference)

            for query in queries:
                result = self._search_and_pick(session, query, reference, use_llm_selection=True)
                if result is not None:
                    return result

            if self.llm and self.llm.available:
                print("[Premocil] heuristica falhou, usando ChatGPT para reescrever a busca")
                llm_query = self.llm.rewrite_query(raw)
                if llm_query:
                    print(f"[Premocil] ChatGPT sugeriu a busca: '{llm_query}'")
                    result = self._search_and_pick(
                        session, llm_query, reference, use_llm_selection=True
                    )
                    if result is not None:
                        return result

            print(f"[Premocil] nenhum resultado aceito para '{raw}'")
            return None
        except Exception as e:
            print(f"[Premocil] error ao buscar '{raw}': {e}")
            return None

    def _search_and_pick(
        self,
        session: requests.Session,
        query: str,
        reference: str,
        use_llm_selection: bool,
    ) -> ProductPrice | None:
        print(f"[Premocil] POST {self.SEARCH_URL} com palavra_busca='{query}'")
        resp = session.post(
            self.SEARCH_URL,
            data={"palavra_busca": query},
            timeout=20,
            allow_redirects=True,
        )
        print(
            f"[Premocil] resposta status={resp.status_code} "
            f"url={resp.url} tamanho={len(resp.text)}"
        )
        resp.raise_for_status()

        picked = self._pick_candidate(resp.text, reference, use_llm_selection)
        if picked is None:
            print(f"[Premocil] variante '{query}' sem resultados aceitos")
            return None
        name, preco, score = picked
        print(f"[Premocil] MATCH (score={score:.2f}): '{name}' R$ {preco:.2f}")
        return ProductPrice(descricao=name, preco=preco, fonte=self.FONTE)

    def _pick_candidate(
        self, html: str, reference: str, use_llm_selection: bool
    ) -> tuple[str, float, float] | None:
        start = html.find('class="catalog-items')
        if start < 0:
            print("[Premocil] pagina sem container catalog-items (sem resultados)")
            return None
        print(f"[Premocil] container catalog-items encontrado na posicao {start}")

        end = html.find("catalog-footer", start)
        segment = html[start:end] if end > 0 else html[start:]

        candidates = []
        for pid, body in re.findall(
            r'<article class="product-card"[^>]*data-id="(\d+)"[^>]*>(.*?)'
            r"(?=<article class=\"product-card\"|$)",
            segment,
            re.S,
        ):
            name_match = re.search(
                r'class="card-product-name"[^>]*>(.*?)</h3>', body, re.S
            )
            price_match = re.search(
                r'class="product-card-price-new">R\$\s*([0-9.,]+)<', body
            )
            if not name_match or not price_match:
                continue

            name = re.sub(r"<[^>]+>", "", name_match.group(1)).strip()
            preco = self._to_float(price_match.group(1))
            if not name or preco is None:
                continue

            score = self._similarity(reference, name)
            print(
                f"[Premocil]   card id={pid} score={score:.2f} "
                f"preco=R$ {price_match.group(1)} nome='{name}'"
            )
            candidates.append({"name": name, "preco": preco, "score": score})

        if not candidates:
            print("[Premocil] cards encontrados porem nenhum com nome+preco validos")
            return None

        ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None

        confident = best["score"] >= self.MATCH_THRESHOLD and (
            second is None or best["score"] - second["score"] >= self.CONFIDENCE_MARGIN
        )
        if confident:
            return best["name"], best["preco"], best["score"]

        if use_llm_selection and self.llm and self.llm.available:
            print(
                f"[Premocil] melhor candidato score={best['score']:.2f} sem confianca, "
                "delegando escolha ao ChatGPT"
            )
            idx = self.llm.select_best(
                reference,
                [{"index": i, "name": c["name"], "preco": c["preco"]} for i, c in enumerate(candidates)],
            )
            if idx is not None and 0 <= idx < len(candidates):
                chosen = candidates[idx]
                print(
                    f"[Premocil] ChatGPT escolheu: '{chosen['name']}' "
                    f"R$ {chosen['preco']:.2f}"
                )
                return chosen["name"], chosen["preco"], chosen["score"]

        if best["score"] >= self.MATCH_THRESHOLD:
            print(
                f"[Premocil] aceitando melhor candidato score={best['score']:.2f} "
                f"como fallback"
            )
            return best["name"], best["preco"], best["score"]

        print(
            f"[Premocil] melhor candidato score={best['score']:.2f} abaixo do limiar "
            f"{self.MATCH_THRESHOLD:.2f}, nao vou chutar"
        )
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        text = unicodedata.normalize("NFD", text.upper())
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        text = re.sub(r"[^A-Z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    _UNIT_TOKENS = {
        "ML", "L", "G", "KG", "MG", "CM", "MM", "M", "X", "CX", "UN", "UND",
        "PCT", "PT", "LT", "MT", "M2", "M3",
    }
    _STOPWORDS = {
        "DE", "DA", "DO", "DAS", "DOS", "COM", "E", "EM", "NO", "NA", "PARA",
        "POR", "A", "O", "AO", "OS", "AS", "UMA", "UM",
    }

    @classmethod
    def _meaningful_query(cls, normalized: str) -> str:
        tokens = normalized.split()
        kept = []
        for tok in tokens:
            if tok in cls._UNIT_TOKENS or tok in cls._STOPWORDS:
                continue
            if len(tok) < 2:
                continue
            if tok.isdigit() or re.fullmatch(r"\d+[A-Z]*", tok):
                continue
            kept.append(tok)
        return " ".join(kept)

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        na = PremocilFetcher._normalize(a)
        nb = PremocilFetcher._normalize(b)
        if not na or not nb:
            return 0.0

        seq = difflib.SequenceMatcher(None, na, nb).ratio()

        ta = set(na.split())
        tb = set(nb.split())
        if ta and tb:
            # Dice: insensível à ordem, melhor que Jaccard para nomes reordenados.
            dice = 2 * len(ta & tb) / (len(ta) + len(tb))
        else:
            dice = 0.0

        return 0.6 * seq + 0.4 * dice

    @staticmethod
    def _to_float(value: str) -> float | None:
        cleaned = value.replace("R$", "").strip().replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None