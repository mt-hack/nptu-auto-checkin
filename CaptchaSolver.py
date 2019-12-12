from urllib.request import urlretrieve
from os import remove
from sys import path
from PIL import Image
from numpy import array, full
from pytesseract import image_to_string

def DownloadCaptcha():
    FilePath = path()[0]

    Url = 'https://webap.nptu.edu.tw/Web/Modules/CaptchaCreator.aspx'
    urlretrieve(Url, FilePath + "/TempImage.jpg")

    File = Image.open(FilePath + "/TempImage.jpg").convert("L")
    Pixel = array(File)
    File.close()
    remove(FilePath + "/TempImage.jpg")

    return Pixel

def ImgProcessing(Pixel):
    Min = 15
    for i in range(len(Pixel)):
        for j in range(len(Pixel[i])):
            if Pixel[i][j] > Min:
                Pixel[i][j] = 255
            else:
                Pixel[i][j] = 0

    for i in range(len(Pixel)):
        for j in range(len(Pixel[i])):
            count = 0
            for a in range(-2, 3):
                for b in range(-2, 3):
                    try:
                        if Pixel[i+a][j+b] <= Min:
                            count += 1
                    except:
                        continue
            if count < 5:
                Pixel[i][j] = 255
            elif count > 15:
                Pixel[i][j] = 0

    Num = 3
    EmptyArray = full(Pixel.shape[1], 255)
    for i in range(0, len(Pixel) - Num):
        Pixel[i] = Pixel[i+Num]
    for a in range(len(Pixel) - Num, len(Pixel)):
        Pixel[a] = EmptyArray
    
    return Pixel

def BypassCaptcha(Pixel):
    Pixel = ImgProcessing(Pixel)
    return image_to_string(Pixel, config="--dpi 120 --oem 3 -c tessedit_char_whitelist=0123456789")
            