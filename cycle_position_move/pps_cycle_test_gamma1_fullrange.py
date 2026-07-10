import pytest
import logging
import time
import sys
import configparser
import threading
import gc

def test_cycle_move(ppsctrl_dut):

    gc.set_threshold(700,10,10)
    # time.sleep(3)
    ppsctrl_dut.set_z_p_linkage(True)
    config = configparser.ConfigParser()
    path = r"../configs/position_move/gamma1/config_full_range_gamma1/track_test_config_gamma1_full_range.ini"
    ppsctrl_dut.set_config_path(path)
    # ppsctrl_dut._update_cycle_count()
    config.read(path)

    axis = config.get("test_axis", "axis")
    logging.info(f"axis : {axis}")
    
    ppsctrl_dut.send_associate_req()
    assert ppsctrl_dut.recv_associate_rsp()


    if "x" in axis:
        ppsctrl_dut.set_x_track_para(
            config.get("x_axis", "track"),
            config.get("x_axis", "track_velocity"),
            config.getint("x_axis", "timeout"),
            config.getint("x_axis", "mode"),
            config.getint("test_axis", "left_cycle_x"),
        )
        ppsctrl_dut.send_single_axis_pos_move_req_x()
        #ppsctrl_dut.send_single_axis_count_move_req_x()
        #ppsctrl_dut.wait_reached_signal_disappear_x()
    if "y" in axis:
        ppsctrl_dut.set_y_track_para(
            config.get("y_axis", "track"),
            config.get("y_axis", "track_velocity"),
            config.getint("y_axis", "timeout"),
            config.getint("y_axis", "mode"),
            config.getint("test_axis", "left_cycle_y"),
        )
        ppsctrl_dut.send_single_axis_pos_move_req_y()
        #ppsctrl_dut.send_single_axis_count_move_req_y()
        #ppsctrl_dut.wait_reached_signal_disappear_y()


    if "iso" in axis:
        ppsctrl_dut.set_iso_track_para(
            config.get("iso_axis", "track"),
            config.get("iso_axis", "track_velocity"),
            config.getint("iso_axis", "timeout"),
            config.getint("iso_axis", "mode"),
            config.getint("test_axis", "left_cycle_iso"),
        )
        ppsctrl_dut.send_single_axis_pos_move_req_iso()
        #ppsctrl_dut.send_single_axis_count_move_req_iso()
        #ppsctrl_dut.wait_reached_signal_disappear_iso()
        
    if "z" in axis:
        ppsctrl_dut.set_z_track_para(
            config.get("z_axis", "track"),
            config.get("z_axis", "track_velocity"),
            config.getint("z_axis", "timeout"),
            config.getint("z_axis", "mode"),
            config.getint("test_axis", "left_cycle_z"),
        )
        ppsctrl_dut.send_single_axis_pos_move_req_z()
        #ppsctrl_dut.send_single_axis_count_move_req_z()
        #ppsctrl_dut.wait_reached_signal_disappear_z()
    
    if "p" in axis:
        ppsctrl_dut.set_p_track_para(
            config.get("p_axis", "track"),
            config.get("p_axis", "track_velocity"),
            config.getint("p_axis", "timeout"),
            config.getint("p_axis", "mode"),
            config.getint("test_axis", "left_cycle_p"),
        )
        ppsctrl_dut.send_single_axis_pos_move_req_p()
        #ppsctrl_dut.send_single_axis_count_move_req_p()
        #ppsctrl_dut.wait_reached_signal_disappear_p()
        #ppsctrl_dut.wait_reached_signal_appear_p()   

    if "r" in axis:
        ppsctrl_dut.set_r_track_para(
            config.get("r_axis", "track"),
            config.get("r_axis", "track_velocity"),
            config.getint("r_axis", "timeout"),
            config.getint("r_axis", "mode"),
            config.getint("test_axis", "left_cycle_r"),
        )
        ppsctrl_dut.send_single_axis_pos_move_req_r()
        #ppsctrl_dut.send_single_axis_count_move_req_r()
        #ppsctrl_dut.wait_reached_signal_disappear_r()
    time.sleep(10)
    
    ppsctrl_dut.display_axis_para()

    assert (
        ppsctrl_dut.x.cycle >= 0
        and ppsctrl_dut.y.cycle >= 0
        and ppsctrl_dut.z.cycle >= 0
        and ppsctrl_dut.r.cycle >= 0
        and ppsctrl_dut.p.cycle >= 0
        and ppsctrl_dut.iso.cycle >= 0
    )



    ppsctrl_dut.create_start_thread()
    assert ppsctrl_dut.track_schedule_process()

    
    

    ppsctrl_dut.send_associate_release_req()
    msg = ppsctrl_dut.recv_associate_release_rsp()
    
    
    assert not msg is None
