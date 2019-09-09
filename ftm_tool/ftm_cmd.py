# -*- coding: utf-8 -*-

import sys
import fileinput
import os
from ctypes import *
import re
import binascii
import struct
import queue
import threading
import ctypes
import inspect
import time
from hplc_cert import debug_leave

# hwq_cfg
hwq_str = "23 23 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 0b 00 00 00 16 00 00 00 0b 00 10 00 10 00 01 00 00 00 01 00 00 02 00 00 03 00 00 04 00 00 40 40"

class Base_Param_Type(Structure):
    _pack_ = 1
    _fields_ = [('cmd_id', c_ushort),
                ('total_len', c_ushort),
                ('len', c_ushort)
                ]

###################################################################################################################
#                                                                                                                 #
#                                           Define python dictionary                                              #
#                                                                                                                 #
###################################################################################################################
DictCommandInfo = {
    "read": 0x02, "write": 0x03,
    "tx init": 0x04, "tx long": 0x04, "tx end": 0x04, "tx gain": 0x04,
    "tx gp bcn": 0x04, "tx sg bcn": 0x04, "tx spg bcn": 0x04,
    "tx gp sof": 0x04, "tx sg sof": 0x04, "tx spg sof": 0x04,
    "tx gp sound": 0x04, "tx sg sound": 0x04, "tx spg sound": 0x04,
    "tx pgp bcn": 0x04, "tx psg bcn": 0x04, "tx pspg bcn": 0x04,
    "tx pgp sof": 0x04, "tx psg sof": 0x04, "tx pspg sof": 0x04,
    "tx pgp sound": 0x04, "tx psg sound": 0x04, "tx pspg sound": 0x04,
    "rx plt": 0x05, "rx init": 0x05, "rx start": 0x05, "rx end": 0x05,
    "tone": 0x06, "tone off": 0x06,
    "print": 0x07, "print all": 0x07, "print tx statistics": 0x07,
    "print rx statistics": 0x07, "print band statistics": 0x07,
    "set period_ms": 0x08, "set pb_size": 0x08, "set pb_num": 0x08,
    "get period_ms": 0x09, "get pb_size": 0x09, "get pb_num": 0x09,
    "scan": 0x0a, "scan all": 0x0a, "scan dump": 0x0a, "scan csi": 0x0a,
    "scan uart": 0x0a, "scan vpp": 0x0a, "scan snr": 0x0a, "scan fa": 0x0a,
    "scan nf": 0x0a, "scan loopback": 0x0a, "scan dc tx": 0x0a, "scan dc rx": 0x0a,
    "scan fft": 0x0a,
    "hwq_cfg": 0x0b,
    "pkt_cfg": 0x0c,
    "test_case": 0x0d,
    "ring_cfg": 0x10,
    "filter_sel": 0x11,
    "filter": 0x12,
    "dis_ring": 0x13,
    "sniffer_cfg": 0x14,
    "rx_msg_show": 0x15,
    "cmd_cfg": 0x16,
    "crc_cfg": 0x17,
    "ping_tput": 0x18,
    "set_tei_nid": 0x19,
    "clear_count": 0x1a,
    "read_pkt_count": 0x1b,
    "rx_tput_test": 0x1c,
    "dis_hwq": 0x1d,
    "pkt_data": 0x1e,
    "i2c write": 0x1f,
    "i2c read": 0x20,
    "read chip id": 0x25,
    "read fw ver": 0x26,
    "burn mac": 0x27,
    "utest stress": 0x28,
    "set_band": 0x2a,
    "read mac": 0x2b,
    "efuse lock": 0x2d,
    "spur_mask_set": 0x2e
}

NoneParamCommandList = [
    "tx_init", "tx_long", "tx_end",
    "rx_plt", "rx_init", "rx_start", "rx_end", "tone_off", "print", "print_all",
    "print_rx_statistics", "print_tx_statistics", "print_band_statistics",
    "get_period_ms", "get_pb_size", "get_pb_num",
    "scan", "scan_all", "scan_uart", "scan_vpp", "scan_snr",
    "scan_fa", "scan_loopback", "scan_dc_tx", "scan_dc_rx",
    "clear_count", "read_pkt_count", "efuse_lock", "spur_mask_set"
]

