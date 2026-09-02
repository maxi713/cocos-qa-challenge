from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEV_WARNING_BANNER = (AppiumBy.XPATH, '//*[contains(@content-desc, "Open debugger")]')
DEV_WARNING_CLOSE_BUTTON = (
    AppiumBy.XPATH,
    '//*[contains(@content-desc, "Open debugger")]/android.view.ViewGroup[4]',
)


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_visible(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def dismiss_dev_warning_if_present(self):
        if self.driver.find_elements(*DEV_WARNING_BANNER):
            self.driver.find_element(*DEV_WARNING_CLOSE_BUTTON).click()
