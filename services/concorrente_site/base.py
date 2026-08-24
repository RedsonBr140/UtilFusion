import difflib
import re
import time
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass

import requests


@dataclass
class ProductPrice:
    descricao: str
    preco: float | None
    fonte: str = ""
    url: str = ""
    image: str = ""


class SiteFetcher(ABC):
    @abstractmethod
    def fetch_by_name(
        self,
        descricao: str,
        gtin: str | None = None,
        referencia: str | None = None,
        imagem_erp: str | None = None,
    ) -> ProductPrice | None:
        raise NotImplementedError


class SmartSiteFetcher(SiteFetcher):
    """Pipeline generico de busca em loja online: normaliza o nome do produto,
    gera variantes de busca, consulta o site, usa ChatGPT para reescrever a
    consulta e escolher entre candidatos e, ao final, confirma com o usuario.

    Subclasses devem definir FONTE e implementar:
      - _search_html(session, query) -> str
      - _parse_candidates(html, reference) -> list[dict]
    (opcionalmente BASE_URL, usado no warmup de cookies da sessao).
    """

    FONTE = ""
    BASE_URL = ""
    # Acima disso aceitamos sem perguntar (junto com uma margem clara).
    MATCH_THRESHOLD = 0.45
    # Margem minima entre o melhor e o segundo melhor para confiar sem ajuda.
    CONFIDENCE_MARGIN = 0.10

    def __init__(self, delay: float = 0.4, llm=None, confirm=None):
        self.delay = delay
        self.llm = llm
        # confirm(descricao_erp, nome_candidato, preco, score, image, imagem_erp) -> bool
        self.confirm = confirm
        self._session = None
        self._pending = None
        self._imagem_erp = ""

    # ---------- sessao ----------

    def _get_session(self) -> requests.Session:
        if self._session is None:
            print(f"[{self.FONTE}] inicializando sessao")
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
            # Warm up para adquirir cookies que a loja espere.
            if self.BASE_URL:
                try:
                    warm = session.get(self.BASE_URL, timeout=15)
                    print(
                        f"[{self.FONTE}] warmup GET {self.BASE_URL} -> {warm.status_code}"
                    )
                except Exception as e:
                    print(f"[{self.FONTE}] warmup GET {self.BASE_URL} -> ERRO: {e}")
            self._session = session
        return self._session

    # ---------- pipeline principal ----------

    def fetch_by_name(
        self,
        descricao: str,
        gtin: str | None = None,
        referencia: str | None = None,
        imagem_erp: str | None = None,
    ) -> ProductPrice | None:
        raw = (descricao or "").strip()
        self._imagem_erp = (imagem_erp or "").strip()
        print(
            f"[{self.FONTE}] fetch_by_name -> descricao='{raw or '(vazia)'}'"
            + (f" gtin={gtin}" if gtin else "")
        )

        reference = self._normalize(raw)
        if not reference:
            print(f"[{self.FONTE}] descricao vazia, nada a fazer")
            return None

        if self.delay:
            print(f"[{self.FONTE}] aguardando {self.delay}s entre requisicoes")
            time.sleep(self.delay)

        try:
            session = self._get_session()
            self._pending = None

            queries = self._query_variants(reference)
            if self.llm and self.llm.available:
                print(
                    f"[{self.FONTE}] usando ChatGPT para sugerir uma busca alternativa"
                )
                llm_query = self.llm.rewrite_query(raw)
                if llm_query:
                    print(f"[{self.FONTE}] ChatGPT sugeriu a busca: '{llm_query}'")
                    if llm_query not in queries:
                        queries.insert(0, llm_query)

                if referencia:
                    print(
                        f"[{self.FONTE}] usando ChatGPT para buscar por referencia "
                        f"'{referencia}'"
                    )
                    llm_ref_query = self.llm.rewrite_query(raw, referencia)
                    if llm_ref_query:
                        print(
                            f"[{self.FONTE}] ChatGPT sugeriu busca por referencia: "
                            f"'{llm_ref_query}'"
                        )
                        if llm_ref_query not in queries:
                            queries.insert(0, llm_ref_query)

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
                    f"[{self.FONTE}] melhor candidato geral score={self._pending['score']:.2f} "
                    "sem confirmacao - perguntando ao usuario"
                )
                if self._ask_user(raw, self._pending):
                    return self._to_product(self._pending)

            print(f"[{self.FONTE}] nenhum resultado aceito para '{raw}'")
            return None
        except Exception as e:
            print(f"[{self.FONTE}] error ao buscar '{raw}': {e}")
            return None

    # ---------- busca especifica da loja (subclasses) ----------

    @abstractmethod
    def _search_html(self, session: requests.Session, query: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _parse_candidates(self, html: str, reference: str) -> list[dict]:
        raise NotImplementedError

    def _search_candidates(
        self, session: requests.Session, query: str, reference: str
    ) -> list[dict]:
        html = self._search_html(session, query)
        candidates = self._parse_candidates(html, reference)
        if not candidates:
            print(f"[{self.FONTE}] variante '{query}' sem resultados aceitos")
        return candidates

    # ---------- decisao generica ----------

    def _fast_match(self, candidates: list[dict], reference: str) -> dict | None:
        """Sem duvida: score alto, margem clara e todos os tokens relevantes do
        ERP presentes no candidato. Aceita sem ChatGPT nem dialogo."""
        ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
        best = ranked[0]
        second = ranked[1] if len(ranked) > 1 else None

        if best["score"] < 0.55:
            return None
        if (
            second is not None
            and best["score"] - second["score"] < self.CONFIDENCE_MARGIN
        ):
            return None

        ref_tokens = {
            t
            for t in reference.split()
            if t not in self._UNIT_TOKENS and t not in self._STOPWORDS
        }
        cand_tokens = set(self._normalize(best["name"]).split())
        missing = {
            t
            for t in ref_tokens
            if not any(self._tokens_compatible(t, ct) for ct in cand_tokens)
        }
        if ref_tokens and missing:
            print(
                f"[{self.FONTE}] score {best['score']:.2f} alto mas tokens do ERP ausentes "
                f"({sorted(missing)}) - nao confiar cegamente"
            )
            return None

        print(
            f"[{self.FONTE}] MATCH SEGURO (score={best['score']:.2f}): "
            f"'{best['name']}' R$ {best['preco']:.2f}"
        )
        return best

    def _decide(self, candidates: list[dict], raw: str, reference: str) -> dict | None:
        """Escolhe sem perguntar, ou guarda o melhor candidato para confirmar
        com o usuario no fim de todas as buscas."""
        top = max(candidates, key=lambda c: c["score"])

        if not (self.llm and self.llm.available):
            if self._brand_conflict(reference, top):
                self._remember_pending(top)
                return None
            if top["score"] >= self.MATCH_THRESHOLD:
                print(
                    f"[{self.FONTE}] MATCH (score={top['score']:.2f}): "
                    f"'{top['name']}' R$ {top['preco']:.2f}"
                )
                return top
            self._remember_pending(top)
            return None

        print(
            f"[{self.FONTE}] melhor candidato score={top['score']:.2f} sem confianca, "
            "delegando escolha ao ChatGPT"
        )
        idx = self.llm.select_best(
            reference,
            [
                {"index": i, "name": c["name"], "preco": c["preco"]}
                for i, c in enumerate(candidates)
            ],
        )

        if idx is None or not (0 <= idx < len(candidates)):
            # ChatGPT desconfiou (ex.: marca diferente) mesmo com score razoavel
            # -> nao aceitar cegamente, deixa para o usuario decidir no fim.
            print(
                f"[{self.FONTE}] ChatGPT nao reconheceu nenhum candidato "
                "(possivel troca de marca)"
            )
            self._remember_pending(top)
            return None

        chosen = candidates[idx]
        if self._brand_conflict(reference, chosen):
            print(
                f"[{self.FONTE}] ChatGPT escolheu '{chosen['name']}' mas "
                "faltam termos-chave do ERP (marca) - em espera para confirmacao"
            )
            self._remember_pending(chosen)
            return None

        if chosen["score"] >= self.MATCH_THRESHOLD:
            print(
                f"[{self.FONTE}] MATCH (score={chosen['score']:.2f}): "
                f"'{chosen['name']}' R$ {chosen['preco']:.2f}"
            )
            return chosen

        print(
            f"[{self.FONTE}] ChatGPT escolheu '{chosen['name']}' mas score "
            f"{chosen['score']:.2f} abaixo do limiar - em espera"
        )
        self._remember_pending(chosen)
        return None

    @staticmethod
    def _tokens_compatible(a: str, b: str) -> bool:
        """True se dois tokens representam a mesma palavra, inclusive quando um e
        abreviacao/prefixo do outro (ex.: PORCEL x PORCELANATO, TURQUES x TURQUESA)."""
        if a == b:
            return True
        if len(a) >= 3 and len(b) >= 3:
            return a.startswith(b) or b.startswith(a)
        return False

    def _brand_conflict(self, reference: str, cand: dict) -> bool:
        """True se o candidato nao contem as palavras-chave (marca, tipo) do ERP.
        Evita aceitar, sem confirmacao, um produto de marca diferente que apenas
        compartilha categoria/codigo (ex.: CIMENTO NACIONAL x CIMENTO MIZU)."""
        ref_tokens = {
            t
            for t in reference.split()
            if len(t) >= 3
            and t.isalpha()
            and t not in self._UNIT_TOKENS
            and t not in self._STOPWORDS
        }
        cand_tokens = set(self._normalize(cand["name"]).split())
        missing = {
            t
            for t in ref_tokens
            if not any(self._tokens_compatible(t, ct) for ct in cand_tokens)
        }
        if missing:
            print(
                f"[{self.FONTE}] candidato '{cand['name']}' sem termos-chave do ERP "
                f"({sorted(missing)}) - possivel marca trocada"
            )
            return True
        return False

    def _remember_pending(self, chosen: dict) -> None:
        if self._pending is None or chosen["score"] > self._pending["score"]:
            self._pending = chosen
            print(
                f"[{self.FONTE}] candidato em espera (score={chosen['score']:.2f}): "
                f"'{chosen['name']}' R$ {chosen['preco']:.2f}"
            )

    def _to_product(self, chosen: dict) -> ProductPrice:
        return ProductPrice(
            descricao=chosen["name"],
            preco=chosen["preco"],
            fonte=self.FONTE,
            url=chosen.get("url", ""),
            image=chosen.get("image", ""),
        )

    def _ask_user(self, raw: str, chosen: dict) -> bool:
        if self.confirm is None:
            return False
        return bool(
            self.confirm(
                raw,
                chosen["name"],
                chosen["preco"],
                chosen["score"],
                chosen.get("image", ""),
                self._imagem_erp,
            )
        )

    # ---------- normalizacao e similaridade ----------

    @staticmethod
    def _normalize(text: str) -> str:
        text = unicodedata.normalize("NFD", text.upper())
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        text = re.sub(r"[^A-Z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    _UNIT_TOKENS = {
        "ML",
        "L",
        "G",
        "KG",
        "MG",
        "CM",
        "MM",
        "M",
        "X",
        "CX",
        "UN",
        "UND",
        "PCT",
        "PT",
        "LT",
        "MT",
        "M2",
        "M3",
    }
    _STOPWORDS = {
        "DE",
        "DA",
        "DO",
        "DAS",
        "DOS",
        "COM",
        "E",
        "EM",
        "NO",
        "NA",
        "PARA",
        "POR",
        "A",
        "O",
        "AO",
        "OS",
        "AS",
        "UMA",
        "UM",
    }

    # Abreviacoes comuns em nomes do ERP, expandidas para deixar a busca
    # mais natural (mesmo sem o apoio do ChatGPT).
    _ABBREVIATIONS = {
        "PORCEL": "PORCELANATO",
        "ACR": "ACRILICA",
        "REV": "REVESTIMENTO",
        "ARG": "ARGAMASSA",
        "CIM": "CIMENTO",
        "CER": "CERAMICA",
        "REJ": "REJUNTE",
        "TIN": "TINTA",
        "PARAF": "PARAFUSO",
        "BUCH": "BUCHA",
    }

    @classmethod
    def _naturalize(cls, normalized: str) -> str:
        """Transforma uma consulta em algo mais natural: expande abreviacoes e
        separa codigos colados (ex.: 'CPII' -> 'CP II', 'ACIII' -> 'AC III')."""
        result = []
        for tok in normalized.split():
            tok = cls._ABBREVIATIONS.get(tok, tok)
            # Separa codigo letra+numero (ex.: 'CPIIF32' -> 'CPIIF 32').
            pieces = re.findall(r"[A-Z]+|\d+", tok)
            if len(pieces) > 1:
                tok = " ".join(pieces)
            # Separa o numeral romano de siglas do tipo AC/CP (ACII, CPIII...).
            tok = re.sub(r"\b(AC|CP)(I{1,3}|IV|V)\b", r"\1 \2", tok)
            result.append(tok)
        return " ".join(result)

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

    @classmethod
    def _query_variants(cls, reference: str) -> list[str]:
        """Variants da busca, do mais especifico para o mais amplo.

        A busca do site tokeniza palavras (ex.: 'CP II F 32'), entao codigos
        colados como 'CPII' nao batem. Se nada der certo, alargar para
        marca+categoria e, por fim, categoria sozinha deixa o ChatGPT (ou o
        usuario) escolher entre os resultados.
        """
        meaningful = cls._meaningful_query(reference)
        natural = cls._naturalize(meaningful) if meaningful else ""
        m_tokens = (natural or meaningful or reference).split()

        variants: list[str] = []
        if natural and natural != meaningful:
            variants.append(natural)
        for v in (meaningful, reference):
            if v and v not in variants:
                variants.append(v)
        for n in (2, 3, 4):
            if len(m_tokens) >= n:
                v = " ".join(m_tokens[:n])
                if v not in variants:
                    variants.append(v)
        # Categoria sozinha: apenas quando nao ha termos mais especificos,
        # senao um termo unico ambíguo (ex.: 'PORCEL') retorna produtos de
        # outras categorias (ex.: soquetes) na busca do site.
        if len(m_tokens) == 1 and m_tokens[0] not in variants:
            variants.append(m_tokens[0])

        print(f"[{cls.FONTE}] variantes de busca: " + " | ".join(variants))
        return variants

    @classmethod
    def _similarity(cls, a: str, b: str) -> float:
        na = cls._normalize(a)
        nb = cls._normalize(b)
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
