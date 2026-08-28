from clients.api_client import ApiClient
from clients.api_response import ApiResponse


class InstrumentsService:

    def __init__(self, client=None):
        self.client = client or ApiClient()

    def get_instruments(self, headers=None):
        response = self.client.get("/instruments", headers=headers)
        return ApiResponse(response)

    def search(self, query, headers=None):
        response = self.client.get("/search", params={"query": query}, headers=headers)
        return ApiResponse(response)
