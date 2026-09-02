from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

SEARCH_TAB = (AppiumBy.XPATH, '//*[@text="Buscar"]')
SEARCH_INPUT = (AppiumBy.ACCESSIBILITY_ID, "Buscar ticker")
SEARCH_TITLE = (AppiumBy.XPATH, '//*[@text="Buscar activos"]')
TICKER_LABEL = (AppiumBy.XPATH, '//*[@text="TICKER O EMPRESA"]')


class SearchPage(BasePage):
    def open(self):
        self.driver.find_element(*SEARCH_TAB).click()
        self.wait.until(EC.element_to_be_clickable(SEARCH_INPUT))

    def title(self):
        return self.wait_visible(SEARCH_TITLE)

    def ticker_label(self):
        return self.wait_visible(TICKER_LABEL)

    def search(self, query):
        self.driver.find_element(*SEARCH_INPUT).send_keys(query)

    def result_row(self, ticker):
        locator = (AppiumBy.XPATH, f'//*[starts-with(@content-desc, "{ticker}")]')
        return self.wait_visible(locator)
