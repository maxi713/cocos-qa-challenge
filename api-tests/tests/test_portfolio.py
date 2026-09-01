import pytest
from assertions.common_assertions import assert_unique_field
from assertions.portfolio_assertions import (
    assert_holding_reflects_purchases,
    assert_holding_schema,
)

pytestmark = pytest.mark.usefixtures("reset_state")


@pytest.fixture
def market_buys(request, orders_service):
    orders = []
    for instrument_id, quantity in request.param:
        order = orders_service.create_order(
            instrument_id=instrument_id,
            side="BUY",
            order_type="MARKET",
            quantity=quantity,
        )
        assert order.status_code == 201
        orders.append(order)

    return orders


@pytest.mark.smoke
def test_portfolio_without_holdings(portfolio_service):
    response = portfolio_service.get_portfolio()

    assert response.status_code == 200
    assert response.body == {"cash": 1000000, "holdings": []}


@pytest.mark.regression
@pytest.mark.parametrize("market_buys", [[(1, 10)]], ids=["single_buy"], indirect=True)
def test_portfolio_with_holdings_schema(portfolio_service, market_buys):
    portfolio = portfolio_service.get_portfolio()
    holding = portfolio.body["holdings"][0]

    assert_holding_schema(holding)


@pytest.mark.regression
@pytest.mark.parametrize("market_buys", [[(1, 10)]], ids=["single_buy"], indirect=True)
def test_holding_after_market_buy(portfolio_service, market_buys):
    order = market_buys[0]

    portfolio = portfolio_service.get_portfolio()
    holding = portfolio.body["holdings"][0]

    assert holding["instrument_id"] == order.body["instrument_id"]
    assert holding["quantity"] == order.body["quantity"]
    assert holding["avg_cost_price"] == order.body["price"]


@pytest.mark.regression
@pytest.mark.parametrize(
    "market_buys", [[(1, 10), (1, 5)]], ids=["same_instrument_twice"], indirect=True
)
def test_check_avg_cost_price_and_unique_instrument_id(portfolio_service, market_buys):
    portfolio = portfolio_service.get_portfolio()
    assert_unique_field(portfolio.body["holdings"], "instrument_id")
    holding = portfolio.body["holdings"][0]

    assert_holding_reflects_purchases(holding, market_buys)


@pytest.mark.regression
@pytest.mark.parametrize("market_buys", [[(1, 5)]], ids=["single_buy"], indirect=True)
def test_partial_sell_keeps_avg_cost_price(
    orders_service, portfolio_service, market_buys
):
    instrument_id = market_buys[0].body["instrument_id"]

    portfolio_before = portfolio_service.get_portfolio()
    holding_before = portfolio_before.body["holdings"][0]

    sell = orders_service.create_order(
        instrument_id=instrument_id, side="SELL", order_type="MARKET", quantity=2
    )
    assert sell.status_code == 201

    portfolio_after = portfolio_service.get_portfolio()
    holding_after = portfolio_after.body["holdings"][0]

    assert holding_after["quantity"] == 3
    assert holding_after["avg_cost_price"] == holding_before["avg_cost_price"]


@pytest.mark.regression
@pytest.mark.parametrize(
    "market_buys", [[(2, 5), (3, 3)]], ids=["two_different_instruments"], indirect=True
)
def test_portfolio_with_multiple_holdings(portfolio_service, market_buys):
    portfolio = portfolio_service.get_portfolio()

    assert_unique_field(portfolio.body["holdings"], "instrument_id")
    holdings_by_id = {h["instrument_id"]: h for h in portfolio.body["holdings"]}

    assert len(portfolio.body["holdings"]) == 2
    assert holdings_by_id[2]["quantity"] == 5
    assert holdings_by_id[3]["quantity"] == 3


@pytest.mark.regression
@pytest.mark.parametrize("market_buys", [[(1, 5)]], ids=["single_buy"], indirect=True)
def test_full_sell_removes_holding(orders_service, portfolio_service, market_buys):
    instrument_id = market_buys[0].body["instrument_id"]

    sell = orders_service.create_order(
        instrument_id=instrument_id, side="SELL", order_type="MARKET", quantity=5
    )
    assert sell.status_code == 201

    portfolio = portfolio_service.get_portfolio()

    assert portfolio.body["holdings"] == []


@pytest.mark.regression
@pytest.mark.parametrize("market_buys", [[(1, 10)]], ids=["single_buy"], indirect=True)
def test_holding_market_value_is_derivable(
    instruments_service, portfolio_service, market_buys
):
    holding = portfolio_service.get_portfolio().body["holdings"][0]

    instruments_by_id = {i["id"]: i for i in instruments_service.get_instruments().body}
    instrument = instruments_by_id[holding["instrument_id"]]

    market_value = holding["quantity"] * holding["last_price"]

    assert holding["last_price"] == instrument["last_price"]
    assert market_value > 0


@pytest.mark.negative
def test_portfolio_without_candidate_id(portfolio_service):
    response = portfolio_service.get_portfolio(headers={"X-Candidate-Id": None})

    assert response.status_code == 400
    assert response.body["error"] == "Missing X-Candidate-Id header"


@pytest.mark.negative
@pytest.mark.parametrize(
    "bugs_tier_header", [None, "nightmare"], ids=["missing", "invalid"]
)
def test_portfolio_with_invalid_bugs_tier(portfolio_service, bugs_tier_header):
    response = portfolio_service.get_portfolio(
        headers={"X-Enable-Bugs": bugs_tier_header}
    )

    assert response.status_code == 400
    assert response.body["error"] == "X-Enable-Bugs must be off, easy, medium, or hard"
