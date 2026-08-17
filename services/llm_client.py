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
            "Voce gera termos de busca para lojas online a partir de nomes de "
            "produtos de um sistema ERP. Dado um nome de produto, produza a frase "
            "de busca mais provavel de encontrar aquele produto no site da loja. "
            "REGRAS: 1) a busca do site indexa palavras individuais, entao escreva "
            "codigos de produto com espacos entre letras e numeros (ex.: "
            "'CP II F 32', e NAO 'CPIIF32', 'CPII-F-32' ou 'CPII F32'); 2) remova "
            "palavras de preenchimento e descritores redundantes (ex.: 'PARAFUSO' "
            "em 'BUCHA P PARAFUSO', 'MULTIUSO', 'RS'), mas MANTENHA palavras que "
            "distinguem produtos (ex.: 'COM ANEL' vs 'SEM ANEL'); 3) conserve os "
            "termos mais distintivos: marca, tipo de produto e a variacao principal "
            "(codigo, tamanho, quantidade quando importa); 4) use o estilo de "
            "nomenclatura que lojas costumam usar. Responda APENAS com a frase, em "
            "MAIUSCULAS, sem aspas e sem pontuacao extra. Se o nome for inutil "
            "(ex.: apenas numeros), responda apenas: none. Exemplos: "
            "'CIMENTO NACIONAL CPII-F-32 RS 50KG' -> 'CIMENTO NACIONAL CP II F 32 "
            "50KG'; 'BUCHA P PARAFUSO COM ANEL N 8 MULTIUSO' -> 'BUCHA COM ANEL 8'."
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
            "Voce recebe a descricao de um produto de um ERP e uma lista de "
            "produtos encontrados no site de uma loja online. Escolha o produto da "
            "lista que corresponde ao produto do ERP. CRITERIOS, nesta ordem: "
            "1) tipo de produto (substantivo principal) deve ser o mesmo "
            "(ex.: BUCHA e diferente de PARAFUSO); 2) MARCA deve ser a mesma - se "
            "a marca do ERP NAO aparecer em nenhum candidato, responda 'none'; "
            "3) codigo/variacao; 4) quantidade/tamanho. Se nenhum produto da "
            "lista corresponde de forma razoavel, responda APENAS 'none'. NAO "
            "adivinhe e NAO escolha por causa de um unico numero em comum. "
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