import httpx


class ODataClient:

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password)

    async def fetch(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()

    async def fetch_all_pages(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        """Собирает все страницы OData (@odata.nextLink)."""
        url: str | None = f"{self.base_url}/{endpoint.lstrip('/')}"
        first = True
        out: list[dict] = []
        async with httpx.AsyncClient(timeout=120.0) as client:
            while url:
                if first:
                    response = await client.get(
                        url, auth=self.auth, params=params
                    )
                    first = False
                else:
                    response = await client.get(url, auth=self.auth)
                response.raise_for_status()
                data = response.json()
                chunk = data.get("value")
                if isinstance(chunk, list):
                    out.extend(chunk)
                url = data.get("@odata.nextLink")
        return out
