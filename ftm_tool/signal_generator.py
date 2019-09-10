#coding=utf-8

import visa
import fileinput
import configparser
import codecs
import hplc_cert
import serial
import serial.tools.list_ports

'''
narrow
频段0：（1MHz，-20dBm）、（8MHz，-30dBm）、（15MHz，-20dBm）
频段1：（1MHz，-20dBm）、（3MHz，-30dBm）、（6MHz，-30dBm）
频段1：（0.5MHz，-20dBm）、（2MHz，-30dBm）、（5MHz，-30dBm）
'''

class NARROW_MARCO:
    # band0
    NARROW_8M = 8
    NARROW_15M = 15
    # band1
    NARROW_1M = 1
    NARROW_3M = 3
    NARROW_6M = 6
    # band2
    NARROW_500K = 500
    NARROW_2M = 2
    NARROW_5M = 5

class signal_generator:

    def __init__(self, record_log):
        self.rm = visa.ResourceManager()
        self.inst = None
        self.record_log = record_log
        self.att_control_ser = serial.Serial()

    def open_signal_generator(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"

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
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, name)

    # white noise
    def sg_set_white_noise(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        white_noise_cfg = ''
        if config_tmp.has_option("signal_generator", "white_noise"):
            white_noise_cfg = config_tmp.get("signal_generator", "white_noise")

        self.inst.write(":SOUR1:APPL:NOISE " + white_noise_cfg)
        self.inst.write(":SOUR1:APPL?")
        noise_cfg = self.inst.read()
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, noise_cfg)
        # output
        self.inst.write(":OUTPut:STATe ON")

    # pulse
    def sg_set_pulse(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

        pulse_cfg = ''
        if config_tmp.has_option("signal_generator", "pulse_cfg"):
            pulse_cfg = config_tmp.get("signal_generator", "pulse_cfg")

        self.inst.write(":SOUR1:APPL:PULS " + pulse_cfg)
        self.inst.write(":SOUR1:APPL?")
        noise_cfg = 'pulse config:' + self.inst.read()
        print(noise_cfg)
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, noise_cfg)

        pulse_width = ''
        if config_tmp.has_option("signal_generator", "pulse_width"):
            pulse_width = config_tmp.get("signal_generator", "pulse_width")

        # self.inst.write(":SOUR1:FUNC:PULS:WIDT 0.000001")
        self.inst.write(":SOUR1:FUNC:PULS:WIDT " + pulse_width)
        self.inst.write(":SOUR1:FUNC:PULS:WIDT?")
        width = 'pulse width:' + self.inst.read()
        print(width)
        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, width)
        # output
        self.inst.write(":OUTPut:STATe ON")

    # spur
    def sg_set_sin(self, int_value):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")
        # band1
        if int_value == NARROW_MARCO.NARROW_1M:
            sin_cfg_1M = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_1M"):
                sin_cfg_1M = config_tmp.get("signal_generator", "sin_cfg_1M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_1M)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 1M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(hplc_cert.debug_leave.LOG_DEBUG, sin_cfg)

        elif int_value == NARROW_MARCO.NARROW_3M:
            sin_cfg_3M = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_3M"):
                sin_cfg_3M = config_tmp.get("signal_generator", "sin_cfg_3M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_3M)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 3M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(hplc_cert.debug_leave.LOG_DEBUG, sin_cfg)
        elif int_value == NARROW_MARCO.NARROW_6M:
            sin_cfg_6M = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_6M"):
                sin_cfg_6M = config_tmp.get("signal_generator", "sin_cfg_6M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_6M)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 6M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(hplc_cert.debug_leave.LOG_DEBUG, sin_cfg)
        # band2
        elif int_value == NARROW_MARCO.NARROW_500K:
            sin_cfg_500k = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_500k"):
                sin_cfg_500k = config_tmp.get("signal_generator", "sin_cfg_500k")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_500k)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 500k:' + self.inst.read()
            print(sin_cfg)
            self.record_log(hplc_cert.debug_leave.LOG_DEBUG, sin_cfg)
        elif int_value == NARROW_MARCO.NARROW_2M:
            sin_cfg_2M = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_2M"):
                sin_cfg_2M = config_tmp.get("signal_generator", "sin_cfg_2M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_2M)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 2M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(hplc_cert.debug_leave.LOG_DEBUG, sin_cfg)
        elif int_value == NARROW_MARCO.NARROW_5M:
            sin_cfg_5M = ''
            if config_tmp.has_option("signal_generator", "sin_cfg_5M"):
                sin_cfg_5M = config_tmp.get("signal_generator", "sin_cfg_5M")

            self.inst.write(":SOUR1:APPL:SIN " + sin_cfg_5M)
            self.inst.write(":SOUR1:APPL?")
            sin_cfg = 'sin config 5M:' + self.inst.read()
            print(sin_cfg)
            self.record_log(hplc_cert.debug_leave.LOG_DEBUG, sin_cfg)
        else:
            log_i = "this narrow is not support:%d" % int_value
            print(log_i)
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, log_i)

    def att_get_init_config(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config_tmp.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")
        # line att
        line_att = 0
        if config_tmp.has_option("att_config", "line_att"):
            line_att = int(config_tmp.get("att_config", "line_att"))

        # success rate
        att_success_rate = 90
        if config_tmp.has_option("att_config", "att_success_rate"):
            att_success_rate = int(config_tmp.get("att_config", "att_success_rate"))

        # pass threshold
        att_pass_threshold = 85
        if config_tmp.has_option("att_config", "att_pass_threshold"):
            att_pass_threshold = int(config_tmp.get("att_config", "att_pass_threshold"))

        return [line_att, att_success_rate, att_pass_threshold]

    def att_control_ser_open(self):
        # config
        config_tmp = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
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

        self.record_log(hplc_cert.debug_leave.LOG_DEBUG, 'att control serial config ' + self.att_control_ser.port +
                        ' %s' % self.att_control_ser.baudrate + ' %s' % self.att_control_ser.bytesize +
                        ' %s' % self.att_control_ser.stopbits + ' ' + self.att_control_ser.parity)

        try:
            self.att_control_ser.open()
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "att control serial open successed!")
        except:
            self.record_log(hplc_cert.debug_leave.LOG_ERROR, "程控衰减器 串口不能被打开！")
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


