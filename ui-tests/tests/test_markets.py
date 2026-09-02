import pytest

from pages.markets_page import MarketsPage


@pytest.mark.smoke
def test_markets_loads_correctly(driver):
    markets_page = MarketsPage(driver)
    markets_page.open()

    assert markets_page.title().is_displayed()
    assert markets_page.total_label().is_displayed()
    assert markets_page.suben_label().is_displayed()
    assert markets_page.bajan_label().is_displayed()
