import re

import requests

from services.concorrente_site.base import SmartSiteFetcher


class TupanFetcher(SmartSiteFetcher):
    BASE_URL = "https://www.tupan.com.br"
    SEARCH_URL = "https://www.tupan.com.br/busca"
    FONTE = "Tupan"

    def _search_html(self, session: requests.Session, query: str) -> str:
        print(f"[{self.FONTE}] GET {self.SEARCH_URL}?s='{query}'")
        resp = session.get(
            self.SEARCH_URL,
            params={"s": query},
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
        candidates = []
        seen = set()
        for name, preco_raw in re.findall(
            r'data-nome="([^"]*)" data-preco="([0-9.]+)"', html
        ):
            name = name.strip()
            try:
                preco = float(preco_raw)
            except ValueError:
                continue
            if not name or preco <= 0 or name in seen:
                continue
            seen.add(name)

            score = self._similarity(reference, name)
            print(
                f"[{self.FONTE}]   card score={score:.2f} "
                f"preco=R$ {preco:.2f} nome='{name}'"
            )
            candidates.append({"name": name, "preco": preco, "score": score})

        if not candidates:
            print(f"[{self.FONTE}] nenhum candidato com nome+preco na pagina")
        return candidates