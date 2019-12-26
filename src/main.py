import logging
import sys
from getpass import getpass
from sys import exit

import selenium.common.exceptions as selenium_exceptions
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import webdriver as wd_manager
from config import Config as WDConfig
from error import InvalidCredentialsError, TooManyAttemptsError, TesseractError
from solver.captcha import get_captcha_from_browser


def configure_logging():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def main():
    username = WDConfig.username
    password = WDConfig.password
    if username is None:
        username = input("Enter your username:")
    if password is None:
        password = getpass("Enter your password:")
    configure_logging()
    webdriver_file = wd_manager.get_driver_package()
    opts = webdriver.ChromeOptions()
    try:
        browser = webdriver.Chrome(webdriver_file, options=opts)
    except selenium_exceptions.WebDriverException:
        logging.critical("You must install Chrome before running this!")
        exit(1)
    browser.get("https://webap.nptu.edu.tw")
    browser.set_window_size(1280, 720)
    browser.find_element_by_id("LoginDefault_ibtLoginStd").click()

    for attempt in range(1, WDConfig.attempts):
        try:
            logging.info(f"Attempting to login... [Attempt: {attempt}/{WDConfig.attempts}]")
            browser.find_element_by_id("LoginStd_txtCheckCode").send_keys(get_captcha_from_browser(browser))
            browser.find_element_by_id("LoginStd_txtAccount").send_keys(username)
            browser.find_element_by_id("LoginStd_txtPassWord").send_keys(password)
            browser.find_element_by_id("LoginStd_ibtLogin").click()
            WebDriverWait(browser, 3).until(expected_conditions.alert_is_present(), "Expected alert from the login page.")
            alert = browser.switch_to.alert
            if "驗證碼不符" in alert.text:
                alert.accept()
                continue
            if "驗證碼未輸入" in alert.text:
                raise TesseractError("Tesseract is not working correctly.")
            if "帳號或密碼錯誤" in alert.text:
                raise InvalidCredentialsError("Username or password incorrect.")
            if "錯誤超過三次" in alert.text:
                raise TooManyAttemptsError('Too many login attempts detected. Try again in 15 minutes.')
        except (InvalidCredentialsError, TooManyAttemptsError) as exception:
            logging.critical(exception.message)
            sys.exit(1)
        # No alerts, assume logged-in
        except selenium_exceptions.TimeoutException:
            break

if __name__ == '__main__':
    main()
