import pytest

from conftest import DYCA_QUANTITY, DYCA_TICKER
from pages.portfolio_page import PortfolioPage


@pytest.mark.smoke
def test_portfolio_loads_correctly(driver):
    portfolio_page = PortfolioPage(driver)
    portfolio_page.open()

    assert portfolio_page.title().is_displayed()
    assert portfolio_page.total_value_label().is_displayed()
    assert portfolio_page.ganancia_label().is_displayed()
    assert portfolio_page.retorno_label().is_displayed()
    assert portfolio_page.costo_invertido_label().is_displayed()
    assert portfolio_page.efectivo_label().is_displayed()
    assert portfolio_page.posiciones_label().is_displayed()


@pytest.mark.regression
@pytest.mark.usefixtures("bought_dyca")
def test_market_buy_appears_in_portfolio(driver):
    portfolio_page = PortfolioPage(driver)
    portfolio_page.open()
    assert portfolio_page.position_row(DYCA_TICKER, DYCA_QUANTITY).is_displayed()


@pytest.mark.smoke
@pytest.mark.usefixtures("reset_state")
def test_portfolio_shows_empty_state_without_holdings(driver):
    portfolio_page = PortfolioPage(driver)
    portfolio_page.open()

    assert portfolio_page.empty_state_title().is_displayed()
    assert portfolio_page.empty_state_description().is_displayed()
