# coding:utf-8

import pytest
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_email():
    sender = '1579749483@qq.com'
    recipient = "11065448@qq.com"
    password = 'apvsvkumfynfgeca'

    # 运行 pytest 测试用例，并生成测试报告
    pytest.main(['--report=smark.html',
                 '--title=郭凡の测试报告',
                 '--tester=fan',
                 '--desc=测试',
                 '--template=2'])

    # 读取最新生成的测试报告文件
    report_dir = "./reports/"
    report_files = os.listdir(report_dir)
    report_files.sort()
    report_file = os.path.join(report_dir, report_files[-1])

    # 创建邮件内容对象
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = '郭凡のPytest Report'
    msg.attach(MIMEText('如约而至，无人可免.', 'plain'))

    # 添加测试报告附件
    with open(report_file, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='html')
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(report_file))
        msg.attach(attachment)

    # 发送邮件
    try:
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        print('Email 发送成功.')
    except Exception as e:
        print('Email sending failed.')
        print(str(e))
    finally:
        server.quit()

if __name__ == '__main__':
    send_email()



# 命令行
# pytest --report=smark_parking.html --title=郭凡の测试报告 --tester=fan --desc=智慧泊车测试 --template=2