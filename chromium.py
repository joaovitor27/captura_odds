from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


class CustomWebDriver(WebDriver):
    def __init__(self, options: webdriver.ChromeOptions, service: Service, pdf_download_folder: str) -> None:
        super().__init__(options, service)
        self.pdf_download_folder: str = pdf_download_folder