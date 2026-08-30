from clients.api_client import ApiClient
from clients.api_response import ApiResponse


class OrdersService:

    def __init__(self, client=None):
        self.client = client or ApiClient()

    def create_order(self, instrument_id, side, order_type, quantity, price=None, headers=None):
        payload = {
            "instrument_id": instrument_id,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if price is not None:
            payload["price"] = price

        response = self.client.post("/orders", payload, headers=headers)
        return ApiResponse(response)

    def get_orders(self, headers=None):
        response = self.client.get("/orders", headers=headers)
        return ApiResponse(response)
