instrument_schema = {
    "type": "object",
    "required": ["id", "ticker", "name", "type", "last_price", "close_price"],
    "properties": {
        "id": {"type": "integer"},
        "ticker": {"type": "string", "minLength": 1},
        "name": {"type": "string", "minLength": 1},
        "type": {"type": "string", "minLength": 1},
        "last_price": {"type": "number", "exclusiveMinimum": 0},
        "close_price": {"type": "number", "exclusiveMinimum": 0},
    },
}
