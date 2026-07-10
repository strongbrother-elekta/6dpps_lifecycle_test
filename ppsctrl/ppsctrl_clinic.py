import typing
import time
import threading
import gc
import datetime as dt
import sys
import os
import logging
import csv
sys.path.append("../ppsctrl/proto/py")
import util_pb2
import associate_pb2

# from proto.py import tblctl_pb2
import tblservicemode_pb2
import configparser

from .traceclient import TraceClient
from logging.handlers import TimedRotatingFileHandler
from google.protobuf import symbol_database as _symbol_database
import queue 

def set_log(filename):
    logger = logging.getLogger()
    #logger.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s Line%(lineno)d [%(levelname)s] %(message)s')

    #time_handler = TimedRotatingFileHandler(filename=filename, when='D', interval=1, backupCount=7)
    time_handler = TimedRotatingFileHandler(filename=filename, when='H', interval=12, backupCount=10)
    time_handler.setLevel(logging.INFO)
    time_handler.setFormatter(file_format)

    logger.addHandler(time_handler)
    return logger



#logger = logging.getLogger(__name__)

logger=set_log('../logs/clinic_test.log')

EPSINON = 0.00001
HEARTBEAT = 0.08
DEFAULT_TIMEOUT=8

     
def append_to_file(file_path, string_to_append):
    with open(file_path, 'a') as file:
        file.write(string_to_append)
        
def write_data_to_csv(file_name, data, fieldnames=None):
    with open(file_name, mode='a', newline='', encoding='utf-8') as file:
        if fieldnames:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:
                writer.writeheader()
        else:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            if file.tell() == 0:
                writer.writeheader()
    writer.writerows(data)
        
