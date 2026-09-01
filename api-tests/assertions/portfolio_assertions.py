import pytest
from jsonschema import validate
from schemas.holding_schema import holding_schema


def assert_holding_schema(holding):
    validate(instance=holding, schema=holding_schema)


def assert_holding_reflects_purchases(holding, orders):
    first_buy, second_buy = orders

    total_quantity = first_buy.body["quantity"] + second_buy.body["quantity"]
    expected_avg_cost = (
        first_buy.body["quantity"] * first_buy.body["price"]
        + second_buy.body["quantity"] * second_buy.body["price"]
    ) / total_quantity

    assert holding["quantity"] == total_quantity
    assert holding["avg_cost_price"] == pytest.approx(expected_avg_cost)
