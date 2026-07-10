import pytest
from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage

def test_input_init(openpage_st):
    openpage_st.ele('@id=tab_select').select('absolute')
    openpage_st.ele('@id=mode_select').select('Position')
    sleep(1)

def test_input_lat_absolute_position(openpage_st):
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('50')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('10')
    assert(float(openpage_st.ele('@id=lateral_pos').value) == 25.0)
    assert(float(openpage_st.ele('@id=lateral_speed').value) == 5.0)
    sleep(1)
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('-50')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('-10')
    assert(float(openpage_st.ele('@id=lateral_pos').value) == -25.0)
    assert(float(openpage_st.ele('@id=lateral_speed').value) == 0.0)
    sleep(1)


def test_input_long_absolute_position(openpage_st):
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('250')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('20')
    assert(float(openpage_st.ele('@id=Longitudinal_pos').value) == 100.0)
    assert(float(openpage_st.ele('@id=Longitudinal_speed').value) == 9.0)
    sleep(1)
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('-50')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('-5')
    assert(float(openpage_st.ele('@id=Longitudinal_pos').value) == 0.0)
    assert(float(openpage_st.ele('@id=Longitudinal_speed').value) == 0.0)
    sleep(1)

def test_input_vertical_absolute_position(openpage_st):
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('50')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('5')
    assert(float(openpage_st.ele('@id=Vertical_pos').value) == 16.0)
    assert(float(openpage_st.ele('@id=Vertical_speed').value) == 3.0)
    sleep(1)
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('-100')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('-3')
    assert(float(openpage_st.ele('@id=Vertical_pos').value) == -50.0)
    assert(float(openpage_st.ele('@id=Vertical_speed').value) == 0.0)
    sleep(1)

def test_input_pitch_absolute_position(openpage_st):
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('5')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.9')
    assert(float(openpage_st.ele('@id=Pitch_pos').value) == 3.0)
    assert(float(openpage_st.ele('@id=Pitch_speed').value) == 0.6)
    sleep(1)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('-6')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('-0.5')
    assert(float(openpage_st.ele('@id=Pitch_pos').value) == -3.0)
    assert(float(openpage_st.ele('@id=Pitch_speed').value) == 0.0)
    sleep(1)

def test_input_roll_absolute_position(openpage_st):
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('6')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.8')
    assert(float(openpage_st.ele('@id=Roll_pos').value) == 3.0)
    assert(float(openpage_st.ele('@id=Roll_speed').value) == 0.6)
    sleep(1)
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('-7')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('-0.7')
    assert(float(openpage_st.ele('@id=Roll_pos').value) == -3.0)
    assert(float(openpage_st.ele('@id=Roll_speed').value) == 0.0)
    sleep(1)

def test_input_iso_absolute_position(openpage_st):
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('120')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('10')
    assert(float(openpage_st.ele('@id=Iso_pos').value) == 95.0)
    assert(float(openpage_st.ele('@id=Iso_speed').value) == 6.0)
    sleep(1)
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('-150')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('-3')
    assert(float(openpage_st.ele('@id=Iso_pos').value) == -95.0)
    assert(float(openpage_st.ele('@id=Iso_speed').value) == 0.0)
    sleep(1)

def test_close_web(openpage_st):
    openpage_st.quit()