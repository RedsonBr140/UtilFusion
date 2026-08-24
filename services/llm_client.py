from openai import OpenAI

_DEFAULT_MODEL = "gpt-4o-mini"


class LLMClient:
    def __init__(self, api_key: str = "", model: str = ""):
        self.model = model.strip() or _DEFAULT_MODEL
        self._client = OpenAI(api_key=api_key) if api_key and api_key.strip() else None

    @property
    def available(self) -> bool:
        return self._client is not None

    def rewrite_query(self, descricao: str, referencia: str | None = None) -> str | None:
        if not self.available:
            return None
        system = (
            "Voce e um comprador experiente de materiais de construcao digitando "
            "a busca em uma loja online. Dado o nome de um produto no ERP, "
            "escreva exatamente a frase que um comprador digitaria para achar o "
            "produto no site da loja.\n"
            "Quando for fornecida uma REFERENCIA (codigo interno do produto), "
            "use a REFERENCIA como termo principal da busca, pois e o "
            "identificador mais confiavel.\n"
            "REGRAS:\n"
            "1) SEMPRE inclua a CATEGORIA/tipo do produto como palavra principal "
            "(ex.: PORCELANATO, PISO, CIMENTO, REVESTIMENTO) e NAO busque apenas "
            "um termo ambíguo: para 'PORCEL.PAMESA...' busque 'PORCELANATO "
            "PAMESA...', nunca apenas 'PORCEL';\n"
            "2) expanda abreviacoes obvias para a palavra completa (ex.: "
            "PORCEL. -> PORCELANATO, ACR. -> ACRILICA, REV. -> "
            "REVESTIMENTO);\n"
            "3) a busca do site indexa palavras individuais, entao escreva "
            "codigos de produto com espacos entre letras e numeros (ex.: "
            "'CP II F 32', e NAO 'CPIIF32' ou 'CPII-F-32');\n"
            "4) remova palavras de preenchimento e descritores redundantes "
            "(ex.: 'PARAFUSO' em 'BUCHA P PARAFUSO', 'MULTIUSO', 'RS'), mas "
            "MANTENHA a marca e a variacao que distingue o produto (cor, "
            "tamanho, quantidade, codigo);\n"
            "5) escreva de forma concisa e natural, como um ser humano "
            "pesquisaria.\n"
            "Responda APENAS com a frase de busca, em MAIUSCULAS, sem aspas e "
            "sem pontuacao extra. Se o nome for inutil (ex.: apenas numeros), "
            "responda apenas: none.\n"
            "Exemplos:\n"
            "'CIMENTO NACIONAL CPII-F-32 RS 50KG' -> 'CIMENTO NACIONAL CP II F "
            "32 50KG'\n"
            "'PORCEL.PAMESA 58X58 RET (A) JAVA TURQUES' -> 'PORCELANATO PAMESA "
            "58X58 JAVA TURQUES'\n"
            "'BUCHA P PARAFUSO COM ANEL N 8 MULTIUSO' -> 'BUCHA COM ANEL 8'."
        )
        try:
            user_content = descricao
            if referencia:
                user_content = f"REFERENCIA: {referencia}\nDESCRICAO: {descricao}"
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_content},
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
            "Voce e um especialista em casamento de produtos entre um sistema ERP "
            "e uma loja online de materiais de construcao.\n\n"
            "Duas regras sao OBRIGATORIAS e qualquer violacao delas exige "
            "responder 'none':\n"
            "1) MARCA: o produto do site DEVE ter a MESMA marca do ERP. Marcas "
            "diferentes NAO sao o mesmo produto, mesmo que categoria, codigo e "
            "tamanho coincidam.\n"
            "2) CATEGORIA (tipo de produto): o candidato DEVE ser da mesma "
            "categoria. Nunca escolha um produto de categoria diferente.\n\n"
            "ERROS CLASSICOS A EVITAR:\n"
            "- ERP 'CIMENTO NACIONAL CP II F 32 50KG' com candidatos "
            "'CIMENTO MIZU CP II F 32 50KG' e 'CIMENTO VOTORANTIM CP II F 32 "
            "50KG': a marca e NACIONAL; como NENHUM candidato contem 'NACIONAL', "
            "responda 'none'.\n"
            "- ERP 'PORCELANATO PAMESA 58X58 JAVA TURQUES' com candidato "
            "'SOQUETE PORCEL E27 SPOT ALCA BR DILUX': SOQUETE e um produto "
            "eletrico, NAO um porcelanato/piso - mesmo contendo 'PORCEL', a "
            "categoria e diferente; responda 'none'.\n\n"
            "CRITERIOS, nesta ordem:\n"
            "1) MARCA identica (procure o nome da marca do ERP dentro do nome do "
            "candidato);\n"
            "2) CATEGORIA/tipo de produto igual (substantivo principal);\n"
            "3) codigo/variacao;\n"
            "4) quantidade/tamanho.\n\n"
            "Se a marca ou a categoria do ERP nao aparecer em nenhum candidato, "
            "responda APENAS 'none'. Nao adivinhe, nao escolha por causa de um "
            "unico numero em comum.\n"
            "Responda apenas com o numero do indice (0, 1, 2...) do melhor "
            "produto ou 'none'."
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