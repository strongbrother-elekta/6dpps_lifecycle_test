import pytest
from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage

standardErr=0.5

def test_mov_lat(openpage_st):
    openpage_st.ele('@id=LateralCheckbox1').input(True)
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('20')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(20.0 - float(openpage_st.ele('@id=lat').value)))

def test_mov_long(openpage_st):
    openpage_st.ele('@id=LongCheckbox1').input(True)
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('25')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(25.0 - float(openpage_st.ele('@id=long').value)))

def test_mov_vertical(openpage_st):
    openpage_st.ele('@id=HeightCheckbox1').input(True)
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('-30')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(15)
    assert(standardErr > abs(-30.0 - float(openpage_st.ele('@id=height').value)))

def test_mov_pitch(openpage_st):
    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('2')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(8)
    assert(standardErr > abs(2.0 - float(openpage_st.ele('@id=pitch').value)))

def test_mov_roll(openpage_st):
    openpage_st.ele('@id=RollCheckbox1').input(True)
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('2')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(2.0 - float(openpage_st.ele('@id=roll').value)))

def test_mov_iso(openpage_st):
    openpage_st.ele('@id=IsoCheckbox1').input(True)
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('60')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(15)
    assert(standardErr > abs(60.0 - float(openpage_st.ele('@id=iso').value)))

def test_mov_reset(openpage_st):
    openpage_st.ele('@id=LateralCheckbox1').input(True)
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('0')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=LongCheckbox1').input(True)
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('50')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=HeightCheckbox1').input(True)
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('0')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('0')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=RollCheckbox1').input(True)
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('0')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=IsoCheckbox1').input(True)
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('0')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(15)


def test_close_web(openpage_st):
    openpage_st.quit()