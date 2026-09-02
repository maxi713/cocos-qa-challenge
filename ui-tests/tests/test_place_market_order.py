import pytest

from pages.orders_page import OrdersPage
from pages.orders_ticket_page import OrdersTicketPage
from pages.search_page import SearchPage

TICKER = "DYCA"
QUANTITY = 1


@pytest.mark.regression
@pytest.mark.usefixtures("reset_state")
def test_market_buy_appears_in_orders_history(driver):
    search_page = SearchPage(driver)
    search_page.open()
    search_page.search(TICKER)
    search_page.result_row(TICKER).click()

    ticket_page = OrdersTicketPage(driver)
    ticket_page.set_quantity(QUANTITY)
    ticket_page.submit()
    ticket_page.wait_for_result()
    ticket_page.dismiss()

    orders_page = OrdersPage(driver)
    orders_page.open()
    history_row = orders_page.history_row(TICKER)
    assert history_row.is_displayed()
