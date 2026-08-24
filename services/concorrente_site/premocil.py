import re

import requests

from services.concorrente_site.base import SmartSiteFetcher


class PremocilFetcher(SmartSiteFetcher):
    BASE_URL = "https://www.premocil.com.br"
    SEARCH_URL = "https://www.premocil.com.br/loja/busca.php?loja=1338870"
    FONTE = "Premocil"

    def _search_html(self, session: requests.Session, query: str) -> str:
        print(f"[{self.FONTE}] POST {self.SEARCH_URL} com palavra_busca='{query}'")
        resp = session.post(
            self.SEARCH_URL,
            data={"palavra_busca": query},
            timeout=20,
            allow_redirects=True,
        )
        print(
            f"[{self.FONTE}] resposta status={resp.status_code} "
            f"url={resp.url} tamanho={len(resp.text)}"
        )
        resp.raise_for_status()
        return resp.text

    def _parse_candidates(self, html: str, reference: str) -> list[dict]:
        start = html.find('class="catalog-items')
        if start < 0:
            print(f"[{self.FONTE}] pagina sem container catalog-items (sem resultados)")
            return []
        print(f"[{self.FONTE}] container catalog-items encontrado na posicao {start}")

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

            link_match = re.search(r'<a\s+href="([^"]+)"', body)
            url = link_match.group(1).strip() if link_match else ""

            score = self._similarity(reference, name)
            print(
                f"[{self.FONTE}]   card id={pid} score={score:.2f} "
                f"preco=R$ {price_match.group(1)} nome='{name}' url='{url}'"
            )
            candidates.append(
                {"name": name, "preco": preco, "score": score, "url": url}
            )

        if not candidates:
            print(
                f"[{self.FONTE}] cards encontrados porem nenhum com nome+preco validos"
            )
        return candidates