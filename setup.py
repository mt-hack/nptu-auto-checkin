from setuptools import setup, find_packages
from os import environ

version = ''
if environ.get('APPVEYOR_BUILD_VERSION'):
    version = environ.get('APPVEYOR_BUILD_VERSION')
else:
    version = '1.0.0'

setup(
    name="NPTUAutoCheckin",
    version=version,
    packages=find_packages(),
    install_requires=['numpy','Pillow','pytesseract','selenium','wheel'],
    author="Still Hsu, Guang-Yih Hsu",
    author_email="business@stillu.cc"
)