import httpx


class ODataClient:

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth = (username, password)

    async def fetch(self, endpoint: str):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/{endpoint}",
                auth=self.auth
            )

            response.raise_for_status()

            return response.json()
