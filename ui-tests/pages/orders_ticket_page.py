from appium.webdriver.common.appiumby import AppiumBy

from .base_page import BasePage

TICKET_TITLE = (AppiumBy.XPATH, '//*[@text="Nueva orden"]')
QUANTITY_INPUT = (AppiumBy.ACCESSIBILITY_ID, "Cantidad de acciones")
SUBMIT_BUTTON = (AppiumBy.XPATH, '//*[@text="Enviar orden"]')
SUBMIT_BUTTON_AFTER_RESULT = (AppiumBy.XPATH, '//*[@text="Enviar otra orden"]')
QUANTITY_REQUIRED_ERROR = (
    AppiumBy.XPATH,
    '//*[@text="Ingresá una cantidad de acciones."]',
)


class OrdersTicketPage(BasePage):
    def title(self):
        return self.wait_visible(TICKET_TITLE)

    def set_quantity(self, quantity):
        field = self.wait_visible(QUANTITY_INPUT)
        field.send_keys(str(quantity))

    def submit(self):
        self.dismiss_dev_warning_if_present()
        self.driver.find_element(*SUBMIT_BUTTON).click()

    def wait_for_result(self):
        self.wait_visible(SUBMIT_BUTTON_AFTER_RESULT)

    def quantity_required_error(self):
        return self.wait_visible(QUANTITY_REQUIRED_ERROR)

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
