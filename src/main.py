import logging
import random
import string
import tempfile
from pathlib import Path
from sys import exit

from PIL import Image
from numpy import array
from selenium import common, webdriver

import webdriver as wd_manager
from error import InvalidCredentialsError, TooManyAttemptsError
from solver.captcha import get_captcha_text


def get_random_png(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length)) + ".png"


def configure_logging():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def get_captcha(browser_instance):
    temp_dir = tempfile.gettempdir()
    temp_file = str(Path(temp_dir, get_random_png(15)))
    if browser_instance.save_screenshot(temp_file):
        image = browser_instance.find_element_by_id("imgCaptcha")
        left = image.location["x"]
        top = image.location["y"]
        right = left + image.size["width"]
        bottom = top + image.size["height"]
        captcha = Image \
            .open(temp_file) \
            .convert('L') \
            .crop((left, top, right, bottom))
        return get_captcha_text(array(captcha))
    else:
        raise IOError("Failed to save a screenshot of the login page.")


configure_logging()
webdriver_file = wd_manager.get_driver_package()
opts = webdriver.ChromeOptions()
try:
    browser = webdriver.Chrome(webdriver_file, options=opts)
except common.exceptions.WebDriverException:
    logging.critical("You must install Chrome before running this!")
    exit(1)
browser.get("https://webap.nptu.edu.tw")
browser.set_window_size(1280, 720)
browser.find_element_by_id("LoginDefault_ibtLoginStd").click()

for attempt in range(1, 5):
    try:
        logging.info(f"Attempting to login... [Attempt: {attempt}/5]")
        browser.find_element_by_id("LoginStd_txtCheckCode").send_keys(get_captcha(browser))
        browser.find_element_by_id("LoginStd_txtAccount").send_keys("Account")
        browser.find_element_by_id("LoginStd_txtPassWord").send_keys("Password")
        browser.find_element_by_id("LoginStd_ibtLogin").click()
        alert = browser.switch_to.alert
        if "驗證碼" in alert.text:
            alert.accept()
        if "帳號或密碼錯誤" in alert.text:
            raise InvalidCredentialsError("Username or password incorrect.")
        if "錯誤超過三次" in alert.text:
            raise TooManyAttemptsError('Too many login attempts detected. Try again in 15 minutes.')
    except common.exceptions.UnexpectedAlertPresentException as alert_exception:
        logging.debug(alert_exception.alert_text)
        continue
    except (InvalidCredentialsError, TooManyAttemptsError) as exception:
        logging.critical(exception.message)
        break
