from jsonschema import validate
from schemas.order_schema import order_schema


def assert_order_schema(order):
    validate(instance=order, schema=order_schema)
