import unittest
from glob import glob
from os import path
from pathlib import Path

from numpy import array
from PIL import Image

from solver.captcha import get_captcha_result


class TestCaptcha(unittest.TestCase):
    def test_captcha(self):
        cwd = Path(__file__).parent
        sample_path = Path(f'{cwd}/samples').resolve()
        print(sample_path)
        samples = glob(path.join(sample_path, '*.jpg'))
        print(samples)
        for sample in samples:
            image = array(Image.open(sample).convert('L'))
            result = get_captcha_result(image)
            expected_result = Path(sample).stem
            print(f'Expected {expected_result}, got {result}')
            self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
