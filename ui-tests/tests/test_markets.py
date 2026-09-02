import pytest

from pages.markets_instrument_detail_page import MarketsInstrumentDetailPage
from pages.markets_page import MarketsPage
from pages.orders_ticket_page import OrdersTicketPage


@pytest.mark.smoke
def test_markets_loads_correctly(driver):
    markets_page = MarketsPage(driver)
    markets_page.open()

    assert markets_page.title().is_displayed()
    assert markets_page.total_label().is_displayed()
    assert markets_page.suben_label().is_displayed()
    assert markets_page.bajan_label().is_displayed()


@pytest.mark.regression
def test_first_instrument_opens_detail_page(driver):
    markets_page = MarketsPage(driver)
    markets_page.open()
    markets_page.first_instrument_row().click()

    detail_page = MarketsInstrumentDetailPage(driver)
    assert detail_page.back_button().is_displayed()
    assert detail_page.cierre_anterior_label().is_displayed()
    assert detail_page.operar_button().is_displayed()


@pytest.mark.regression
def test_operar_ahora_opens_from_instrument_detail_page(driver):
    markets_page = MarketsPage(driver)
    markets_page.open()
    markets_page.first_instrument_row().click()

    detail_page = MarketsInstrumentDetailPage(driver)
    detail_page.tap_operar_ahora()

    ticket_page = OrdersTicketPage(driver)
    assert ticket_page.title().is_displayed()


@pytest.mark.regression
def test_back_button_returns_to_markets_home(driver):
    markets_page = MarketsPage(driver)
    markets_page.open()
    markets_page.first_instrument_row().click()

    detail_page = MarketsInstrumentDetailPage(driver)
    detail_page.back_button().click()

    assert markets_page.title().is_displayed()
