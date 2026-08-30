from clients.api_client import ApiClient
from clients.api_response import ApiResponse


class PortfolioService:

    def __init__(self, client=None):
        self.client = client or ApiClient()

    def get_portfolio(self, headers=None):
        response = self.client.get("/portfolio", headers=headers)
        return ApiResponse(response)
