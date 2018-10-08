"""Login to BUPT's network"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import datetime
import logging
import logging.handlers
import os
import socket
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
PROBE_URL = 'https://baidu.com'  # SSL needed.
PROBE_MAX_TIMEOUT = 4
MAX_TIME_TO_LOGIN = 30


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


def get_primary_ip() -> str:
    socket.setdefaulttimeout(PROBE_MAX_TIMEOUT)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test_socket:
        try:
            test_socket.connect(('8.8.8.8', 53))
            primary_ip = test_socket.getsockname()[0]
        except socket.timeout:
            primary_ip = '127.0.0.1'
    return primary_ip


def do_need_login() -> bool:
    try:
        requests.get(PROBE_URL, timeout=PROBE_MAX_TIMEOUT)
        return False
    except requests.exceptions.ConnectTimeout:
        return True


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
    primary_ip = get_primary_ip()
    if primary_ip[:3] == '10.':
        do_need_isp_auth = False
        if do_need_login():
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
                    do_need_isp_auth = True
                else:
                    notifier.notify('准出认证失败')
            else:
                notifier.notify('准入认证失败')
        else:
            notifier.notify('无需准入、准出认证')
            do_need_isp_auth = True
        if do_need_isp_auth:
            requests.post('http://10.3.8.217/login', data={
                'user': STUDENT_ID,
                'pass': PASSWORD,
                'NETWORK_LINE': NETWORK_LINE
            })
            for i in range(MAX_TIME_TO_LOGIN):
                if requests.get('http://10.3.8.217/dial').json()['code'] == 0:
                    do_need_isp_auth = True
                    break
                time.sleep(1)
            if do_need_isp_auth:
                notifier.notify('宽带认证通过')
            else:
                notifier.notify('宽带认证失败')
        else:
            notifier.notify('不进行宽带认证')
    else:
        notifier.notify('非校园网，无需认证')


if __name__ == '__main__':
    main()
