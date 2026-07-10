import pytest
from DrissionPage import *
import re
from time import sleep
import csv
import os
import datetime#写入时间
from DrissionPage import ChromiumPage
import configparser

standardErr=0.5

x_max=-614240790
x_zero=-637474775
x_min=-660734680
x_speed=4652916

y_max=31131090
y_zero=-3786384
y_min=-38723180
y_speed=10467652

p_max=-1211316660
p_zero=-1241616020
p_min=-1267541920
p_speed=6075119

z_max=4719999
z_zero=2613747
z_min=-3968230
z_speed=658200

r_max=22921540
r_zero=9109595
r_min=-4828150
r_speed=4390000

iso_max=577567167
iso_zero=531088824
iso_min=484610988
iso_speed=2272909

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
    openpage_st.ele('@id=mode_select').select('Count')
    sleep(1)

def test_read_config(openpage_st):
    global x_max, y_max, z_max, p_max, r_max, iso_max
    global x_zero, y_zero, z_zero, p_zero, r_zero, iso_zero
    global x_min, y_min, z_min, p_min, r_min, iso_min

    config = configparser.ConfigParser()
    config.read('ppscount.ini')

    section = config['lateral']
    x_max = section['max']
    x_zero = section['zero']
    x_min = section['min']

    section = config['longtitudinal']
    y_max = section['max']
    y_zero = section['zero']
    y_min = section['min']

    section = config['vertical']
    z_max = section['max']
    z_zero = section['zero']
    z_min = section['min']

    section = config['pitch']
    p_max = section['max']
    p_zero = section['zero']
    p_min = section['min']

    section = config['roll']
    r_max = section['max']
    r_zero = section['zero']
    r_min = section['min']

    section = config['iso']
    iso_max = section['max']
    iso_zero = section['zero']
    iso_min = section['min']

def test_mov_lat_pos(openpage_st):
    openpage_st.ele('@id=LateralCheckbox1').input(True)
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input(str(int(x_max) - int(x_zero)))
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input(str(x_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(25.0 - float(openpage_st.ele('@id=lat').value)))

def test_mov_lat_neg(openpage_st):
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input(str(int(x_min) - int(x_max)))
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input(str(x_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(-25.0 - float(openpage_st.ele('@id=lat').value)))

def test_mov_long_pos(openpage_st):
    openpage_st.ele('@id=LongCheckbox1').input(True)
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input(str(int(y_max) - int(y_zero)))
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input(str(y_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(100.0 - float(openpage_st.ele('@id=long').value)))

def test_mov_long_neg(openpage_st):
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input(str(int(y_min) - int(y_max)))
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input(str(y_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(0.0 - float(openpage_st.ele('@id=long').value)))

def test_mov_pitch_pos(openpage_st):
    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input(str(int(p_max) - int(p_zero)))
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input(str(p_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(3.0 - float(openpage_st.ele('@id=pitch').value)))

def test_mov_pitch_neg(openpage_st):
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input(str(int(p_min) - int(p_max)))
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input(str(p_speed))
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
    openpage_st.ele('@id=mode_select').select('Count')
    sleep(1)

def test_mov_vertical_pos(openpage_st):
    openpage_st.ele('@id=HeightCheckbox1').input(True)
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input(str(int(z_max) - int(z_zero)))
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input(str(z_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(27.0 - float(openpage_st.ele('@id=height').value)))

def test_mov_vertical_neg(openpage_st):
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input(str(int(z_min) - int(z_max)))
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input(str(z_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(40)
    assert(standardErr > abs(-55.0 - float(openpage_st.ele('@id=height').value)))

def test_mov_roll_pos(openpage_st):
    openpage_st.ele('@id=RollCheckbox1').input(True)
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input(str(int(r_max) - int(r_zero)))
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input(str(r_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(3.0 - float(openpage_st.ele('@id=roll').value)))

def test_mov_roll_neg(openpage_st):
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input(str(int(r_min) - int(r_max)))
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input(str(r_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    assert(standardErr > abs(-3.0 - float(openpage_st.ele('@id=roll').value)))

def test_mov_iso_pos(openpage_st):
    openpage_st.ele('@id=IsoCheckbox1').input(True)
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input(str(int(iso_max) - int(iso_zero)))
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input(str(iso_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(30)
    assert(standardErr > abs(96.0 - float(openpage_st.ele('@id=iso').value)))

def test_mov_iso_neg(openpage_st):
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input(str(int(iso_min) - int(iso_max)))
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input(str(iso_speed))
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(60)
    assert(standardErr > abs(-96.0 - float(openpage_st.ele('@id=iso').value)))

def test_mov_reset(openpage_st):
    openpage_st.ele('@id=tab_select').select('Absolute')
    openpage_st.ele('@id=mode_select').select('Position')
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