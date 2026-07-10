import pytest
from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage

def test_snapshot(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('lateral')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(5)
    openpage_st.close()
    sleep(2)

    new_page = ChromiumPage()
    new_page.get('http://192.168.30.9:8000/')
    new_page.ele('@id:username').input('admin')
    new_page.ele('@id:password').input('3286')
    new_page.ele('@id:btn').click()
    sleep(32)
    assert(new_page.ele('@value=SAVE').click())
    sleep(3)
    new_page.quit()
