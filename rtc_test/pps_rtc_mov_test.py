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

def test_rtc_move_x(ppsctrl_dut):
    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_x(0, 5)
    assert ppsctrl_dut.rtc_check_reach_target_x(0, 12)
    sleep(2)

    # move to positive end
    ppsctrl_dut.rtc_send_move_to_end_req_x(1, 5)
    assert ppsctrl_dut.rtc_check_reach_target_x(25, 12)
    sleep(2)

    # move to negative end and stop
    ppsctrl_dut.rtc_send_move_to_end_req_x(2, 5)
    sleep(4)
    ppsctrl_dut.rtc_send_stop_move_req_x()
    sleep(5)
    ppsctrl_dut.rtc_send_move_to_end_req_x(2, 5)
    assert ppsctrl_dut.rtc_check_reach_target_x(-25, 20)
    sleep(2)

    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_x(0, 5)
    assert ppsctrl_dut.rtc_check_reach_target_x(0, 12)
    sleep(2)

def test_rtc_move_y(ppsctrl_dut):
    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_y(50, 9)
    assert ppsctrl_dut.rtc_check_reach_target_y(50, 20)
    sleep(2)

    # move to positive end
    ppsctrl_dut.rtc_send_move_to_end_req_y(1, 9)
    assert ppsctrl_dut.rtc_check_reach_target_y(100, 20)
    sleep(2)

    # move to negative end and stop
    ppsctrl_dut.rtc_send_move_to_end_req_y(2, 9)
    # sleep(4)
    # ppsctrl_dut.rtc_send_stop_move_req_y()
    # sleep(5)
    # ppsctrl_dut.rtc_send_move_to_end_req_y(2, 9)
    assert ppsctrl_dut.rtc_check_reach_target_y(0, 20)
    sleep(2)

    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_y(50, 9)
    assert ppsctrl_dut.rtc_check_reach_target_y(50, 20)
    sleep(2)

def test_rtc_move_z(ppsctrl_dut):
    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_z(0, 5)
    assert ppsctrl_dut.rtc_check_reach_target_z(0, 20)
    sleep(2)

    # move to positive end
    ppsctrl_dut.rtc_send_move_to_end_req_z(1, 5)
    assert ppsctrl_dut.rtc_check_reach_target_z(25, 20)
    sleep(2)

    # move to negative end and stop
    ppsctrl_dut.rtc_send_move_to_end_req_z(2, 5)
    sleep(4)
    ppsctrl_dut.rtc_send_stop_move_req_z()
    sleep(5)
    ppsctrl_dut.rtc_send_move_to_end_req_z(2, 5)
    assert ppsctrl_dut.rtc_check_reach_target_z(-50, 20)
    sleep(2)

    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_z(0, 5)
    assert ppsctrl_dut.rtc_check_reach_target_z(0, 20)
    sleep(2)

def test_rtc_move_r(ppsctrl_dut):
    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_r(0, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_r(0, 20)
    sleep(2)

    # move to positive end
    ppsctrl_dut.rtc_send_move_to_end_req_r(1, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_r(3, 20)
    sleep(2)

    # move to negative end and stop
    ppsctrl_dut.rtc_send_move_to_end_req_r(2, 0.6)
    sleep(4)
    ppsctrl_dut.rtc_send_stop_move_req_r()
    sleep(5)
    ppsctrl_dut.rtc_send_move_to_end_req_r(2, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_r(-3, 20)
    sleep(2)

    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_r(0, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_r(0, 20)
    sleep(2)

def test_rtc_move_p(ppsctrl_dut):
    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_p(0, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_p(0, 20)
    sleep(2)

    # move to positive end
    ppsctrl_dut.rtc_send_move_to_end_req_p(1, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_p(3, 20)
    sleep(2)

    # move to negative end and stop
    ppsctrl_dut.rtc_send_move_to_end_req_p(2, 0.6)
    sleep(4)
    ppsctrl_dut.rtc_send_stop_move_req_p()
    sleep(5)
    ppsctrl_dut.rtc_send_move_to_end_req_p(2, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_p(-3, 20)
    sleep(2)

    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_p(0, 0.6)
    assert ppsctrl_dut.rtc_check_reach_target_p(0, 20)
    sleep(2)

def test_rtc_move_iso(ppsctrl_dut):
    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_iso(0, 6)
    assert ppsctrl_dut.rtc_check_reach_target_iso(0, 30)
    sleep(2)

    # move to positive end
    ppsctrl_dut.rtc_send_move_to_end_req_iso(1, 6)
    assert ppsctrl_dut.rtc_check_reach_target_iso(95, 30)
    sleep(2)

    # move to negative end and stop
    ppsctrl_dut.rtc_send_move_to_end_req_iso(2, 6)
    sleep(10)
    ppsctrl_dut.rtc_send_stop_move_req_iso()
    sleep(5)
    ppsctrl_dut.rtc_send_move_to_end_req_iso(2, 6)
    assert ppsctrl_dut.rtc_check_reach_target_iso(-95, 60)
    sleep(2)

    # move to zero point
    ppsctrl_dut.rtc_send_move_to_point_req_iso(0, 6)
    assert ppsctrl_dut.rtc_check_reach_target_iso(0, 30)
    sleep(2)


