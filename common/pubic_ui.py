from time import sleep
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from common.get_driver import Common
from conf.exceldata import ReadUi

data_list = ReadUi().get_data_ui()


class Key:

    def __init__(self):
        self.driver = Common.get_driver('edge')

    # 浏览器操作------------------------------------------------------------------
    def open(self, txt):
        # 打开网址
        self.driver.get(txt)
        # 最大化浏览器窗口
        self.driver.maximize_window()
        # 隐式等待10秒
        self.driver.implicitly_wait(10)

    def quit(self):
        # 退出浏览器
        self.driver.quit()

    def sleep(self, txt):
        # 强制等待
        sleep(txt)

    # 元素操作函数-----------------------------------------------------------------
        # 查找元素的通用方法
    def find_element(self, value, by="xpath"):
        try:
            # 使用 getattr 获取 By 类中的属性
            by_attribute = getattr(By, by.upper(), By.XPATH)  # 默认为 XPath
            return self.driver.find_element(by_attribute, value)
        except Exception as e:
            print(f"Error finding element: {e}")
            raise

    def input(self, txt, value, by="xpath"):
        # 输入
        el = self.find_element(value, by)
        if el:
            el.send_keys(txt)

    def click(self, value, by="xpath"):
        # 点击
        el = self.find_element(value, by)
        if el:
            el.click()

    def select(self, value, txt, by="xpath"):
        # 定位下拉框元素
        dropdown = self.find_element(value, by)

        if dropdown:
            # 使用 Select 类来操作下拉框
            select = Select(dropdown)
            try:
                # 通过可见文本选择选项
                select.select_by_visible_text(txt)
                print(f"Selected option '{txt}' from dropdown successfully.")
            except NoSuchElementException:
                print(f"Option '{txt}' not found in dropdown.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Dropdown element not found.")

    # 显示等待
    def driver_wait(self, by, value, time_=5):
        WebDriverWait(self.driver, time_, 0.5). \
            until(lambda element: self.find_element(by, value), message='显示等待失败')

    # 鼠标悬停
    def action(self, by, value):
        ActionChains(self.driver).move_to_element(self.find_element(by, value)).perform()

    # 输出标签页标题
    def title(self):
        print(self.driver.title)

    # 句柄切换，关闭第一个标签页
    def window_switch(self):
        handles = self.driver.window_handles
        self.driver.close()
        self.driver.switch_to.window(handles[1])

    # 句柄切换，不关闭第一个标签页
    def window_switch_old(self):
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[1])

    def gettext(self, value, by="xpath"):
        # 获取元素文本
        el = self.find_element(value, by)
        if el:
            return el.text
        else:
            return None

    def tttt(self, value, by="xpath"):
        return self.driver.find_elements(by, value)



def get_title():
    title_list = []
    for i in data_list:
        title_list.append(i['用例标题'])
    return title_list


