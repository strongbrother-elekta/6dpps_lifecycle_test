import pytest
from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage

standardErr=0.5

def test_mov_init(openpage_st):
    openpage_st.ele('@id=LateralCheckbox1').input(True)
    openpage_st.ele('@id=lateral_pos').input('0')
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=LongCheckbox1').input(True)
    openpage_st.ele('@id=Longitudinal_pos').input('50')
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=HeightCheckbox1').input(True)
    openpage_st.ele('@id=Vertical_pos').input('0')
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').input('0')
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=RollCheckbox1').input(True)
    openpage_st.ele('@id=Roll_pos').input('0')
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()

    openpage_st.ele('@id=IsoCheckbox1').input(True)
    openpage_st.ele('@id=Iso_pos').input('0')
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    openpage_st.ele('@id=tab_select').select('Relative')
    sleep(1)

def test_mov_lat_pos(openpage_st):
    openpage_st.ele('@id=LateralCheckbox1').input(True)
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('25')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(25.0 - float(openpage_st.ele('@id=lat').value)))

def test_mov_lat_neg(openpage_st):
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('-50')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(-25.0 - float(openpage_st.ele('@id=lat').value)))

def test_mov_long_pos(openpage_st):
    openpage_st.ele('@id=LongCheckbox1').input(True)
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('50')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(100.0 - float(openpage_st.ele('@id=long').value)))

def test_mov_long_neg(openpage_st):
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('-100')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(0.0 - float(openpage_st.ele('@id=long').value)))

def test_mov_pitch_pos(openpage_st):
    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('3')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(3.0 - float(openpage_st.ele('@id=pitch').value)))

def test_mov_pitch_neg(openpage_st):
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('-6')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(-3.0 - float(openpage_st.ele('@id=pitch').value)))

def test_mov_pitch_zero(openpage_st):
    openpage_st.ele('@id=tab_select').select('Absolute')
    openpage_st.ele('@id=mode_select').select('Position')
    sleep(1)
    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('0')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(0.0 - float(openpage_st.ele('@id=pitch').value)))
    openpage_st.ele('@id=tab_select').select('Relative')
    openpage_st.ele('@id=mode_select').select('Position')
    sleep(1)

def test_mov_vertical_pos(openpage_st):
    openpage_st.ele('@id=HeightCheckbox1').input(True)
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('27')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(27.0 - float(openpage_st.ele('@id=height').value)))

def test_mov_vertical_neg(openpage_st):
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('-82')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(40)
    assert(standardErr > abs(-55.0 - float(openpage_st.ele('@id=height').value)))

def test_mov_roll_pos(openpage_st):
    openpage_st.ele('@id=RollCheckbox1').input(True)
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('3')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(3.0 - float(openpage_st.ele('@id=roll').value)))

def test_mov_roll_neg(openpage_st):
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('-6')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(-3.0 - float(openpage_st.ele('@id=roll').value)))

def test_mov_iso_pos(openpage_st):
    openpage_st.ele('@id=IsoCheckbox1').input(True)
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('96')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(30)
    assert(standardErr > abs(96.0 - float(openpage_st.ele('@id=iso').value)))

def test_mov_iso_neg(openpage_st):
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('-192')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(60)
    assert(standardErr > abs(-96.0 - float(openpage_st.ele('@id=iso').value)))

def test_mov_reset(openpage_st):
    openpage_st.ele('@id=tab_select').select('Absolute')
    sleep(1)
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