"""Login to BUPT's network"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import datetime
import logging
import logging.handlers
import os
import sys
import time
import requests

IS_WINDOWS_10 = os.name == 'nt' and sys.getwindowsversion().major == 10
if IS_WINDOWS_10:
    from win10toast import ToastNotifier


STUDENT_ID = '1234567890'  # 10 位数学号
PASSWORD = '123456'  # 身份证号后 6 位
NETWORK_LINE = 'CUC-BRAS'  # 宽带线路，默认为中国联通
LOG_PATH = 'portal_login.log'  # 日志文件的路径


def set_logger(log_path):
    """Log into log file at `log_path`, at level `INFO`"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_path, when='midnight', interval=1, backupCount=10, encoding='utf8', atTime=datetime.time(3, 30))
    file_handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s'))
    logging.getLogger(None).addHandler(file_handler)
    logging.info("Start ....")


class Notifier(object):
    def __init__(self):
        if IS_WINDOWS_10:
            self.toaster = ToastNotifier()

    def notify(self, text):
        """Send to text to both logging and toast hub."""
        logging.info(text)
        if IS_WINDOWS_10:
            self.toaster.show_toast(
                '校园网认证', text, duration=None, threaded=True)


def main():
    """Core"""
    set_logger(LOG_PATH)
    notifier = Notifier()
    response_in = requests.post('http://10.3.8.216/login', data={
        'user': STUDENT_ID,
        'pass': PASSWORD
    })
    if '无需认证' in response_in.text or '成功' in response_in.text:
        notifier.notify('准入认证通过')
        response_out = requests.post('http://10.3.8.211', data={
            'DDDDD': STUDENT_ID,
            'upass': PASSWORD,
            'R1': '0'
        })
        if '成功登录' in response_out.text:
            notifier.notify('准出认证通过')
            requests.post('http://10.3.8.217/login', data={
                'user': STUDENT_ID,
                'pass': PASSWORD,
                'NETWORK_LINE': NETWORK_LINE
            })
            is_auth_passed = False
            for i in range(30):
                if requests.get('http://10.3.8.217/dial').json()['code'] == 0:
                    is_auth_passed = True
                    break
                time.sleep(1)
            if is_auth_passed:
                notifier.notify('宽带认证通过')
            else:
                notifier.notify('宽带认证失败')
        else:
            notifier.notify('准出认证失败')
    else:
        notifier.notify('准入认证失败')


if __name__ == '__main__':
    main()
