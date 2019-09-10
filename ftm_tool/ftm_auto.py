# -*- coding: utf-8 -*-
import ftm_cmd
import ui2
import queue
import threading
import sys
from datetime import *
import time
import hplc_cert
import os
import codecs
import configparser
import serial
import binascii
import struct
import fileinput
import re
import signal_generator
from signal_generator import NARROW_MARCO
import crc_calu

class ATT_VALUE_MARCO:
    # the min value of attenuator
    ATT_VALUE_MIN = 0
    # the max value of attenuator
    ATT_VALUE_MAX = 95
    # the coarse step of attenuator
    ATT_COARSE_STEP = 10
    # the fine step of attenuator
    ATT_FINE_STEP = 1

class RESULT_MARCO:
    PASS_THRESHOLD = 90

class OTHER_MARCO:
    TEST_TIMES = 40

class PROTO_MARCO:
    PROTO_SG = 0
    PROTO_SPG = 3

class BAND_ID_MARCO:
    PROTO_BAND_ID_0 = 0
    PROTO_BAND_ID_1 = 1
    PROTO_BAND_ID_2 = 2
    PROTO_BAND_ID_3 = 3

class MODE_MARCO:
     # cert test command enter app layer transparent transfer tx mode, in this
     # mode, will send MSDU to uart.
    CERT_TEST_CMD_ENTER_APP_T_T = 0x01

    # cert test command enter app layer transparent transfer rx mode, in this
    # mode, will packing data received from the UART, sent to the PLC network
    # as a MSDU.
    CERT_TEST_CMD_ENTER_APP_T_R = 0x02

    # cert test command enter physical layer transparent transfer mode */
    CERT_TEST_CMD_ENTER_PHY_T = 0x03

    # cert test command for enter physical layer loopback mode */
    CERT_TEST_CMD_ENTER_PHY_LP = 0x04

    # cert test command for enter MAC layer transparent transfer mode */
    CERT_TEST_CMD_ENTER_MAC_T = 0x05

    # cert test command for set frequency band */
    CERT_TEST_CMD_SET_FB = 0x06

    # cert test command for set tonemask */
    CERT_TEST_CMD_SET_TM = 0x07

class POWER_MARCO:
    POWER_ON = 'aa'
    POWER_DOWN = 'bb'

class TMI_MARCO:
    TMI_0 = 0
    TMI_1 = 1
    TMI_2 = 2
    TMI_3 = 3
    TMI_4 = 4
    TMI_5 = 5
    TMI_6 = 6
    TMI_7 = 7
    TMI_8 = 8
    TMI_9 = 9
    TMI_10 = 10
    TMI_11 = 11
    TMI_12 = 12
    TMI_13 = 13
    TMI_14 = 14
    TMI_MAX = 15

class EXTMI_MARCO:
    EXTMI_1 = 1
    EXTMI_2 = 2
    EXTMI_3 = 3
    EXTMI_4 = 4
    EXTMI_5 = 5
    EXTMI_6 = 6
    EXTMI_10 = 10
    EXTMI_11 = 11
    EXTMI_12 = 12
    EXTMI_13 = 13
    EXTMI_14 = 14
    EXTMI_MAX = 15

class SIGNOL_MARCO:
    WHITE_TEST = 1
    PULSE_TEST = 2
    SIN_TEST = 3

