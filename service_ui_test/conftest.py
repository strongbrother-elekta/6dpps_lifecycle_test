import pytest
#from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions

path=r'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
ChromiumOptions().set_browser_path(path).save()

@pytest.fixture(scope="session")
def openpage_st():
    page =ChromiumPage()  # 创建页面对象，默认driver模式
    page.get('https://192.168.30.9:8443/')  # 访问个人中心页面（未登录，重定向到登录页面）
    page.ele('@id:username').input('admin')
    page.ele('@id:password').input('2988')
    page.ele('@id:btn').click()
    return page