DictCtypeToCtypes = {
    "uint8_t": c_ubyte,
    "uint16_t": c_ushort,
    "uint32_t": c_uint
}

DictCtypesFmt = {
    "c_char": "c", "c_byte": "b", "c_ubyte": "B",
    "c_short": "h", "c_ushort": "H",
    "c_int": "i", "c_uint": "I",
    "c_long": "l", "c_ulong": "L",
    "c_float": "f", "c_double": "d"
}

DictTmi = {
    "0": 520, "1": 520, "2": 136, "3": 136,
    "4": 136, "5": 136, "6": 136, "7": 520,
    "8": 520, "9": 520, "10": 520, "11": 264,
    "12": 264, "13": 72, "14": 72
}

DictExtTmi = {
    "1": 520, "2": 520, "3": 520,
    "4": 520, "5": 520, "6": 520,
    "10": 136, "11": 136,
    "12": 136, "13": 136, "14": 136
}

DictTxPhase = {
    'all': 0,
    'a': 1,
    'b': 2,
    'c': 3
}

DicParam_hwq_cfg = {
    "-m": "tx_mode",
    "-q": "hwqid",
    "-t": "qtype",
    "-c": "qcap"
}

DicParam_pkt_cfg = {
    "-p": "proto",
    "-q": "qid",
    "-b": "bcast",
    "-d": "delimiter_type",
    "-n": "nid",
    "-dt": "dtei",
    "-st": "stei",
    "-t": "tmi",
    "-et": "ext_tmi",
    "-l": "lid",
    "-pn": "pb_num",
    "-na": "need_ack",
    "-ne": "need_encry",
    "-nd": "need_decrypt",
    "-ai": "avln_idx_in_desc",
    "-kti": "key_table_idx_in_desc",
    "-ki": "key_idx_in_desc",
    "-hrc": "hw_retry_cnt",
    "-ph": "phase",
    "-pi": "pkt_idx"
}

DicParam_pkt_data = {
    "-dn": "data_num"
}

DicParam_test_case = {
    "-i": "interval_time",
    "-n": "packe_num",
    "-ui": "user_updata_time"
}

DicParam_ring_cfg = {
    "-id": "ring_id",
    "-rs": "ring_sz",
    "-bs": "buf_sz",
    "-fs": "bufsz_filter_sel",
    "-f": "filter",
    "-t": "cfg_type",
    "-o": "cfg_offset",
    "-e": "cfg_enable",
    "-c": "cert_flag"
}

DicParam_ping_tput = {
    "-st": "stei",
    "-dt": "dtei",
    "-n": "nid",
    "-t": "tmi",
    "-et": "ext_tmi",
    "-pn": "pb_num",
    "-c": "cont",
    "-pot": "ping_or_tput"
}

# - command: set_band
class Sset_band(Base_Param_Type):
    _pack_ = 1
    _fields_ = [('data0', c_ubyte),
                ('data1', c_ubyte),
                ('data2', c_ubyte)
                ]

class Sread(Base_Param_Type):  # Sturcture read
    _pack_ = 1
    _fields_ = [('data0', c_uint),
                ('data1', c_ushort)
                ]


class Swrite(Base_Param_Type):  # Sturcture write
    _pack_ = 1
    _fields_ = [('data0', c_uint),
                ('data1', c_uint)
                ]

