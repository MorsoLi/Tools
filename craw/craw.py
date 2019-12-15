from proxy import GetFreeproxy
from user_agent import get_UA
import random
import requests
import time
from selenium import webdriver
import sys
import os


def get_ip():
    free_proxy = GetFreeproxy()
    free_proxy.get_proxy()
    ip_list = free_proxy.ip_list
    return ip_list


if __name__ == '__main__':
    url_list = ["https://baidu.com"]
    # 无限循环，每次都要打开一个浏览器窗口，不是标签
    ip_list = get_ip()
    ua_list = get_UA()
    while 1:
        # 调用函数获取浏览器标识, 字符串
        headers = random.choice(ua_list)
        # 调用函数获取IP代理地址,这里获取是字符串，而不是像前两个教程获得的是数组
        proxy = random.choice(ip_list)
        # 使用chrome自定义
        chrome_options = webdriver.ChromeOptions()
        # 设置代理
        chrome_options.add_argument('--proxy-server=http://'+proxy)
        # 设置UA
        chrome_options.add_argument('--user-agent="'+headers+'"')
        # 使用设置初始化webdriver
        driver = webdriver.Chrome(chrome_options=chrome_options)
        print(chrome_options._arguments)
        try:
            # 访问超时30秒
            driver.set_page_load_timeout(30)
            # 访问网页
            url = url_list[random.randint(0, len(url_list)-1)]
            driver.get(url)
            # 退出当前浏览器
            driver.close()
            # 延迟1~3秒继续
            time_delay = random.randint(2, 3)
            while time_delay > 0:
                time.sleep(1)
                time_delay = time_delay - 1
                pass
        except:
            print("timeout")
            # 退出浏览器
            driver.quit()
            time.sleep(1)
            # 重启脚本, 之所以选择重启脚本是因为，长时间运行该脚本会出现一些莫名其妙的问题，不如重启解决
            python = sys.executable
            os.execl(python, python, *sys.argv)
        finally:
            pass
