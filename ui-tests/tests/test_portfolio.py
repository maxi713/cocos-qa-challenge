import pytest

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
