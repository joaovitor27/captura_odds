from selenium.webdriver.chrome.webdriver import WebDriver


class CustomWebDriver(WebDriver):
    def __init__(self, options, service, pdf_download_folder):
        super().__init__(options, service)
        self.pdf_download_folder = pdf_download_folder
