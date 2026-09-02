import pytest

from conftest import DYCA_TICKER
from pages.orders_page import OrdersPage
from pages.orders_ticket_page import OrdersTicketPage
from pages.search_page import SearchPage


@pytest.mark.smoke
def test_orders_loads_correctly(driver):
    orders_page = OrdersPage(driver)
    orders_page.open()

    assert orders_page.title().is_displayed()
    assert orders_page.actividad_label().is_displayed()


@pytest.mark.regression
@pytest.mark.usefixtures("bought_dyca")
def test_market_buy_appears_in_orders_history(driver):
    orders_page = OrdersPage(driver)
    orders_page.open()
    assert orders_page.history_row(DYCA_TICKER).is_displayed()


@pytest.mark.negative
def test_submit_without_quantity_shows_required_error(driver):
    search_page = SearchPage(driver)
    search_page.open()
    search_page.search(DYCA_TICKER)
    search_page.result_row(DYCA_TICKER).click()

    ticket_page = OrdersTicketPage(driver)
    ticket_page.submit()
    assert ticket_page.quantity_required_error().is_displayed()
