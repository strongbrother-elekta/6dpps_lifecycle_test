import pytest
import logging
import time
import sys
import configparser
from time import sleep


def test_association(ppsctrl_dut):
    ppsctrl_dut.send_associate_req()
    assert ppsctrl_dut.recv_associate_rsp()
    sleep(1)

def test_rtc_set_mode_clinical(ppsctrl_dut):
    ppsctrl_dut.rtc_set_integrity_mode(1)
    assert ppsctrl_dut.rtc_check_integrity_mode_reply()
    sleep(1)

def test_rtc_set_mode_service(ppsctrl_dut):
    ppsctrl_dut.rtc_set_integrity_mode(2)
    assert ppsctrl_dut.rtc_check_integrity_mode_reply()
    sleep(1)

def test_rtc_iec61217_asu(ppsctrl_dut):
    ppsctrl_dut.rtc_send_iec_61217_req(5, 5, 5, 1, 1, 10)
    assert ppsctrl_dut.rtc_check_asu_61217_reply()
    sleep(1)


