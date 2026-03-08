from ..client.odata_client import ODataClient


class SyncService:

    def __init__(self, client: ODataClient):
        self.client = client

    async def sync_sales(self):

        data = await self.client.fetch(
            "Document_РеализацияТоваровУслуг"
        )

        return data["value"]
