import os
from tempfile import mkdtemp
from typing import Iterable, Any, List, Union

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from chromium import CustomWebDriver

DEFAULT_TIMEOUT = 5


class DriverUtils:
    @staticmethod
    def find_by_id(driver: Union[WebDriver, WebElement], _id: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        if isinstance(driver, WebDriver):
            DriverUtils.wait_presence(driver, By.ID, _id, timeout)
        return driver.find_element(By.ID, _id)

    @staticmethod
    def is_present_by_id(driver: Union[WebDriver, WebElement], _id: str) -> bool:
        return len(driver.find_elements(By.ID, _id)) > 0

    @staticmethod
    def is_present_by_xpath(driver: Union[WebDriver, WebElement], xpath: str) -> bool:
        return len(driver.find_elements(By.XPATH, xpath)) > 0

    @staticmethod
    def find_by_tag(driver: Union[WebDriver, WebElement], tag: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        if isinstance(driver, WebDriver):
            DriverUtils.wait_presence(driver, By.TAG_NAME, tag, timeout)
        return driver.find_element(By.TAG_NAME, tag)

    @staticmethod
    def text_by_id(driver: Union[WebDriver, WebElement], _id: str) -> str:
        return DriverUtils.find_by_id(driver, _id).text

    @staticmethod
    def find_all_by_id(driver: WebDriver, _id: str) -> List[WebElement]:
        DriverUtils.wait_presence(driver, By.ID, _id, DEFAULT_TIMEOUT)
        return driver.find_elements(By.ID, _id)

    @staticmethod
    def find_by_xpath(driver: WebDriver, xpath: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        DriverUtils.wait_presence(driver, By.XPATH, xpath, timeout)
        return driver.find_element(By.XPATH, xpath)

    @staticmethod
    def find_by_class_name(driver: WebDriver, xpath: str) -> WebElement:
        DriverUtils.wait_presence(driver, By.CLASS_NAME, xpath, DEFAULT_TIMEOUT)
        return driver.find_element(By.CLASS_NAME, xpath)

    @staticmethod
    def wait_condition(driver: WebDriver, condition: Any, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return WebDriverWait(driver, timeout=timeout).until(condition)

    @staticmethod
    def wait_until_input_value_is_by_id(driver: WebDriver, el_id: str, value: Any) -> WebElement:
        return DriverUtils.wait_condition(
            driver,
            lambda x: str(DriverUtils.find_by_id(x, el_id).get_attribute('value')) == str(value)
        )

    @staticmethod
    def wait_presence(driver: WebDriver, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_condition(driver, ec.presence_of_element_located(
            (by, val)
        ), timeout)

    @staticmethod
    def wait_visibility(driver: WebDriver, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_condition(driver, ec.visibility_of_element_located(
            (by, val)
        ), timeout)

    @staticmethod
    def wait_clickable(driver: WebDriver, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_condition(driver, ec.element_to_be_clickable(
            (by, val)
        ), timeout)

    @staticmethod
    def wait_invisibility(driver: WebDriver, by: str, val: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_condition(driver, ec.invisibility_of_element_located(
            (by, val)
        ), timeout)

    @staticmethod
    def wait_presence_by_id(driver: WebDriver, _id: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_presence(driver, By.ID, _id, timeout)

    @staticmethod
    def wait_visibility_by_id(driver: WebDriver, _id: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_visibility(driver, By.ID, _id, timeout)

    @staticmethod
    def wait_clickable_by_id(driver: WebDriver, _id: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_clickable(driver, By.ID, _id, timeout)

    @staticmethod
    def wait_invisibility_by_id(driver: WebDriver, _id: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_invisibility(driver, By.ID, _id, timeout)

    @staticmethod
    def wait_presence_by_xpath(driver: WebDriver, xpath: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_presence(driver, By.XPATH, xpath, timeout)

    @staticmethod
    def wait_visibility_by_xpath(driver: WebDriver, xpath: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_visibility(driver, By.XPATH, xpath, timeout)

    @staticmethod
    def wait_clickable_by_xpath(driver: WebDriver, xpath: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_clickable(driver, By.XPATH, xpath, timeout)

    @staticmethod
    def wait_invisibility_by_xpath(driver: WebDriver, xpath: str, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return DriverUtils.wait_invisibility(driver, By.XPATH, xpath, timeout)

    @staticmethod
    def wait_visibility_and_click_by_xpath(driver: WebDriver,
                                           xpaths: Iterable[str],
                                           timeout: int = DEFAULT_TIMEOUT) -> None:
        for xpath in xpaths:
            DriverUtils.wait_clickable_by_xpath(driver, xpath, timeout)
            DriverUtils.find_by_xpath(driver, xpath).click()

    @staticmethod
    def new_driver(headless: bool = False) -> CustomWebDriver:
        options = webdriver.ChromeOptions()

        pdf_download_folder = mkdtemp()
        prefs = {
            'download.prompt_for_download': False,
            'download.default_directory': pdf_download_folder,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
        }

        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280x720')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-zygote')

        if os.environ.get('CHROME_BINARY'):
            options.binary_location = os.environ.get('CHROME_BINARY')

        chromedriver_path: Union[str, None] = os.environ.get('CHROMEDRIVER_PATH')
        options.add_experimental_option('prefs', prefs)

        if chromedriver_path is None:
            chromedriver_path = ChromeDriverManager().install()

        driver = CustomWebDriver(service=Service(executable_path=chromedriver_path),
                                 options=options, pdf_download_folder=pdf_download_folder)
        driver.maximize_window()

        return driver

    @staticmethod
    def accept_alert(driver: WebDriver):
        try:
            driver.switch_to.alert.accept()
        except WebDriverException:
            ...

    @staticmethod
    def wait_alert(driver: WebDriver, timeout: int = 30):
        WebDriverWait(driver, timeout=timeout).until(ec.alert_is_present())