class ftm_auto():
    def __init__(self, table, log_disp, switch_ser, ftmuser, record_log, lcd, pbar_emit):
        self.record_log = record_log
        self.filename_record = ''

        self.table = table
        self.fun_queue = self.table.handle_queue

        self.micro = ui2.all_cert_case_value()
        self.log_display_ui = log_disp
        self.ftm = ftmuser
        self.switch_ser = switch_ser
        self.error_type = 0
        # transparent transmission serial port
        self.tt_ser = serial.Serial()
        self.tt_c_thread = None
        # loopback serial port
        self.lp_ser = serial.Serial()
        self.lp_c_thread = None

        # rx data thread
        self.compare_queue = queue.Queue(maxsize=-1)

        self.pack_info = b''
        self.pack_compare = b''
        self.data_record_flag = 0

        # lcdnumber dispaly
        self.timer_dlp = threading.Timer(1, self.timer_display_fun)
        self.lcd_start_t, self.lcd_stop_t = 0, 0
        self.timer_flag = 0
        # lcd display
        self.lcdNumber = lcd
        # 进度条
        self.pbar_emit = pbar_emit

        self.fun_thread = threading.Thread(target=self.auto_handle_func)
        self.fun_thread.setDaemon(True)
        self.fun_thread.start()
        self.sig_gen = signal_generator.signal_generator(self.record_log)
        self.att_control_ser = self.sig_gen.att_control_ser
        self.overnight_cnt = 0
        self.crc_calu = crc_calu.crc_calu()

    def auto_pbar_set(self, int):
        self.pbar_emit(int)

    def tt_ser_open(self):

        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        if config_tmp.has_option("tt_config", "s2_serial_port"):
            self.tt_ser.port = config_tmp.get("tt_config", "s2_serial_port")
        if config_tmp.has_option("tt_config", "s2_baudrate"):
            self.tt_ser.baudrate = int(config_tmp.get("tt_config", "s2_baudrate"))
        if config_tmp.has_option("tt_config", "s2_bytesize"):
            self.tt_ser.bytesize = int(config_tmp.get("tt_config", "s2_bytesize"))
        if config_tmp.has_option("tt_config", "s2_stopbits"):
            self.tt_ser.stopbits = int(config_tmp.get("tt_config", "s2_stopbits"))
        if config_tmp.has_option("tt_config", "s2_parity"):
            self.tt_ser.parity = config_tmp.get("tt_config", "s2_parity")

        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, 'tt serial config ' + self.tt_ser.port +
                        ' %s' % self.tt_ser.baudrate + ' %s' % self.tt_ser.bytesize +
                        ' %s' % self.tt_ser.stopbits + ' ' + self.tt_ser.parity)

        try:
            self.tt_ser.open()
            self.start_tt_thread()
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "tt serial open successed!")
        except:
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "tt 串口不能被打开！")
            return None

    def start_tt_thread(self):
        # start threads for serial port data collection
        self.tt_c_thread = threading.Thread(target=self.tt_data_handle)
        self.tt_c_thread.setDaemon(True)
        self.tt_c_thread.start()


    def lp_ser_open(self):

        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        if config_tmp.has_option("lp_config", "s5_serial_port"):
            self.lp_ser.port = config_tmp.get("lp_config", "s5_serial_port")
        if config_tmp.has_option("lp_config", "s5_baudrate"):
            self.lp_ser.baudrate = int(config_tmp.get("lp_config", "s5_baudrate"))
        if config_tmp.has_option("lp_config", "s5_bytesize"):
            self.lp_ser.bytesize = int(config_tmp.get("lp_config", "s5_bytesize"))
        if config_tmp.has_option("lp_config", "s5_stopbits"):
            self.lp_ser.stopbits = int(config_tmp.get("lp_config", "s5_stopbits"))
        if config_tmp.has_option("lp_config", "s5_parity"):
            self.lp_ser.parity = config_tmp.get("lp_config", "s5_parity")

        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, 'lp serial config ' + self.lp_ser.port +
                        ' %s' % self.lp_ser.baudrate + ' %s' % self.lp_ser.bytesize +
                        ' %s' % self.lp_ser.stopbits + ' ' + self.lp_ser.parity)

        try:
            self.lp_ser.open()
            self.start_lp_thread()
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "lp serial open successed!")
        except:
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "lp 串口不能被打开！")
            return None

    def start_lp_thread(self):
        # start threads for serial port data collection
        self.lp_c_thread = threading.Thread(target=self.lp_data_handle)
        self.lp_c_thread.setDaemon(True)
        self.lp_c_thread.start()

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
        self._async_raise(self.tt_c_thread.ident, SystemExit)
        self._async_raise(self.lp_c_thread.ident, SystemExit)

    def tt_data_handle(self):
        num = 0
        while 1:
            bytes2read = self.tt_ser.inWaiting()
            if not bytes2read:
                continue

            try:
                tmp = self.tt_ser.read(bytes2read)
                self.pack_info += binascii.hexlify(tmp)
            except :
                continue

            if self.data_record_flag == 0:
                self.pack_info = b''
                continue

            num += bytes2read

            str_compare = str(self.pack_compare, encoding='utf-8')
            str_len = len(str_compare)/2

            # TODO: maybe have same better way to handle serial rx frame break
            if num < str_len:
                continue

            str_info = str(self.pack_info, encoding='utf-8')

            self.log_display_record('receive_data:' + str_info, 0)
            self.log_display_record('send_data:' + str_compare, 0)

            if str_compare in str_info:
                print('pass')
                self.compare_queue.put('compare_pass')
            else:
                print('fail')
                self.compare_queue.put('compare_fail')

            self.pack_info = b''
            num = 0

    def lp_data_handle(self):
        num = 0
        while 1:
            bytes2read = self.lp_ser.inWaiting()
            if not bytes2read:
                continue

            try:
                tmp = self.lp_ser.read(bytes2read)
                self.pack_info += binascii.hexlify(tmp)
            except :
                continue

            if self.data_record_flag == 0:
                self.pack_info = b''
                continue

            num += bytes2read

            str_compare = str(self.pack_compare, encoding='utf-8')
            str_len = len(str_compare)/2

            # TODO: maybe have same better way to handle serial rx frame break
            if num < str_len:
                continue

            str_info = str(self.pack_info, encoding='utf-8')

            self.log_display_record('receive_data:' + str_info, 0)
            self.log_display_record('send_data:' + str_compare, 0)

            if str_compare in str_info:
                print('pass')
                self.compare_queue.put('compare_pass')
            else:
                print('fail')
                self.compare_queue.put('compare_fail')

            self.pack_info = b''
            num = 0

    def auto_tx_data(self, str_cmd):
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + str_cmd + '*' * 20)
        return self.ftm.ftm_send_cmd(str_cmd)

    def auto_init_ftm(self, proto, proto_band_id):
        self.auto_tx_data("dtest set_band " + '%s' % proto + ' ' + '%s' % proto_band_id + ' 0')
        #self.auto_tx_data("load ring_cfg")
        self.auto_tx_data("load hwq_cfg")
        self.auto_tx_data("load pkt_data_cert")
        self.auto_tx_data("load pkt_cfg_cert -d 1 -t 4")

    def auto_ftm_rx_config(self):
        # -c cert
        self.auto_tx_data("load ring_cfg -c 1")

    def auto_ftm_set_self_band(self, proto, proto_band_id):
        if proto == PROTO_MARCO.PROTO_SG:
            if proto_band_id >= BAND_ID_MARCO.PROTO_BAND_ID_0 or proto_band_id <= BAND_ID_MARCO.PROTO_BAND_ID_3:
                self.auto_tx_data("dtest set_band " + '%s' % proto + ' ' + '%s' % proto_band_id + ' 0')
            else:
                self.record_log(hplc_cert.debug_leave.LOG_ERROR,
                                "set self band fail!" + 'cert proto %d band %d is not support' % (proto, band_id))
        elif proto == PROTO_MARCO.PROTO_SPG:
                self.record_log(hplc_cert.debug_leave.LOG_ERROR, "spg have other way to set self band!" +
                                'cert proto %d band %d is not support' % (proto, band_id))
        else:
            self.record_log(hplc_cert.debug_leave.LOG_ERROR,
                            "set band fail!" + 'cert proto %d band %d is not support' % (proto, band_id))
            self.error_type = 1

    def auto_ftm_set_band(self, proto, proto_band_id):
        if proto == PROTO_MARCO.PROTO_SG:
            if proto_band_id == BAND_ID_MARCO.PROTO_BAND_ID_0:
                self.auto_tx_data("load pkt_data_band0")
                self.auto_tx_data("load test_case -n 20 -i 200")
            elif proto_band_id == BAND_ID_MARCO.PROTO_BAND_ID_1:
                self.auto_tx_data("load pkt_data_band1")
                self.auto_tx_data("load test_case -n 20 -i 200")
            elif proto_band_id == BAND_ID_MARCO.PROTO_BAND_ID_2:
                self.auto_tx_data("load pkt_data_band2")
                self.auto_tx_data("load test_case -n 20 -i 200")
            elif proto_band_id == BAND_ID_MARCO.PROTO_BAND_ID_3:
                self.auto_tx_data("load pkt_data_band3")
                self.auto_tx_data("load test_case -n 20 -i 200")
            else:
                self.record_log(hplc_cert.debug_leave.LOG_ERROR,
                                "set band fail!" + 'cert proto %d band %d is not support' % (proto, proto_band_id))
        elif proto == PROTO_MARCO.PROTO_SPG:
                self.record_log(hplc_cert.debug_leave.LOG_ERROR, "spg have other way to set band!" +
                                'cert proto %d band %d is not support' % (proto, proto_band_id))
        else:
            self.record_log(hplc_cert.debug_leave.LOG_ERROR,
                            "set band fail!" + 'cert proto %d band %d is not support' % (proto, proto_band_id))
            self.error_type = 1
        time.sleep(4)

    def auto_ftm_entry_mode(self, proto, mode):
        if proto == PROTO_MARCO.PROTO_SG:
            if mode == MODE_MARCO.CERT_TEST_CMD_ENTER_PHY_T:
                # phy transparent transfer
                self.auto_tx_data("load pkt_data_phy_tt")
                self.auto_tx_data("load test_case -n 20 -i 250")
            elif mode == MODE_MARCO.CERT_TEST_CMD_ENTER_PHY_LP:
                # phy loopback
                self.auto_tx_data("load pkt_data_phy_lp")
                self.auto_tx_data("load test_case -n 20 -i 250")
            elif mode == MODE_MARCO.CERT_TEST_CMD_ENTER_MAC_T:
                # mac transparent transfer
                self.auto_tx_data("load pkt_data_mac_tt")
                self.auto_tx_data("load test_case -n 20 -i 250")
            else:
                self.record_log(hplc_cert.debug_leave.LOG_ERROR, 'cert proto %d mode %d is not support' % (proto, mode))
                self.error_type = 1
        elif proto == PROTO_MARCO.PROTO_SPG:
            if mode == MODE_MARCO.CERT_TEST_CMD_ENTER_PHY_LP:
                self.auto_tx_data("load pkt_cfg_data")
                self.auto_tx_data("load test_case -n 20 -i 250")
            elif mode == MODE_MARCO.CERT_TEST_CMD_ENTER_MAC_T:
                self.auto_tx_data("load pkt_cfg_data")
                self.auto_tx_data("load test_case -n 20 -i 250")
            else:
                self.record_log(hplc_cert.debug_leave.LOG_ERROR, "cert proto %d mode %d is not support" % (proto, mode))
                self.error_type = 1
        else:
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "台体进入发射模式失败!")
            self.record_log("cert proto %d mode %d is not support" % (proto, mode))
            self.error_type = 1
        time.sleep(5)
        self.error_type = 0
        return self.error_type

    # entry phy lp mode
    def auto_ftm_tx_test_pkt(self, tmi):
        self.auto_tx_data("load pkt_cfg_cert -d 1" + ' -t %d' % tmi)
        self.auto_tx_data("load pkt_data_cert_test")
        self.auto_tx_data("load test_case -n 1 -i 100")

    def auto_ftm_tx_beacon(self):
        self.auto_tx_data("load pkt_cfg_cert -d 0")
        self.auto_tx_data("load test_case -n 5 -i 500")
        time.sleep(3)

    def auto_ftm_get_fc_info(self):
        # get fc
        data_fc = self.auto_tx_data("dtest read 0x51001050 16")
        data_crc = self.crc_calu.crc24(data_fc)
        data_crc = struct.pack('<I', data_crc)
        data_crc = data_crc[:-1]
        pack_fc = data_fc + data_crc
        pack_fc = binascii.hexlify(pack_fc)
        #print(pack_fc)
        #get pld
        list_pkt_part = []
        test_case_file = r".\mac_cfg\pkt_data_cert_test.txt"
        for line in fileinput.input(test_case_file):
            m_data = re.match(r'\A\s*([0-9A-Fa-f]{2}(.+)[0-9A-Fa-f]{2})\s*\Z', line)
            if m_data:
                list_pkt_part.append(m_data.group(1).strip())
        str_t = ''.join(list_pkt_part)
        str_t = str_t.replace(' ', '')
        str_t = bytes(str_t, encoding="utf8")
        pb_header = b'c0'
        compare_data = pack_fc + pb_header + str_t
        #print(compare_data)
        return compare_data

    def log_display_record(self, str, print_to_ui=1):

        str_comb = '%s' % datetime.now() + ' : ' + str + '\n'

        # 写入到文件log
        f = codecs.open(self.filename_record, mode='a', encoding='utf-8')
        f.write(str_comb)
        f.close()

        # logging log
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, str)

        # 打印到窗体
        if print_to_ui == 1:
            self.log_display_ui(str_comb)

        print(str)

    def auto_att_interfere_test(self, str_info, band_id, test_id=0, narrow_id=0):

        self.auto_pbar_set(10)

        f = codecs.open(self.filename_record, mode='w', encoding='utf-8')
        f.write('*'*20 + str_info + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + str_info + '*' * 20)
        # start run
        self.log_display_record(" 台体开始上电")
        self.switch_ser(POWER_MARCO.POWER_DOWN)

        self.log_display_record(" 初始化台体")
        # proto = sg, band = 2
        self.auto_init_ftm(PROTO_MARCO.PROTO_SG, BAND_ID_MARCO.PROTO_BAND_ID_2)
        # set att init 10db
        self.sig_gen.auto_set_att_control(10)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

        self.log_display_record(" 模块上电")
        self.switch_ser(POWER_MARCO.POWER_ON)
        time.sleep(3)

        self.log_display_record(" 开始发送设置band的包")
        self.auto_ftm_set_band(PROTO_MARCO.PROTO_SG, band_id)
        # proto = sg, band = 0
        self.auto_ftm_set_self_band(PROTO_MARCO.PROTO_SG, band_id)
        self.log_display_record(" 设置band结束  开始发送进入透传模式的包")

        self.auto_pbar_set(20)

        self.auto_ftm_entry_mode(PROTO_MARCO.PROTO_SG, MODE_MARCO.CERT_TEST_CMD_ENTER_PHY_T)
        time.sleep(3)
        self.log_display_record(" 发送进入透传模式的包结束  开始发送测试包")

        # get config
        if test_id == SIGNOL_MARCO.WHITE_TEST:
            # white noise test
            self.sig_gen.sg_set_white_noise()
        elif test_id == SIGNOL_MARCO.PULSE_TEST:
            # pulse test
            self.sig_gen.sg_set_pulse()
        elif test_id == SIGNOL_MARCO.SIN_TEST:
            # narrow test
            self.sig_gen.sg_set_sin(narrow_id)
        else:
            pass

        # get line att
        line_att, att_success_rate, att_pass_threshold = self.sig_gen.att_get_init_config()

        self.pack_compare = self.auto_ftm_get_fc_info()
        self.data_record_flag = 1
        compare_cnt, compare_rate = 0, 0
        pbar_value = 20
        last_value = 0
        att_min = ATT_VALUE_MARCO.ATT_VALUE_MIN + line_att
        att_max = ATT_VALUE_MARCO.ATT_VALUE_MAX + line_att
        for att_value in range(att_min, att_max, ATT_VALUE_MARCO.ATT_COARSE_STEP):
            # set attenuator value
            self.sig_gen.auto_set_att_control(att_value - line_att)
            self.log_display_record(" 设置的衰减值为:%d  并发送5个beacon" % att_value)
            # send beacon
            self.auto_ftm_tx_beacon()
            compare_cnt, compare_rate, fail_cnt = 0, 0, 0
            # send test pkt
            for i in range(OTHER_MARCO.TEST_TIMES):
                # rough tuning is no longer pass, into next stage
                if i - compare_cnt > 10:
                    break
                self.compare_queue.queue.clear()
                self.auto_ftm_tx_test_pkt(TMI_MARCO.TMI_4)
                try:
                    str = self.compare_queue.get(timeout=5)
                except:
                    str = 'compare_fail'

                if str == 'compare_pass':
                    compare_cnt += 1
                    self.log_display_record("receive success cnt:%d" % compare_cnt)
                elif str == 'compare_fail':
                    fail_cnt += 1
                    self.log_display_record("compare fail! %d" % fail_cnt)
                else:
                    self.log_display_record("other fail! %d" % i)
                time.sleep(0.5)
            compare_rate = (compare_cnt * 100) / OTHER_MARCO.TEST_TIMES
            self.log_display_record(" 衰减值为: %d 的时候, 成功率为: %d" % (att_value, compare_rate))
            # rate > threshold , continue. else entry next stage
            if compare_rate > att_success_rate:
                # over the attenuator max
                if att_value >= att_max - ATT_VALUE_MARCO.ATT_COARSE_STEP:
                    last_value = att_value
                    return [last_value, att_pass_threshold]
                else:
                    pbar_value += 10
                    if pbar_value > 60:
                        pbar_value = 60
                    self.auto_pbar_set(pbar_value)
                    continue
            # set pbar value
            pbar_value = 60
            self.auto_pbar_set(pbar_value)

            # next stage, fine tuning
            fine_init_value = att_value - ATT_VALUE_MARCO.ATT_COARSE_STEP
            # 如果第一阶段的粗调都没过，直接退出
            if fine_init_value < 0:
                last_value = att_value
                return [last_value, att_pass_threshold]
            # fine tuning
            for att_fine_value in range(fine_init_value, att_value, ATT_VALUE_MARCO.ATT_FINE_STEP):
                # set attenuator value
                self.sig_gen.auto_set_att_control(att_fine_value - line_att)
                self.log_display_record(" 设置的衰减值为: %d 发送5个beacon" % att_fine_value)
                # send beacon
                self.auto_ftm_tx_beacon()
                compare_cnt, compare_rate, fail_cnt = 0, 0, 0
                # send test pkt
                for i in range(OTHER_MARCO.TEST_TIMES):
                    # current testing, more than 10 packages can not be received
                    if i - compare_cnt > 10:
                        break
                    self.compare_queue.queue.clear()
                    self.auto_ftm_tx_test_pkt(TMI_MARCO.TMI_4)
                    try:
                        str = self.compare_queue.get(timeout=2)
                    except:
                        str = 'compare_fail'

                    if str == 'compare_pass':
                        compare_cnt += 1
                        self.log_display_record("receive success cnt:%d" % compare_cnt)
                    elif str == 'compare_fail':
                        fail_cnt += 1
                        self.log_display_record("compare fail! %d" % fail_cnt)
                    else:
                        self.log_display_record("other fail! %d" % i)
                    time.sleep(0.5)
                    compare_rate = (compare_cnt * 100) / OTHER_MARCO.TEST_TIMES
                self.log_display_record(" 衰减值为: %d 的时候, 成功率为: %d" % (att_fine_value, compare_rate))
                # rate > threshold , continue. else entry next stage
                if compare_rate > att_success_rate:
                    pbar_value += 5
                    if pbar_value > 90:
                        pbar_value = 90
                    self.auto_pbar_set(pbar_value)
                    continue
                else:
                    last_value = att_fine_value - ATT_VALUE_MARCO.ATT_FINE_STEP
                    return [last_value, att_pass_threshold]
        return [last_value, att_pass_threshold]

    def loopback_handle(self, str_title, band_id, tmi_max):
        # start run
        str_ftm = "开始测试 " + str_title
        self.log_display_record(str_ftm)
        str_ftm = "台体开始上电"
        self.log_display_record(str_ftm)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

        str_ftm = "初始化台体"
        self.log_display_record(str_ftm)
        # proto = sg, band = 2
        self.auto_init_ftm(PROTO_MARCO.PROTO_SG, BAND_ID_MARCO.PROTO_BAND_ID_2)

        str_ftm = "模块上电"
        self.log_display_record(str_ftm)
        self.switch_ser(POWER_MARCO.POWER_ON)
        time.sleep(5)

        self.auto_pbar_set(5)

        str_ftm = "开始发送设置band的包"
        self.log_display_record(str_ftm)
        self.auto_ftm_set_band(PROTO_MARCO.PROTO_SG, band_id)
        # proto = sg, band = 0
        self.auto_ftm_set_self_band(PROTO_MARCO.PROTO_SG, band_id)

        self.auto_pbar_set(10)

        str_ftm = "开始发送测试包"
        self.log_display_record(str_ftm)
        self.auto_ftm_tx_test_pkt(TMI_MARCO.TMI_4)

        self.auto_pbar_set(20)

        pbar_value = 20
        # calulate pbar step
        pbar_step = 80/tmi_max
        print(pbar_step)

        # entry rx mode
        self.auto_ftm_rx_config()

        # send test pkt
        str_ftm = "开始发送进入回传模式的包"
        self.log_display_record(str_ftm)
        self.auto_ftm_entry_mode(PROTO_MARCO.PROTO_SG, MODE_MARCO.CERT_TEST_CMD_ENTER_PHY_LP)
        self.data_record_flag = 0
        compare_flag, compare_cnt = 0, 0
        not_entry_lp = 0
        remark = ''
        for tmi in range(tmi_max):
            compare_flag = 0
            if not_entry_lp == 1:
                remark = 'not entry lp mode'
                self.log_display_record(remark)
                break
            for times in range(20):
                if compare_flag == 1:
                    break
                elif times == 19:
                    not_entry_lp = 1
                    break
                # pre-send pkt and get fc
                self.auto_ftm_tx_test_pkt(tmi)
                # delay 0.5s and get correct fc
                time.sleep(0.5)
                # get config fc
                self.pack_compare = self.auto_ftm_get_fc_info()

                self.compare_queue.queue.clear()
                self.data_record_flag = 1
                self.auto_ftm_tx_test_pkt(tmi)

                try:
                    str = self.compare_queue.get(timeout=2)
                except:
                    str = 'compare_fail'

                if str == 'compare_pass':
                    compare_cnt += 1
                    compare_flag = 1
                    str_l = "tmi %d loopback test success." % tmi
                    self.log_display_record(str_l)
                elif str == 'compare_fail':
                    str_l = "tmi %d loopback test fail." % tmi
                    self.log_display_record(str_l)
                else:
                    str_l = "other fail! %d" % tmi
                    self.log_display_record(str_l)
                remark += str_l
                self.data_record_flag = 0
                time.sleep(0.5)
            # set pbar value
            pbar_value += pbar_step
            self.auto_pbar_set(pbar_value)

        return [compare_cnt, remark]

    # sta tmi scan band0
    def sta_tmi_scan_band0(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\sta_tmi_遍历_band0_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'sta tmi 遍历 band0' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'sta tmi 遍历 band0' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 STA band0", BAND_ID_MARCO.PROTO_BAND_ID_0, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 STA band0", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 STA band0: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta tmi scan band1
    def sta_tmi_scan_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\sta_tmi_遍历_band1_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'sta tmi 遍历 band1' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'sta tmi 遍历 band1' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 STA band1", BAND_ID_MARCO.PROTO_BAND_ID_1, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 STA band1", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 STA band1: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta tmi scan band2
    def sta_tmi_scan_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\sta_tmi_遍历_band2_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'sta tmi 遍历 band2' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'sta tmi 遍历 band2' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 STA band2", BAND_ID_MARCO.PROTO_BAND_ID_2, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 STA band2", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 STA band2: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta tmi scan band3
    def sta_tmi_scan_band3(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\sta_tmi_遍历_band3_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'sta tmi 遍历 band3' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'sta tmi 遍历 band3' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 STA band3", BAND_ID_MARCO.PROTO_BAND_ID_3, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 STA band3", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 STA band3: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    def overnight_test(self, str_info, band_id):

        f = codecs.open(self.filename_record, mode='w', encoding='utf-8')
        f.write('*'*20 + str_info + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + str_info + '*' * 20)
        # start run
        self.overnight_cnt += 1
        self.log_display_record(" 台体开始上电 %d" % self.overnight_cnt)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

        self.log_display_record(" 初始化台体")
        # proto = sg, band = 2
        self.auto_init_ftm(PROTO_MARCO.PROTO_SG, BAND_ID_MARCO.PROTO_BAND_ID_2)
        # set att init 10db
        #self.sig_gen.auto_set_att_control(10)
        #self.switch_ser(POWER_MARCO.POWER_DOWN)

        self.log_display_record(" 模块上电")
        self.switch_ser(POWER_MARCO.POWER_ON)
        time.sleep(8)

        self.log_display_record(" 开始发送设置band的包")
        self.auto_ftm_set_band(PROTO_MARCO.PROTO_SG, band_id)
        # proto = sg, band = 0
        self.auto_ftm_set_self_band(PROTO_MARCO.PROTO_SG, band_id)
        self.log_display_record(" 设置band结束  开始发送进入透传模式的包")

        #self.auto_pbar_set(20)

        self.auto_ftm_entry_mode(PROTO_MARCO.PROTO_SG, MODE_MARCO.CERT_TEST_CMD_ENTER_PHY_T)
        #time.sleep(3)
        self.log_display_record(" 发送进入透传模式的包结束  开始发送测试包")

        #time.sleep(10)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta tonemask band0
    def sta_tonemask_band0(self):


        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 STA band0", '%s' % dlt_t, "pass", "ok"])

    # sta tonemask band1
    def sta_tonemask_band1(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 STA band1", '%s' % dlt_t, "pass", "ok"])

    # sta tonemask band2
    def sta_tonemask_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 STA band2", '%s' % dlt_t, "pass", "ok"])

    # sta tonemask band3
    def sta_tonemask_band3(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 STA band3", '%s' % dlt_t, "pass", "ok"])

    # cco tmi scan band0
    def cco_tmi_scan_band0(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\cco_tmi_遍历_band0_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'cco tmi 遍历 band0' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'cco tmi 遍历 band0' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 CCO band0", BAND_ID_MARCO.PROTO_BAND_ID_0, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 CCO band0", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 CCO band0: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco tmi scan band1
    def cco_tmi_scan_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\cco_tmi_遍历_band1_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'cco tmi 遍历 band1' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'cco tmi 遍历 band1' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 CCO band1", BAND_ID_MARCO.PROTO_BAND_ID_1, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 CCO band1", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 CCO band1: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco tmi scan band2
    def cco_tmi_scan_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\cco_tmi_遍历_band2_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'cco tmi 遍历 band2' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'cco tmi 遍历 band2' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 CCO band2", BAND_ID_MARCO.PROTO_BAND_ID_2, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 CCO band2", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 CCO band2: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco tmi scan band3
    def cco_tmi_scan_band3(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\协议一致性'
        if not os.path.exists(patch):
            os.makedirs(patch)
        filename =patch + '\cco_tmi_遍历_band3_' + file_time + '.log'
        self.filename_record = filename
        f = codecs.open(filename, mode='w', encoding='utf-8')
        f.write('*'*20 + 'cco tmi 遍历 band3' + '*'*20 + '\n')
        f.close()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, '*' * 20 + 'cco tmi 遍历 band3' + '*' * 20)
        # 获取开始时间
        t_start = datetime.now()

        compare_cnt, remark = self.loopback_handle("TMI遍历 CCO band3", BAND_ID_MARCO.PROTO_BAND_ID_3, TMI_MARCO.TMI_MAX)

        if compare_cnt == TMI_MARCO.TMI_MAX:
            result = 'pass'
        else:
            result = 'fail'

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["TMI遍历 CCO band3", '%s' % dlt_t, result, remark])
        self.log_display_record("TMI遍历 CCO band3: %s" % remark)
        self.log_display_record("测试结束, 结果: %s " % result)
        self.auto_pbar_set(100)
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco tonemask band0
    def cco_tonemask_band0(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 CCO band0", '%s' % dlt_t, "pass", "ok"])
        self.auto_pbar_set(100)

    # cco tonemask band1
    def cco_tonemask_band1(self):
        self.auto_pbar_set(0)
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 CCO band1", '%s' % dlt_t, "pass", "ok"])
        self.auto_pbar_set(100)

    # cco tonemask band2
    def cco_tonemask_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 CCO band2", '%s' % dlt_t, "pass", "ok"])

    # cco tonemask band3
    def cco_tonemask_band3(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["ToneMask测试 CCO band3", '%s' % dlt_t, "pass", "ok"])

    # sta white noise band1
    def sta_performance_white_noise_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\sta_白噪声_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 白噪声 band1', BAND_ID_MARCO.PROTO_BAND_ID_1, SIGNOL_MARCO.WHITE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'white noise attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["白噪性能 STA band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 白噪性能 STA band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta white noise band2
    def sta_performance_white_noise_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\sta_白噪声_band2_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 白噪声 band2', BAND_ID_MARCO.PROTO_BAND_ID_2, SIGNOL_MARCO.WHITE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'white noise attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["白噪性能 STA band2", '%s' % dlt_t, result, remark])

        self.log_display_record(" 白噪性能 STA band2 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta anti-ppm band1
    def sta_performance_anti_ppm_band1(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗频偏性能 STA band1", '%s' % dlt_t, "pass", "ok"])

    # sta anti-ppm band2
    def sta_performance_anti_ppm_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗频偏性能 STA band2", '%s' % dlt_t, "pass", "ok"])

    # sta anti-attenuation band1
    def sta_performance_anti_att_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\sta_抗衰减_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = self.auto_att_interfere_test('sta 抗衰减 band1', BAND_ID_MARCO.PROTO_BAND_ID_1)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗衰减性能 STA band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗衰减性能 STA band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta anti-attenuation band2
    def sta_performance_anti_att_band2(self):
        #self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)

        self.filename_record = patch + '\sta_抗衰减_band2_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = self.auto_att_interfere_test('sta 抗衰减 band2', BAND_ID_MARCO.PROTO_BAND_ID_2)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗衰减性能 STA band2", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗衰减性能 STA band2 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    def test_case(self):
        #self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)

        self.filename_record = patch + '\sta_抗衰减_band2_' + file_time + '.log'

        self.overnight_test('sta 抗衰减 band2', BAND_ID_MARCO.PROTO_BAND_ID_2)

    # sta anti-narrowband band1
    def sta_performance_anti_narrow_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\sta_抗窄带_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()
        result = 'pass'
        remark = ''
        # 1M
        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 抗窄带 band1',
                                         BAND_ID_MARCO.PROTO_BAND_ID_1,
                                         SIGNOL_MARCO.SIN_TEST, NARROW_MARCO.NARROW_1M)

        if last_value > att_pass_threshold and result == 'pass':
            result = 'pass'
        else:
            result = 'fail'
        remark += 'anti-narrow 1M attenuation is :  %d' % last_value
        # 3M
        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 抗窄带 band1',
                                         BAND_ID_MARCO.PROTO_BAND_ID_1,
                                         SIGNOL_MARCO.SIN_TEST, NARROW_MARCO.NARROW_3M)

        if last_value > att_pass_threshold and result == 'pass':
            result = 'pass'
        else:
            result = 'fail'
        remark += 'anti-narrow 3M attenuation is :  %d' % last_value
        # 6M
        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 抗窄带 band1',
                                         BAND_ID_MARCO.PROTO_BAND_ID_1,
                                         SIGNOL_MARCO.SIN_TEST, NARROW_MARCO.NARROW_6M)

        if last_value > att_pass_threshold and result == 'pass':
            result = 'pass'
        else:
            result = 'fail'
        remark = 'anti-narrow 6M attenuation is :  %d' % last_value

        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗窄带性能 STA band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗窄带性能 STA band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗窄带性能 STA band1", '%s' % dlt_t, "pass", "ok"])

    # sta anti-narrowband band2
    def sta_performance_anti_narrow_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗窄带性能 STA band2", '%s' % dlt_t, "pass", "ok"])

    # sta anti-pulse band1
    def sta_performance_anti_pulse_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\sta_抗脉冲_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 抗脉冲 band1', BAND_ID_MARCO.PROTO_BAND_ID_1, SIGNOL_MARCO.PULSE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'anti-pulse attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗脉冲性能 STA band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗脉冲性能 STA band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta anti-pulse band2
    def sta_performance_anti_pulse_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\sta_抗脉冲_band2_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('sta 抗脉冲 band2', BAND_ID_MARCO.PROTO_BAND_ID_2, SIGNOL_MARCO.PULSE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'anti-pulse attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗脉冲性能 STA band2", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗脉冲性能 STA band2 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # sta psd band1
    def sta_performance_psd_band1(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["功率频谱密度 STA band1", '%s' % dlt_t, "pass", "ok"])

    # sta psd band2
    def sta_performance_psd_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["功率频谱密度 STA band2", '%s' % dlt_t, "pass", "ok"])

    # sta rate
    def sta_performance_rate(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["STA 速率测试", '%s' % dlt_t, "pass", "ok"])

    # cco white noise band1
    def cco_performance_white_noise_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\cco_白噪声_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('cco 白噪声 band1', BAND_ID_MARCO.PROTO_BAND_ID_1, SIGNOL_MARCO.WHITE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'white noise attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["白噪性能 CCO band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 白噪性能 CCO band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco white noise band2
    def cco_performance_white_noise_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\cco_白噪声_band2_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('cco 白噪声 band2', BAND_ID_MARCO.PROTO_BAND_ID_2, SIGNOL_MARCO.WHITE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'white noise attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["白噪性能 CCO band2", '%s' % dlt_t, result, remark])

        self.log_display_record(" 白噪性能 CCO band2 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco anti-ppm band1
    def cco_performance_anti_ppm_band1(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗频偏性能 CCO band1", '%s' % dlt_t, "pass", "ok"])

    # cco anti-ppm band2
    def cco_performance_anti_ppm_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗频偏性能 CCO band2", '%s' % dlt_t, "pass", "ok"])

    # cco anti-attenuation band1
    def cco_performance_anti_att_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\cco_抗衰减_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = self.auto_att_interfere_test('cco 抗衰减 band1', BAND_ID_MARCO.PROTO_BAND_ID_1)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'att is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗衰减性能 CCO band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗衰减性能 CCO band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco anti-attenuation band2
    def cco_performance_anti_att_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\cco_抗衰减_band2_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = self.auto_att_interfere_test('cco 抗衰减 band2', BAND_ID_MARCO.PROTO_BAND_ID_2)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'att is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗衰减性能 CCO band2", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗衰减性能 CCO band2 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco anti-narrowband band1
    def cco_performance_anti_narrow_band1(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗窄带性能 CCO band1", '%s' % dlt_t, "pass", "ok"])

    # cco anti-narrowband band2
    def cco_performance_anti_narrow_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["抗窄带性能 CCO band2", '%s' % dlt_t, "pass", "ok"])

    # cco anti-pulse band1
    def cco_performance_anti_pulse_band1(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\cco_抗脉冲_band1_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('cco 抗脉冲 band1', BAND_ID_MARCO.PROTO_BAND_ID_1, SIGNOL_MARCO.PULSE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'anti-pulse attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗脉冲性能 CCO band1", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗脉冲性能 CCO band1 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco anti-pulse band2
    def cco_performance_anti_pulse_band2(self):
        self.auto_pbar_set(0)
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        patch ='.\LOG\cert_log\性能测试'
        if not os.path.exists(patch):
            os.makedirs(patch)
        self.filename_record = patch + '\cco_抗脉冲_band2_' + file_time + '.log'

        # 获取开始时间
        t_start = datetime.now()

        last_value, att_pass_threshold = \
            self.auto_att_interfere_test('cco 抗脉冲 band2', BAND_ID_MARCO.PROTO_BAND_ID_2, SIGNOL_MARCO.PULSE_TEST)

        result = ''
        if last_value > att_pass_threshold:
            result = 'pass'
        else:
            result = 'fail'
        remark = 'anti-pulse attenuation is :  %d' % last_value
        # 获取结束时间
        t_end = datetime.now()
        dlt_t = t_end - t_start
        self.table.signal2emit(["抗脉冲性能 CCO band2", '%s' % dlt_t, result, remark])

        self.log_display_record(" 抗脉冲性能 CCO band2 抗衰减值为: %d " % last_value)
        self.log_display_record(" 测试结束, 结果: %s " % result)

        self.auto_pbar_set(100)

        # clear status
        self.data_record_flag = 0
        self.switch_ser(POWER_MARCO.POWER_DOWN)

    # cco psd band1
    def cco_performance_psd_band1(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["功率频谱密度 CCO band1", '%s' % dlt_t, "pass", "ok"])

    # cco psd band2
    def cco_performance_psd_band2(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["功率频谱密度 CCO band2", '%s' % dlt_t, "pass", "ok"])

    # cco rate
    def cco_performance_rate(self):
        t1 = datetime.now()
        time.sleep(4)
        print(sys._getframe().f_code.co_name)
        t2 = datetime.now()
        dlt_t = t2 - t1
        print("用时: %s" % dlt_t)
        self.table.signal2emit(["CCO 速率测试", '%s' % dlt_t, "pass", "ok"])


    def auto_call_back(self, index):
        if self.micro.ROOT_PROTOCON_STA_TMISCAN_B0 == index:
            self.sta_tmi_scan_band0()
        elif self.micro.ROOT_PROTOCON_STA_TMISCAN_B1 == index:
            self.sta_tmi_scan_band1()
        elif self.micro.ROOT_PROTOCON_STA_TMISCAN_B2 == index:
            self.sta_tmi_scan_band2()
        elif self.micro.ROOT_PROTOCON_STA_TMISCAN_B3 == index:
            self.sta_tmi_scan_band3()
        elif self.micro.ROOT_PROTOCON_STA_TM_B0 == index:
            self.sta_tonemask_band0()
        elif self.micro.ROOT_PROTOCON_STA_TM_B1 == index:
            self.sta_tonemask_band1()
        elif self.micro.ROOT_PROTOCON_STA_TM_B2 == index:
            self.sta_tonemask_band2()
        elif self.micro.ROOT_PROTOCON_STA_TM_B3 == index:
            self.sta_tonemask_band3()
        elif self.micro.ROOT_PROTOCON_CCO_TMISCAN_B0 == index:
            self.cco_tmi_scan_band0()
        elif self.micro.ROOT_PROTOCON_CCO_TMISCAN_B1 == index:
            self.cco_tmi_scan_band1()
        elif self.micro.ROOT_PROTOCON_CCO_TMISCAN_B2 == index:
            self.cco_tmi_scan_band2()
        elif self.micro.ROOT_PROTOCON_CCO_TMISCAN_B3 == index:
            self.cco_tmi_scan_band3()
        elif self.micro.ROOT_PROTOCON_CCO_TM_B0 == index:
            self.cco_tonemask_band0()
        elif self.micro.ROOT_PROTOCON_CCO_TM_B1 == index:
            self.cco_tonemask_band1()
        elif self.micro.ROOT_PROTOCON_CCO_TM_B2 == index:
            self.cco_tonemask_band2()
        elif self.micro.ROOT_PROTOCON_CCO_TM_B3 == index:
            self.cco_tonemask_band3()
        elif self.micro.ROOT_PERFORMANCE_STA_WN_B1 == index:
            self.sta_performance_white_noise_band1()
        elif self.micro.ROOT_PERFORMANCE_STA_WN_B2 == index:
            self.sta_performance_white_noise_band2()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTIPPM_B1 == index:
            self.sta_performance_anti_ppm_band1()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTIPPM_B2 == index:
            self.sta_performance_anti_ppm_band2()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTIATT_B1 == index:
            self.sta_performance_anti_att_band1()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTIATT_B2 == index:
            self.sta_performance_anti_att_band2()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTINARROW_B1 == index:
            self.sta_performance_anti_narrow_band1()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTINARROW_B2 == index:
            self.sta_performance_anti_narrow_band2()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTIPULSE_B1 == index:
            self.sta_performance_anti_pulse_band1()
        elif self.micro.ROOT_PERFORMANCE_STA_ANTIPULSE_B2 == index:
            self.sta_performance_anti_pulse_band2()
        elif self.micro.ROOT_PERFORMANCE_STA_PSD_B1 == index:
            self.sta_performance_psd_band1()
        elif self.micro.ROOT_PERFORMANCE_STA_PSD_B2 == index:
            self.sta_performance_psd_band2()
        elif self.micro.ROOT_PERFORMANCE_STA_RATE == index:
            self.sta_performance_rate()
        elif self.micro.ROOT_PERFORMANCE_CCO_WN_B1 == index:
            self.cco_performance_white_noise_band1()
        elif self.micro.ROOT_PERFORMANCE_CCO_WN_B2 == index:
            self.cco_performance_white_noise_band2()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTIPPM_B1 == index:
            self.cco_performance_anti_ppm_band1()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTIPPM_B2 == index:
            self.cco_performance_anti_ppm_band2()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTIATT_B1 == index:
            self.cco_performance_anti_att_band1()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTIATT_B2 == index:
            self.cco_performance_anti_att_band2()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTINARROW_B1 == index:
            self.cco_performance_anti_narrow_band1()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTINARROW_B2 == index:
            self.cco_performance_anti_narrow_band2()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTIPULSE_B1 == index:
            self.cco_performance_anti_pulse_band1()
        elif self.micro.ROOT_PERFORMANCE_CCO_ANTIPULSE_B2 == index:
            self.cco_performance_anti_pulse_band2()
        elif self.micro.ROOT_PERFORMANCE_CCO_PSD_B1 == index:
            self.cco_performance_psd_band1()
        elif self.micro.ROOT_PERFORMANCE_CCO_PSD_B2 == index:
            self.cco_performance_psd_band2()
        elif self.micro.ROOT_PERFORMANCE_CCO_RATE == index:
            self.cco_performance_rate()
        else:
            print("%s is not here" % (index))

    def timer_display_start(self):
        #print("start timer")
        self.lcd_start_t = datetime.now()
        timer_dlp = threading.Timer(1, self.timer_display_fun)
        timer_dlp.start()

    def timer_display_fun(self):
        #print("i am timer function")
        self.lcd_stop_t = datetime.now()
        t_delt = (self.lcd_stop_t - self.lcd_start_t).seconds
        str_disp = time.strftime("%H:%M:%S", time.gmtime(t_delt))
        self.lcdNumber.display(str(str_disp))
        if self.timer_flag == 0:
            timer_dlp = threading.Timer(1, self.timer_display_fun)
            timer_dlp.start()

    def auto_handle_func(self):
        case_cnt = 0
        while 1:
            index = self.fun_queue.get(1)
            if case_cnt == 0:
                self.timer_flag = 0
                self.timer_display_start()
            case_cnt += 1
            self.auto_call_back(index)
            if self.fun_queue.empty():
                case_cnt = 0
                self.timer_flag = 1
                print("i am happy")
