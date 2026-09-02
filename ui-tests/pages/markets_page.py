from appium.webdriver.common.appiumby import AppiumBy

from .base_page import BasePage

MARKETS_TAB = (AppiumBy.XPATH, '//*[@text="Mercados"]')
MARKETS_TITLE = (AppiumBy.XPATH, '(//*[@text="Mercados"])[1]')
MARKETS_TOTAL_TITLE = (AppiumBy.XPATH, '//*[@text="Total"]')
SUBEN_TITLE = (AppiumBy.XPATH, '//*[@text="Suben"]')
BAJAN_TITLE = (AppiumBy.XPATH, '//*[@text="Bajan"]')


class MarketsPage(BasePage):
    def open(self):
        self.driver.find_element(*MARKETS_TAB).click()
        self.wait_visible(MARKETS_TITLE)

    def title(self):
        return self.wait_visible(MARKETS_TITLE)

    def total_label(self):
        return self.wait_visible(MARKETS_TOTAL_TITLE)

    def suben_label(self):
        return self.wait_visible(SUBEN_TITLE)

    def bajan_label(self):
        return self.wait_visible(BAJAN_TITLE)

    def first_instrument_row(self):
        locator = (
            AppiumBy.XPATH,
            '(//*[contains(@content-desc, "ultimo precio")])[1]',
        )
        return self.wait_visible(locator)
