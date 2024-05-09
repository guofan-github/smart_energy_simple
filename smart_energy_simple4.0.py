import pytest

if __name__ == '__main__':
    pytest.main(['-vs', '-r D', 'testcases/test_ui.py',
                 '--report=smark.html',
                 '--title=smark_energy_simple4.0の测试报告',
                 '--tester=fan',
                 '--template=2'])

