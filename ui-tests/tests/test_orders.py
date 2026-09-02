import pytest

from pages.orders_page import OrdersPage


@pytest.mark.smoke
def test_orders_loads_correctly(driver):
    orders_page = OrdersPage(driver)
    orders_page.open()

    assert orders_page.title().is_displayed()
    assert orders_page.actividad_label().is_displayed()
