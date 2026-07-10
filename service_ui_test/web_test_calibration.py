import pytest
from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage

def test_cali_x(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('lateral')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(40)
    assert(element.ele('@value=SAVE').click())
    sleep(1)

def test_cali_y(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('longitudinal')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(50)
    assert(element.ele('@value=SAVE').click())
    sleep(1)

def test_cali_z(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('vertical')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(60)
    assert(element.ele('@value=SAVE').click())
    sleep(1)

def test_cali_p(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('pitch')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(240)
    assert(element.ele('@value=SAVE').click())
    sleep(1)

def test_cali_r(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('roll')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(150)
    assert(element.ele('@value=SAVE').click())
    sleep(1)

def test_cali_iso(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('iso')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(100)
    assert(element.ele('@value=SAVE').click())
    sleep(1)
    

def test_cali_column(openpage_st):
    sleep(1)
    openpage_st.ele('@id:axios').select('column')
    element = openpage_st.ele('@class=btn-container')
    sleep(1)
    assert(element.ele('@value=START').click())
    sleep(1)
    assert(element.ele('@value=NEXT').click())
    sleep(1)
    assert(element.ele('@value=SAVE').click())
    sleep(1)

def test_close_web(openpage_st):
    openpage_st.quit()