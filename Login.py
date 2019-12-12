from sys import path
from os import remove
from time import sleep
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PIL import Image
from numpy import array
from CaptchaSolver import BypassCaptcha

def GetCaptchaImg():
    Browser.save_screenshot("ScreenShot.png")
    Img = Browser.find_element_by_id("imgCaptcha")
    ImgLocation = Img.location
    ImgSize = Img.size
    Left = ImgLocation["x"]
    Top = ImgLocation["y"]
    Right = Left + ImgSize["width"]
    Bottom = Top + ImgSize["height"]
    Captcha = Image.open("ScreenShot.png").convert("L").crop((Left, Top, Right, Bottom))
    remove("ScreenShot.png")
    return array(Captcha)


opts = webdriver.ChromeOptions()

Browser = webdriver.Chrome(path[0] + "/ChromeDriver", options=opts)
Browser.get("https://webap.nptu.edu.tw")
Browser.set_window_size(1280, 720)
sleep(2.5)
Browser.find_element_by_id("LoginDefault_ibtLoginStd").click()
sleep(2.5)

while True:
    Browser.find_element_by_id("LoginStd_txtCheckCode").send_keys(BypassCaptcha(GetCaptchaImg()))
    Browser.find_element_by_id("LoginStd_txtAccount").send_keys("Account")
    Browser.find_element_by_id("LoginStd_txtPassWord").send_keys("Password")
    Browser.find_element_by_id("LoginStd_ibtLogin").click()
    sleep(2.5)

    try:
        Alert = Browser.switch_to.alert
        
        if "驗證碼" in Alert.text:
            Alert.accept()
            continue
        else:
            print(Alert.text)
            break
    except:
        break