import typing
import time
import threading
import gc

# import re
import logging
import sys

sys.path.append("../ppsctrl/proto/py")
import util_pb2
import associate_pb2

# from proto.py import tblctl_pb2
import tblservicemode_pb2
import configparser

from .traceclient import TraceClient

logger = logging.getLogger(__name__)

EPSINON = 0.00001
HEARTBEAT = 0.8


class TableMoveParam:
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
        self.count = 0
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


class PPSCtrl:
    def __init__(self, traceclient: TraceClient):
        """Constructor.
        Args:
            TraceClient: TraceClient class instance.
        """
        self._log_labels: typing.List[str] = []
        self._log_data: typing.List[str] = []
        # self._parse_config_file = parseconfigfile.ParseConfigFile()
        self.traceclient = traceclient
        self.timer = threading.Timer(HEARTBEAT, self._func)
        self.association_id = 0
        self.sequence_num_bi = 0

        self.x = TableMoveParam(util_pb2.AxisIndex.LATERAL)
        self.y = TableMoveParam(util_pb2.AxisIndex.LONGITUDINAL)
        self.z = TableMoveParam(util_pb2.AxisIndex.VERTICAL)
        self.r = TableMoveParam(util_pb2.AxisIndex.ROLL)
        self.p = TableMoveParam(util_pb2.AxisIndex.PITCH)
        self.iso = TableMoveParam(util_pb2.AxisIndex.ISO)

        self.x_count = 0
        self.y_count = 0
        self.z_count = 0
        self.r_count = 0
        self.p_count = 0
        self.iso_count = 0

        self.is_z_p_linkage = False
        self.is_first = True
        self.configfile = None
        self.cf = configparser.ConfigParser()

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
        gc.collect()
        self.x = TableMoveParam(util_pb2.AxisIndex.LATERAL)
        self.y = TableMoveParam(util_pb2.AxisIndex.LONGITUDINAL)
        self.z = TableMoveParam(util_pb2.AxisIndex.VERTICAL)
        self.r = TableMoveParam(util_pb2.AxisIndex.ROLL)
        self.p = TableMoveParam(util_pb2.AxisIndex.PITCH)
        self.iso = TableMoveParam(util_pb2.AxisIndex.ISO)

        self.x_count = 0
        self.y_count = 0
        self.z_count = 0
        self.r_count = 0
        self.p_count = 0
        self.iso_count = 0

        self.is_z_p_linkage = False
        self.is_first = True
        self.configfile = None

    def set_config_path(self, path):
        self.configfile = path
        self.cf.read(path)
        # self._load_config_para()

    """
    def _load_config_para(self):
        axis = self.cf.get("test_axis", "axis")
        if "x" in axis:
            self.set_x_move_para(
                self.cf.getfloat("x_axis", "pos"),
                self.cf.getfloat("x_axis", "speed"),
                self.cf.getint("x_axis", "mode"),
                self.cf.getint("test_axis", "left_cycle_x"),
            )

        if "y" in axis:
            self.set_y_move_para(
                self.cf.getfloat("y_axis", "pos"),
                self.cf.cf.getfloat("y_axis", "speed"),
                self.cf.getint("y_axis", "mode"),
                self.cf.getint("test_axis", "left_cycle_y"),
            )

        if "z" in axis:
            self.set_z_move_para(
                self.cf.getfloat("z_axis", "pos"),
                self.cf.getfloat("z_axis", "speed"),
                self.cf.getint("z_axis", "mode"),
                self.cf.getint("test_axis", "left_cycle_z"),
            )

        if "r" in axis:
            self.set_r_move_para(
                self.cf.getfloat("r_axis", "pos"),
                self.cf.getfloat("r_axis", "speed"),
                self.cf.getint("r_axis", "mode"),
                self.cf.getint("test_axis", "left_cycle_r"),
            )

        if "p" in axis:
            self.set_p_move_para(
                self.cf.getfloat("p_axis", "pos"),
                self.cf.getfloat("p_axis", "speed"),
                self.cf.getint("p_axis", "mode"),
                self.cf.getint("test_axis", "left_cycle_p"),
            )

        if "iso" in axis:
            self.set_iso_move_para(
                self.cf.getfloat("iso_axis", "pos"),
                self.cf.getfloat("iso_axis", "speed"),
                self.cf.getint("iso_axis", "mode"),
                self.cf.getint("test_axis", "left_cycle_iso"),
            )
    """

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
        serverRx.assoc_req.version = 1
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        logging.info(f"parse_serverRx : {serverRx}")
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

    def recv_associate_rsp(self, timeout=1.0):
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
                if (
                    serverTx.assoc_rep.status_code
                    == associate_pb2.ServerTx.AssociateRep.StatusCode.SUCCESS
                ):
                    self.association_id = serverTx.association_id
                    self.timer.start()
                    ret = True
                else:
                    ret = False
                del serverTx
                del msg
                gc.collect()
                break

            del serverTx
            del msg
            gc.collect()

        return ret

    def send_associate_release_req(self):
        serverRx = associate_pb2.ServerRx()
        serverRx.association_id = self.association_id
        self.sequence_num_bi = self.sequence_num_bi + 1
        serverRx.sequence_num_bi = self.sequence_num_bi
        serverRx.assoc_release_req.SetInParent()
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        logging.info(f"parse_serverRx : {serverRx}")
        self.timer.cancel()
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

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
            # logging.info(f'parse_serverTx : {serverTx}')
            if serverTx.WhichOneof("Msg") == "assoc_release_rep":
                logging.info(f"parse_serverTx : {serverTx}")
                ret = True
                del serverTx
                del msg
                gc.collect()
                break

            del serverTx
            del msg
            gc.collect()

        return ret

    def send_keepalive_req(self):
        serverRx = associate_pb2.ServerRx()
        serverRx.association_id = self.association_id
        self.sequence_num_bi = self.sequence_num_bi + 1
        serverRx.sequence_num_bi = self.sequence_num_bi
        serverRx.keep_alive_req.SetInParent()
        serverRx_protobuf_data = serverRx.SerializeToString()
        self.traceclient.sendMsg(serverRx_protobuf_data)
        # logging.info(f'parse_serverRx : {serverRx}')
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

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
                gc.collect()
                break

            del serverTx
            del msg
            gc.collect()

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
        gc.collect()

    def _recv_data_rep(self, timeout=1.0):
        timeout_at = time.time() + timeout
        while True:
            msg = self.traceclient.readMsg()
            if msg is None:
                time.sleep(0.01)
                if time.time() > timeout_at:
                    return None
                else:
                    continue
            serverTx = associate_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(msg)
            # logging.info(f'parse_serverTx : {serverTx}')
            if serverTx.WhichOneof("Msg") == "data":
                break
        # if self._crc32(serverTx.data.payload) != serverTx.data.crc
        #   print(serverTx.data.crc)
        #   return None
        del msg
        gc.collect()
        return serverTx.data.payload

    def send_auto_cal_req(self):
        serverRx = tblservicemode_pb2.ServerRx()
        serverRx.autoCalReq.axes = util_pb2.AxisIndex.LONGITUDINAL
        serverRx.autoCalReq.auto_cal_stage = (
            tblservicemode_pb2.AutoCalStage.CONFIRM_MOVE_TO_LASER_CENTER
        )

        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

    def _send_single_axis_pos_move_req(self, movePara: TableMoveParam):
        serverRx = tblservicemode_pb2.ServerRx()
        axisReq = serverRx.pos_move_req.reqs.add()
        axisReq.axis = movePara.axis
        axisReq.pos = movePara.pos
        axisReq.speed = movePara.speed
        axisReq.mode = movePara.mode

        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

    def send_single_axis_pos_move_req_x(self):
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

    def send_pos_move_req(self):
        serverRx = tblservicemode_pb2.ServerRx()
        if self.x.speed < -EPSINON or self.x.speed > EPSINON:
            axisReq = serverRx.pos_move_req.reqs.add()
            axisReq.axis = self.x.axis
            axisReq.pos = self.x.pos
            axisReq.speed = self.x.speed
            axisReq.mode = self.x.mode

        if self.y.speed < -EPSINON or self.y.speed > EPSINON:
            axisReq = serverRx.pos_move_req.reqs.add()
            axisReq.axis = self.y.axis
            axisReq.pos = self.y.pos
            axisReq.speed = self.y.speed
            axisReq.mode = self.y.mode

        if self.z.speed < -EPSINON or self.z.speed > EPSINON:
            axisReq = serverRx.pos_move_req.reqs.add()
            axisReq.axis = self.z.axis
            axisReq.pos = self.z.pos
            axisReq.speed = self.z.speed
            axisReq.mode = self.z.mode

        if self.r.speed < -EPSINON or self.r.speed > EPSINON:
            axisReq = serverRx.pos_move_req.reqs.add()
            axisReq.axis = self.r.axis
            axisReq.pos = self.r.pos
            axisReq.speed = self.r.speed
            axisReq.mode = self.r.mode

        if self.p.speed < -EPSINON or self.p.speed > EPSINON:
            axisReq = serverRx.pos_move_req.reqs.add()
            axisReq.axis = self.p.axis
            axisReq.pos = self.p.pos
            axisReq.speed = self.p.speed
            axisReq.mode = self.p.mode

        if self.iso.speed < -EPSINON or self.iso.speed > EPSINON:
            axisReq = serverRx.pos_move_req.reqs.add()
            axisReq.axis = self.iso.axis
            axisReq.pos = self.iso.pos
            axisReq.speed = self.iso.speed
            axisReq.mode = self.iso.mode

        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

    def _send_single_axis_count_move_req(self, movePara: TableMoveParam):
        serverRx = tblservicemode_pb2.ServerRx()
        axisReq = serverRx.count_move_req.reqs.add()
        axisReq.axis = movePara.axis
        axisReq.count = movePara.count
        axisReq.count_velocity = movePara.count_velocity
        axisReq.mode = movePara.mode

        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

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

    def send_count_move_req(self):
        serverRx = tblservicemode_pb2.ServerRx()
        if self.x.count_velocity != 0:
            axisReq = serverRx.count_move_req.reqs.add()
            axisReq.axis = self.x.axis
            axisReq.count = self.x.count
            axisReq.count_velocity = self.x.count_velocity
            axisReq.mode = self.x.mode

        if self.y.count_velocity != 0:
            axisReq = serverRx.count_move_req.reqs.add()
            axisReq.axis = self.y.axis
            axisReq.count = self.y.count
            axisReq.count_velocity = self.y.count_velocity
            axisReq.mode = self.y.mode

        if self.z.count_velocity != 0:
            axisReq = serverRx.count_move_req.reqs.add()
            axisReq.axis = self.z.axis
            axisReq.count = self.z.count
            axisReq.count_velocity = self.z.count_velocity
            axisReq.mode = self.z.mode

        if self.r.count_velocity != 0:
            axisReq = serverRx.count_move_req.reqs.add()
            axisReq.axis = self.r.axis
            axisReq.count = self.r.count
            axisReq.count_velocity = self.r.count_velocity
            axisReq.mode = self.r.mode

        if self.p.count_velocity != 0:
            axisReq = serverRx.count_move_req.reqs.add()
            axisReq.axis = self.p.axis
            axisReq.count = self.p.count
            axisReq.count_velocity = self.p.count_velocity
            axisReq.mode = self.p.mode

        if self.iso.count_velocity != 0:
            axisReq = serverRx.count_move_req.reqs.add()
            axisReq.axis = self.iso.axis
            axisReq.count = self.iso.count
            axisReq.count_velocity = self.iso.count_velocity
            axisReq.mode = self.iso.mode

        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

    def recv_pos_move_rep(self):
        ret = False
        while True:
            serverTxdata = self._recv_data_rep()
            if serverTxdata is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdata)
            if serverTx.WhichOneof("Msg") == "pos_move_rep":
                logging.info(f"serverTx.pos_move_rep : {serverTx.pos_move_rep}")
                if serverTx.pos_move_rep.status == util_pb2.ReplyStatus.OK:
                    ret = True
                del serverTx
                del serverTxdata
                gc.collect()
                break

            del serverTx
            del serverTxdata
            gc.collect()

        return ret

    def recv_count_move_rep(self):
        ret = False
        while True:
            serverTxdata = self._recv_data_rep()
            if serverTxdata is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdata)
            if serverTx.WhichOneof("Msg") == "count_move_rep":
                logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")
                if serverTx.count_move_rep.status == util_pb2.ReplyStatus.OK:
                    ret = True
                del serverTx
                del serverTxdata
                gc.collect()
                break

            del serverTx
            del serverTxdata
            gc.collect()

        return ret

    def _wait_reached_signal_disappear(self, axis: util_pb2.AxisIndex, timeout=4.0):
        timeout_at = time.time() + timeout
        ret = False
        while True:
            serverTxdata = self._recv_data_rep()
            if serverTxdata is None:
                break
            if time.time() > timeout_at:
                logging.info("wait_reached_signal_disappear timeout")
                del serverTxdata
                gc.collect()
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdata)
            if serverTx.WhichOneof("Msg") == "count_move_rep":
                logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")
                if serverTx.count_move_rep.status != util_pb2.ReplyStatus.OK:
                    del serverTx
                    del serverTxdata
                    gc.collect()
                    break
            if serverTx.WhichOneof("Msg") == "service_status_push":
                for axes in serverTx.service_status_push.axes:
                    if axes.axis == axis:
                        if not axes.is_target_reached:
                            logging.info(f"serverTx.service_status_push.axes : {axes}")
                            del serverTx
                            del serverTxdata
                            gc.collect()
                            ret = True
                            return ret

            del serverTx
            del serverTxdata
            gc.collect()
        return ret

    def _wait_reached_signal_appear(self, axis: util_pb2.AxisIndex, timeout=16.0):
        timeout_at = time.time() + timeout
        ret = False
        while True:
            serverTxdata = self._recv_data_rep()
            if serverTxdata is None:
                break
            if time.time() > timeout_at:
                logging.info("wait_reached_signal_appear timeout")
                del serverTxdata
                gc.collect()
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdata)
            if serverTx.WhichOneof("Msg") == "count_move_rep":
                logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")
                if serverTx.count_move_rep.status != util_pb2.ReplyStatus.OK:
                    del serverTx
                    del serverTxdata
                    gc.collect()
                    break
            if serverTx.WhichOneof("Msg") == "service_status_push":
                for axes in serverTx.service_status_push.axes:
                    if axes.axis == axis:
                        if axes.is_target_reached:
                            logging.info(f"serverTx.service_status_push.axes : {axes}")
                            del serverTx
                            del serverTxdata
                            gc.collect()
                            ret = True
                            return ret

            del serverTx
            del serverTxdata
            gc.collect()
        return ret

    def wait_reached_signal_disappear_x(self):
        return self._wait_reached_signal_disappear(self.x.axis)

    def wait_reached_signal_disappear_y(self):
        return self._wait_reached_signal_disappear(self.y.axis)

    def wait_reached_signal_disappear_z(self):
        return self._wait_reached_signal_disappear(self.z.axis)

    def wait_reached_signal_disappear_r(self):
        return self._wait_reached_signal_disappear(self.r.axis)

    def wait_reached_signal_disappear_p(self):
        return self._wait_reached_signal_disappear(self.p.axis)

    def wait_reached_signal_appear_p(self):
        return self._wait_reached_signal_appear(self.p.axis)

    def wait_reached_signal_disappear_iso(self):
        return self._wait_reached_signal_disappear(self.iso.axis)

    def _send_table_stop_move_req(self, axis: util_pb2.AxisIndex):
        serverRx = tblservicemode_pb2.ServerRx()
        serverRx.stop_move_req.axes.append(axis)
        logging.info(f"parse_serverRx : {serverRx}")
        serverRx_protobuf_data = serverRx.SerializeToString()
        self._send_data_req(serverRx_protobuf_data)
        del serverRx_protobuf_data
        del serverRx
        gc.collect()

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

    def recv_table_stop_move_rep(self):
        ret = False
        while True:
            serverTxdata = self._recv_data_rep()
            if serverTxdata is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdata)
            if serverTx.WhichOneof("Msg") == "stop_move_rep":
                if serverTx.stop_move_rep.status == util_pb2.ReplyStatus.OK:
                    ret = True
                    del serverTx
                    del serverTxdata
                    gc.collect()
                break
            del serverTx
            del serverTxdata
            gc.collect()

        return ret

    def set_z_p_linkage(self, flag):
        self.is_z_p_linkage = flag

    def set_reached_timeout(self, timeout):
        self.reached_timeout = timeout

    def recv_table_reached(self):
        ret = False
        # is_z_p_linkage = False
        p_startmove = False
        p_finishmove = False
        # is_first = True
        default_timeout = 8
        x_timeout = default_timeout
        y_timeout = default_timeout
        z_timeout = default_timeout
        p_timeout = default_timeout
        r_timeout = default_timeout
        iso_timeout = default_timeout

        while True:
            serverTxdataPayload = self._recv_data_rep()
            if serverTxdataPayload is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdataPayload)
            # logging.info(serverTx.WhichOneof('Msg'))
            if serverTx.WhichOneof("Msg") == "service_status_push":
                for axes in serverTx.service_status_push.axes:
                    # logging.info(f"serverTx.service_status_push.axes : {axes}")
                    if axes.is_target_reached:
                        # logging.info(f"serverTx.service_status_push.axes reached: {axes}")
                        if axes.axis == util_pb2.AxisIndex.LATERAL:
                            self.x_count += 1
                            if self.x_count == x_timeout:
                                self.x_count = 0

                                if (
                                    self.x.count == self.x.count_s
                                    and x_timeout == self.x.timeout
                                ):
                                    self.x.cycle = self.x.cycle - 1

                                if self.x.cycle <= 0:
                                    self.x.cycle = 0
                                    x_timeout = default_timeout
                                else:
                                    if self.x.count == self.x.count_s:
                                        self.x.count = self.x.count_e
                                        x_timeout = default_timeout
                                    else:
                                        self.x.count = self.x.count_s
                                        x_timeout = self.x.timeout

                                    self.send_single_axis_count_move_req_x()
                                    if not self.wait_reached_signal_disappear_x():
                                        self.send_single_axis_count_move_req_x()
                                        assert self.wait_reached_signal_disappear_x()

                        if axes.axis == util_pb2.AxisIndex.LONGITUDINAL:
                            self.y_count += 1
                            if self.y_count == y_timeout:
                                self.y_count = 0

                                if (
                                    self.y.count == self.y.count_s
                                    and y_timeout == self.y.timeout
                                ):
                                    self.y.cycle = self.y.cycle - 1

                                if self.y.cycle <= 0:
                                    self.y.cycle = 0
                                    y_timeout = default_timeout
                                else:
                                    if self.y.count == self.y.count_s:
                                        self.y.count = self.y.count_e
                                        y_timeout = default_timeout
                                    else:
                                        self.y.count = self.y.count_s
                                        y_timeout = self.y.timeout

                                    self.send_single_axis_count_move_req_y()
                                    if not self.wait_reached_signal_disappear_y():
                                        self.send_single_axis_count_move_req_y()
                                        assert self.wait_reached_signal_disappear_y()

                        if axes.axis == util_pb2.AxisIndex.VERTICAL:
                            if self.is_z_p_linkage:
                                if p_startmove == False:
                                    self.z_count += 1
                                    if self.z_count == z_timeout:
                                        self.z_count = 0

                                        if (
                                            self.z.count == self.z.count_s
                                            and z_timeout == self.z.timeout
                                        ):
                                            self.z.cycle = self.z.cycle - 1

                                        if self.z.cycle <= 0:
                                            self.z.cycle = 0
                                            z_timeout = default_timeout
                                            # p_startmove = False
                                        else:
                                            if self.z.count == self.z.count_m:
                                                if self.is_first:
                                                    # self.send_single_axis_count_move_req_p()
                                                    # self.wait_reached_signal_disappear_p()
                                                    self.is_first = False
                                                    p_startmove = True
                                                    continue
                                                else:
                                                    if p_finishmove:
                                                        p_finishmove = False
                                                        # p_startmove = False
                                                    else:
                                                        p_startmove = True
                                                        continue

                                            if self.z.count == self.z.count_s:
                                                if self.z.count_m != 0:
                                                    self.z.count = self.z.count_m
                                                    z_timeout = default_timeout
                                                else:
                                                    self.z.count = self.z.count_e
                                                    z_timeout = default_timeout
                                            elif self.z.count == self.z.count_m:
                                                self.z.count = self.z.count_e
                                                z_timeout = default_timeout
                                            elif self.z.count == self.z.count_e:
                                                self.z.count = self.z.count_s
                                                z_timeout = self.z.timeout
                                            else:
                                                logging.info(f"Error: {self.z.count}")
                                                continue

                                            self.send_single_axis_count_move_req_z()
                                            if (
                                                not self.wait_reached_signal_disappear_z()
                                            ):
                                                self.send_single_axis_count_move_req_z()
                                                assert (
                                                    self.wait_reached_signal_disappear_z()
                                                )
                            else:
                                self.z_count += 1
                                if self.z_count == z_timeout:
                                    self.z_count = 0

                                    if (
                                        self.z.count == self.z.count_s
                                        and z_timeout == self.z.timeout
                                    ):
                                        self.z.cycle = self.z.cycle - 1

                                    if self.z.cycle <= 0:
                                        self.z.cycle = 0
                                        z_timeout = default_timeout
                                    else:
                                        if self.z.count == self.z.count_s:
                                            self.z.count = self.z.count_e
                                            z_timeout = default_timeout
                                        else:
                                            self.z.count = self.z.count_s
                                            z_timeout = self.z.timeout

                                        self.send_single_axis_count_move_req_z()
                                        if not self.wait_reached_signal_disappear_z():
                                            self.send_single_axis_count_move_req_z()
                                            assert (
                                                self.wait_reached_signal_disappear_z()
                                            )

                        if axes.axis == util_pb2.AxisIndex.ROLL:
                            self.r_count += 1
                            if self.r_count == r_timeout:
                                self.r_count = 0

                                if (
                                    self.r.count == self.r.count_s
                                    and r_timeout == self.r.timeout
                                ):
                                    self.r.cycle = self.r.cycle - 1

                                if self.r.cycle <= 0:
                                    self.r.cycle = 0
                                    r_timeout = default_timeout
                                else:
                                    if self.r.count == self.r.count_s:
                                        self.r.count = self.r.count_e
                                        r_timeout = default_timeout
                                    else:
                                        self.r.count = self.r.count_s
                                        r_timeout = self.r.timeout

                                    self.send_single_axis_count_move_req_r()
                                    if not self.wait_reached_signal_disappear_r():
                                        self.send_single_axis_count_move_req_r()
                                        assert self.wait_reached_signal_disappear_r()

                        if axes.axis == util_pb2.AxisIndex.PITCH:
                            if self.is_z_p_linkage:
                                if p_startmove:
                                    self.p_count += 1
                                    if self.p_count == p_timeout:
                                        self.p_count = 0

                                        if (
                                            self.p.count == self.p.count_m
                                            and p_timeout == self.p.timeout
                                        ):
                                            self.p.cycle = self.p.cycle - 1
                                            p_startmove = False
                                            p_finishmove = True
                                            p_timeout = default_timeout
                                            continue

                                        if self.p.cycle <= 0:
                                            self.p.cycle = 0
                                            p_timeout = default_timeout
                                            p_startmove = False
                                            p_finishmove = True
                                        # else:
                                        #    if self.p.count == self.p.count_s:
                                        #        self.p.count = self.p.count_e
                                        #        p_timeout = default_timeout
                                        #    else:
                                        #        self.p.count = self.p.count_s
                                        #        p_timeout = self.p.timeout
                                        else:
                                            if self.p.count == self.p.count_m:
                                                self.p.count = self.p.count_s
                                                p_timeout = default_timeout
                                            elif self.p.count == self.p.count_s:
                                                self.p.count = self.p.count_e
                                                p_timeout = default_timeout
                                            elif self.p.count == self.p.count_e:
                                                self.p.count = self.p.count_m
                                                p_timeout = self.p.timeout

                                            self.send_single_axis_count_move_req_p()
                                            if (
                                                not self.wait_reached_signal_disappear_p()
                                            ):
                                                self.send_single_axis_count_move_req_p()
                                                assert (
                                                    self.wait_reached_signal_disappear_p()
                                                )
                            else:
                                self.p_count += 1
                                if self.p_count == p_timeout:
                                    self.p_count = 0

                                    if (
                                        self.p.count == self.p.count_s
                                        and p_timeout == self.p.timeout
                                    ):
                                        self.p.cycle = self.p.cycle - 1

                                    if self.p.cycle <= 0:
                                        self.p.cycle = 0
                                        p_timeout = default_timeout
                                    else:
                                        if self.p.count == self.p.count_s:
                                            self.p.count = self.p.count_e
                                            p_timeout = default_timeout
                                        else:
                                            self.p.count = self.p.count_s
                                            p_timeout = self.p.timeout

                                        self.send_single_axis_count_move_req_p()
                                        if not self.wait_reached_signal_disappear_p():
                                            self.send_single_axis_count_move_req_p()
                                            assert (
                                                self.wait_reached_signal_disappear_p()
                                            )

                        if axes.axis == util_pb2.AxisIndex.ISO:
                            self.iso_count += 1
                            if self.iso_count == iso_timeout:
                                self.iso_count = 0

                                if (
                                    self.iso.count == self.iso.count_s
                                    and iso_timeout == self.iso.timeout
                                ):
                                    self.iso.cycle = self.iso.cycle - 1

                                if self.iso.cycle <= 0:
                                    self.iso.cycle = 0
                                    iso_timeout = default_timeout
                                else:
                                    if self.iso.count == self.iso.count_s:
                                        self.iso.count = self.iso.count_e
                                        iso_timeout = default_timeout
                                    else:
                                        self.iso.count = self.iso.count_s
                                        iso_timeout = self.iso.timeout

                                    self.send_single_axis_count_move_req_iso()
                                    if not self.wait_reached_signal_disappear_iso():
                                        self.send_single_axis_count_move_req_iso()
                                        assert self.wait_reached_signal_disappear_iso()

                logging.info(
                    f"Cycle: x : {self.x.cycle}, y : {self.y.cycle}, z : {self.z.cycle}, r : {self.r.cycle},  p : {self.p.cycle},  iso : {self.iso.cycle}"
                )
                if not self.configfile is None:
                    self._update_cycle_count()
                if (
                    self.x.cycle == 0
                    and self.y.cycle == 0
                    and self.z.cycle == 0
                    and self.r.cycle == 0
                    and self.p.cycle == 0
                    and self.iso.cycle == 0
                ):
                    ret = True
                    del serverTxdataPayload
                    del serverTx
                    gc.collect()
                    break
            del serverTxdataPayload
            del serverTx
            gc.collect()
            # if serverTx.WhichOneof("Msg") == "pos_move_rep":
            # logging.info(f"serverTx.pos_move_rep : {serverTx.pos_move_rep}")

            # if serverTx.WhichOneof("Msg") == "count_move_rep":
            # logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")

            # if serverTx.WhichOneof('Msg') == "diagnosis_info_push":
            #     logging.info(f'serverTx.diagnosis_info_push : {serverTx.diagnosis_info_push}')

            # if serverTx.WhichOneof("Msg") == "fault_report":
            # logging.info(f"serverTx.fault_report : {serverTx.fault_report}")
            # for error in serverTx.fault_report.fault_option:
            # logging.info(f"serverTx.fault_report.fault_option : {error}")
            # self.send_table_stop_move_req_x()
            # self.send_table_stop_move_req_y()
            # self.send_table_stop_move_req_z()
            # self.send_table_stop_move_req_r()
            # self.send_table_stop_move_req_p()
            # self.send_table_stop_move_req_iso()

            # return ret

        return ret

    def recv_table_reached_once(self):
        ret = False
        # is_z_p_linkage = False
        p_startmove = False
        p_finishmove = False
        # is_first = True
        default_timeout = 8
        x_timeout = default_timeout
        y_timeout = default_timeout
        z_timeout = default_timeout
        p_timeout = default_timeout
        r_timeout = default_timeout
        iso_timeout = default_timeout

        if self.x.cycle > 0:
            x_finish = False
        else:
            x_finish = True
            self.x.cycle = 0

        if self.y.cycle > 0:
            y_finish = False
        else:
            y_finish = True
            self.y.cycle = 0

        if self.z.cycle > 0:
            z_finish = False
        else:
            z_finish = True
            self.z.cycle = 0

        if self.r.cycle > 0:
            r_finish = False
        else:
            r_finish = True
            self.r.cycle = 0

        if self.p.cycle > 0:
            p_finish = False
        else:
            p_finish = True
            self.p.cycle = 0

        if self.iso.cycle > 0:
            iso_finish = False
        else:
            iso_finish = True
            self.iso.cycle = 0

        while True:
            serverTxdataPayload = self._recv_data_rep()
            if serverTxdataPayload is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdataPayload)
            # logging.info(serverTx.WhichOneof('Msg'))
            if serverTx.WhichOneof("Msg") == "service_status_push":
                for axes in serverTx.service_status_push.axes:
                    # logging.info(f"serverTx.service_status_push.axes : {axes}")
                    if axes.is_target_reached:
                        # logging.info(f"serverTx.service_status_push.axes reached: {axes}")
                        if axes.axis == util_pb2.AxisIndex.LATERAL:
                            if x_finish:
                                continue
                            self.x_count += 1
                            if self.x_count == x_timeout:
                                self.x_count = 0

                                if (
                                    self.x.count == self.x.count_s
                                    and x_timeout == self.x.timeout
                                    or self.x.cycle == 0
                                ):
                                    x_finish = True
                                    continue

                                if self.x.count == self.x.count_s:
                                    self.x.count = self.x.count_e
                                    x_timeout = default_timeout
                                else:
                                    self.x.count = self.x.count_s
                                    x_timeout = self.x.timeout

                                self.send_single_axis_count_move_req_x()
                                if not self.wait_reached_signal_disappear_x():
                                    self.send_single_axis_count_move_req_x()
                                    assert self.wait_reached_signal_disappear_x()

                        if axes.axis == util_pb2.AxisIndex.LONGITUDINAL:
                            if y_finish:
                                continue
                            self.y_count += 1
                            if self.y_count == y_timeout:
                                self.y_count = 0

                                if (
                                    self.y.count == self.y.count_s
                                    and y_timeout == self.y.timeout
                                    or self.y.cycle == 0
                                ):
                                    y_finish = True
                                    continue

                                if self.y.count == self.y.count_s:
                                    self.y.count = self.y.count_e
                                    y_timeout = default_timeout
                                else:
                                    self.y.count = self.y.count_s
                                    y_timeout = self.y.timeout

                                self.send_single_axis_count_move_req_y()
                                if not self.wait_reached_signal_disappear_y():
                                    self.send_single_axis_count_move_req_y()
                                    assert self.wait_reached_signal_disappear_y()

                        if axes.axis == util_pb2.AxisIndex.VERTICAL:
                            if z_finish:
                                continue
                            if self.is_z_p_linkage:
                                if not p_startmove:
                                    self.z_count += 1
                                    if self.z_count == z_timeout:
                                        self.z_count = 0

                                        if (
                                            self.z.count == self.z.count_s
                                            and z_timeout == self.z.timeout
                                            or self.z.cycle == 0
                                        ):
                                            z_finish = True
                                            continue

                                        if self.z.count == self.z.count_m:
                                            if self.is_first:
                                                # self.send_single_axis_count_move_req_p()
                                                # self.wait_reached_signal_disappear_p()
                                                self.is_first = False
                                                p_startmove = True
                                                continue
                                            else:
                                                if p_finishmove:
                                                    p_finishmove = False
                                                    # p_startmove = False
                                                else:
                                                    p_startmove = True
                                                    continue

                                        if self.z.count == self.z.count_s:
                                            if self.z.count_m != 0:
                                                self.z.count = self.z.count_m
                                                z_timeout = default_timeout
                                            else:
                                                self.z.count = self.z.count_e
                                                z_timeout = default_timeout
                                        elif self.z.count == self.z.count_m:
                                            self.z.count = self.z.count_e
                                            z_timeout = default_timeout
                                        elif self.z.count == self.z.count_e:
                                            self.z.count = self.z.count_s
                                            z_timeout = self.z.timeout
                                        else:
                                            logging.info(f"Error: {self.z.count}")
                                            continue

                                        self.send_single_axis_count_move_req_z()
                                        if not self.wait_reached_signal_disappear_z():
                                            self.send_single_axis_count_move_req_z()
                                            assert (
                                                self.wait_reached_signal_disappear_z()
                                            )
                            else:
                                self.z_count += 1
                                if self.z_count == z_timeout:
                                    self.z_count = 0

                                    if (
                                        self.z.count == self.z.count_s
                                        and z_timeout == self.z.timeout
                                        or self.z.cycle == 0
                                    ):
                                        z_finish = True
                                        continue

                                    if self.z.count == self.z.count_s:
                                        if self.z.count_m != 0:
                                            self.z.count = self.z.count_m
                                            z_timeout = default_timeout
                                        else:
                                            self.z.count = self.z.count_e
                                            z_timeout = default_timeout
                                    elif self.z.count == self.z.count_m:
                                        self.z.count = self.z.count_e
                                        z_timeout = default_timeout
                                    elif self.z.count == self.z.count_e:
                                        self.z.count = self.z.count_s
                                        z_timeout = self.z.timeout
                                    else:
                                        logging.info(f"Error: {self.z.count}")
                                        continue

                                    self.send_single_axis_count_move_req_z()
                                    if not self.wait_reached_signal_disappear_z():
                                        self.send_single_axis_count_move_req_z()
                                        assert self.wait_reached_signal_disappear_z()

                        if axes.axis == util_pb2.AxisIndex.ROLL:
                            if r_finish:
                                continue
                            self.r_count += 1
                            if self.r_count == r_timeout:
                                self.r_count = 0

                                if (
                                    self.r.count == self.r.count_s
                                    and r_timeout == self.r.timeout
                                    or self.r.cycle == 0
                                ):
                                    r_finish = True
                                    continue

                                if self.r.count == self.r.count_s:
                                    self.r.count = self.r.count_e
                                    r_timeout = default_timeout
                                else:
                                    self.r.count = self.r.count_s
                                    r_timeout = self.r.timeout

                                self.send_single_axis_count_move_req_r()
                                if not self.wait_reached_signal_disappear_r():
                                    self.send_single_axis_count_move_req_r()
                                    assert self.wait_reached_signal_disappear_r()

                        if axes.axis == util_pb2.AxisIndex.PITCH:
                            if p_finish:
                                continue
                            if self.is_z_p_linkage:
                                if p_startmove:
                                    self.p_count += 1
                                    if self.p_count == p_timeout:
                                        self.p_count = 0

                                        if (
                                            self.p.count == self.p.count_s
                                            and p_timeout == self.p.timeout
                                            or self.p.cycle == 0
                                        ):
                                            p_finish = True
                                            p_startmove = False
                                            p_finishmove = True
                                            p_timeout = default_timeout
                                            continue

                                        if self.p.count == self.p.count_m:
                                            self.p.count = self.p.count_s
                                            p_timeout = default_timeout
                                        elif self.p.count == self.p.count_s:
                                            self.p.count = self.p.count_e
                                            p_timeout = default_timeout
                                        elif self.p.count == self.p.count_e:
                                            self.p.count = self.p.count_m
                                            p_timeout = self.p.timeout

                                        self.send_single_axis_count_move_req_p()
                                        if not self.wait_reached_signal_disappear_p():
                                            self.send_single_axis_count_move_req_p()
                                            assert (
                                                self.wait_reached_signal_disappear_p()
                                            )
                            else:
                                self.p_count += 1
                                if self.p_count == p_timeout:
                                    self.p_count = 0

                                    if (
                                        self.p.count == self.p.count_s
                                        and p_timeout == self.p.timeout
                                        or self.p.cycle == 0
                                    ):
                                        p_finish = True
                                        continue

                                    if self.p.count == self.p.count_m:
                                        self.p.count = self.p.count_s
                                        p_timeout = default_timeout
                                    elif self.p.count == self.p.count_s:
                                        self.p.count = self.p.count_e
                                        p_timeout = default_timeout
                                    elif self.p.count == self.p.count_e:
                                        self.p.count = self.p.count_m
                                        p_timeout = self.p.timeout

                                    self.send_single_axis_count_move_req_p()
                                    if not self.wait_reached_signal_disappear_p():
                                        self.send_single_axis_count_move_req_p()
                                        assert self.wait_reached_signal_disappear_p()

                        if axes.axis == util_pb2.AxisIndex.ISO:
                            if iso_finish:
                                continue
                            self.iso_count += 1
                            if self.iso_count == iso_timeout:
                                self.iso_count = 0

                                if (
                                    self.iso.count == self.iso.count_s
                                    and iso_timeout == self.iso.timeout
                                    or self.iso.cycle == 0
                                ):
                                    iso_finish = True
                                    continue

                                if self.iso.count == self.iso.count_s:
                                    self.iso.count = self.iso.count_e
                                    iso_timeout = default_timeout
                                else:
                                    self.iso.count = self.iso.count_s
                                    iso_timeout = self.iso.timeout

                                self.send_single_axis_count_move_req_iso()
                                if not self.wait_reached_signal_disappear_iso():
                                    self.send_single_axis_count_move_req_iso()
                                    assert self.wait_reached_signal_disappear_iso()

                logging.info(
                    f"Cycle: x : {self.x.cycle}, y : {self.y.cycle}, z : {self.z.cycle}, r : {self.r.cycle},  p : {self.p.cycle},  iso : {self.iso.cycle}"
                )

                if (
                    x_finish
                    and y_finish
                    and z_finish
                    and r_finish
                    and p_finish
                    and iso_finish
                ):
                    p_startmove = False
                    p_finishmove = False
                    # is_first = True

                    if self.x.cycle > 0:
                        self.x.cycle -= 1
                    if self.y.cycle > 0:
                        self.y.cycle -= 1
                    if self.z.cycle > 0:
                        self.z.cycle -= 1
                    if self.r.cycle > 0:
                        self.r.cycle -= 1
                    if self.p.cycle > 0:
                        self.p.cycle -= 1
                    if self.iso.cycle > 0:
                        self.iso.cycle -= 1

                    if not self.configfile is None:
                        self._update_cycle_count()
                    if (
                        self.x.cycle == 0
                        and self.y.cycle == 0
                        and self.z.cycle == 0
                        and self.r.cycle == 0
                        and self.p.cycle == 0
                        and self.iso.cycle == 0
                    ):
                        ret = True
                        del serverTxdataPayload
                        del serverTx
                        gc.collect()
                        break

                    if self.x.cycle > 0:
                        x_finish = False
                        self.x.count = self.x.count_e
                        x_timeout = default_timeout
                        self.send_single_axis_count_move_req_x()
                        if not self.wait_reached_signal_disappear_x():
                            self.send_single_axis_count_move_req_x()
                            assert self.wait_reached_signal_disappear_x()
                    else:
                        x_finish = True

                    if self.y.cycle > 0:
                        y_finish = False
                        self.y.count = self.y.count_e
                        y_timeout = default_timeout
                        self.send_single_axis_count_move_req_y()
                        if not self.wait_reached_signal_disappear_y():
                            self.send_single_axis_count_move_req_y()
                            assert self.wait_reached_signal_disappear_y()
                    else:
                        y_finish = True

                    if self.z.cycle > 0:
                        z_finish = False
                        self.z.count = self.z.count_m
                        z_timeout = default_timeout
                        self.send_single_axis_count_move_req_z()
                        if not self.wait_reached_signal_disappear_z():
                            self.send_single_axis_count_move_req_z()
                            assert self.wait_reached_signal_disappear_z()
                    else:
                        z_finish = True

                    if self.r.cycle > 0:
                        r_finish = False
                        self.r.count = self.r.count_e
                        r_timeout = default_timeout
                        self.send_single_axis_count_move_req_r()
                        if not self.wait_reached_signal_disappear_r():
                            self.send_single_axis_count_move_req_r()
                            assert self.wait_reached_signal_disappear_r()
                    else:
                        r_finish = True

                    if self.p.cycle > 0:
                        p_finish = False
                    else:
                        p_finish = True

                    if self.iso.cycle > 0:
                        iso_finish = False
                        self.iso.count = self.iso.count_e
                        iso_timeout = default_timeout
                        self.send_single_axis_count_move_req_iso()
                        if not self.wait_reached_signal_disappear_iso():
                            self.send_single_axis_count_move_req_iso()
                            assert self.wait_reached_signal_disappear_iso()
                    else:
                        iso_finish = True

            del serverTxdataPayload
            del serverTx
            gc.collect()
            # if serverTx.WhichOneof("Msg") == "pos_move_rep":
            # logging.info(f"serverTx.pos_move_rep : {serverTx.pos_move_rep}")

            # if serverTx.WhichOneof("Msg") == "count_move_rep":
            # logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")

            # if serverTx.WhichOneof('Msg') == "diagnosis_info_push":
            #     logging.info(f'serverTx.diagnosis_info_push : {serverTx.diagnosis_info_push}')

            # if serverTx.WhichOneof("Msg") == "fault_report":
            # logging.info(f"serverTx.fault_report : {serverTx.fault_report}")
            # for error in serverTx.fault_report.fault_option:
            # logging.info(f"serverTx.fault_report.fault_option : {error}")
            # self.send_table_stop_move_req_x()
            # self.send_table_stop_move_req_y()
            # self.send_table_stop_move_req_z()
            # self.send_table_stop_move_req_r()
            # self.send_table_stop_move_req_p()
            # self.send_table_stop_move_req_iso()

            # return ret

        return ret

    def recv_track_reached(self):
        ret = False
        p_startmove = False
        default_timeout = 8
        x_timeout = default_timeout
        y_timeout = default_timeout
        z_timeout = default_timeout
        p_timeout = default_timeout
        r_timeout = default_timeout
        iso_timeout = default_timeout
        x_track_count = len(self.x.track)
        y_track_count = len(self.y.track)
        z_track_count = len(self.z.track)
        r_track_count = len(self.r.track)
        p_track_count = len(self.p.track)
        iso_track_count = len(self.iso.track)
        x_cur = 1
        y_cur = 1
        z_cur = 1
        r_cur = 1
        p_cur = 1
        iso_cur = 1
        while True:
            serverTxdataPayload = self._recv_data_rep()
            if serverTxdataPayload is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdataPayload)
            # logging.info(serverTx.WhichOneof('Msg'))
            if serverTx.WhichOneof("Msg") == "service_status_push":
                for axes in serverTx.service_status_push.axes:
                    # logging.info(f"serverTx.service_status_push.axes : {axes}")
                    if axes.is_target_reached:
                        # logging.info(
                        #     f"serverTx.service_status_push.axes reached: {axes}"
                        # )
                        if axes.axis == util_pb2.AxisIndex.LATERAL:
                            self.x_count += 1
                            if self.x_count == x_timeout:
                                self.x_count = 0
                                if x_cur >= x_track_count:
                                    self.x.cycle = self.x.cycle - 1
                                    if self.x.cycle <= 0:
                                        self.x.cycle = 0
                                        continue
                                    else:
                                        x_timeout = default_timeout
                                        x_cur = 0
                                if self.x.cycle <= 0:
                                    self.x.cycle = 0
                                    x_timeout = default_timeout
                                    continue
                                self.x.count = int(self.x.track[x_cur])
                                self.x.count_velocity = int(
                                    self.x.track_velocity[x_cur]
                                )
                                x_cur += 1
                                if x_cur == x_track_count:
                                    x_timeout = self.x.timeout
                                self.send_single_axis_count_move_req_x()
                                if not self.wait_reached_signal_disappear_x():
                                    self.send_single_axis_count_move_req_x()
                                    assert self.wait_reached_signal_disappear_x()

                        if axes.axis == util_pb2.AxisIndex.LONGITUDINAL:
                            self.y_count += 1
                            if self.y_count == y_timeout:
                                self.y_count = 0
                                if y_cur >= y_track_count:
                                    self.y.cycle = self.y.cycle - 1
                                    if self.y.cycle <= 0:
                                        self.y.cycle = 0
                                        continue
                                    else:
                                        y_timeout = default_timeout
                                        y_cur = 0
                                if self.y.cycle <= 0:
                                    self.y.cycle = 0
                                    y_timeout = default_timeout
                                    continue
                                self.y.count = int(self.y.track[y_cur])
                                self.y.count_velocity = int(
                                    self.y.track_velocity[y_cur]
                                )
                                y_cur += 1
                                if y_cur == y_track_count:
                                    y_timeout = self.y.timeout
                                self.send_single_axis_count_move_req_y()
                                if not self.wait_reached_signal_disappear_y():
                                    self.send_single_axis_count_move_req_y()
                                    assert self.wait_reached_signal_disappear_y()

                        if axes.axis == util_pb2.AxisIndex.VERTICAL:
                            if self.is_z_p_linkage:
                                if not p_startmove:
                                    self.z_count += 1
                                    if self.z_count == z_timeout:
                                        self.z_count = 0
                                        if z_cur >= z_track_count:
                                            self.z.cycle = self.z.cycle - 1
                                            if self.z.cycle <= 0:
                                                self.z.cycle = 0
                                                p_startmove = True
                                                continue
                                            else:
                                                z_timeout = default_timeout
                                                z_cur = 0
                                                p_startmove = True
                                                continue
                                        if self.z.cycle <= 0:
                                            self.z.cycle = 0
                                            z_timeout = default_timeout
                                            p_startmove = True
                                            continue
                                        self.z.count = int(self.z.track[z_cur])
                                        self.z.count_velocity = int(
                                            self.z.track_velocity[z_cur]
                                        )
                                        z_cur += 1
                                        if z_cur == z_track_count:
                                            z_timeout = self.z.timeout
                                        self.send_single_axis_count_move_req_z()
                                        if not self.wait_reached_signal_disappear_z():
                                            self.send_single_axis_count_move_req_z()
                                            assert (
                                                self.wait_reached_signal_disappear_z()
                                            )
                            else:
                                self.z_count += 1
                                if self.z_count == z_timeout:
                                    self.z_count = 0
                                    if z_cur >= z_track_count:
                                        self.z.cycle = self.z.cycle - 1
                                        if self.z.cycle <= 0:
                                            self.z.cycle = 0
                                            continue
                                        else:
                                            z_timeout = default_timeout
                                            z_cur = 0
                                    if self.z.cycle <= 0:
                                        self.z.cycle = 0
                                        z_timeout = default_timeout
                                        continue
                                    self.z.count = int(self.z.track[z_cur])
                                    self.z.count_velocity = int(
                                        self.z.track_velocity[z_cur]
                                    )
                                    z_cur += 1
                                    if z_cur == z_track_count:
                                        z_timeout = self.z.timeout
                                    self.send_single_axis_count_move_req_z()
                                    if not self.wait_reached_signal_disappear_z():
                                        self.send_single_axis_count_move_req_z()
                                        assert self.wait_reached_signal_disappear_z()

                        if axes.axis == util_pb2.AxisIndex.ROLL:
                            self.r_count += 1
                            if self.r_count == r_timeout:
                                self.r_count = 0
                                if r_cur >= r_track_count:
                                    self.r.cycle = self.r.cycle - 1
                                    if self.r.cycle <= 0:
                                        self.r.cycle = 0
                                        continue
                                    else:
                                        r_timeout = default_timeout
                                        r_cur = 0
                                if self.r.cycle <= 0:
                                    self.r.cycle = 0
                                    r_timeout = default_timeout
                                    continue
                                self.r.count = int(self.r.track[r_cur])
                                self.r.count_velocity = int(
                                    self.r.track_velocity[r_cur]
                                )
                                r_cur += 1
                                if r_cur == r_track_count:
                                    r_timeout = self.r.timeout
                                self.send_single_axis_count_move_req_r()
                                if not self.wait_reached_signal_disappear_r():
                                    self.send_single_axis_count_move_req_r()
                                    assert self.wait_reached_signal_disappear_r()

                        if axes.axis == util_pb2.AxisIndex.PITCH:
                            if self.is_z_p_linkage:
                                if p_startmove:
                                    self.p_count += 1
                                    if self.p_count == p_timeout:
                                        self.p_count = 0
                                        if p_cur >= p_track_count:
                                            self.p.cycle = self.p.cycle - 1
                                            if self.p.cycle <= 0:
                                                self.p.cycle = 0
                                                continue
                                            else:
                                                p_timeout = default_timeout
                                                p_cur = 0
                                                p_startmove = False
                                        if self.p.cycle <= 0:
                                            self.p.cycle = 0
                                            p_timeout = default_timeout
                                            p_startmove = False
                                            continue
                                        self.p.count = int(self.p.track[p_cur])
                                        self.p.count_velocity = int(
                                            self.p.track_velocity[p_cur]
                                        )
                                        p_cur += 1
                                        if p_cur == p_track_count:
                                            p_timeout = self.p.timeout
                                        self.send_single_axis_count_move_req_p()
                                        if not self.wait_reached_signal_disappear_p():
                                            self.send_single_axis_count_move_req_p()
                                            assert (
                                                self.wait_reached_signal_disappear_p()
                                            )
                            else:
                                self.p_count += 1
                                if self.p_count == p_timeout:
                                    self.p_count = 0
                                    if p_cur >= p_track_count:
                                        self.p.cycle = self.p.cycle - 1
                                        if self.p.cycle <= 0:
                                            self.p.cycle = 0
                                            continue
                                        else:
                                            p_timeout = default_timeout
                                            p_cur = 0
                                    if self.p.cycle <= 0:
                                        self.p.cycle = 0
                                        p_timeout = default_timeout
                                        continue
                                    self.p.count = int(self.p.track[p_cur])
                                    self.p.count_velocity = int(
                                        self.p.track_velocity[p_cur]
                                    )
                                    p_cur += 1
                                    if p_cur == p_track_count:
                                        p_timeout = self.p.timeout
                                    self.send_single_axis_count_move_req_p()
                                    if not self.wait_reached_signal_disappear_p():
                                        self.send_single_axis_count_move_req_p()
                                        assert self.wait_reached_signal_disappear_p()

                        if axes.axis == util_pb2.AxisIndex.ISO:
                            self.iso_count += 1
                            if self.iso_count == iso_timeout:
                                self.iso_count = 0
                                if iso_cur >= iso_track_count:
                                    self.iso.cycle = self.iso.cycle - 1
                                    if self.iso.cycle <= 0:
                                        self.iso.cycle = 0
                                        continue
                                    else:
                                        iso_timeout = default_timeout
                                        iso_cur = 0
                                if self.iso.cycle <= 0:
                                    self.iso.cycle = 0
                                    iso_timeout = default_timeout
                                    continue
                                self.iso.count = int(self.iso.track[iso_cur])
                                self.iso.count_velocity = int(
                                    self.iso.track_velocity[iso_cur]
                                )
                                iso_cur += 1
                                if iso_cur == iso_track_count:
                                    iso_timeout = self.iso.timeout
                                self.send_single_axis_count_move_req_iso()
                                if not self.wait_reached_signal_disappear_iso():
                                    self.send_single_axis_count_move_req_iso()
                                    assert self.wait_reached_signal_disappear_iso()

                logging.info(
                    f"Cycle: x : {self.x.cycle}, y : {self.y.cycle}, z : {self.z.cycle}, r : {self.r.cycle},  p : {self.p.cycle},  iso : {self.iso.cycle}"
                )
                if not self.configfile is None:
                    self._update_cycle_count()
                if (
                    self.x.cycle == 0
                    and self.y.cycle == 0
                    and self.z.cycle == 0
                    and self.r.cycle == 0
                    and self.p.cycle == 0
                    and self.iso.cycle == 0
                ):
                    ret = True
                    del serverTxdataPayload
                    del serverTx
                    gc.collect()
                    break
            del serverTxdataPayload
            del serverTx
            gc.collect()
            # if serverTx.WhichOneof("Msg") == "pos_move_rep":
            # logging.info(f"serverTx.pos_move_rep : {serverTx.pos_move_rep}")

            # if serverTx.WhichOneof("Msg") == "count_move_rep":
            # logging.info(f"serverTx.count_move_rep : {serverTx.count_move_rep}")

            # if serverTx.WhichOneof('Msg') == "diagnosis_info_push":
            #     logging.info(f'serverTx.diagnosis_info_push : {serverTx.diagnosis_info_push}')

            # if serverTx.WhichOneof("Msg") == "fault_report":
            # logging.info(f"serverTx.fault_report : {serverTx.fault_report}")
            # for error in serverTx.fault_report.fault_option:
            # logging.info(f"serverTx.fault_report.fault_option : {error}")
            # self.send_table_stop_move_req_x()
            # self.send_table_stop_move_req_y()
            # self.send_table_stop_move_req_z()
            # self.send_table_stop_move_req_r()
            # self.send_table_stop_move_req_p()
            # self.send_table_stop_move_req_iso()

            # return ret

        return ret

    def wait(self, count=0):
        ret = False
        cnt = count
        while True:
            serverTxdataPayload = self._recv_data_rep()
            if serverTxdataPayload is None:
                break
            serverTx = tblservicemode_pb2.ServerTx()
            parse_serverTx_len = serverTx.ParseFromString(serverTxdataPayload)
            # logging.info(serverTx.WhichOneof('Msg'))
            if serverTx.WhichOneof("Msg") == "service_status_push":
                cnt -= 1
                if cnt == 0:
                    ret = True
                    del serverTx
                    del serverTxdataPayload
                    gc.collect()
                    break

            del serverTx
            del serverTxdataPayload
            gc.collect()

        return ret

    def set_x_move_para(
        # self, pos, speed, mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION, cycle=0
        self,
        count_s,
        count_e,
        count_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        # self.x.pos = pos
        # self.x.speed = speed
        self.x.count_s = count_s
        self.x.count_e = count_e
        self.x.count = self.x.count_s
        self.x.count_velocity = count_velocity
        self.x.timeout = timeout
        self.x.mode = mode
        self.x.cycle = cycle

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
        self.x.count = int(self.x.track[0])
        self.x.count_velocity = int(self.x.track_velocity[0])
        self.x.timeout = timeout
        self.x.track_count = len(self.x.track)
        self.x.mode = mode
        self.x.cycle = cycle

    def set_y_move_para(
        # self, pos, speed, mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION, cycle=0
        self,
        count_s,
        count_e,
        count_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        # self.y.pos = pos
        # self.y.speed = speed
        self.y.count_s = count_s
        self.y.count_e = count_e
        self.y.count = self.y.count_s
        self.y.count_velocity = count_velocity
        self.y.timeout = timeout
        self.y.mode = mode
        self.y.cycle = cycle

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
        self.y.count = int(self.y.track[0])
        self.y.count_velocity = int(self.y.track_velocity[0])
        self.y.timeout = timeout
        self.y.track_count = len(self.y.track)
        self.y.mode = mode
        self.y.cycle = cycle

    def set_z_move_para(
        # self, pos, speed, mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION, cycle=0
        self,
        count_s,
        count_e,
        count_m,
        count_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        # self.z.pos = pos
        # self.z.speed = speed
        self.z.count_s = count_s
        self.z.count_e = count_e
        self.z.count_m = count_m
        self.z.count = self.z.count_s
        self.z.count_velocity = count_velocity
        self.z.timeout = timeout
        self.z.mode = mode
        self.z.cycle = cycle

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

    def set_r_move_para(
        # self, pos, speed, mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION, cycle=0
        self,
        count_s,
        count_e,
        count_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        # self.r.pos = pos
        # self.r.speed = speed
        self.r.count_s = count_s
        self.r.count_e = count_e
        self.r.count = self.r.count_s
        self.r.count_velocity = count_velocity
        self.r.timeout = timeout
        self.r.mode = mode
        self.r.cycle = cycle

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
        self.r.count = int(self.r.track[0])
        self.r.count_velocity = int(self.r.track_velocity[0])
        self.r.timeout = timeout
        self.r.track_count = len(self.r.track)
        self.r.mode = mode
        self.r.cycle = cycle

    def set_p_move_para(
        # self, pos, speed, mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION, cycle=0
        self,
        count_s,
        count_e,
        count_m,
        count_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        # self.p.pos = pos
        # self.p.speed = speed
        self.p.count_s = count_s
        self.p.count_e = count_e
        self.p.count_m = count_m
        self.p.count = self.p.count_m
        self.p.count_velocity = count_velocity
        self.p.timeout = timeout
        self.p.mode = mode
        self.p.cycle = cycle

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
        self.p.count = int(self.p.track[0])
        self.p.count_velocity = int(self.p.track_velocity[0])
        self.p.timeout = timeout
        self.p.track_count = len(self.p.track)
        self.p.mode = mode
        self.p.cycle = cycle

    def set_iso_move_para(
        # self, pos, speed, mode=tblservicemode_pb2.PositionMode.RELATIVE_MOTION, cycle=0
        self,
        count_s,
        count_e,
        count_velocity,
        timeout=12,
        mode=tblservicemode_pb2.PositionMode.ABSOLUTE_MOTION,
        cycle=0,
    ):
        # self.iso.pos = pos
        # self.iso.speed = speed
        self.iso.count_s = count_s
        self.iso.count_e = count_e
        self.iso.count = self.iso.count_s
        self.iso.count_velocity = count_velocity
        self.iso.timeout = timeout
        self.iso.mode = mode
        self.iso.cycle = cycle

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
        self.iso.count = int(self.iso.track[0])
        self.iso.count_velocity = int(self.iso.track_velocity[0])
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