import logging
import unicodedata
import zipfile
from pathlib import Path
from sys import platform
from os import chmod, stat

import requests
from tqdm import tqdm


def get_driver_package():
    current_file = Path(__file__)
    parent_dir = current_file.parent
    target_driver_path = Path(parent_dir, "ChromeDriver")
    if target_driver_path.is_file():
        logging.info(f"WebDriver file already downloaded @ {target_driver_path}.")
        return str(target_driver_path)
    else:
        target_version = '79.0.3945.36'
        remote_link = ''
        if platform.startswith('win32'):
            remote_link = f'https://chromedriver.storage.googleapis.com/{target_version}/chromedriver_win32.zip'
        elif platform.startswith('linux'):
            remote_link = f'https://chromedriver.storage.googleapis.com/{target_version}/chromedriver_linux64.zip'
        elif platform.startswith('darwin'):
            remote_link = f'https://chromedriver.storage.googleapis.com/{target_version}/chromedriver_mac64.zip'
        else:
            raise OSError("This platform is not supported.")
        logging.warning(f'WebDriver not found. Attempting to download Chrome {target_version} for {platform}...')
        driver_zip = Path(parent_dir, "chromedriver-download.zip")
        response = requests.get(remote_link, stream=True)
        with driver_zip.open('wb') as file_handle:
            for chunk in tqdm(response.iter_content(chunk_size=512)):
                if chunk:
                    file_handle.write(chunk)
            logging.info("Finished downloading Chrome WebDriver.")
        with zipfile.ZipFile(driver_zip, "r") as zip_handle:
            logging.info("Attempting to extract ChromeDriver...")
            for zip_entry in zip_handle.filelist:
                if unicodedata.normalize('NFKD', zip_entry.filename.casefold()).startswith("chromedriver"):
                    zip_entry.filename = target_driver_path.name
                    zip_handle.extract(zip_entry)
        if target_driver_path.is_file():
            chmod(target_driver_path, stat(target_driver_path).st_mode | 0o111)

            logging.info("Extracted ChromeDriver.")
            return str(target_driver_path)
        else:
            raise FileNotFoundError("ChromeDriver could not be extracted.")