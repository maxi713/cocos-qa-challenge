from appium.webdriver.common.appiumby import AppiumBy

from .base_page import BasePage

PORTFOLIO_TAB = (AppiumBy.XPATH, '//*[@text="Portafolio"]')
PORTFOLIO_TITLE = (AppiumBy.XPATH, '(//*[@text="Portafolio"])[1]')
TOTAL_TITLE = (AppiumBy.XPATH, '//*[@text="VALOR TOTAL"]')
GANANCIA_TITLE = (AppiumBy.XPATH, '//*[@text="Ganancia"]')
RETORNO_TITLE = (AppiumBy.XPATH, '//*[@text="Retorno"]')
COSTO_INVERTIDO_TITLE = (AppiumBy.XPATH, '//*[@text="Costo invertido"]')
EFECTIVO_TITLE = (AppiumBy.XPATH, '//*[@text="Efectivo"]')
POSICIONES_TITLE = (AppiumBy.XPATH, '(//*[@text="Posiciones"])[1]')
EMPTY_STATE_TITLE = (
    AppiumBy.XPATH,
    '//*[@text="No hay posiciones en el portfolio"]',
)
EMPTY_STATE_DESCRIPTION = (
    AppiumBy.XPATH,
    '//*[@text="Cuando la API devuelva tenencias, van a aparecer en esta lista."]',
)


class PortfolioPage(BasePage):
    def open(self):
        self.driver.find_element(*PORTFOLIO_TAB).click()
        self.wait_visible(PORTFOLIO_TITLE)

    def title(self):
        return self.wait_visible(PORTFOLIO_TITLE)

    def total_value_label(self):
        return self.wait_visible(TOTAL_TITLE)

    def ganancia_label(self):
        return self.wait_visible(GANANCIA_TITLE)

    def retorno_label(self):
        return self.wait_visible(RETORNO_TITLE)

    def costo_invertido_label(self):
        return self.wait_visible(COSTO_INVERTIDO_TITLE)

    def efectivo_label(self):
        return self.wait_visible(EFECTIVO_TITLE)

    def posiciones_label(self):
        return self.wait_visible(POSICIONES_TITLE)

    def empty_state_title(self):
        return self.wait_visible(EMPTY_STATE_TITLE)

    def empty_state_description(self):
        return self.wait_visible(EMPTY_STATE_DESCRIPTION)

    def position_row(self, ticker, quantity):
        locator = (
            AppiumBy.XPATH,
            f'//*[starts-with(@content-desc, "{ticker}, cantidad {quantity}")]',
        )
        return self.wait_visible(locator)
