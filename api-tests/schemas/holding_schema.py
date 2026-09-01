holding_schema = {
    "type": "object",
    "required": [
        "instrument_id",
        "ticker",
        "quantity",
        "last_price",
        "close_price",
        "avg_cost_price",
    ],
    "properties": {
        "instrument_id": {"type": "integer"},
        "ticker": {"type": "string", "minLength": 1},
        "quantity": {"type": "integer", "exclusiveMinimum": 0},
        "last_price": {"type": "number", "exclusiveMinimum": 0},
        "close_price": {"type": "number", "exclusiveMinimum": 0},
        "avg_cost_price": {"type": "number", "exclusiveMinimum": 0},
    },
}
