from appium.webdriver.common.appiumby import AppiumBy

from .base_page import BasePage

QUANTITY_INPUT = (AppiumBy.ACCESSIBILITY_ID, "Cantidad de acciones")
SUBMIT_BUTTON = (AppiumBy.XPATH, '//*[@text="Enviar orden"]')
SUBMIT_BUTTON_AFTER_RESULT = (AppiumBy.XPATH, '//*[@text="Enviar otra orden"]')


class OrdersTicketPage(BasePage):
    def set_quantity(self, quantity):
        field = self.wait_visible(QUANTITY_INPUT)
        field.send_keys(str(quantity))

    def submit(self):
        self.driver.find_element(*SUBMIT_BUTTON).click()

    def wait_for_result(self):
        self.wait_visible(SUBMIT_BUTTON_AFTER_RESULT)

    def dismiss(self):
        size = self.driver.get_window_size()
        width, height = size["width"], size["height"]
        self.driver.execute_script(
            "mobile: swipeGesture",
            {
                "left": 0,
                "top": int(height * 0.6),
                "width": width,
                "height": int(height * 0.35),
                "direction": "down",
                "percent": 1.0,
            },
        )
