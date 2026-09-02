import subprocess

import pytest
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

APPIUM_SERVER_URL = "http://127.0.0.1:4723"
APP_PACKAGE = "com.cocos.trading"
APP_ACTIVITY = ".MainActivity"

API_URL = "https://dummy-api-topaz.vercel.app"
CANDIDATE_ID = "maxi2161"


@pytest.fixture()
def reset_state():
    requests.post(
        f"{API_URL}/reset",
        headers={"X-Candidate-Id": CANDIDATE_ID, "X-Enable-Bugs": "off"},
    )


def _restart_app():
    subprocess.run(["adb", "shell", "am", "force-stop", APP_PACKAGE], check=True)
    subprocess.run(
        ["adb", "shell", "am", "start", "-n", f"{APP_PACKAGE}/{APP_ACTIVITY}"],
        check=True,
    )


@pytest.fixture()
def driver():
    _restart_app()

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android Emulator"
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.no_reset = True

    drv = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    WebDriverWait(drv, 30).until(
        EC.presence_of_element_located((AppiumBy.XPATH, '//*[@text="Mercados"]'))
    )
    yield drv
    drv.quit()