class ftm_tool:
    # the folder for test case
    # error flag
    error_flag = 0

    def __init__(self, record_log):
        self.record_log = record_log
        self.utest_package_len = 0
        self.multi_return_flag = ''
        self.pack_info, self.comd_flag, self.dump_data_str = b'', b'', b''
        self.TestCaseFolder = r".\mac_cfg"

        self.notice_queue = queue.Queue(maxsize=-1)
        self.response_queue = queue.Queue(maxsize=10)

        self.msg_info_cmd = ''
        self.ser_send_data = None

    def start_thread(self, serport):
        # start threads for serial port data collection
        self.c_thread = threading.Thread(target=self.raw_data_commands_parsing)
        self.c_thread.setDaemon(True)
        self.c_thread.start()

        self.f_thread = threading.Thread(target=self.collect_info_from_ser, args=(serport,))
        self.f_thread.setDaemon(True)
        self.f_thread.start()

    def ftm_tx_data_fun(self, ser_tx_func):
        self.ser_send_data = ser_tx_func

    def string2hex_bytes_string(self, obj_string):
        obj_bytes_string = obj_string.encode("utf-8")
        obj_bytes_hex_string = binascii.hexlify(obj_bytes_string)
        return obj_bytes_hex_string

    def pkt_data_without_padding(self, obj_data_list):
        list_pkt = []
        list_temp_pkt = (' '.join(obj_data_list)).split()
        for i in list_temp_pkt:
            list_pkt.append(int(i, 16))
        t_pkt_data = tuple(list_pkt)

        return t_pkt_data

    def exe_cmd(self, msg_info):

        self.msg_info_cmd = msg_info

        command, file_name, param_str, info = "", "", "", ""
        module_id, message_id = 3, 0
        param_list, send_list = [], []

        dic_keys = DictCommandInfo.keys()
        #dic_keys.sort(key=len)
        if msg_info.lower() == 'exit':
            sys.exit()
        elif msg_info.find('load') >= 0:
            for key in dic_keys:
                m = re.match(r"load\s+" + r"(\b" + key + r"\w*\b)" + r"(\s+(.*)\s*)*", msg_info)
                if m:
                    file_name = m.group(1)
                    param_str = m.group(3)
                    command = key
                    message_id = DictCommandInfo[key]
                    break
        elif (msg_info.find('dtest') >= 0):
            for key in dic_keys:
                m = re.match(r"dtest\s+" + r"(\b" + key + r"\b)" + r"(\s+(.*)\s*)*", msg_info)
                if m:
                    param_str = m.group(3)
                    p_list_temp = list(key)
                    for i in range(len(p_list_temp)):
                        if p_list_temp[i] == " ":
                            p_list_temp[i] = r"_"
                    command = ''.join(p_list_temp)
                    message_id = DictCommandInfo[key]
        else:
            print("cmd error\n")
            return

        #self.record_log(debug_leave.LOG_DEBUG, '*' * 20 + "Sending Start" + "*" * 25)
        #self.record_log(debug_leave.LOG_DEBUG, r"The Command case is : %s, The ModuleID is: %s, The MessageID is: %s"
        #             % (msg_info, module_id, message_id))

        if (msg_info.find('load') >= 0):
            test_case_file = self.TestCaseFolder + "\\" + file_name + r".txt"
            if not os.path.exists(test_case_file):
                self.record_log(debug_leave.LOG_ERROR, "Load File does not exist! ")
                error_flag = 1
                return

            fields_list, structure_param_list, structure_value_list = [], [], []
            list_pkt_part, list_pkt, list_pkt_padding = [], [], []
            str_tmi, str_ext_tmi, str_pb_num, str_pkt_len = '', '', '', ''

            for line in fileinput.input(test_case_file):
                m = re.search(r'\s*(\w+)\s+(\w+)\s*=\s*(.+)\s*;', line)
                m_pkt = re.search(r'\s*(\w+)\s+pkt\s*\[\s*\]\s*=\s*', line)
                m_data = re.match(r'\A\s*([0-9A-Fa-f]{2}(.+)[0-9A-Fa-f]{2})\s*\Z', line)
                if m:
                    if m.group(2) == "pkt_len":
                        str_pkt_len = m.group(3)
                    elif m.group(2) == "tmi":
                        str_tmi = m.group(3)
                    elif m.group(2) == "ext_tmi":
                        str_ext_tmi = m.group(3)
                    elif m.group(2) == "pb_num":
                        str_pb_num = m.group(3)
                    structure_param_list.append(m.group(2))
                    structure_value_list.append(m.group(3))
                    fields_list.append((m.group(2), DictCtypeToCtypes[m.group(1)]))
                elif m_pkt:
                    pkt_type = m_pkt.group(1)
                elif m_data:
                    list_pkt_part.append(m_data.group(1).strip())

            if msg_info.find("load pkt_cfg") >= 0:
                if param_str:
                    list_pkt_param = param_str.split(" ")
                    if "-t" in list_pkt_param:
                        tmi_index = list_pkt_param.index("-t")
                        str_tmi = list_pkt_param[tmi_index + 1]
                    elif "-et" in list_pkt_param:
                        ext_tmi_index = list_pkt_param.index("-et")
                        str_ext_tmi = list_pkt_param[ext_tmi_index + 1]
                    elif "-pn" in list_pkt_param:
                        pb_num_index = list_pkt_param.index("-pn")
                        str_pb_num = list_pkt_param[pb_num_index + 1]
                    elif "-pl" in list_pkt_param:
                        pkt_len_index = list_pkt_param.index("-pl")
                        str_pkt_len = list_pkt_param[pkt_len_index + 1]

            if list_pkt_part:
                tuple_pkt_data = self.pkt_data_without_padding(list_pkt_part)

                structure_param_list.append(r"pkt")
                structure_value_list.append(str(tuple_pkt_data))
                fields_list.append((r"pkt", DictCtypeToCtypes[pkt_type] * len(tuple_pkt_data)))

            class Structure_Command(Base_Param_Type):
                _pack_ = 1
                _fields_ = fields_list

            t = Structure_Command()
            len_buffer = sizeof(t)
            t.cmd_id = message_id
            t.total_len = len_buffer - 6
            t.len = len_buffer - 6
            if len(structure_param_list) == len(structure_value_list):
                for i in range(len(structure_param_list)):
                    execstr = r"t.", structure_param_list[i], r" = ", structure_value_list[i]
                    exec (''.join(execstr), locals())
            try:
                if param_str:
                    param_list = param_str.split(" ")
                    dic_param = r"DicParam_" + command
                    if (len(param_list) % 2 == 0 and param_list[0].find("-") == 0):
                        i = 0
                        while i < len(param_list):
                            pm = re.match(r"\A(-[a-z]+)(\d+)\Z", param_list[i])
                            if pm:
                                param_mark = pm.group(1)
                                execstr = dic_param + r".has_key('" + param_mark + r"')"
                                m = eval(execstr)
                                if m:
                                    dstr = dic_param + r"['" + param_mark + r"']"
                                    tt = eval(dstr)
                                    execstr = r"t." + tt + pm.group(2) + r" = ", param_list[i + 1]
                                    exec(''.join(execstr), locals())
                            execstr = "'%s' in %s" % (param_list[i], dic_param)
                            m = eval(execstr)
                            if m:
                                dstr = dic_param + r'["' + param_list[i] + r'"]'
                                tt = eval(dstr)
                                execstr = r"t." + tt + r" = ", param_list[i + 1]
                                exec(''.join(execstr), locals())
                            i += 2
                    else:
                        self.record_log(debug_leave.LOG_ERROR, "The Parameters not matched, please check ....")
                        error_flag = 1
                        return
            except Exception:
                self.record_log(debug_leave.LOG_ERROR, "Error: The Parameters not matched, please check ....")
                error_flag = 1
                return
            if re.match(r"\s*load\s+ping_tput\s*(.*)\Z", msg_info):
                ping_flag = 0
                ping_param2 = t.dtei  # ping_tput return parameter dtei
                ping_param7 = t.ping_or_tput  # ping_tput return parameter ping_or_tput
        elif msg_info.find('dtest') >= 0:
            cmd_struc = r"S" + command + r"()"  # All Structures starts with 'S'
            t = eval(cmd_struc)
            len_buffer = sizeof(t)
            t.cmd_id = message_id
            t.total_len = len_buffer - 6
            t.len = len_buffer - 6
            if param_str:
                param_list = param_str.split(" ")
                if param_list != [] and re.search(r"0x(\w+)-0x(\w+)", param_list[0]):  # write 0x*-0x* *
                    mem_range_list = param_list[0].split('-')
                    param_list[0] = mem_range_list[0]
                    param_list.insert(1, mem_range_list[1])
                num = len(param_list)
                while num > 0:
                    try:
                        if re.match(r"0x(\w+)", param_list[num - 1]):
                            i_num = int(param_list[num - 1], 16)
                        elif param_list[num - 1] in DictTxPhase.keys():  # tx phase parameters
                            i_num = param_list[num - 1]
                        elif re.match(r"dtest burn mac", msg_info):
                            i_num = int(param_list[num - 1], 16)
                        else:
                            i_num = int(param_list[num - 1])
                    except Exception:
                        self.record_log(debug_leave.LOG_ERROR, r"Parameters Error...Please Check Command!")
                        error_flag = 1
                        return
                    send_list.append(i_num)
                    num -= 1
                send_list.reverse()

                if re.match(r"\s*dtest\s+tx\s+(gp|sg|spg|pgp|psg|pspg)\s+(bcn|sof|sound)\s+(\d+)\s+(\w+)\s+(\d+)\s*\Z",
                            msg_info):
                    t.data2 = send_list[0]
                    t.data_phase = DictTxPhase[send_list[1]]
                    t.data3 = send_list[2]
                elif re.match(r"\s*dtest\s+tx\s+gain\s+(\d+)\s*", msg_info):
                    t.data0 = send_list[0]
                elif re.match(r"\s*dtest\s+tone\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.data0, t.data1 = send_list
                elif re.match(r"\s*dtest\s+set\s+(period_ms|pb_size|pb_num)\s+(\d+)\s*\Z", msg_info):
                    t.data1 = send_list[0]
                elif re.match(r"\s*dtest\s+read\s+0x(\w+)\s+(\d+)\s*\Z", msg_info):
                    t.data0, t.data1 = send_list
                    if t.data1 % 4 == 0:
                        pass
                    else:
                        logger.info(r"Warning: num of bytes to read should be a mutiple of 4...")
                        if t.data1 / 4 == 0:
                            t.data1 = 4
                        else:
                            t.data1 = 4 * (t.data1 / 4)
                elif re.match(r"\s*dtest\s+write\s+0x(\w+)(-0x(\w+))?\s+0x(\w+)\s*\Z", msg_info):
                    if (len(send_list) == 2):
                        t.data0, t.data1 = send_list
                    elif (len(send_list) == 3):
                        num_value = (send_list[1] - send_list[0]) / 4 + 1

                        class WriteRange(Base_Param_Type):
                            _pack_ = 1
                            _fields_ = [('data', c_uint * (2 * num_value))]

                        t = WriteRange()
                        t.cmd_id = 3
                        t.total_len = num_value * 4 * 2
                        t.len = num_value * 4 * 2
                        wr_list = []
                        for i in range(0, num_value):
                            wr_list.append(send_list[0] + i * 4)
                            wr_list.append(send_list[2])
                        t.data = tuple(wr_list)
                        len_buffer = sizeof(t)
                elif re.match(r"\s*dtest\s+filter_sel\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.ring_id, t.bufsz_filter_sel = send_list
                elif re.match(r"\s*dtest\s+filter\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.ring_id, t.filter = send_list
                elif re.match(r"\s*dtest\s+dis_ring\s+(\d+)\s*\Z", msg_info):
                    t.data0 = send_list[0]
                elif re.match(r"\s*dtest\s+scan\s+dump\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.data1, t.data2 = send_list
                    self.multi_return_flag = "1"
                elif re.match(r"\s*dtest\s+scan\s+nf\s+(\d+)\s*\Z", msg_info):
                    t.data1 = send_list[0]
                elif re.match(r"\s*dtest\s+scan\s+csi\s+(\d+)\s(\d+)\s*\Z", msg_info):
                    t.data1, t.data2 = send_list
                elif re.match(r"\s*dtest\s+scan\s+fft\s+(-?\d+)\s*\Z", msg_info):
                    if -24 <= t.data1 <= 60:
                        t.data1 = send_list[0]
                        self.multi_return_flag = "1"
                    else:
                        self.record_log(debug_leave.LOG_ERROR,
                                        r"Parameters out of range, it should be [-24:60], please reload...")
                        error_flag = 1
                        return
                elif re.match(r"\s*dtest\s+sniffer_cfg\s+(\d+)\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.enable, t.sel, t.pb_offset = send_list
                    sniffer_flag = t.enable
                    if sniffer_flag == 1:
                        if os.path.exists(Result_Log):
                            os.remove(Result_Log)
                        index_num = 0
                        truncate_flag = 1
                    elif sniffer_flag == 0:
                        index_num = 0
                elif re.match(r"\s*dtest\s+rx_msg_show\s+(\d+)\s*\Z", msg_info):
                    t.data0 = send_list[0]
                elif re.match(r"\s*dtest\s+set_tei_nid\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.data0, t.data1 = send_list
                elif re.match(r"\s*dtest\s+rx_tput_test\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    t.data0, t.data1 = send_list
                elif re.match(r"\s*dtest\s+dis_hwq\s+(\d+)\s*\Z", msg_info):
                    t.data0 = send_list[0]
                elif re.match(r"\s*dtest\s+i2c write\s+(\d+)\s+0x(\w+)\s+0x(\w+)\s*\Z", msg_info):
                    t.data0, t.data1, t.data2 = send_list
                elif re.match(r"\s*dtest\s+i2c read\s+(\d+)\s*\Z", msg_info):
                    t.data0 = send_list[0]
                elif re.match(r"\s*dtest\s+set_band\s+(\d+)\s+(\d+)\s+(\d+)\s*\Z", msg_info):
                    if 0 <= t.data0 <= 3 and 0 <= t.data1 <= 7 and 0 <= t.data2 <= 3:
                        t.data0, t.data1, t.data2 = send_list
                    else:
                        logger.info(r"Parameters out of range, please reload...")
                        error_flag = 1
                        return
                elif re.match(r"\s*dtest\s+burn mac"
                              r"\s+(\w{2})\s+(\w{2})\s+(\w{2})\s+(\w{2})\s+(\w{2})\s+(\w{2})\s*\Z", msg_info):
                    t.data0, t.data1, t.data2, t.data3, t.data4, t.data5 = send_list
                else:
                    self.record_log(debug_leave.LOG_ERROR, r"Parameters format were illegal, please reload...")
                    error_flag = 1
                    return
            elif command in NoneParamCommandList:
                pass
            else:
                self.record_log(debug_leave.LOG_ERROR, r"Command Parameters missing, please reload...")
                error_flag = 1
                return
        else:
            self.record_log(debug_leave.LOG_ERROR, r"Error: Command Not Matched! Please check the issue...")
            len_buffer = 0
            error_flag = 1
            return

        sat = string_at(addressof(t), len_buffer)  # eg. \x1f\x00d\x00\x01\x00\x02\x00\x03\x00
        sat_ascii_str = binascii.hexlify(sat).decode('utf-8')
        p_list = list(sat_ascii_str)
        i = 2
        while i < len(p_list):
            p_list.insert(i, " ")
            i += 3
        self.record_log(debug_leave.LOG_DEBUG, "Packed Data String at: %s --- %s" % (sat_ascii_str, "".join(p_list)))

        str_data = sat_ascii_str
        str_preinfo = str_data[0:6 * 2]  # cmd_id total_len len: 6 bytes
        str_data_ex_preinfo = str_data[6 * 2:]  # data info exclude pre info
        length_real_data = len(str_data_ex_preinfo) / 2  # byte unit
        if re.match(r"\s*load\s+pkt_data(.*)\s*\Z", msg_info) and length_real_data > 100:  # 100 bytes segment
            send_times_pkt = length_real_data / 100  # send times
            remainder_pkt = length_real_data % 100  # remainder (bytes)
            sum_pkt = 0
            str_head = r"2323" + r"00" * 12
            str_moduleid = r"03000000"
            str_messageid = struct.pack('<I', message_id).encode("hex")
            str_tail = r"4040"
            for i in range(send_times_pkt):
                str_totallen = r"6A000000"
                str_data = str_preinfo[0:8] + r"6400" + str_data_ex_preinfo[sum_pkt: (sum_pkt + 100 * 2)]
                str_send_data = str_head + str_moduleid + str_messageid + str_totallen + str_data + str_tail
                self.comd_flag = str_preinfo[0:4]
                time.sleep(1)
                self.record_log(debug_leave.LOG_DEBUG, "Pkt data segment " + str(i + 1) + " send: %s" % str_send_data)
                sum_pkt += 100 * 2
            if remainder_pkt != 0:
                str_totallen = struct.pack('<I', remainder_pkt + 6).encode("hex")
                str_datalen = struct.pack('<H', remainder_pkt).encode("hex")
                str_data = str_preinfo[0:8] + str_datalen + str_data_ex_preinfo[-(remainder_pkt * 2):]
                str_send_data = str_head + str_moduleid + str_messageid + str_totallen + str_data + str_tail
                self.comd_flag = str_preinfo[0:4]
                self.record_log(debug_leave.LOG_DEBUG,
                                "Pkt data segment " + str(send_times_pkt + 1) + " send: %s" % str_send_data)
        else:
            str_head = r"2323" + r"00" * 12
            str_moduleid = r"03000000"
            str_messageid = binascii.hexlify(struct.pack('<I', message_id)).decode("utf-8")
            str_totallen = binascii.hexlify(struct.pack('<I', len_buffer)).decode("utf-8")
            str_data = sat_ascii_str
            str_tail = r"4040"
            str_send_data = str_head + str_moduleid + str_messageid + str_totallen + str_data + str_tail
            self.comd_flag = (str_preinfo[0:4]).encode("utf-8")
            return str_send_data

    def raw_data_commands_parsing(self):
        sinfo = b''
        while 1:
            qinfo_bytes_str = self.notice_queue.get(1)
            self.record_log(debug_leave.LOG_DEBUG, "return: %s" % qinfo_bytes_str.decode("utf-8"))
            sinfo = binascii.unhexlify(qinfo_bytes_str)
            total_data = sinfo[2: -2]  # remove starter 2323 and end marker 4040
            big_head_fmt = '<6B6B2H2I'  # 24
            len_big_header_fmt = struct.calcsize(big_head_fmt)
            data_big_header = total_data[0:len_big_header_fmt]
            ss = struct.Struct(big_head_fmt)
            unpack_data_big_header = ss.unpack(data_big_header)

            r_module_id = unpack_data_big_header[-4]
            r_msg_id = unpack_data_big_header[-2]
            r_msg_len = unpack_data_big_header[-1]
            data_msg_body = total_data[-r_msg_len:]

            if (r_module_id == 3 and r_msg_id == 1):
                little_header_fmt = '<HHH'
                len_little_header_fmt = struct.calcsize(little_header_fmt)
                data_little_header = data_msg_body[0: len_little_header_fmt]
                ss = struct.Struct(little_header_fmt)
                unpakc_data_little_header = ss.unpack(data_little_header)
                rid, tlen, dlen = unpakc_data_little_header
                data_valid = data_msg_body[len_little_header_fmt:-3]
                ''''
                if (rid != 0x0f and rid != 0x0e):
                    self.record_log(debug_leave.LOG_DEBUG, '-' * 20 + "CallBacking End" + "-" * 25)
                    self.record_log(debug_leave.LOG_DEBUG, "Unpacked Head Data: %s" % str(unpack_data_big_header))
                    self.record_log(debug_leave.LOG_DEBUG, "Cmd_ID: %s, Total_len: %s, Len: %s" % (rid, tlen, dlen))
                '''
                if 0 == tlen == dlen:
                    self.record_log(debug_leave.LOG_ERROR, "Error: Data length should't be 0")
                    continue

                if rid == DictCommandInfo["hwq_cfg"] and tlen == dlen:
                    self.record_log(debug_leave.LOG_DEBUG, self.msg_info_cmd + " command tx successed")
                    self.response_queue.put(self.msg_info_cmd)
                elif rid == DictCommandInfo["set_band"] and tlen == dlen:
                    self.record_log(debug_leave.LOG_DEBUG, self.msg_info_cmd + " command tx successed")
                    self.response_queue.put(self.msg_info_cmd)
                elif rid == DictCommandInfo["pkt_cfg"] and tlen == dlen:
                    self.record_log(debug_leave.LOG_DEBUG, self.msg_info_cmd + " command tx successed")
                    self.response_queue.put(self.msg_info_cmd)
                elif rid == DictCommandInfo["pkt_data"] and tlen == dlen:
                    self.record_log(debug_leave.LOG_DEBUG, self.msg_info_cmd + " command tx successed")
                    self.response_queue.put(self.msg_info_cmd)
                elif rid == DictCommandInfo["test_case"] and tlen == dlen: 
                    self.record_log(debug_leave.LOG_DEBUG, self.msg_info_cmd + " command tx successed")
                    self.response_queue.put(self.msg_info_cmd)
                elif rid == DictCommandInfo["ring_cfg"] and tlen == dlen:
                    self.record_log(debug_leave.LOG_DEBUG, self.msg_info_cmd + " command tx successed")
                    self.response_queue.put(self.msg_info_cmd)
                elif rid == DictCommandInfo["read"] and tlen == dlen:
                    self.record_log(debug_leave.LOG_DEBUG, data_valid)
                    self.response_queue.put(data_valid)
                else:
                    self.record_log(debug_leave.LOG_ERROR, "this rid %d no support" % rid)

    def collect_info_from_ser(self, serport):
        length_fmt = struct.Struct('<I')
        str_packet_descriptor = b"2323\w{24}\w{8}01[0]{6}(\w{8})"
        m_ptest_str = b"2323\w{12}[0]{12}0200\w{4}11[0]{6}((\w{2})+?)((40)+)?4040"
        m_ptest_comp = re.compile(m_ptest_str)
        bytes2read = ''

        while 1:
            bytes2read = serport.inWaiting()
            if not bytes2read:
                continue
            tmp = serport.read(bytes2read)
            self.pack_info += binascii.hexlify(tmp)

            comd_descriptor_m_str = str_packet_descriptor + self.comd_flag
            comd_descriptor_m = re.search(comd_descriptor_m_str, self.pack_info)
            utest_m_str = (b"2323\w{12}[0]{12}\w{8}29[0]{6}(\w{8})(\w{" +
                           str(self.utest_package_len * 2).encode("utf-8") +
                           b"})4040")
            utest_m = re.search(utest_m_str, self.pack_info)
            ptest_m = m_ptest_comp.search(self.pack_info)

            if self.comd_flag:
                if comd_descriptor_m:
                    str_packet_len_format = comd_descriptor_m.group(1)
                    hex_str_packet_len = binascii.a2b_hex(str_packet_len_format)
                    un_datalen = length_fmt.unpack(hex_str_packet_len)
                    cur_packet_len = int(un_datalen[0])

                    comd_m_str = (comd_descriptor_m_str +
                                  b"(\w{" +
                                  str(cur_packet_len * 2 - len(self.comd_flag)).encode("utf-8") +
                                  b"})4040")
                    comd_m = re.search(comd_m_str, self.pack_info)

                    if comd_m:
                        self.notice_queue.put(comd_m.group(0))
                        self.pack_info = self.pack_info.replace(comd_m.group(0), b"")
                        if self.multi_return_flag:  # multiple commands return
                            continue
                        else:
                            self.comd_flag = b''
                    else:
                        continue

                if utest_m:
                    str_datalen = utest_m.group(1)
                    hstr_datalen = binascii.a2b_hex(str_datalen)
                    fmt = struct.Struct('<I')
                    un_datalen = fmt.unpack(hstr_datalen)
                    datalen = int(un_datalen[0])
                    if self.utest_package_len == datalen:
                        self.notice_queue.put(utest_m.group(0))
                        self.pack_info = self.pack_info.replace(utest_m.group(0), b"")
                        self.comd_flag = b''
                    else:
                        self.record_log(debug_leave.LOG_ERROR, "Error: Uart Stress Test Received package Length Mismatched!")
                        self.record_log(debug_leave.LOG_ERROR, "Will Auto Discard Packet:\n %s\n" % utest_m.group(0))
                        self.pack_info = self.pack_info.replace(utest_m.group(0), b"")
                        self.comd_flag = b''
                        continue

                if ptest_m:
                    self.notice_queue.put(ptest_m.group(0))
                    self.pack_info = self.pack_info.replace(ptest_m.group(0), b"")
                    self.comd_flag = b''

                continue

            if len(self.pack_info) > 200000:  # auto clear redundant data
                self.pack_info = b''

    def ftm_send_cmd(self, str_cmd):
        info = self.exe_cmd(str_cmd)
        self.ser_send_data(info)
        ret = 'error'

        try:
            response = self.response_queue.get(timeout=5)
            self.record_log(debug_leave.LOG_DEBUG, 'send cmd %s successed!' % str_cmd)
            if str_cmd.find('read') >= 0:
                return response
            return response
        except Exception:
            self.record_log(debug_leave.LOG_ERROR, 'send cmd something wrong!!')
            return ret

    # kill child thread
    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    # kill child thread
    def stop_thread(self):
        self._async_raise(self.c_thread.ident, SystemExit)
        self._async_raise(self.f_thread.ident, SystemExit)
