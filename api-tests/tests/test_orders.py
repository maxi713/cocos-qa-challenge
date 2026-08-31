import pytest
from assertions.order_assertions import assert_order_schema
from utils.polling import wait_for_order_resolution

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


@pytest.mark.regression
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


@pytest.mark.regression
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


@pytest.mark.regression
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


_LIMIT_PENDING_SKIP_REASON = (
    "No se puede testear de forma confiable: una LIMIT puede pasar de "
    "PENDING a FILLED/REJECTED en milisegundos, ni bien se crea. No hay "
    "forma de forzarla a quedarse en PENDING para chequear la reserva. "
    "Hallazgo de testability, pendiente de preguntarle a devs si se puede "
    "exponer algo para simular esto."
)


@pytest.mark.regression
@pytest.mark.skip(reason=_LIMIT_PENDING_SKIP_REASON)
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


@pytest.mark.regression
@pytest.mark.skip(reason=_LIMIT_PENDING_SKIP_REASON)
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


_LIMIT_RESOLUTION_SKIP_REASON = (
    "No hay forma de garantizar a que estado resuelve una LIMIT: probe "
    "con price = 2x el precio real y aun asi salio ~50/50 entre FILLED y "
    "REJECTED. Hallazgo de testability, pendiente de preguntarle a devs si "
    "se puede forzar el resultado de alguna manera."
)


@pytest.mark.regression
@pytest.mark.skip(reason=_LIMIT_RESOLUTION_SKIP_REASON)
def test_limit_buy_order_resolves_to_filled(orders_service, portfolio_service):
    portfolio = portfolio_service.get_portfolio()

    order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="LIMIT", quantity=1, price=91.44
    )
    resolved = wait_for_order_resolution(orders_service, order.body["id"], timeout=2)

    assert resolved["status"] == "FILLED"

    portfolio_after = portfolio_service.get_portfolio()
    assert portfolio_after.body["cash"] == portfolio.body["cash"] - (
        resolved["quantity"] * resolved["price"]
    )
    assert portfolio_after.body["holdings"][0]["quantity"] == resolved["quantity"]


@pytest.mark.regression
@pytest.mark.skip(reason=_LIMIT_RESOLUTION_SKIP_REASON)
def test_limit_buy_order_resolves_to_rejected(orders_service, portfolio_service):
    portfolio = portfolio_service.get_portfolio()

    order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="LIMIT", quantity=1, price=91.44
    )
    resolved = wait_for_order_resolution(orders_service, order.body["id"], timeout=2)

    assert resolved["status"] == "REJECTED"

    portfolio_after = portfolio_service.get_portfolio()
    assert portfolio_after.body["cash"] == portfolio.body["cash"]
    assert portfolio_after.body["holdings"] == portfolio.body["holdings"]


@pytest.mark.negative
@pytest.mark.parametrize(
    "instrument_id, side, order_type, quantity, price, expected_error",
    [
        (1, "BUY", "MARKET", 0, None, "quantity must be a positive number"),
        (1, "BUY", "MARKET", -1, None, "quantity must be a positive number"),
        (1, "BUY", "MARKET", 1.5, None, "quantity must be a positive integer"),
        (1, "HOLD", "MARKET", 1, None, "side must be BUY or SELL"),
        (1, "BUY", "STOP", 1, None, "type must be MARKET or LIMIT"),
        (99999, "BUY", "MARKET", 1, None, "Instrument not found"),
        pytest.param(
            1, "BUY", "LIMIT", 1, 0, "TODO: confirm real message once Bug 4 is fixed",
            marks=pytest.mark.xfail(
                reason="Bug 4: LIMIT acepta price <= 0 en vez de dar 400",
                strict=True,
            ),
        ),
        pytest.param(
            1, "BUY", "LIMIT", 1, -10, "TODO: confirm real message once Bug 4 is fixed",
            marks=pytest.mark.xfail(
                reason="Bug 4: LIMIT acepta price <= 0 en vez de dar 400",
                strict=True,
            ),
        ),
    ],
    ids=[
        "zero_quantity",
        "negative_quantity",
        "fractional_quantity",
        "invalid_side",
        "invalid_type",
        "nonexistent_instrument",
        "zero_price",
        "negative_price",
    ],
)
def test_create_order_with_invalid_fields(
    orders_service, instrument_id, side, order_type, quantity, price, expected_error
):
    response = orders_service.create_order(
        instrument_id=instrument_id,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )

    assert response.status_code == 400
    assert response.body["error"] == expected_error


@pytest.mark.negative
@pytest.mark.parametrize(
    "payload",
    [
        {"instrument_id": 1, "side": "BUY", "type": "MARKET"},
        {"instrument_id": 1, "side": "BUY", "type": "LIMIT", "quantity": 1},
        {"side": "BUY", "type": "MARKET", "quantity": 1},
    ],
    ids=["missing_quantity", "missing_price_on_limit", "missing_instrument_id"],
)
def test_create_order_with_missing_field(orders_service, payload):
    response = orders_service.create_order_with_payload(payload)

    assert response.status_code == 400


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


@pytest.mark.negative
def test_sell_without_holdings(orders_service):
    response = orders_service.create_order(
        instrument_id=1, side="SELL", order_type="MARKET", quantity=1
    )

    assert response.status_code == 400
    assert response.body["error"] == "Insufficient shares"


@pytest.mark.negative
def test_buy_without_enough_cash(orders_service):
    response = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="MARKET", quantity=999999999
    )

    assert response.status_code == 400
    assert response.body["error"] == "Insufficient cash"


@pytest.mark.negative
def test_create_order_without_candidate_id(orders_service):
    response = orders_service.create_order(
        instrument_id=1,
        side="BUY",
        order_type="MARKET",
        quantity=1,
        headers={"X-Candidate-Id": None},
    )

    assert response.status_code == 400


@pytest.mark.negative
@pytest.mark.parametrize(
    "bugs_tier_header", [None, "algo_random"], ids=["missing", "invalid"]
)
def test_create_order_with_invalid_bugs_tier(orders_service, bugs_tier_header):
    response = orders_service.create_order(
        instrument_id=1,
        side="BUY",
        order_type="MARKET",
        quantity=1,
        headers={"X-Enable-Bugs": bugs_tier_header},
    )

    assert response.status_code == 400


@pytest.mark.regression
def test_market_order_ignores_submitted_price(orders_service, instruments_service):
    real_price = next(
        i for i in instruments_service.get_instruments().body if i["id"] == 1
    )["last_price"]

    response = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="MARKET", quantity=1, price=999999
    )

    assert response.status_code == 201
    assert response.body["price"] == real_price


@pytest.mark.regression
@pytest.mark.skip(reason=_LIMIT_PENDING_SKIP_REASON)
def test_limit_buy_orders_cumulative_reservation_exceeds_cash(orders_service):
    first_order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="LIMIT", quantity=6000, price=100
    )
    second_order = orders_service.create_order(
        instrument_id=1, side="BUY", order_type="LIMIT", quantity=5000, price=100
    )

    assert first_order.status_code == 201
    assert second_order.status_code == 400
    assert second_order.body["error"] == "Insufficient cash"
