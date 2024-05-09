import os
import re
import shutil
import time
import zipfile
from telnetlib import EC

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def update_driver(bw_type):
    url = "https://www.baidu.com"
    new_path = 'E:/gf/pytest_smart_energy4.0_simple/driver/'
    if bw_type == "chrome":
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        # 1.使用ChromeDriverManager安装ChromeDriver，并返回驱动程序的路径
        driver_path = ChromeDriverManager().install()
        # 打印驱动程序路径
        print(driver_path)
        # C:\Users\Ms-xiao\.wdm\drivers\chromedriver\win64\120.0.6099.109\chromedriver-win32/chromedriver.exe
        # 2.把下载的驱动文件，复制到指定位置
        shutil.copy(driver_path, new_path)
        # 3.验证一下安装好的驱动，是否可用
        driver = webdriver.Chrome(service=ChromeService(new_path + 'chromedriver.exe'))
        # 打开百度网页
        driver.get(url)

    elif bw_type == "edge":
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        driver_path = EdgeChromiumDriverManager().install()
        # 2.把下载的驱动文件，复制到指定位置
        shutil.copy(driver_path, new_path)
        driver = webdriver.Edge(service=EdgeService(new_path + 'msedgedriver.exe'))
        driver.get(url)

    elif bw_type == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager
        driver_path = GeckoDriverManager().install()
        shutil.copy(driver_path, new_path)
        driver = webdriver.Firefox(service=FirefoxService(new_path + 'geckodriver.exe'))
        driver.get(url)

    elif bw_type == "IE":
        from selenium.webdriver.ie.service import Service as IEService
        from webdriver_manager.microsoft import IEDriverManager
        driver = webdriver.Ie(service=IEService(IEDriverManager().install()))
        driver.get(url)


class Common:
    # 单例模式
    driver = None
    session = None
    DRIVER_PATH = 'E:/gf/pytest_smart_energy4.0_simple/driver/'

    # 打开浏览器
    @classmethod
    def get_driver(cls, browser_type="edge"):
        # 判断驱动是否需要更新
        update_driver(browser_type)
        if cls.driver is None:
            if browser_type == 'edge' or browser_type == 'gg':
                cls.driver = webdriver.Edge()
            elif browser_type == 'firefox' or browser_type == 'ff':
                cls.driver = webdriver.Firefox()
            elif browser_type == "chrome" or browser_type == "goole":
                cls.driver = webdriver.Chrome()
            else:
                print("不是吧？这么多浏览器没有一个你能用的？QAQ")
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)
        return cls.driver

    # 判断元素是否存在
    @classmethod
    def element_exist(cls, by, value):
        try:
            cls.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

    # 显式等待
    @classmethod
    def wait_element_presence(cls, by, value, time_out=10):
        return WebDriverWait(cls.driver, time_out).until(lambda dr: dr.find_element(by, value))

    # 显示等待加强版（直接传入方法）
    @classmethod
    def wait_element_method(cls, method, time_out=5):
        return WebDriverWait(cls.driver, time_out).until(method)

    # 显示等待判断元素是否可见，如果可见就返回这个元素
    @classmethod
    def wait_element_EC(cls, by, value, time_out=10):
        return WebDriverWait(cls.driver, time_out).until(
            expected_conditions.visibility_of(cls.driver.find_element(by, value)))

    # 关闭浏览器
    @classmethod
    def close_browser(cls):
        cls.driver.quit()
        cls.driver = None

    # 接口：获取session
    @classmethod
    def get_session(cls):
        if cls.session is None:
            cls.session = requests.session()
        return cls.session

    # 接口：关闭session
    @classmethod
    def close_session(cls):
        cls.session.close()
        cls.session = None
