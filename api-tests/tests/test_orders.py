import pytest
from assertions.order_assertions import assert_order_schema

pytestmark = pytest.mark.usefixtures("reset_state")


@pytest.fixture
def portfolio_with_existing_holding(orders_service, portfolio_service):
    order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="MARKET", quantity=10
    )
    assert order.status_code == 201

    return portfolio_service.get_portfolio()


@pytest.mark.smoke
def test_market_buy_order_is_filled_immediately(orders_service):
    response = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="MARKET", quantity=10
    )

    assert response.status_code == 201
    assert_order_schema(response.body)
    assert response.body["status"] == "FILLED"
    assert response.body["side"] == "BUY"
    assert response.body["type"] == "MARKET"
    assert response.body["instrument_id"] == 1
    assert response.body["quantity"] == 10


def test_market_buy(orders_service, portfolio_service):
    portfolio = portfolio_service.get_portfolio()

    create_order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="MARKET", quantity=10
    )
    portfolio_after = portfolio_service.get_portfolio()

    assert create_order.status_code == 201
    assert portfolio_after.body["cash"] == portfolio.body["cash"] - (
        create_order.body["price"] * create_order.body["quantity"]
    )
    assert portfolio_after.body["holdings"][0]["quantity"] == 10


def test_market_sell(
    orders_service, portfolio_service, portfolio_with_existing_holding
):
    portfolio = portfolio_with_existing_holding

    create_order = orders_service.create_order(
        instrument_id=1, side="SELL", order_type="MARKET", quantity=1
    )
    portfolio_after = portfolio_service.get_portfolio()

    assert create_order.status_code == 201
    assert_order_schema(create_order.body)
    assert portfolio_after.body["cash"] == portfolio.body["cash"] + (
        create_order.body["price"] * create_order.body["quantity"]
    )
    assert (
        portfolio_after.body["holdings"][0]["quantity"]
        == portfolio.body["holdings"][0]["quantity"] - 1
    )


def test_limit_buy_order_is_pending(orders_service):
    response = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="LIMIT", quantity=6, price=30.0
    )

    assert response.status_code == 201
    assert_order_schema(response.body)
    assert response.body["status"] == "PENDING"
    assert response.body["price"] == 30.0
    assert response.body["side"] == "BUY"
    assert response.body["type"] == "LIMIT"
    assert response.body["instrument_id"] == 1
    assert response.body["quantity"] == 6


@pytest.mark.skip(
    reason=(
        "Flaky por diseño del sistema: una orden LIMIT puede resolver "
        "(FILLED/REJECTED) en milisegundos despues de creada, incluso "
        "consultando el status en la siguiente llamada inmediata sin demora "
        "artificial. No hay forma de forzar o congelar el estado PENDING para "
        "verificar la reserva de forma aislada. Reportado como hallazgo de "
        "testability, pendiente de definir con devs si se puede exponer un "
        "modo test/mock para esto."
    )
)
def test_limit_buy_reserves_cash_while_pending(orders_service, portfolio_service):
    portfolio = portfolio_service.get_portfolio()

    order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="LIMIT", quantity=6, price=30.0
    )
    portfolio_after = portfolio_service.get_portfolio()

    assert order.status_code == 201
    assert order.body["status"] == "PENDING"
    assert portfolio_after.body["cash"] == portfolio.body["cash"] - (
        order.body["quantity"] * order.body["price"]
    )
    assert portfolio_after.body["holdings"] == portfolio.body["holdings"]


@pytest.mark.skip(
    reason=(
        "Flaky por diseño del sistema: una orden LIMIT puede resolver "
        "(FILLED/REJECTED) en milisegundos despues de creada, incluso "
        "consultando el status en la siguiente llamada inmediata sin demora "
        "artificial. No hay forma de forzar o congelar el estado PENDING para "
        "verificar la reserva de forma aislada. Reportado como hallazgo de "
        "testability, pendiente de definir con devs si se puede exponer un "
        "modo test/mock para esto."
    )
)
def test_limit_sell_reserves_holdings_while_pending(
    orders_service, portfolio_service, portfolio_with_existing_holding
):
    portfolio = portfolio_with_existing_holding

    order = orders_service.create_order(
        instrument_id=1, side="SELL", order_type="LIMIT", quantity=1, price=60.0
    )
    portfolio_after = portfolio_service.get_portfolio()

    assert order.status_code == 201
    assert order.body["status"] == "PENDING"
    assert portfolio_after.body["cash"] == portfolio.body["cash"]
    assert (
        portfolio_after.body["holdings"][0]["quantity"]
        == portfolio.body["holdings"][0]["quantity"] - 1
    )


@pytest.mark.smoke
def test_get_orders_returns_the_created_order(orders_service):
    created_order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="MARKET", quantity=5
    ).body

    response = orders_service.get_orders()

    assert response.status_code == 200
    assert len(response.body) == 1
    assert_order_schema(response.body[0])
    assert response.body[0] == created_order
