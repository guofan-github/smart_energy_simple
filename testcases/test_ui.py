import datetime
import os
import pytest
import logging
from common.pubic_ui import Key, get_title
from conf.exceldata import ReadUi, backup_excel_file_ui
from conf.公共信息 import screenshot_path


class TestUi:
    data_list = ReadUi().get_data_ui()

    def setup_class(self):
        self.wd = Key()
        ReadUi().clear_excel_result_ui()
        logging.info('**************************历史测试结果已清除**********************************')
        backup_excel_file_ui()
        logging.info('******************************文件已备份*************************************')

    def teardown_class(self):
        self.wd.quit()
        logging.info('******************************关闭浏览器*************************************')

    @pytest.mark.parametrize("data", data_list, ids=get_title())
    def test_execute_cases(self, data):
        self._prepare_test_data(data)
        self.execute_test_case()

    def _prepare_test_data(self, data):
        self.sheet = data['sheet标题']
        logging.info(f'sheet标题：{self.sheet}')
        self.name = data['用例标题']
        logging.info(f'用例标题：{self.name}')
        self.test_steps = data['用例步骤']
        self.execute = data['是否执行']
        logging.info(f'{self.execute}')

    def execute_test_case(self):
        for step in self.test_steps:
            self._execute_step(step)
            logging.info(f'步骤{self.desc} - {self.keyword}执行完毕')

    def _execute_step(self, step):
        self.desc = step['步骤描述']
        logging.info(f'步骤描述：{self.desc}')
        self.id = step['序号']
        logging.info(f'步骤{self.id}')
        self.keyword = step['关键字行为']
        logging.info(f'{self.desc} - 关键字行为：{self.keyword}')
        self.method = step['定位方法']
        logging.info(f'{self.desc} - 定位方法：{self.method}')
        self.element = step['元素位置']
        logging.info(f'{self.desc} - 元素位置：{self.element}')
        self.input = step['输入内容']
        logging.info(f'{self.desc} - 输入内容：{self.input}')
        self.expect = step['断言值']
        logging.info(f'{self.desc} - 断言值：{self.expect}')

        if self.execute == '否':
            ReadUi()._write_to_excel(self.id, '跳过用例', self.sheet)
            pytest.skip('跳过测试')

        print(f"正在执行：{self.desc} - {self.keyword}")
        logging.info(f"正在执行：{self.desc} - {self.keyword}")
        data = {'by': self.method, 'value': self.element, 'txt': self.input}
        logging.info(f'字典：{data}')
        data = {k: v for k, v in data.items() if v is not None}
        logging.info(f'字典去掉空值：{data}')

        result = getattr(self.wd, self.keyword)(**data)
        logging.info(f'执行结果：{result}')

        self._assert_result(result)

    def _assert_result(self, result):
        if self.expect:
            try:
                assert result == self.expect
                self.results = '测试通过'
                ReadUi()._write_to_excel(self.id, self.results, self.sheet)
                logging.info(f'步骤{self.id} - 测试通过')
            except Exception as e:
                self._take_screenshot()
                self.results = f'测试失败:{str(e)}'
                ReadUi()._write_to_excel(self.id, self.results, self.sheet)
                logging.info(f'执行步骤{self.desc}出现异常，原因：{e}')
                raise Exception('断言失败')
            finally:
                logging.info(f'写回测试结果到excel：{self.results}')
                ReadUi()._write_to_excel(self.id, self.results, self.sheet)

    def _take_screenshot(self):
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # 指定截图保存路径
        screenshot_dir = screenshot_path
        if not os.path.exists(screenshot_dir):
            # 如果目录不存在，则创建它
            os.makedirs(screenshot_dir)

        # 截图文件的完整路径
        screenshot_path_ = f"{screenshot_dir}/{self.desc}_{current_time}.png"

        # 使用WebDriver进行截图
        self.wd.driver.save_screenshot(screenshot_path_)
        logging.info(f'步骤{self.desc} - 截图已保存至: {screenshot_path_}')
