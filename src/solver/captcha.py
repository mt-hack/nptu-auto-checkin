from io import BytesIO

from PIL import Image
from numpy import full, array
from pytesseract import image_to_string


def image_processing(pixel):
    minimum = 15
    for i in range(len(pixel)):
        for j in range(len(pixel[i])):
            if pixel[i][j] > minimum:
                pixel[i][j] = 255
            else:
                pixel[i][j] = 0

    for i in range(len(pixel)):
        for j in range(len(pixel[i])):
            count = 0
            for a in range(-2, 3):
                for b in range(-2, 3):
                    try:
                        if pixel[i + a][j + b] <= minimum:
                            count += 1
                    except:
                        continue
            if count < 5:
                pixel[i][j] = 255
            elif count > 15:
                pixel[i][j] = 0
    num = 3
    empty_array = full(pixel.shape[1], 255)
    for i in range(0, len(pixel) - num):
        pixel[i] = pixel[i + num]
    for a in range(len(pixel) - num, len(pixel)):
        pixel[a] = empty_array
    return pixel


def get_captcha_text(pixel):
    pixel = image_processing(pixel)
    return image_to_string(pixel, config="--dpi 120 --oem 3 -c tessedit_char_whitelist=0123456789")


def get_captcha_from_browser(browser_instance):
    stream = browser_instance.get_screenshot_as_png()
    ss = BytesIO(stream)
    image = browser_instance.find_element_by_id("imgCaptcha")
    left = image.location["x"]
    top = image.location["y"]
    right = left + image.size["width"]
    bottom = top + image.size["height"]
    captcha = Image \
        .open(ss) \
        .convert('L') \
        .crop((left, top, right, bottom))
    return get_captcha_text(array(captcha))
