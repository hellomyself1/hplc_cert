# -*- coding: utf-8 -*-

import visa
import configparser
import serial
import serial.tools.list_ports
from macro_const import DebugLeave, NarrowMarco


class SignalGenerator:

    def __init__(self, record_log):
        self.rm = None
        self.inst = None
        self.record_log = record_log
        self.att_control_ser = serial.Serial()

    def open_signal_generator(self):
        # noinspection PyBroadException
        try:
            self.rm = visa.ResourceManager()
        except Exception:
            return

        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\\config\\cert_config.ini"
        # noinspection PyBroadException
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        sg_name = ''
        if config_tmp.has_option("signal_generator", "sg_name"):
            sg_name = str(config_tmp.get("signal_generator", "sg_name"))
        print(sg_name)
        # 'USB0::0x1AB1::0x0642::DG1ZA202102461::INSTR'
        self.inst = self.rm.open_resource(sg_name)
        # check signal generator
        self.inst.write("*IDN?")
        name = self.inst.read()
        self.record_log(DebugLeave.LOG_DEBUG, name)
        # 设置输出阻抗为50Ω
        self.inst.write(":OUTP1:LOAD 50")

    def close_signal_generator(self):
        # noinspection PyBroadException
        try:
            self.inst.write(":OUTPut1:STATe OFF")
        except Exception:
            pass

    # white noise
    def sg_set_white_noise(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\\config\\cert_config.ini"
        # noinspection PyBroadException
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        white_noise_cfg = ''
        if config_tmp.has_option("signal_generator", "white_noise"):
            white_noise_cfg = config_tmp.get("signal_generator", "white_noise")
        print(white_noise_cfg)
        # set channel 1, nuit dbm
        self.inst.write("SOUR1:VOLT:UNIT DBM")
        self.inst.write(":SOUR1:APPL:NOISE " + white_noise_cfg)
        self.inst.write(":SOUR1:APPL?")
        noise_cfg = self.inst.read()
        self.record_log(DebugLeave.LOG_DEBUG, noise_cfg)
        # output
        self.inst.write(":OUTPut1:STATe ON")

    # pulse
    def sg_set_pulse(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\\config\\cert_config.ini"
        # noinspection PyBroadException
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        pulse_cfg = ''
        if config_tmp.has_option("signal_generator", "pulse_cfg"):
            pulse_cfg = config_tmp.get("signal_generator", "pulse_cfg")

        # set channel 1, nuit dbm
        self.inst.write("SOUR1:VOLT:UNIT VPP")
        self.inst.write(":SOUR1:APPL:PULS " + pulse_cfg)
        self.inst.write(":SOUR1:APPL?")
        noise_cfg = 'pulse config:' + self.inst.read()

        self.record_log(DebugLeave.LOG_DEBUG, noise_cfg)

        pulse_width = ''
        if config_tmp.has_option("signal_generator", "pulse_width"):
            pulse_width = config_tmp.get("signal_generator", "pulse_width")

        # self.inst.write(":SOUR1:FUNC:PULS:WIDT 0.000001")
        self.inst.write(":SOUR1:FUNC:PULS:WIDT " + pulse_width)
        self.inst.write(":SOUR1:FUNC:PULS:WIDT?")
        width = 'pulse width:' + self.inst.read()
        print(width)
        self.record_log(DebugLeave.LOG_DEBUG, width)
        # output
        self.inst.write(":OUTPut1:STATe ON")

    # spur
    def sg_set_sin(self, int_value):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\\config\\cert_config.ini"
        # noinspection PyBroadException
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")
        # set channel 1, nuit dbm
        self.inst.write("SOUR1:VOLT:UNIT DBM")
        # band1
        if int_value == NarrowMarco.NARROW_1M:
            sin_cfg_1m = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_1M"):
                sin_cfg_1m = config_tmp.get("signal_generator", "sin_cfg_1M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_1m)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 1M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(DebugLeave.LOG_DEBUG, sin_cfg)
            # output
            self.inst.write(":OUTPut1:STATe ON")

        elif int_value == NarrowMarco.NARROW_3M:
            sin_cfg_3m = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_3M"):
                sin_cfg_3m = config_tmp.get("signal_generator", "sin_cfg_3M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_3m)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 3M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(DebugLeave.LOG_DEBUG, sin_cfg)
            # output
            self.inst.write(":OUTPut1:STATe ON")
        elif int_value == NarrowMarco.NARROW_6M:
            sin_cfg_6m = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_6M"):
                sin_cfg_6m = config_tmp.get("signal_generator", "sin_cfg_6M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_6m)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 6M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(DebugLeave.LOG_DEBUG, sin_cfg)
            # output
            self.inst.write(":OUTPut1:STATe ON")
        # band2
        elif int_value == NarrowMarco.NARROW_500K:
            sin_cfg_500k = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_500k"):
                sin_cfg_500k = config_tmp.get("signal_generator", "sin_cfg_500k")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_500k)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 500k:' + self.inst.read()
            print(sin_cfg)
            self.record_log(DebugLeave.LOG_DEBUG, sin_cfg)
            # output
            self.inst.write(":OUTPut1:STATe ON")
        elif int_value == NarrowMarco.NARROW_2M:
            sin_cfg_2m = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_2M"):
                sin_cfg_2m = config_tmp.get("signal_generator", "sin_cfg_2M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_2m)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 2M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(DebugLeave.LOG_DEBUG, sin_cfg)
            # output
            self.inst.write(":OUTPut1:STATe ON")
        elif int_value == NarrowMarco.NARROW_5M:
            sin_cfg_5m = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_5M"):
                sin_cfg_5m = config_tmp.get("signal_generator", "sin_cfg_5M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_5m)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 5M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(DebugLeave.LOG_DEBUG, sin_cfg)
            # output
            self.inst.write(":OUTPut1:STATe ON")
        else:
            log_i = "this narrow is not support:%d" % int_value
            print(log_i)
            self.record_log(DebugLeave.LOG_ERROR, log_i)

    def att_get_init_config(self, test_id):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\\config\\cert_config.ini"
        # noinspection PyBroadException
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")
        if test_id == 0:
            section = "att_config"
        else:
            section = "write_pulse_spur_config"
        # line att
        line_att = 0
        if config_tmp.has_option(section, "line_att"):
            line_att = int(config_tmp.get(section, "line_att"))

        # success rate
        att_success_rate = 90
        if config_tmp.has_option(section, "att_success_rate"):
            att_success_rate = int(config_tmp.get(section, "att_success_rate"))

        # pass threshold
        att_pass_threshold = 85
        if config_tmp.has_option(section, "att_pass_threshold"):
            att_pass_threshold = int(config_tmp.get(section, "att_pass_threshold"))
        print(line_att)
        print(att_success_rate)
        print(att_pass_threshold)
        return [line_att, att_success_rate, att_pass_threshold]

    def att_control_ser_open(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\\config\\cert_config.ini"
        # noinspection PyBroadException
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        if config_tmp.has_option("att_control_config", "s4_serial_port"):
            self.att_control_ser.port = config_tmp.get("att_control_config", "s4_serial_port")
        if config_tmp.has_option("att_control_config", "s4_baudrate"):
            self.att_control_ser.baudrate = int(config_tmp.get("att_control_config", "s4_baudrate"))
        if config_tmp.has_option("att_control_config", "s4_bytesize"):
            self.att_control_ser.bytesize = int(config_tmp.get("att_control_config", "s4_bytesize"))
        if config_tmp.has_option("att_control_config", "s4_stopbits"):
            self.att_control_ser.stopbits = int(config_tmp.get("att_control_config", "s4_stopbits"))
        if config_tmp.has_option("att_control_config", "s4_parity"):
            self.att_control_ser.parity = config_tmp.get("att_control_config", "s4_parity")

        self.record_log(DebugLeave.LOG_DEBUG, 'att control serial config ' + self.att_control_ser.port +
                        ' %s' % self.att_control_ser.baudrate + ' %s' % self.att_control_ser.bytesize +
                        ' %s' % self.att_control_ser.stopbits + ' ' + self.att_control_ser.parity)
        # noinspection PyBroadException
        try:
            self.att_control_ser.open()
            self.record_log(DebugLeave.LOG_ERROR, "att control serial open successed!")
        except Exception:
            self.record_log(DebugLeave.LOG_ERROR, "程控衰减器 串口不能被打开！")
            return None

    # send str
    def att_control_send_cmd(self, str_cmd):
        if self.att_control_ser.isOpen():
            input_s = str_cmd
            if input_s != "":
                # ascii发送
                input_s = (input_s + '\r\n').encode('utf-8')
            self.att_control_ser.write(input_s)
        else:
            pass

    def auto_set_att_control(self, att_value):
        str_set_cmd = 'SA1 %d' % att_value
        self.att_control_send_cmd(str_set_cmd)
        # TODO: need closed-loop test. read and check
