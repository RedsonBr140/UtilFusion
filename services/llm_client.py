from openai import OpenAI

_DEFAULT_MODEL = "gpt-4o-mini"


class LLMClient:
    def __init__(self, api_key: str = "", model: str = ""):
        self.model = model.strip() or _DEFAULT_MODEL
        self._client = OpenAI(api_key=api_key) if api_key and api_key.strip() else None

    @property
    def available(self) -> bool:
        return self._client is not None

    def rewrite_query(self, descricao: str) -> str | None:
        if not self.available:
            return None
        system = (
            "Voce e um assistente que converte nomes de produtos do ERP de uma loja "
            "de materiais de construcao em termos de busca usados pelo site da "
            "Premocil (premocil.com.br). O site indexa produtos com nomes como: "
            "'ARGAMASSA QUARTZOLIT AC1 INTERNO 20KG', 'SUVINIL CORANTE VERMELHO "
            "50ML', 'TINTA FORTNIL ESMALTE F SUPER 3,6L BRANCO FOSCO'. "
            "Dado um nome do ERP, responda APENAS com a frase de busca em "
            "MAIUSCULAS, sem aspas e sem pontuacao extra, mantendo marca, tipo de "
            "produto, codigo/variacao e quantidade quando fizer sentido. Se o nome "
            "for inutil (ex.: apenas numeros), responda apenas: none"
        )
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": descricao},
                ],
                temperature=0,
                max_tokens=60,
            )
            text = (resp.choices[0].message.content or "").strip()
            if not text or text.strip().lower() == "none":
                return None
            return text
        except Exception as e:
            print(f"[LLM] erro ao reescrever consulta: {e}")
            return None

    def select_best(self, descricao: str, candidates: list[dict]) -> int | None:
        if not self.available or not candidates:
            return None
        lines = []
        for c in candidates:
            price = c.get("preco")
            price_txt = f"R$ {price:.2f}" if isinstance(price, (int, float)) else "?"
            lines.append(f"{c['index']}: {c['name']} ({price_txt})")
        system = (
            "Voce recebe a descricao de um produto do ERP e uma lista de produtos "
            "encontrados no site de uma loja. Escolha o produto da lista que "
            "corresponde ao produto do ERP. Responda apenas com o numero do indice "
            "(0, 1, 2...) do melhor produto, ou 'none' se nenhum corresponde."
        )
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": f"ERP: {descricao}\n\nProdutos do site:\n"
                        + "\n".join(lines)
                        + "\n\nMelhor indice:",
                    },
                ],
                temperature=0,
                max_tokens=10,
            )
            text = (resp.choices[0].message.content or "").strip()
            match = __import__("re").search(r"-?\d+", text)
            if match is None or "none" in text.lower():
                return None
            return int(match.group(0))
        except Exception as e:
            print(f"[LLM] erro ao selecionar produto: {e}")
            return None