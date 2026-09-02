import pytest

from pages.search_page import SearchPage

TICKER = "DYCA"


@pytest.mark.smoke
def test_search_loads_correctly(driver):
    search_page = SearchPage(driver)
    search_page.open()

    assert search_page.title().is_displayed()
    assert search_page.ticker_label().is_displayed()


@pytest.mark.regression
def test_search_finds_ticker(driver):
    search_page = SearchPage(driver)
    search_page.open()
    search_page.search(TICKER)

    result = search_page.result_row(TICKER)
    assert result.is_displayed()
