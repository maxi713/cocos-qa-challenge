from appium.webdriver.common.appiumby import AppiumBy

from .base_page import BasePage

ORDERS_TAB = (AppiumBy.XPATH, '//*[@text="Órdenes"]')
ORDERS_TITLE = (AppiumBy.XPATH, '(//*[@text="Órdenes"])[1]')
ACTIVIDAD_LABEL = (AppiumBy.XPATH, '//*[@text="ACTIVIDAD"]')


class OrdersPage(BasePage):
    def open(self):
        self.driver.find_element(*ORDERS_TAB).click()
        self.wait_visible(ORDERS_TITLE)

    def title(self):
        return self.wait_visible(ORDERS_TITLE)

    def actividad_label(self):
        return self.wait_visible(ACTIVIDAD_LABEL)

    def history_row(self, ticker):
        locator = (AppiumBy.XPATH, f'//*[contains(@content-desc, "{ticker} a ")]')
        return self.wait_visible(locator)
