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

    # Acima disso aceitamos sem perguntar (junto com uma margem clara).
    MATCH_THRESHOLD = 0.45
    # Margem mínima entre o melhor e o segundo melhor para confiar sem ajuda.
    CONFIDENCE_MARGIN = 0.10

    def __init__(self, delay: float = 0.4, llm=None, confirm=None):
        self.delay = delay
        self.llm = llm
        # confirm(descricao_erp, nome_candidato, preco, score) -> bool
        self.confirm = confirm
        self._session = None
        self._pending = None

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
            self._pending = None

            queries = self._query_variants(reference)
            if self.llm and self.llm.available:
                print("[Premocil] usando ChatGPT para sugerir uma busca alternativa")
                llm_query = self.llm.rewrite_query(raw)
                if llm_query:
                    print(f"[Premocil] ChatGPT sugeriu a busca: '{llm_query}'")
                    if llm_query not in queries:
                        queries.append(llm_query)

            # Coleciona o melhor candidato ao longo de todas as buscas e so
            # pergunta ao usuario uma vez, no fim. Uma rejeicao prematura por
            # consulta fazia produtos validos (ex.: BUCHA) serem abandonados
            # antes de a busca mais ampla encontrar o resultado certo.
            for query in queries:
                candidates = self._search_candidates(session, query, reference)
                if not candidates:
                    continue

                fast = self._fast_match(candidates, reference)
                if fast is not None:
                    return self._to_product(fast)

                chosen = self._decide(candidates, raw, reference)
                if chosen is not None:
                    return self._to_product(chosen)

            if self._pending is not None:
                print(
                    f"[Premocil] melhor candidato geral score={self._pending['score']:.2f} "
                    "sem confirmacao - perguntando ao usuario"
                )
                if self._ask_user(raw, self._pending):
                    return self._to_product(self._pending)

            print(f"[Premocil] nenhum resultado aceito para '{raw}'")
            return None
        except Exception as e:
            print(f"[Premocil] error ao buscar '{raw}': {e}")
            return None

    @classmethod
    def _query_variants(cls, reference: str) -> list[str]:
        """Variants da busca, do mais especifico para o mais amplo.

        A busca do site tokeniza palavras (ex.: 'CP II F 32'), entao codigos
        colados como 'CPII' nao batem. Se nada der certo, alargar para
        marca+categoria e, por fim, categoria sozinha deixa o ChatGPT (ou o
        usuario) escolher entre os resultados.
        """
        meaningful = cls._meaningful_query(reference)
        m_tokens = (meaningful or reference).split()

        variants: list[str] = []
        for v in (meaningful, reference):
            if v and v not in variants:
                variants.append(v)
        for n in (2, 3, 4):
            if len(m_tokens) >= n:
                v = " ".join(m_tokens[:n])
                if v not in variants:
                    variants.append(v)
        # Categoria sozinha: ultimo recurso estrutural.
        if m_tokens and m_tokens[0] not in variants:
            variants.append(m_tokens[0])

        print("[Premocil] variantes de busca: " + " | ".join(variants))
        return variants

    def _search_candidates(
        self, session: requests.Session, query: str, reference: str
    ) -> list[dict]:
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
        candidates = self._parse_candidates(resp.text, reference)
        if not candidates:
            print(f"[Premocil] variante '{query}' sem resultados aceitos")
        return candidates

    def _parse_candidates(self, html: str, reference: str) -> list[dict]:
        start = html.find('class="catalog-items')
        if start < 0:
            print("[Premocil] pagina sem container catalog-items (sem resultados)")
            return []
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
        return candidates

    def _fast_match(self, candidates: list[dict], reference: str) -> dict | None:
        """Sem duvida: score alto, margem clara e todos os tokens relevantes do
        ERP presentes no candidato. Aceita sem ChatGPT nem dialogo."""
        ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None

        if best["score"] < 0.55:
            return None
        if second is not None and best["score"] - second["score"] < self.CONFIDENCE_MARGIN:
            return None

        ref_tokens = {
            t for t in reference.split()
            if t not in self._UNIT_TOKENS and t not in self._STOPWORDS
        }
        cand_tokens = set(self._normalize(best["name"]).split())
        if ref_tokens and not ref_tokens.issubset(cand_tokens):
            print(
                f"[Premocil] score {best['score']:.2f} alto mas tokens do ERP ausentes "
                f"({ref_tokens - cand_tokens}) - nao confiar cegamente"
            )
            return None

        print(
            f"[Premocil] MATCH SEGURO (score={best['score']:.2f}): "
            f"'{best['name']}' R$ {best['preco']:.2f}"
        )
        return best

    def _decide(self, candidates: list[dict], raw: str, reference: str) -> dict | None:
        """Escolhe sem perguntar, ou guarda o melhor candidato para confirmar
        com o usuario no fim de todas as buscas."""
        top = max(candidates, key=lambda c: c["score"])

        if not (self.llm and self.llm.available):
            if top["score"] >= self.MATCH_THRESHOLD:
                print(
                    f"[Premocil] MATCH (score={top['score']:.2f}): "
                    f"'{top['name']}' R$ {top['preco']:.2f}"
                )
                return top
            self._remember_pending(top)
            return None

        print(
            f"[Premocil] melhor candidato score={top['score']:.2f} sem confianca, "
            "delegando escolha ao ChatGPT"
        )
        idx = self.llm.select_best(
            reference,
            [{"index": i, "name": c["name"], "preco": c["preco"]} for i, c in enumerate(candidates)],
        )

        if idx is None or not (0 <= idx < len(candidates)):
            # ChatGPT desconfiou (ex.: marca diferente) mesmo com score razoavel
            # -> nao aceitar cegamente, deixa para o usuario decidir no fim.
            print("[Premocil] ChatGPT nao reconheceu nenhum candidato (possivel troca de marca)")
            self._remember_pending(top)
            return None

        chosen = candidates[idx]
        if chosen["score"] >= self.MATCH_THRESHOLD:
            print(
                f"[Premocil] MATCH (score={chosen['score']:.2f}): "
                f"'{chosen['name']}' R$ {chosen['preco']:.2f}"
            )
            return chosen

        print(
            f"[Premocil] ChatGPT escolheu '{chosen['name']}' mas score "
            f"{chosen['score']:.2f} abaixo do limiar - em espera"
        )
        self._remember_pending(chosen)
        return None

    def _remember_pending(self, chosen: dict) -> None:
        if self._pending is None or chosen["score"] > self._pending["score"]:
            self._pending = chosen
            print(
                f"[Premocil] candidato em espera (score={chosen['score']:.2f}): "
                f"'{chosen['name']}' R$ {chosen['preco']:.2f}"
            )

    @staticmethod
    def _to_product(chosen: dict) -> ProductPrice:
        return ProductPrice(
            descricao=chosen["name"], preco=chosen["preco"], fonte=PremocilFetcher.FONTE
        )

    def _ask_user(self, raw: str, chosen: dict) -> bool:
        if self.confirm is None:
            return False
        return bool(self.confirm(raw, chosen["name"], chosen["preco"], chosen["score"]))

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