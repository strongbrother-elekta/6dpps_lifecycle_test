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

x_max=''
x_zero=''
x_min=''

y_max=''
y_zero=''
y_min=''

p_max=''
p_zero=''
p_min=''

z_max=''
z_zero=''
z_min=''

r_max=''
r_zero=''
r_min=''

iso_max=''
iso_zero=''
iso_min=''

retries = 0
max_retries = 1000

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
    sleep(20)

def test_record_zero(openpage_st):
    global x_zero, y_zero, z_zero, p_zero, r_zero, iso_zero, retries
    while retries < max_retries:
        try:
            x_zero = openpage_st.ele('@id:dynamic').eles('tag:span')[21].text
            y_zero = openpage_st.ele('@id:dynamic').eles('tag:span')[22].text
            z_zero = openpage_st.ele('@id:dynamic').eles('tag:span')[23].text
            p_zero = openpage_st.ele('@id:dynamic').eles('tag:span')[24].text
            r_zero = openpage_st.ele('@id:dynamic').eles('tag:span')[25].text
            iso_zero = openpage_st.ele('@id:dynamic').eles('tag:span')[26].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)


def test_mov_lat_pos(openpage_st):
    global x_max, retries
    openpage_st.ele('@id=LateralCheckbox1').input(True)
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('25')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    while retries < max_retries:
        try:
            x_max = openpage_st.ele('@id:dynamic').eles('tag:span')[21].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_lat_neg(openpage_st):
    global x_min, retries
    openpage_st.ele('@id=lateral_pos').clear()
    openpage_st.ele('@id=lateral_pos').input('-25')
    openpage_st.ele('@id=lateral_speed').clear()
    openpage_st.ele('@id=lateral_speed').input('5')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    while retries < max_retries:
        try:
            x_min = openpage_st.ele('@id:dynamic').eles('tag:span')[21].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_long_pos(openpage_st):
    global y_max, retries
    openpage_st.ele('@id=LongCheckbox1').input(True)
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('100')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(15)
    while retries < max_retries:
        try:
            y_max = openpage_st.ele('@id:dynamic').eles('tag:span')[22].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_long_neg(openpage_st):
    global y_min, retries
    openpage_st.ele('@id=Longitudinal_pos').clear()
    openpage_st.ele('@id=Longitudinal_pos').input('0')
    openpage_st.ele('@id=Longitudinal_speed').clear()
    openpage_st.ele('@id=Longitudinal_speed').input('9')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(30)
    while retries < max_retries:
        try:
            y_min = openpage_st.ele('@id:dynamic').eles('tag:span')[22].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_pitch_pos(openpage_st):
    global p_max, retries
    openpage_st.ele('@id=PitchCheckbox1').input(True)
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('3')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    while retries < max_retries:
        try:
            p_max = openpage_st.ele('@id:dynamic').eles('tag:span')[24].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_pitch_neg(openpage_st):
    global p_min, retries
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('-3')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    while retries < max_retries:
        try:
            p_min = openpage_st.ele('@id:dynamic').eles('tag:span')[24].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_pitch_zero(openpage_st):
    openpage_st.ele('@id=Pitch_pos').clear()
    openpage_st.ele('@id=Pitch_pos').input('0')
    openpage_st.ele('@id=Pitch_speed').clear()
    openpage_st.ele('@id=Pitch_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    assert(standardErr > abs(0.0 - float(openpage_st.ele('@id=pitch').value)))

def test_mov_vertical_pos(openpage_st):
    global z_max, retries
    openpage_st.ele('@id=HeightCheckbox1').input(True)
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('27')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    while retries < max_retries:
        try:
            z_max = openpage_st.ele('@id:dynamic').eles('tag:span')[23].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_vertical_neg(openpage_st):
    global z_min, retries
    openpage_st.ele('@id=Vertical_pos').clear()
    openpage_st.ele('@id=Vertical_pos').input('-55')
    openpage_st.ele('@id=Vertical_speed').clear()
    openpage_st.ele('@id=Vertical_speed').input('3')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(40)
    while retries < max_retries:
        try:
            z_min = openpage_st.ele('@id:dynamic').eles('tag:span')[23].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_roll_pos(openpage_st):
    global r_max, retries
    openpage_st.ele('@id=RollCheckbox1').input(True)
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('3')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(10)
    while retries < max_retries:
        try:
            r_max = openpage_st.ele('@id:dynamic').eles('tag:span')[25].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_roll_neg(openpage_st):
    global r_min, retries
    openpage_st.ele('@id=Roll_pos').clear()
    openpage_st.ele('@id=Roll_pos').input('-3')
    openpage_st.ele('@id=Roll_speed').clear()
    openpage_st.ele('@id=Roll_speed').input('0.6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(20)
    while retries < max_retries:
        try:
            r_min = openpage_st.ele('@id:dynamic').eles('tag:span')[25].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_iso_pos(openpage_st):
    global iso_max, retries
    openpage_st.ele('@id=IsoCheckbox1').input(True)
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('96')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(30)
    while retries < max_retries:
        try:
            iso_max = openpage_st.ele('@id:dynamic').eles('tag:span')[26].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_mov_iso_neg(openpage_st):
    global iso_min, retries
    openpage_st.ele('@id=Iso_pos').clear()
    openpage_st.ele('@id=Iso_pos').input('-96')
    openpage_st.ele('@id=Iso_speed').clear()
    openpage_st.ele('@id=Iso_speed').input('6')
    sleep(1)
    openpage_st.ele('@id=Asu-confirm').click()
    sleep(60)
    while retries < max_retries:
        try:
            iso_min = openpage_st.ele('@id:dynamic').eles('tag:span')[26].text
            break
        except:
            retries = retries + 1
            sleep(0.1)
            print(retries)

def test_write_config(openpage_st):
    config = configparser.ConfigParser()
    config['lateral'] = {}
    config['lateral']['max'] = x_max
    config['lateral']['zero'] = x_zero
    config['lateral']['min'] = x_min

    config['longtitudinal'] = {}
    config['longtitudinal']['max'] = y_max
    config['longtitudinal']['zero'] = y_zero
    config['longtitudinal']['min'] = y_min

    config['vertical'] = {}
    config['vertical']['max'] = z_max
    config['vertical']['zero'] = z_zero
    config['vertical']['min'] = z_min

    config['pitch'] = {}
    config['pitch']['max'] = p_max
    config['pitch']['zero'] = p_zero
    config['pitch']['min'] = p_min

    config['roll'] = {}
    config['roll']['max'] = r_max
    config['roll']['zero'] = r_zero
    config['roll']['min'] = r_min

    config['iso'] = {}
    config['iso']['max'] = iso_max
    config['iso']['zero'] = iso_zero
    config['iso']['min'] = iso_min

    with open('ppscount.ini', 'w') as configfile:
        config.write(configfile)

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