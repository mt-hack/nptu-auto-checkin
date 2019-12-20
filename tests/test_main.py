import os
import sys
from unittest import TestCase

sys.path.append("..")

from src.solver.captcha import get_random_png


class TestMain(TestCase):
    def test_get_random_png(self):
        test_length = 10
        random_png_name = get_random_png(test_length)
        png_extension = ".png"
        self.assertEqual(len(random_png_name), test_length + len(png_extension))
        self.assertEqual(os.path.splitext(random_png_name)[1], png_extension)
