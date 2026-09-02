from appium.webdriver.common.appiumby import AppiumBy

from .base_page import BasePage

BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Volver a mercados")
CIERRE_ANTERIOR_LABEL = (AppiumBy.XPATH, '//*[@text="Cierre anterior"]')
OPERAR_BUTTON = (AppiumBy.XPATH, '//*[@text="Operar ahora"]')


class MarketsInstrumentDetailPage(BasePage):
    def back_button(self):
        return self.wait_visible(BACK_BUTTON)

    def cierre_anterior_label(self):
        return self.wait_visible(CIERRE_ANTERIOR_LABEL)

    def operar_button(self):
        return self.wait_visible(OPERAR_BUTTON)

    def tap_operar_ahora(self):
        self.operar_button()
        self.dismiss_dev_warning_if_present()
        self.operar_button().click()
