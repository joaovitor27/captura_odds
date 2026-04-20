# This is a sample Python script.
import os

from chromium import CustomWebDriver
from driver import DriverUtils


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def get_url_site() -> str:
    return 'https://reidopitaco.bet.br/betting/sports/20000000169?tab=competitions'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    driver = DriverUtils.new_driver()
    driver.get(get_url_site())