def axis_move_handler_x(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while self.x.cycle>0:
        self.xindex=1
        track_count = len(self.x.track)
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H:%M:%S")
        self.count_x+=1
        append_to_file(self.statistic_file_name_x,  str(self.count_x)+ ';'+ str(formatted_now) + ';')
        while self.xindex<track_count:
            #logging.info(f"------axis_move_handler_x thread have start {track_count}")  
            if self.next_move_x==True and self.send_stop==False:
                self.x.count = int(self.x.track[self.xindex])
                self.x.count_velocity = int(self.x.track_velocity[self.xindex])
                logging.info(f"------axis_move_handler_x-------- {self.xindex}/{track_count}/{self.x.count}/{self.send_stop}")  
                self.next_move_x=False
                time.sleep(1)
                self.send_single_axis_pos_move_req_x()
                self.xindex += 1
            else:
                #logging.info(f"------axis_move_handler_x are sleeping")  
                time.sleep(0.01)
        self.phase1_barrier.wait()
        if self.x.cycle == self.x.cycle: # 新增
            self.pitch_sem.release()    # 新增
        
        self.x.cycle = self.x.cycle - 1
        if self.x.cycle <= 0:
            self.x.cycle = 0
        self.phase2_barrier.wait()
        append_to_file(self.statistic_file_name_x,'\n')
    logging.info(f"------axis_move_handler_x thread exit -------------------")  

def axis_move_handler_y(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while self.y.cycle>0:
        self.yindex=1
        track_count = len(self.y.track)
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H:%M:%S")
        self.count_y+=1
        append_to_file(self.statistic_file_name_y,  str(self.count_y)+ ';'+ str(formatted_now) + ';')
        while self.yindex<track_count:
            #logging.info(f"------axis_move_handler_y thread have start {track_count}")  
            if self.next_move_y==True and self.send_stop==False:
                self.y.count = int(self.y.track[self.yindex])
                self.y.count_velocity = int(self.y.track_velocity[self.yindex])
                logging.info(f"------axis_move_handler_y-------- {self.yindex}/{track_count}/{self.y.count}/{self.send_stop}")  
                self.next_move_y=False
                time.sleep(1)
                self.send_single_axis_pos_move_req_y()
                self.yindex += 1
            else:
                #logging.info(f"------axis_move_handler_y are sleeping")  
                time.sleep(0.01)
        self.phase1_barrier.wait()
        self.y.cycle = self.y.cycle - 1
        if self.y.cycle <= 0:
            self.y.cycle = 0      
        self.phase2_barrier.wait()
        append_to_file(self.statistic_file_name_y,'\n')   
    logging.info(f"------axis_move_handler_y thread exit -------------------")

def axis_move_handler_z(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while self.z.cycle>0:
        self.zindex=1
        track_count = len(self.z.track)
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H:%M:%S")
        self.count_z+=1
        append_to_file(self.statistic_file_name_z,  str(self.count_z)+ ';'+ str(formatted_now) + ';')
        while self.zindex<track_count:
            #logging.info(f"------axis_move_handler_z thread have start index:{self.zindex} / {track_count}")  
            if self.next_move_z==True and self.send_stop==False:
                self.z.count = float(self.z.track[self.zindex])
                self.z.count_velocity = float(self.z.track_velocity[self.zindex])
                logging.info(f"------axis_move_handler_z-------- {self.zindex}/{track_count}/{self.z.count}/{self.send_stop}")  
                self.next_move_z=False
                time.sleep(1)
                self.send_single_axis_pos_move_req_z()
                self.zindex += 1
            else:
                #logging.info(f"------axis_move_handler_z are sleeping")  
                time.sleep(0.01)
        self.phase1_barrier.wait()
        self.z.cycle = self.z.cycle - 1
        if self.z.cycle <= 0:
            self.z.cycle = 0  
        self.phase2_barrier.wait()
        append_to_file(self.statistic_file_name_z,'\n')
    logging.info(f"------axis_move_handler_z thread exit -------------------")  


def axis_move_handler_p(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while self.p.cycle>0:
        self.pitch_sem.acquire()
        self.pindex=1
        track_count = len(self.p.track)
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H:%M:%S")
        self.count_p+=1
        append_to_file(self.statistic_file_name_p,  str(self.count_p)+ ';'+ str(formatted_now) + ';')
        while self.pindex<track_count:
            #logging.info(f"------axis_move_handler_p thread have start {track_count}")  
            if self.next_move_p==True and self.send_stop==False:
                self.p.count = float(self.p.track[self.pindex])
                self.p.count_velocity = float(self.p.track_velocity[self.pindex])
                logging.info(f"------axis_move_handler_p-------- {self.pindex}/{track_count}/{self.p.count}/{self.send_stop}")  
                self.next_move_p=False
                time.sleep(1)
                self.send_single_axis_pos_move_req_p()
                self.pindex += 1
            else:
                #logging.info(f"------axis_move_handler_p are sleeping")  
                time.sleep(0.01)
        while self.next_move_p==False:
            time.sleep(1)
        self.roll_sem.release()          
        self.p.cycle = self.p.cycle - 1
        if self.p.cycle <= 0:
            self.p.cycle = 0   
        self.phase2_barrier.wait()
        append_to_file(self.statistic_file_name_p,'\n')
        
    logging.info(f"------axis_move_handler_p thread exit -------------------")        

def axis_move_handler_r(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while self.r.cycle>0:
        self.roll_sem.acquire()
        self.rindex=1
        track_count = len(self.r.track)
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H:%M:%S")
        self.count_r+=1
        append_to_file(self.statistic_file_name_r,  str(self.count_r)+ ';'+ str(formatted_now) + ';')
        while self.rindex<track_count: 
            #logging.info(f"------axis_move_handler_r thread have start {track_count}")  
            if self.next_move_r==True and self.send_stop==False:
                self.r.count = float(self.r.track[self.rindex])
                self.r.count_velocity = float(self.r.track_velocity[self.rindex])
                logging.info(f"------axis_move_handler_r-------- {self.rindex}/{track_count}/{self.r.count}/{self.send_stop}")  
                self.next_move_r=False
                time.sleep(1)
                self.send_single_axis_pos_move_req_r()
                self.rindex += 1
            else:
                #logging.info(f"------axis_move_handler_r are sleeping")  
                time.sleep(0.01)
                
        while self.next_move_r==False:    # 新增
            time.sleep(1)               # 新增
            
        self.iso_sem.release()  # 新增
        self.r.cycle = self.r.cycle - 1
        if self.r.cycle <= 0:
            self.r.cycle = 0
        time.sleep(self.r.timeout/10)
        self.phase2_barrier.wait()
        append_to_file(self.statistic_file_name_r,'\n')
    logging.info(f"------axis_move_handler_r thread exit -------------------")        

def axis_move_handler_iso(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while self.iso.cycle>0:
        self.iso_sem.acquire()  # 新增
        self.isoindex=1
        track_count = len(self.iso.track)
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d-%H:%M:%S")
        self.count_iso+=1
        append_to_file(self.statistic_file_name_iso,  str(self.count_iso)+ ';'+ str(formatted_now) + ';')
        while self.isoindex<track_count:
            #logging.info(f"------axis_move_handler_iso thread have start {track_count}")  
            if self.next_move_iso==True and self.send_stop==False:
                self.iso.count = int(self.iso.track[self.isoindex])
                self.iso.count_velocity = int(self.iso.track_velocity[self.isoindex])
                 #logging.info(f"------axis_move_handler_iso-------- {self.isoindex}/{track_count}/{self.send_stop}")  
                self.next_move_iso=False
                time.sleep(1)
                self.send_single_axis_pos_move_req_iso()
                self.isoindex += 1
            else:
                #logging.info(f"------axis_move_handler_x are sleeping")  
                time.sleep(0.1)
        # self.phase1_barrier.wait()        # 去掉同步X Y Z ISO 号线程中的ISO
        
        while self.next_move_iso==False:
            time.sleep(1)
        # self.pitch_sem.release()        # 去掉pitch线程
        self.iso.cycle = self.iso.cycle - 1
        if self.iso.cycle <= 0:
            self.iso.cycle = 0 
        self.phase2_barrier.wait()
        append_to_file(self.statistic_file_name_iso, '\n')
    logging.info(f"------axis_move_handler_iso thread exit -------------------")


def heartbeat_process(self,threadName):
    logging.info(f"thread {threadName} started at {time.ctime(time.time())}") 
    while True:
        self.send_keepalive_req()
        self.heartbeat+=1
        if self.heartbeat>1500:
            self.release_associate=False
            self.associate=False
            self.send_stop=True
            time.sleep(1)# stop other thread 
            while self.release_associate==False:
                self.send_associate_release_req()
                logging.info(f"------heartbeat_process release-associating -------------------{self.release_associate}")    
                time.sleep(0.5)
            logging.info(f"------heartbeat_process release-associate done -------------------{self.release_associate}")    
            while self.associate==False:
                self.send_associate_req()
                logging.info(f"------heartbeat_process associating  -------------------{self.associate}")  
                time.sleep(0.2)
            logging.info(f"------heartbeat_process associate done  -------------------{self.associate}")  

            self.reset_params_disconnect()
        time.sleep(HEARTBEAT)
    logging.info(f"------heartbeat_process thread exit -------------------")



class TableMoveParamPosition:
    def __init__(
        self,
        axis: util_pb2.AxisIndex,
        # mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        self.axis = axis
        self.pos = 0.0
        self.speed = 0.0
        self.count = 0.0
        self.count_s = 0
        self.count_e = 0
        self.count_m = 0
        self.count_velocity = 0
        self.timeout = 0
        self.track = ""
        self.track_velocity = ""
        
        self.track_count = 0
        self.mode = mode
        self.cycle = cycle


        self.time_span_x=[]
        self.time_span_y=[]
        self.time_span_z=[]
        self.time_span_p=[]
        self.time_span_r=[]     
        self.time_span_iso=[]



class PPSCtrl_Clinic:
    def __init__(self, traceclient: TraceClient):
        self._log_labels: typing.List[str] = []
        self._log_data: typing.List[str] = []
        # self._parse_config_file = parseconfigfile.ParseConfigFile()
        self.traceclient = traceclient
        #self.timer = threading.Timer(HEARTBEAT, self._func)
        self.association_id = 0
        self.sequence_num_bi = 0

        self.x = TableMoveParamPosition(util_pb2.AxisIndex.LATERAL)
        self.y = TableMoveParamPosition(util_pb2.AxisIndex.LONGITUDINAL)
        self.z = TableMoveParamPosition(util_pb2.AxisIndex.VERTICAL)
        self.r = TableMoveParamPosition(util_pb2.AxisIndex.ROLL)
        self.p = TableMoveParamPosition(util_pb2.AxisIndex.PITCH)
        self.iso = TableMoveParamPosition(util_pb2.AxisIndex.ISO)

        self.is_z_p_linkage = False
        self.configfile = None
        self.bigcycle =0
        self.stage=0
        self.req_id=0
        self.next_move_x=False
        self.next_move_y=False
        self.next_move_z=False
        self.next_move_p=False
        self.next_move_r=False
        self.next_move_iso=False
        self.axis_z_move_done=False
        self.axis_p_move_done=False
        
        self.xindex=0
        self.yindex=0
        self.zindex=0
        self.pindex=0
        self.rindex=0
        self.isoindex=0
        
        self.last_pos_x=0.0
        self.last_pos_y=0.0
        self.last_pos_z=0.0
        self.last_pos_p=0.0
        self.last_pos_r=0.0
        self.last_pos_iso=0.0
        
        
        self.count_x=0
        self.count_y=0
        self.count_z=0
        self.count_p=0
        self.count_r=0
        self.count_iso=0
        
       
        self.cf = configparser.ConfigParser()
        self.heartbeat=0
        self.loop_count=0
        self.release_associate=False
        self.associate=False
        self.send_stop=False
        
        # 同步工具定义 
        # self.phase1_barrier = threading.Barrier(4)         # 用于同步X Y Z ISO 号线程完成 
        self.phase1_barrier = threading.Barrier(3)         # 用于同步X Y Z 号线程完成 ，新增
        self.pitch_sem = threading.Semaphore(0)           # 控制PITCH线程启动 
        self.roll_sem = threading.Semaphore(0)           # 控制ROLL线程启动 
        self.iso_sem = threading.Semaphore(0)            # 控制Iso线程启动, 新增
        self.all_done_event = threading.Event()            # 全局退出事件 
        self.phase2_barrier = threading.Barrier(6)
        
        
        now = dt.datetime.now()
        formatted_now = now.strftime("%Y%m%d%H%M%S")
        folder_path=str(os.getcwd()+ '\\reports\\'+ str(formatted_now))
        
        try:
            os.mkdir(folder_path)
        except FileExistsError:
            print(f"Folder '{folder_path}' error.")
            
        self.statistic_file_name_x=folder_path+'//target_cycle_time_x.txt'
        self.statistic_file_name_y=folder_path+'//target_cycle_time_y.txt'
        self.statistic_file_name_z=folder_path+'//target_cycle_time_z.txt'
        self.statistic_file_name_p=folder_path+'//target_cycle_time_p.txt'
        self.statistic_file_name_r=folder_path+'//target_cycle_time_r.txt'
        self.statistic_file_name_iso=folder_path+'//target_cycle_time_iso.txt'
 
        
    crc32_table = [
        0x0,
        0x4C11DB7,
        0x9823B6E,
        0xD4326D9,
        0x130476DC,
        0x17C56B6B,
        0x1A864DB2,
        0x1E475005,
        0x2608EDB8,
        0x22C9F00F,
        0x2F8AD6D6,
        0x2B4BCB61,
        0x350C9B64,
        0x31CD86D3,
        0x3C8EA00A,
        0x384FBDBD,
        0x4C11DB70,
        0x48D0C6C7,
        0x4593E01E,
        0x4152FDA9,
        0x5F15ADAC,
        0x5BD4B01B,
        0x569796C2,
        0x52568B75,
        0x6A1936C8,
        0x6ED82B7F,
        0x639B0DA6,
        0x675A1011,
        0x791D4014,
        0x7DDC5DA3,
        0x709F7B7A,
        0x745E66CD,
        0x9823B6E0,
        0x9CE2AB57,
        0x91A18D8E,
        0x95609039,
        0x8B27C03C,
        0x8FE6DD8B,
        0x82A5FB52,
        0x8664E6E5,
        0xBE2B5B58,
        0xBAEA46EF,
        0xB7A96036,
        0xB3687D81,
        0xAD2F2D84,
        0xA9EE3033,
        0xA4AD16EA,
        0xA06C0B5D,
        0xD4326D90,
        0xD0F37027,
        0xDDB056FE,
        0xD9714B49,
        0xC7361B4C,
        0xC3F706FB,
        0xCEB42022,
        0xCA753D95,
        0xF23A8028,
        0xF6FB9D9F,
        0xFBB8BB46,
        0xFF79A6F1,
        0xE13EF6F4,
        0xE5FFEB43,
        0xE8BCCD9A,
        0xEC7DD02D,
        0x34867077,
        0x30476DC0,
        0x3D044B19,
        0x39C556AE,
        0x278206AB,
        0x23431B1C,
        0x2E003DC5,
        0x2AC12072,
        0x128E9DCF,
        0x164F8078,
        0x1B0CA6A1,
        0x1FCDBB16,
        0x18AEB13,
        0x54BF6A4,
        0x808D07D,
        0xCC9CDCA,
        0x7897AB07,
        0x7C56B6B0,
        0x71159069,
        0x75D48DDE,
        0x6B93DDDB,
        0x6F52C06C,
        0x6211E6B5,
        0x66D0FB02,
        0x5E9F46BF,
        0x5A5E5B08,
        0x571D7DD1,
        0x53DC6066,
        0x4D9B3063,
        0x495A2DD4,
        0x44190B0D,
        0x40D816BA,
        0xACA5C697,
        0xA864DB20,
        0xA527FDF9,
        0xA1E6E04E,
        0xBFA1B04B,
        0xBB60ADFC,
        0xB6238B25,
        0xB2E29692,
        0x8AAD2B2F,
        0x8E6C3698,
        0x832F1041,
        0x87EE0DF6,
        0x99A95DF3,
        0x9D684044,
        0x902B669D,
        0x94EA7B2A,
        0xE0B41DE7,
        0xE4750050,
        0xE9362689,
        0xEDF73B3E,
        0xF3B06B3B,
        0xF771768C,
        0xFA325055,
        0xFEF34DE2,
        0xC6BCF05F,
        0xC27DEDE8,
        0xCF3ECB31,
        0xCBFFD686,
        0xD5B88683,
        0xD1799B34,
        0xDC3ABDED,
        0xD8FBA05A,
        0x690CE0EE,
        0x6DCDFD59,
        0x608EDB80,
        0x644FC637,
        0x7A089632,
        0x7EC98B85,
        0x738AAD5C,
        0x774BB0EB,
        0x4F040D56,
        0x4BC510E1,
        0x46863638,
        0x42472B8F,
        0x5C007B8A,
        0x58C1663D,
        0x558240E4,
        0x51435D53,
        0x251D3B9E,
        0x21DC2629,
        0x2C9F00F0,
        0x285E1D47,
        0x36194D42,
        0x32D850F5,
        0x3F9B762C,
        0x3B5A6B9B,
        0x315D626,
        0x7D4CB91,
        0xA97ED48,
        0xE56F0FF,
        0x1011A0FA,
        0x14D0BD4D,
        0x19939B94,
        0x1D528623,
        0xF12F560E,
        0xF5EE4BB9,
        0xF8AD6D60,
        0xFC6C70D7,
        0xE22B20D2,
        0xE6EA3D65,
        0xEBA91BBC,
        0xEF68060B,
        0xD727BBB6,
        0xD3E6A601,
        0xDEA580D8,
        0xDA649D6F,
        0xC423CD6A,
        0xC0E2D0DD,
        0xCDA1F604,
        0xC960EBB3,
        0xBD3E8D7E,
        0xB9FF90C9,
        0xB4BCB610,
        0xB07DABA7,
        0xAE3AFBA2,
        0xAAFBE615,
        0xA7B8C0CC,
        0xA379DD7B,
        0x9B3660C6,
        0x9FF77D71,
        0x92B45BA8,
        0x9675461F,
        0x8832161A,
        0x8CF30BAD,
        0x81B02D74,
        0x857130C3,
        0x5D8A9099,
        0x594B8D2E,
        0x5408ABF7,
        0x50C9B640,
        0x4E8EE645,
        0x4A4FFBF2,
        0x470CDD2B,
        0x43CDC09C,
        0x7B827D21,
        0x7F436096,
        0x7200464F,
        0x76C15BF8,
        0x68860BFD,
        0x6C47164A,
        0x61043093,
        0x65C52D24,
        0x119B4BE9,
        0x155A565E,
        0x18197087,
        0x1CD86D30,
        0x29F3D35,
        0x65E2082,
        0xB1D065B,
        0xFDC1BEC,
        0x3793A651,
        0x3352BBE6,
        0x3E119D3F,
        0x3AD08088,
        0x2497D08D,
        0x2056CD3A,
        0x2D15EBE3,
        0x29D4F654,
        0xC5A92679,
        0xC1683BCE,
        0xCC2B1D17,
        0xC8EA00A0,
        0xD6AD50A5,
        0xD26C4D12,
        0xDF2F6BCB,
        0xDBEE767C,
        0xE3A1CBC1,
        0xE760D676,
        0xEA23F0AF,
        0xEEE2ED18,
        0xF0A5BD1D,
        0xF464A0AA,
        0xF9278673,
        0xFDE69BC4,
        0x89B8FD09,
        0x8D79E0BE,
        0x803AC667,
        0x84FBDBD0,
        0x9ABC8BD5,
        0x9E7D9662,
        0x933EB0BB,
        0x97FFAD0C,
        0xAFB010B1,
        0xAB710D06,
        0xA6322BDF,
        0xA2F33668,
        0xBCB4666D,
        0xB8757BDA,
        0xB5365D03,
        0xB1F740B4,
    ]
    
        
    def _crc32(self, binaries):
        crc = 0xFFFFFFFF
        index = 0
        while index < len(binaries):
            crc = self.crc32_table[(crc & 0xFF) ^ binaries[index]] ^ (crc // 256)
            index = index + 1
        return crc ^ 0xFFFFFFFF

    def reset_params(self):
        del self.x
        del self.y
        del self.z
        del self.r
        del self.p
        del self.iso
        #gc.collect()
        self.x = TableMoveParamPosition(util_pb2.AxisIndex.LATERAL)
        self.y = TableMoveParamPosition(util_pb2.AxisIndex.LONGITUDINAL)
        self.z = TableMoveParamPosition(util_pb2.AxisIndex.VERTICAL)
        self.r = TableMoveParamPosition(util_pb2.AxisIndex.ROLL)
        self.p = TableMoveParamPosition(util_pb2.AxisIndex.PITCH)
        self.iso = TableMoveParamPosition(util_pb2.AxisIndex.ISO)

        self.is_z_p_linkage = False
        self.configfile = None
        self.stage=0
        self.req_id=0
        self.heartbeat=0
        self.loop_count=0
        self.release_associate=False
        self.associate=False
        self.bigcycle =0
        self.send_stop=False
        self.next_move_x=False
        self.next_move_y=False
        self.next_move_z=False
        self.next_move_p=False
        self.next_move_r=False
        self.next_move_iso=False
        self.axis_z_move_done=False
        self.axis_p_move_done=False
        self.xindex=0
        self.yindex=0
        self.zindex=0
        self.pindex=0
        self.rindex=0
        self.isoindex=0
        
    def reset_params_disconnect(self):
        self.stage=0
        self.req_id=0
        self.heartbeat=0
        self.loop_count=0
        #self.release_associate=False
        #self.associate=False
        self.bigcycle =0
        self.next_move_x=True
        self.next_move_y=True
        self.next_move_z=True
        self.next_move_p=True
        self.next_move_r=True
        self.next_move_iso=True
        self.axis_z_move_done=False
        self.axis_p_move_done=False
        self.is_z_p_linkage = True
        
        if self.xindex>3:
           self.xindex=1
        else:
           self.xindex=4 
               
        if self.yindex>3:
           self.yindex=1
        else:
           self.yindex=4 

        if self.zindex>3:
           self.zindex=1
        else:
           self.zindex=4         
        
        if self.pindex>3:
           self.pindex=1
        else:
           self.pindex=4         
        
        if self.rindex>3:
           self.rindex=1
        else:
           self.rindex=4  
           
        if self.isoindex>3:
           self.isoindex=1
        else:
           self.isoindex=4   
           
        self.send_stop=False
           

    def set_config_path(self, path):
        self.configfile = path
        self.cf.read(path)
        # self._load_config_para()

    def set_big_cycle(self,value):
        self.bigcycle=value

    def set_stage(self,value):
        self.stage=value

    def _update_cycle_count(self):
        if self.configfile == None:
            return
        # self.cf.add_section('test_axis')
        self.cf.set("test_axis", "left_cycle_x", str(self.x.cycle))
        self.cf.set("test_axis", "left_cycle_y", str(self.y.cycle))
        self.cf.set("test_axis", "left_cycle_z", str(self.z.cycle))
        self.cf.set("test_axis", "left_cycle_r", str(self.r.cycle))
        self.cf.set("test_axis", "left_cycle_p", str(self.p.cycle))
        self.cf.set("test_axis", "left_cycle_iso", str(self.iso.cycle))
        self.cf.write(open(self.configfile, "w"))

    def _update_track_count(self):
        if self.configfile == None:
            return
        # self.cf.add_section('test_axis')
        self.cf.set("test_axis", "left_track_count_x", str(self.x.track_count))
        self.cf.set("test_axis", "left_track_count_y", str(self.y.track_count))
        self.cf.set("test_axis", "left_track_count_z", str(self.z.track_count))
        self.cf.set("test_axis", "left_track_count_r", str(self.r.track_count))
        self.cf.set("test_axis", "left_track_count_p", str(self.p.track_count))
        self.cf.set("test_axis", "left_track_count_iso", str(self.iso.track_count))
        self.cf.write(open(self.configfile, "w"))

    def _func(self):
        self.send_keepalive_req()
        self.timer = threading.Timer(HEARTBEAT, self._func)
        self.timer.daemon = True
        self.timer.start()

    def send_associate_req(self):
        serverRx = associate_pb2.ServerRx()
        serverRx.association_id = 1
        self.sequence_num_bi = self.sequence_num_bi + 1
        serverRx.sequence_num_bi = self.sequence_num_bi
        serverRx.assoc_req.version = '1.0.0.74'
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        logging.info(f"send_associate_req : {serverRx}")
        del serverRx_protobuf_data
        del serverRx
        #gc.collect()

    def recv_associate_rsp(self, timeout=5.0):
        timeout_at = time.time() + timeout
        ret = False
        while True:
            msg = self.traceclient.readMsg()
            if msg is None:
                time.sleep(0.01)
                if time.time() > timeout_at:
                    logging.info("recv_associate_rsp timeout")
                    break
                else:
                    continue
            serverTx = associate_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(msg)
            if serverTx.WhichOneof("Msg") == "assoc_rep":
                logging.info(f"parse_serverTx : {serverTx}")
                # if (serverTx.assoc_rep.status_code == associate_pb2.ServerTx.AssociateRep.StatusCode.SUCCESS):
                if True:
                    self.association_id = serverTx.association_id
                    self.associate=True
                    #self.timer.start()
                    ret = True
                else:
                    ret = False
                del serverTx
                del msg
                #gc.collect()
                break

            del serverTx
            del msg
            #gc.collect()

        return ret

    def send_associate_release_req(self):
        serverRx = associate_pb2.ServerRx()
        serverRx.association_id = self.association_id
        self.sequence_num_bi = self.sequence_num_bi + 1
        serverRx.sequence_num_bi = self.sequence_num_bi
        serverRx.assoc_release_req.SetInParent()
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        logging.info(f"send_associate_release_req : {serverRx}")
        #self.timer.cancel()
        del serverRx_protobuf_data
        serverRx_protobuf_data=None
        del serverRx
        serverRx=None
        #gc.collect()

    def recv_associate_release_rsp(self, timeout=1.0):
        timeout_at = time.time() + timeout
        ret = False
        while True:
            msg = self.traceclient.readMsg()
            if msg is None:
                time.sleep(0.01)
                if time.time() > timeout_at:
                    break
                else:
                    continue
            serverTx = associate_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(msg)
            logging.info(f'parse_serverTx : {serverTx}')
            if serverTx.WhichOneof("Msg") == "assoc_release_rep":
                logging.info(f"parse_serverTx : {serverTx}")
                ret = True
                del serverTx
                del msg
                #gc.collect()
                break

            del serverTx
            del msg
            #gc.collect()

        return ret

    def send_keepalive_req(self):
        serverRx = associate_pb2.ServerRx()
        serverRx.association_id = self.association_id
        self.sequence_num_bi = self.sequence_num_bi + 1
        serverRx.sequence_num_bi = self.sequence_num_bi
        serverRx.keep_alive_req.SetInParent()
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        #logging.info(f'parse_serverRx : {serverRx}')
        self.heartbeat+=1
        del serverRx_protobuf_data
        serverRx_protobuf_data=None
        del serverRx
        serverRx=None
        #gc.collect()

    def recv_keepalive_rsp(self, timeout=1.0):
        timeout_at = time.time() + timeout
        ret = False
        while True:
            msg = self.traceclient.readMsg()
            if msg is None:
                time.sleep(0.01)
                if time.time() > timeout_at:
                    break
                else:
                    continue
            serverTx = associate_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(msg)
            # logging.info(f'parse_serverTx : {serverTx}')
            if serverTx.WhichOneof("Msg") == "keep_alive_rep":
                logging.info(f"parse_serverTx : {serverTx}")
                ret = True
                del serverTx
                del msg
                #gc.collect()
                break

            del serverTx
            del msg
            #gc.collect()

        return ret

    def _send_data_req(self, Payload):
        serverRx = associate_pb2.ServerRx()
        serverRx.association_id = self.association_id
        self.sequence_num_bi = self.sequence_num_bi + 1
        serverRx.sequence_num_bi = self.sequence_num_bi
        serverRx.data.payload = Payload
        serverRx.data.crc = self._crc32(Payload)
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        # logging.info(f'parse_serverRx : {serverRx}')
        del serverRx_protobuf_data
        del serverRx
        #gc.collect()
        
       
        
    def _send_single_axis_pos_move_req(self, movePara: TableMoveParamPosition):
        serverRx = tblservicemode_pb2.ServerRx()
        axisReq = serverRx.pos_move_req.reqs.add()
        #logging.info(f"----------------1 : {movePara.axis} {movePara.count} {movePara.count_velocity} {movePara.mode} ")
        axisReq.axis = movePara.axis
        if movePara.axis== util_pb2.AxisIndex.LONGITUDINAL:
            axisReq.pos = float(movePara.count/10)
        else:
            axisReq.pos = float(movePara.count)
        self.req_id+=1
        #axisReq.pos_id=self.req_id    
        axisReq.speed = float(movePara.count_velocity)
        axisReq.mode = movePara.mode
        axisReq.useSecondSensor=True
        logging.info(f"position move req : axis:{axisReq.axis},reqpos:{axisReq.pos}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        serverRx_protobuf_data=None
        del serverRx
        serverRx=None
        #gc.collect()


    def send_single_axis_pos_move_req_x(self):
        logging.info(f"send_single_axis_pos_move_req_x")
        return self._send_single_axis_pos_move_req(self.x)

    def send_single_axis_pos_move_req_y(self):
        return self._send_single_axis_pos_move_req(self.y)

    def send_single_axis_pos_move_req_z(self):
        return self._send_single_axis_pos_move_req(self.z)

    def send_single_axis_pos_move_req_r(self):
        return self._send_single_axis_pos_move_req(self.r)

    def send_single_axis_pos_move_req_p(self):
        return self._send_single_axis_pos_move_req(self.p)

    def send_single_axis_pos_move_req_iso(self):
        return self._send_single_axis_pos_move_req(self.iso)


    def _send_single_axis_count_move_req(self, movePara: TableMoveParamPosition):
        serverRx = tblservicemode_pb2.ServerRx()
        axisReq = serverRx.count_move_req.reqs.add()
        axisReq.axis = movePara.axis
        axisReq.count = movePara.count
        axisReq.count_velocity = movePara.count_velocity
        axisReq.mode = movePara.mode
        self.req_id+=1
        axisReq.req_id=self.req_id
        logging.info(f"parse_axisReq : {axisReq}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        serverRx_protobuf_data=None
        del serverRx
        serverRx=None
        #gc.collect()

    def send_single_axis_count_move_req_x(self):
        return self._send_single_axis_count_move_req(self.x)

    def send_single_axis_count_move_req_y(self):
        return self._send_single_axis_count_move_req(self.y)

    def send_single_axis_count_move_req_z(self):
        return self._send_single_axis_count_move_req(self.z)

    def send_single_axis_count_move_req_r(self):
        return self._send_single_axis_count_move_req(self.r)

    def send_single_axis_count_move_req_p(self):
        return self._send_single_axis_count_move_req(self.p)

    def send_single_axis_count_move_req_iso(self):
        return self._send_single_axis_count_move_req(self.iso)

    

    def _send_table_stop_move_req(self, axis: util_pb2.AxisIndex):
        serverRx = tblservicemode_pb2.ServerRx()
        serverRx.stop_move_req.axes.append(axis)
        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        #gc.collect()

    def send_table_stop_move_req_x(self):
        return self._send_table_stop_move_req(self.x.axis)

    def send_table_stop_move_req_y(self):
        return self._send_table_stop_move_req(self.y.axis)

    def send_table_stop_move_req_z(self):
        return self._send_table_stop_move_req(self.z.axis)

    def send_table_stop_move_req_r(self):
        return self._send_table_stop_move_req(self.r.axis)

    def send_table_stop_move_req_p(self):
        return self._send_table_stop_move_req(self.p.axis)

    def send_table_stop_move_req_iso(self):
        return self._send_table_stop_move_req(self.iso.axis)

    def set_z_p_linkage(self, flag):
        self.is_z_p_linkage = flag

    def set_reached_timeout(self, timeout):
        self.reached_timeout = timeout
     

    def set_x_track_para(
        self,
        track,
        track_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):

        self.x.track = track.split(",")
        self.x.track_velocity = track_velocity.split(",")
        assert len(self.x.track) == len(self.x.track_velocity)
        
        self.x.count = float(self.x.track[0])
        self.x.count_velocity = float(self.x.track_velocity[0])
        self.x.timeout = timeout
        self.x.track_count = len(self.x.track)
        self.x.mode = mode
        self.x.cycle = cycle
        


    def set_y_track_para(
        self,
        track,
        track_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        self.y.track = track.split(",")
        self.y.track_velocity = track_velocity.split(",")
        assert len(self.y.track) == len(self.y.track_velocity)
        
        self.y.count = float(self.y.track[0])
        self.y.count_velocity = float(self.y.track_velocity[0])
        self.y.timeout = timeout
        self.y.track_count = len(self.y.track)
        self.y.mode = mode
        self.y.cycle = cycle



    def set_z_track_para(
        self,
        track,
        track_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        self.z.track = track.split(",")
        self.z.track_velocity = track_velocity.split(",")
        assert len(self.z.track) == len(self.z.track_velocity)
        self.z.count = int(self.z.track[0])
        self.z.count_velocity = int(self.z.track_velocity[0])
        self.z.timeout = timeout
        self.z.track_count = len(self.z.track)
        self.z.mode = mode
        self.z.cycle = cycle

 

    def set_r_track_para(
        self,
        track,
        track_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        self.r.track = track.split(",")
        self.r.track_velocity = track_velocity.split(",")
        assert len(self.r.track) == len(self.r.track_velocity)
        self.r.count = float(self.r.track[0])
        self.r.count_velocity = float(self.r.track_velocity[0])
        self.r.timeout = timeout
        self.r.track_count = len(self.r.track)
        self.r.mode = mode
        self.r.cycle = cycle

    def set_p_track_para(
        self,
        track,
        track_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        self.p.track = track.split(",")
        self.p.track_velocity = track_velocity.split(",")
        assert len(self.p.track) == len(self.p.track_velocity)
        self.p.count = float(self.p.track[0])
        self.p.count_velocity = float(self.p.track_velocity[0])
        self.p.timeout = timeout
        self.p.track_count = len(self.p.track)
        self.p.mode = mode
        self.p.cycle = cycle


    def set_iso_track_para(
        self,
        track,
        track_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        self.iso.track = track.split(",")
        self.iso.track_velocity = track_velocity.split(",")
        assert len(self.iso.track) == len(self.iso.track_velocity)
        
        self.iso.count = float(self.iso.track[0])
        self.iso.count_velocity = float(self.iso.track_velocity[0])
        self.iso.timeout = timeout
        self.iso.track_count = len(self.iso.track)
        self.iso.mode = mode
        self.iso.cycle = cycle

    def display_axis_para(self):
        logging.info(
            # f'x axis : {self.x}'
            f"x axis : {self.x.axis}, {self.x.count_s}, {self.x.count_e}, {self.x.count_velocity}, {self.x.timeout}, {self.x.mode}, {self.x.cycle}, {self.x.track}, {self.x.track_velocity}"
        )
        logging.info(
            # f"y axis : {self.y}"
            f"y axis : {self.y.axis}, {self.y.count_s}, {self.y.count_e}, {self.y.count_velocity}, {self.y.timeout}, {self.y.mode}, {self.y.cycle}, {self.y.track}, {self.y.track_velocity}"
        )
        logging.info(
            # f"z axis : {self.z}"
            f"z axis : {self.z.axis}, {self.z.count_s}, {self.z.count_e}, {self.z.count_m}, {self.z.count_velocity}, {self.z.timeout}, {self.z.mode}, {self.z.cycle}, {self.z.track}, {self.z.track_velocity}"
        )
        logging.info(
            # f"r axis : {self.r}"
            f"r axis : {self.r.axis}, {self.r.count_s}, {self.r.count_e}, {self.r.count_velocity}, {self.r.timeout}, {self.r.mode}, {self.r.cycle}, {self.r.track}, {self.r.track_velocity}"
        )
        logging.info(
            # f"p axis : {self.p}"
            f"p axis : {self.p.axis}, {self.p.count_s}, {self.p.count_e}, {self.p.count_velocity}, {self.p.timeout}, {self.p.mode}, {self.p.cycle}, {self.p.track}, {self.p.track_velocity}"
        )
        logging.info(
            # f"iso axis : {self.iso}"
            f"iso axis : {self.iso.axis}, {self.iso.count_s}, {self.iso.count_e}, {self.iso.count_velocity}, {self.iso.timeout}, {self.iso.mode}, {self.iso.cycle}, {self.iso.track}, {self.iso.track_velocity}"
        )

 
    def new_recv_data_rep(self):
        ret_data=None
        logging.info(f"message remain size:{self.traceclient.get_queue_size()}")
        msg = self.traceclient.readMsg()
        items_count = len(msg)
        items_index=0;
        while items_index<items_count:
            if msg[items_index] is not None:
                serverTx = associate_pb2.ServerTx()
                parse_serverTx_len = serverTx.ParseFromString(msg)
                if serverTx.WhichOneof("Msg") == "data":
                    ret_data=serverTx.data.payload
                if serverTx.WhichOneof("Msg") == "keep_alive_rep":
                    if self.loop_count%10 == 0:
                        logging.info(f'keep_alive_rep : {serverTx}')
                    self.heartbeat=0
                if serverTx.WhichOneof("Msg") == "assoc_release_rep":
                    self.release_associate=True
                    logging.info(f"assoc_release_rep : {serverTx}")
                if serverTx.WhichOneof("Msg") == "assoc_rep":
                    if (serverTx.assoc_rep.status_code == associate_pb2.ServerTx.AssociateRep.StatusCode.SUCCESS):
                        self.association_id = serverTx.association_id
                        self.associate=True
                    logging.info(f"assoc_rep : {serverTx}")
                del serverTx
        del msg 
        #gc.collect()
        return ret_data     

        
    def create_start_thread(self):
        try:
            thread_heartbeat = threading.Thread(target=heartbeat_process,args=(self,'Thread-heartbeat'))
            threadx = threading.Thread(target=axis_move_handler_x,args=(self,'Thread-x'))
            thready = threading.Thread(target=axis_move_handler_y,args=(self,'Thread-y'))
            threadz = threading.Thread(target=axis_move_handler_z,args=(self,'Thread-z'))
            threadp = threading.Thread(target=axis_move_handler_p,args=(self,'Thread-p'))
            threadr = threading.Thread(target=axis_move_handler_r,args=(self,'Thread-r'))
            threadiso = threading.Thread(target=axis_move_handler_iso,args=(self,'Thread-iso'))
        except:
            logging.info(f"Axis x thread create failed@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        thread_heartbeat.start()

        threadx.start()
        thready.start()
        threadz.start()
        threadp.start()
        threadr.start()
        threadiso.start()


        
    def track_schedule_process(self):
        logging.info(f"system's garbege threasholds:{gc.get_threshold()}")
        ret = False
        while True:
            #ret_data=None
            #if self.loop_count%10==0:
            #    logging.info(f"message remain size:{self.traceclient.get_queue_size()}")
            time1=time.perf_counter()
            #msg = self.traceclient.readMsg1()
            try:
                msg=self.traceclient.recvMsgSocket1()
            except Exception as e:
                logging.exception("Unexcepted error: %s", e)
                continue

            time2=time.perf_counter()
            #logging.info(f"read message time is:{(time2-time1)*100*10000}")
            #items_count = len(msg)
            #if items_count==0:
            #    time.sleep(0.01)
            #    logging.info(f"message queue is empty")
            #   continue  
            #items_index=0;
            #while items_index<items_count:
            time3=time.perf_counter()  
            if msg is not None:
                #time4=time.perf_counter()   
                serverTx = associate_pb2.ServerTx()
                parse_serverTx_len = serverTx.ParseFromString(msg)
                if serverTx.WhichOneof("Msg") == "keep_alive_rep":
                    #if abs(serverTx.sequence_num_bi - self.sequence_num_bi)<1000:
                    self.heartbeat=0
                if serverTx.WhichOneof("Msg") == "assoc_release_rep":
                    #if abs(serverTx.sequence_num_bi - self.sequence_num_bi)<1000:
                    self.release_associate=True
                    #else:
                    #    logging.info(f"got a assoc release rep not for current req : {serverTx}")
                if serverTx.WhichOneof("Msg") == "assoc_rep":
                    if (serverTx.assoc_rep.status_code == associate_pb2.ServerTx.AssociateRep.StatusCode.SUCCESS):
                        self.association_id = serverTx.association_id
                        self.associate=True
                    logging.info(f"assoc_rep : {serverTx}")
                #time5=time.perf_counter()
                #logging.info(f"associate message process time is:{(time5-time4)*100*10000},itemcount:{items_count}")
                if serverTx.WhichOneof("Msg") == "data":
                    serverTx1 = tblservicemode_pb2.ServerTx()
                    parse_serverTx_len = serverTx1.ParseFromString(serverTx.data.payload)
                    #del serverTx.data
                    #logging.info(serverTx.WhichOneof('Msg'))
                    if serverTx1.WhichOneof("Msg") == "service_status_push":
                        #logging.info(f"------------------------------------service_status_push with status_id : {serverTx1.service_status_push}");
                        for axes in serverTx1.service_status_push.axes:
                            if axes.is_target_reached:
                                #logging.info(f"------------------------------------o axis_info{axes}")
                                if axes.axis == util_pb2.AxisIndex.LATERAL:
                                    if abs(float(self.x.count) - axes.secondary_position) < 0.1 and self.next_move_x==False:
                                        append_to_file(self.statistic_file_name_x, str(self.x.count)+ ',' + str(axes.primary_position) + ',' + str(axes.secondary_position) + ';')
                                        self.last_pos_x=self.x.count
                                        self.next_move_x=True
                                        logging.info(f"------------------------------------x : {self.next_move_x},sef.x.count:{self.x.count/10},target:{axes.secondary_position} abs:{abs(float(self.x.count/10) - axes.secondary_position)}")
                                if axes.axis == util_pb2.AxisIndex.LONGITUDINAL:
                                    if abs(float(self.y.count/10) - axes.secondary_position) < 0.1 and self.next_move_y==False:
                                        append_to_file(self.statistic_file_name_y, str(self.y.count)+ ',' + str(axes.primary_position) + ',' + str(axes.secondary_position) + ';')
                                        self.last_pos_y=self.y.count
                                        self.next_move_y=True
                                        logging.info(f"------------------------------------y : {self.next_move_y},sef.y.count:{self.y.count/10},target:{axes.secondary_position} abs:{abs(float(self.y.count/10) - axes.secondary_position)}")
                                if axes.axis == util_pb2.AxisIndex.PITCH:
                                    if abs(float(self.p.count) - axes.secondary_position) < 0.3 and self.next_move_p==False:
                                        append_to_file(self.statistic_file_name_p, str(self.p.count)+ ',' + str(axes.primary_position) + ',' + str(axes.secondary_position) + ';')
                                        self.last_pos_p=self.p.count
                                        self.next_move_p=True
                                        logging.info(f"------------------------------------p : {self.next_move_p},sef.p.count:{self.p.count},target:{axes.secondary_position} abs:{abs(self.p.count - axes.secondary_position)}")
                                    #else:
                                    #    if self.last_pos_p!=self.p.count:
                                    #        logging.info(f"------------------------------------p : {self.next_move_p},sef.p.count:{self.p.count},target:{axes.secondary_position} abs:{abs(self.p.count - axes.secondary_position)}")   
                                if axes.axis == util_pb2.AxisIndex.VERTICAL:
                                    if abs(float(self.z.count) - axes.secondary_position) < 0.5 and self.next_move_z==False:
                                        append_to_file(self.statistic_file_name_z, str(self.z.count)+ ',' + str(axes.primary_position) + ',' + str(axes.secondary_position) + ';')
                                        self.last_pos_z=self.z.count
                                        self.next_move_z=True
                                        logging.info(f"------------------------------------z : {self.next_move_z},sef.z.count:{self.z.count},target:{axes.secondary_position},abs:{abs(self.z.count - axes.secondary_position)}")  
                                    #else:
                                    #    if self.last_pos_z!=self.z.count:
                                    #        logging.info(f"------------------------------------z1 : {self.next_move_z},sef.z.count:{self.z.count},target:{axes.secondary_position},abs:{abs(self.z.count - axes.secondary_position)}")  
                                if axes.axis == util_pb2.AxisIndex.ROLL:
                                    if abs(float(self.r.count) - axes.secondary_position) < 0.8 and self.next_move_r==False:
                                        append_to_file(self.statistic_file_name_r, str(self.r.count)+ ',' + str(axes.primary_position) + ',' + str(axes.secondary_position) + ';')
                                        self.last_pos_r=self.r.count
                                        self.next_move_r=True
                                        logging.info(f"------------------------------------r : {self.next_move_r},sef.r.count:{self.r.count},target:{axes.secondary_position} abs:{abs(self.r.count - axes.secondary_position)}")
                                    #else:
                                    #    if self.last_pos_r!=self.r.count:
                                    #        logging.info(f"------------------------------------r1 : {self.next_move_r},sef.r.count:{self.r.count},target:{axes.secondary_position} abs:{abs(self.r.count - axes.secondary_position)}")
                                if axes.axis == util_pb2.AxisIndex.ISO:
                                    if abs(float(self.iso.count) - axes.secondary_position) < 1 and self.next_move_iso==False:
                                        append_to_file(self.statistic_file_name_iso, str(self.iso.count)+ ',' + str(axes.primary_position) + ',' + str(axes.secondary_position) + ';')
                                        self.last_pos_iso=self.iso.count
                                        self.next_move_iso=True
                                        logging.info(f"------------------------------------iso : {self.next_move_iso},sef.iso.count:{self.iso.count},target:{axes.secondary_position} abs:{abs(float(self.iso.count) - axes.secondary_position)}")              

                    #if serverTx.WhichOneof("Msg") == "pos_move_rep":
                    #    logging.info(f"serverTx.pos_move_rep : {serverTx.pos_move_rep}")

                    #if serverTx.WhichOneof("Msg") == "count_move_rep":
                    #    logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")

                    #if serverTx.WhichOneof('Msg') == "diagnosis_info_push":
                    #     logging.info(f'serverTx.diagnosis_info_push')

                    #if serverTx1.WhichOneof("Msg") == "fault_report":
                    #   logging.info(f"serverTx1.fault_report")
                    #   for error in serverTx1.fault_report.fault_option:
                    #       logging.info(f"serverTx1.fault_report.fault_option : {error}")
                    #del serverTx1
                    #serverTx1=None
                del serverTx
                serverTx=None
                #time6=time.perf_counter()
                #logging.info(f"service message process time is:{(time6-time5)*100*10000},itemcount:{items_count}")
            time7=time.perf_counter() 
            
            self.loop_count+=1
            if self.loop_count%6000 == 0:
                logging.info(f"read message and one message process time is:{(time2-time1)*100*10000} / {(time7-time3)*100*10000}")
                logging.info(f"@@@@@@@@@ Left Cycles: {self.bigcycle} Current Cycle Stage - {self.stage} @@@@@@@ x  : {self.x.cycle}, y : {self.y.cycle}, z : {self.z.cycle}, r : {self.r.cycle},  p : {self.p.cycle},  iso : {self.iso.cycle}")
                if not self.configfile is None:
                    self._update_cycle_count() 

            if (self.x.cycle == 0 and self.y.cycle == 0 and self.z.cycle == 0 and self.r.cycle == 0 and self.p.cycle == 0 and self.iso.cycle == 0):
                ret = True
                logging.info(f"#############################Return2: {ret}") 
                break
                
            del msg
            msg=None
        logging.info(f"#############################Return3: {ret}")
        return ret

    