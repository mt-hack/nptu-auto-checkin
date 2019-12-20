from os import remove
from sys import path
from time import sleep

from PIL import Image
from numpy import array
from selenium import webdriver

from .solver.captcha import get_captcha


def get_captcha_from_site():
    browser.save_screenshot("ScreenShot.png")
    image = browser.find_element_by_id("imgCaptcha")
    image_location = image.location
    image_size = image.size
    left = image_location["x"]
    top = image_location["y"]
    right = left + image_size["width"]
    bottom = top + image_size["height"]
    captcha = Image.open("ScreenShot.png").convert("L").crop((left, top, bottom, right))
    remove("ScreenShot.png")
    return array(captcha)


opts = webdriver.ChromeOptions()
browser = webdriver.Chrome(path[0] + "/ChromeDriver", options=opts)
browser.get("https://webap.nptu.edu.tw")
browser.set_window_size(1280, 720)
sleep(2.5)
browser.find_element_by_id("LoginDefault_ibtLoginStd").click()
sleep(2.5)

while True:
    browser.find_element_by_id("LoginStd_txtCheckCode").send_keys(get_captcha(get_captcha_from_site()))
    browser.find_element_by_id("LoginStd_txtAccount").send_keys("Account")
    browser.find_element_by_id("LoginStd_txtPassWord").send_keys("Password")
    browser.find_element_by_id("LoginStd_ibtLogin").click()
    sleep(2.5)

    try:
        Alert = browser.switch_to.alert

        if "驗證碼" in Alert.text:
            Alert.accept()
            continue
        else:
            print(Alert.text)
            break
    except:
        break
