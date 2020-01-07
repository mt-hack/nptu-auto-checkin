import logging
import os
import time
from getpass import getpass
from sys import exit
from urllib.parse import urljoin

import schedule
import selenium.common.exceptions as selenium_exceptions
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import webdriver as wd_manager
from config import Config as WDConfig
from error import PreAuthenticationError, PostAuthenticationError
from schedule_builder import get_jobs
from solver.captcha import get_captcha_from_browser


def configure_logging():
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def logout(browser):
    logout_element = browser.find_element_by_id('CommonHeader_ibtLogOut')
    if logout_element:
        try:
            logout_element.click()
            WebDriverWait(browser, 3).until(expected_conditions.alert_is_present(), None)
            alert = browser.switch_to.alert
            if "確定" in alert.text or "太久" in alert.text:
                alert.accept()
                logging.info("Logged out.")
        except selenium_exceptions.TimeoutException:
            raise PostAuthenticationError("Logout prompt expected but not found.")
    else:
        raise PostAuthenticationError("Logout button not found.")


def checkin(browser, is_check_in, job_description):
    try:
        browser.get(urljoin(browser.current_url, '../B40/B4001SPage.aspx'))
        WebDriverWait(browser, 3).until(expected_conditions.alert_is_present(), None)
        alert = browser.switch_to.alert
        if "請先設定" in alert.text:
            alert.accept()
            # raise PostAuthenticationError(
            #    "Contract duration not set. Please set it first manually before attempting to check-in.")
    except PostAuthenticationError as exception:
        logging.critical(exception)
        logout(browser)
        return
    except selenium_exceptions.TimeoutException:
        pass
    try:
        if is_check_in is None:
            is_check_in = browser.find_element_by_id('B4001A_lblIN').text == ""

        if is_check_in:
            checkin_button = browser.find_element_by_name('B4001A:btnIN')
            if not checkin_button:
                raise PostAuthenticationError("Check-in button cannot be found.")
            checkin_button.click()
        else:
            checkout_button = browser.find_element_by_name('B4001A:btnOFF')
            work_description_field = browser.find_element_by_name("B4001A:txtJOB_NOTES")
            if not checkout_button:
                raise PostAuthenticationError("Check-out button cannot be found.")
            if not work_description_field:
                raise PostAuthenticationError("Work description field cannot be found.")
            work_description_field.send_keys(job_description)
            checkout_button.click()
        
        try:
            WebDriverWait(browser, 3).until(expected_conditions.alert_is_present(),
                                            "Expected a logout prompt, got nothing.")
            alert = browser.switch_to.alert
            logging.info(alert.text)
            alert.accept()
        except selenium_exceptions.TimeoutException as exception:
            logging.critical(exception)
            pass
    except PostAuthenticationError as exception:
        logging.critical(exception)
    finally:
        logout(browser)


def begin_checkin(username, password, is_check_in, job_description):
    webdriver_file = wd_manager.get_driver_package()
    options = webdriver.ChromeOptions()
    options.add_argument('--force-device-scale-factor=1')
    try:
        browser = webdriver.Chrome(webdriver_file, options=options)
    except selenium_exceptions.WebDriverException:
        logging.critical("You must install Chrome before running this!")
        exit(1)
    browser.get("https://webap.nptu.edu.tw/web/Secure/default.aspx")
    browser.set_window_size(1280, 720)
    login_page_button = browser.find_element_by_id("LoginDefault_ibtLoginStd")
    if not login_page_button:
        logging.critical("NPTU page cannot be reached at the moment.")
        return
    login_page_button.click()

    for attempt in range(1, WDConfig.attempts):
        try:
            logging.info(f"Attempting to login... [Attempt: {attempt}/{WDConfig.attempts}]")
            captcha = get_captcha_from_browser(browser)
            captcha_field = browser.find_element_by_id("LoginStd_txtCheckCode")
            captcha_field.clear()
            user_field = browser.find_element_by_id("LoginStd_txtAccount")
            user_field.clear()
            password_field = browser.find_element_by_id("LoginStd_txtPassWord")
            user_field.clear()
            WebDriverWait(browser, 1)
            user_field.send_keys(username)
            captcha_field.send_keys(captcha)
            password_field.send_keys(password)
            browser.find_element_by_id("LoginStd_ibtLogin").click()
            WebDriverWait(browser, 3).until(expected_conditions.alert_is_present(),
                                            "Expected alert from the login page.")
            alert = browser.switch_to.alert
            if "驗證碼不符" in alert.text:
                alert.accept()
                continue
            if "驗證碼未輸入" in alert.text:
                raise PreAuthenticationError("Tesseract is not working correctly.")
            if "帳號或密碼錯誤" in alert.text:
                raise PreAuthenticationError("Username or password incorrect.")
            if "非正常狀態下登出" in alert.text:
                raise PreAuthenticationError("User is already logged in. Try again in 15 minutes.")
            if "錯誤超過三次" in alert.text:
                raise PreAuthenticationError('Too many login attempts detected. Try again in 15 minutes.')
        except PreAuthenticationError as exception:
            logging.critical(exception.message)
            break
        except selenium_exceptions.TimeoutException:
            logging.info('Logged in.')
            checkin(browser, is_check_in, job_description)
            break
    try:
        browser.close()
    except:
        pass


def main():
    configure_logging()
    username = WDConfig.username
    password = WDConfig.password
    if username is None or password is None:
        username = input("Enter your username:")
        password = getpass("Enter your password:")
        begin_checkin(username, password, None, "處理相關指定之事務。")
    else:
        jobs = get_jobs()
        # implement json parsing and use the schedule package

        for job in jobs:
            if job['DayOfWeek'] == 0:
                schedule.every().monday.at(job['StartTime']).do(begin_checkin,
                                                                [username, password, True, None])
                schedule.every().monday.at(job['EndTime']).do(begin_checkin,
                                                              [username, password, False, job['WorkDescription']])
            if job['DayOfWeek'] == 1:
                schedule.every().tuesday.at(job['StartTime']).do(begin_checkin,
                                                                 [username, password, True, None])
                schedule.every().tuesday.at(job['EndTime']).do(begin_checkin,
                                                               [username, password, False, job['WorkDescription']])
            if job['DayOfWeek'] == 2:
                schedule.every().wednesday.at(job['StartTime']).do(begin_checkin,
                                                                   [username, password, True, None])
                schedule.every().wednesday.at(job['EndTime']).do(begin_checkin,
                                                                 [username, password, False, job['WorkDescription']])
            if job['DayOfWeek'] == 3:
                schedule.every().thursday.at(job['StartTime']).do(begin_checkin,
                                                                  [username, password, True, None])
                schedule.every().thursday.at(job['EndTime']).do(begin_checkin,
                                                                [username, password, False, job['WorkDescription']])
            if job['DayOfWeek'] == 4:
                schedule.every().friday.at(job['StartTime']).do(begin_checkin,
                                                                [username, password, True, None])
                schedule.every().friday.at(job['EndTime']).do(begin_checkin,
                                                              [username, password, False, job['WorkDescription']])
            if job['DayOfWeek'] == 5:
                schedule.every().saturday.at(job['StartTime']).do(begin_checkin,
                                                                [username, password, True, None])
                schedule.every().saturday.at(job['EndTime']).do(begin_checkin,
                                                              [username, password, False, job['WorkDescription']])
            if job['DayOfWeek'] == 6:
                schedule.every().sunday.at(job['StartTime']).do(begin_checkin,
                                                                [username, password, True, None])
                schedule.every().sunday.at(job['EndTime']).do(begin_checkin,
                                                              [username, password, False, job['WorkDescription']])
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    main()
