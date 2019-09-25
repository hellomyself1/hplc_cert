import sys
import os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTextEdit, QLCDNumber
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSignal
from ui_hplc import Ui_Form
import ftm_cmd
import ui2
import configparser
import ftm_auto
from datetime import *
import time
import logging
import fileinput
import re
import binascii
import struct
from PyQt5.QtCore import QTimer
import excel

class debug_leave:
    LOG_DEBUG = 1
    LOG_INFO = 2
    LOG_WARNING = 3
    LOG_ERROR = 4
    LOG_CRITICAL = 5


class Pyqt5_Serial(QtWidgets.QWidget, Ui_Form):
    signal_pbar = pyqtSignal(int)
    signal_txt = pyqtSignal(str)
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.initlogging()
        self.setWindowTitle("HPLC 测试系统")
        self.ser = serial.Serial()

        self.tree = ui2.treeWidget_class(self.treeWidget, self.tableWidget, self.record_log)
        self.ft = ftm_cmd.FtmTool(self.record_log)
        self.fa = ftm_auto.FtmAuto(self.tree.tw, self.signal_txt_emit, self.dut_switch_send_cmd,
                                      self.ftm_switch_send_cmd, self.ft, self.record_log,
                                      self.lcdNumber, self.signal_pbar_emit)
        self.dut_switch_ser = serial.Serial()
        self.ftm_switch_ser = serial.Serial()

    def init(self):

        self.lcdNumber.setDigitCount(8)
        self.lcdNumber.setSegmentStyle(QLCDNumber.Flat)
        self.lcdNumber.display('00:00:00')
        self.lcdNumber.setStyleSheet("border: 0.1px solid black; color: green; background: silver;")
        self.pbar.setValue(0)

        # open connect function
        self.open_button.clicked.connect(self.port_open)

        # close
        self.close_button.clicked.connect(self.port_close)

        self.smoe_test.clicked.connect(self.some_test_func)

        self.pushButton_start.clicked.connect(self.test_start)
        self.pushButton_stop.clicked.connect(self.test_stop)

        # connect function
        # pbar
        self.signal_pbar.connect(self.pbar_set)
        # txt
        self.signal_txt.connect(self.log_display)

        # config
        self.config = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            self.config.read(config_file, encoding="utf-8")
        except Exception:
            print("file open fail")

    def signal_pbar_emit(self, value):
        self.signal_pbar.emit(value)

    def signal_txt_emit(self, str):
        self.signal_txt.emit(str)

    def initlogging(self):
        file_name = os.path.split(__file__)[-1].split(".")[0]
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        logging.basicConfig(filename='./LOG/' + file_name + file_time  + '.log',
                            format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                            level=logging.DEBUG,
                            filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')

    # record log
    def record_log(self, leave, str_info):
        if leave == debug_leave.LOG_DEBUG:
            logging.debug(str_info)
        elif leave == debug_leave.LOG_INFO:
            logging.info(str_info)
        elif leave == debug_leave.LOG_WARNING:
            logging.warning(str_info)
        elif leave == debug_leave.LOG_ERROR:
            logging.error(str_info)
        elif leave == debug_leave.LOG_CRITICAL:
            logging.critical(str_info)
        else:
            logging.error("this leave %d do not support" % leave)

    def cli_serial_port_open(self):

        if self.config.has_option("cli_config", "s1_serial_port"):
            self.ser.port = self.config.get("cli_config", "s1_serial_port")
        if self.config.has_option("cli_config", "s1_baudrate"):
            self.ser.baudrate = int(self.config.get("cli_config", "s1_baudrate"))
        if self.config.has_option("cli_config", "s1_bytesize"):
            self.ser.bytesize = int(self.config.get("cli_config", "s1_bytesize"))
        if self.config.has_option("cli_config", "s1_stopbits"):
            self.ser.stopbits = int(self.config.get("cli_config", "s1_stopbits"))
        if self.config.has_option("cli_config", "s1_parity"):
            self.ser.parity = self.config.get("cli_config", "s1_parity")

        self.record_log(debug_leave.LOG_DEBUG, 'cli serial config ' + self.ser.port + ' %s' % self.ser.baudrate +
                        ' %s' % self.ser.bytesize + ' %s' % self.ser.stopbits + ' ' + self.ser.parity)

        try:
            self.ser.open()
            self.record_log(debug_leave.LOG_ERROR, "cli serial open successed!")
        except:
            QMessageBox.critical(self, "Port Error", "cli串口不能被打开！")
            self.record_log(debug_leave.LOG_ERROR, "cli串口不能被打开！")
            return None

        if self.ser.isOpen():
            self.record_log(debug_leave.LOG_DEBUG, "cli serial open successed")
            # open rx thread
            self.ft.start_thread(self.ser)
            # set tx data callback
            self.ft.ftm_tx_data_fun(self.data_send_cmd)

            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)

    def dut_power_on_serial_port_open(self):
        if self.config.has_option("dut_switch_config", "s3_serial_port"):
            self.dut_switch_ser.port = self.config.get("dut_switch_config", "s3_serial_port")
        if self.config.has_option("dut_switch_config", "s3_baudrate"):
            self.dut_switch_ser.baudrate = int(self.config.get("dut_switch_config", "s3_baudrate"))
        if self.config.has_option("dut_switch_config", "s3_bytesize"):
            self.dut_switch_ser.bytesize = int(self.config.get("dut_switch_config", "s3_bytesize"))
        if self.config.has_option("dut_switch_config", "s3_stopbits"):
            self.dut_switch_ser.stopbits = int(self.config.get("dut_switch_config", "s3_stopbits"))
        if self.config.has_option("dut_switch_config", "s3_parity"):
            self.dut_switch_ser.parity = self.config.get("dut_switch_config", "s3_parity")

        self.record_log(debug_leave.LOG_DEBUG, 'dut power on serial config ' + self.dut_switch_ser.port +
                        ' %s' % self.dut_switch_ser.baudrate + ' %s' % self.dut_switch_ser.bytesize +
                        ' %s' % self.dut_switch_ser.stopbits + ' ' + self.dut_switch_ser.parity)

        if self.dut_switch_ser.isOpen():
            self.record_log(debug_leave.LOG_DEBUG, "dut power on serial open successed")

        try:
            self.dut_switch_ser.open()
            self.record_log(debug_leave.LOG_ERROR, "dut power on serial open successed!")
        except:
            QMessageBox.critical(self, "Port Error", "dut power on串口不能被打开！")
            self.record_log(debug_leave.LOG_ERROR, "dut power on 串口不能被打开！")
            return None

    def ftm_power_on_serial_port_open(self):
        if self.config.has_option("ftm_switch_config", "s6_serial_port"):
            self.ftm_switch_ser.port = self.config.get("ftm_switch_config", "s6_serial_port")
        if self.config.has_option("ftm_switch_config", "s6_baudrate"):
            self.ftm_switch_ser.baudrate = int(self.config.get("ftm_switch_config", "s6_baudrate"))
        if self.config.has_option("ftm_switch_config", "s6_bytesize"):
            self.ftm_switch_ser.bytesize = int(self.config.get("ftm_switch_config", "s6_bytesize"))
        if self.config.has_option("ftm_switch_config", "s6_stopbits"):
            self.ftm_switch_ser.stopbits = int(self.config.get("ftm_switch_config", "s6_stopbits"))
        if self.config.has_option("ftm_switch_config", "s6_parity"):
            self.ftm_switch_ser.parity = self.config.get("ftm_switch_config", "s6_parity")

        self.record_log(debug_leave.LOG_DEBUG, 'ftm power on serial config ' + self.ftm_switch_ser.port +
                        ' %s' % self.ftm_switch_ser.baudrate + ' %s' % self.ftm_switch_ser.bytesize +
                        ' %s' % self.ftm_switch_ser.stopbits + ' ' + self.ftm_switch_ser.parity)

        if self.ftm_switch_ser.isOpen():
            self.record_log(debug_leave.LOG_DEBUG, "ftm power on serial open successed")

        try:
            self.ftm_switch_ser.open()
            self.record_log(debug_leave.LOG_ERROR, "ftm power on serial open successed!")
        except:
            QMessageBox.critical(self, "Port Error", "ftm power on串口不能被打开！")
            self.record_log(debug_leave.LOG_ERROR, "ftm power on 串口不能被打开！")
            return None

    # open serial
    def port_open(self):
        # cli serial port open
        self.cli_serial_port_open()
        # dut power on serial port open
        self.dut_power_on_serial_port_open()
        # ftm power on ftm port open
        self.ftm_power_on_serial_port_open()
        # tt serial port open
        self.fa.tt_ser_open()
        # lp serial port open
        self.fa.lp_ser_open()
        # att control serial port open
        self.fa.sig_gen.att_control_ser_open()
        # open signal generator
        self.fa.sig_gen.open_signal_generator()

    # close serial
    def port_close(self):
        try:
            self.ft.stop_thread()
            self.fa.stop_thread()
            self.ser.close()
            self.dut_switch_ser.close()
            self.ftm_switch_ser.close()
            self.fa.tt_ser.close()
            self.fa.att_control_ser.close()
        except:
            self.record_log(debug_leave.LOG_ERROR, "关闭串口出错！")
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)

    # dut power on/down cmd
    def dut_switch_send_cmd(self, str_cmd):
        if self.dut_switch_ser.isOpen():
            input_s = str_cmd
            if input_s != "":
                input_s = input_s.strip()
                send_list = []
                while input_s != '':
                    try:
                        num = int(input_s[0:2], 16)
                    except ValueError:
                        QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                        return None
                    input_s = input_s[2:].strip()
                    send_list.append(num)
                input_s = bytes(send_list)

            self.dut_switch_ser.write(input_s)
        else:
            pass

    # ftm power on/down cmd
    def ftm_switch_send_cmd(self, str_cmd):
        if self.ftm_switch_ser.isOpen():
            input_s = str_cmd
            if input_s != "":
                input_s = input_s.strip()
                send_list = []
                while input_s != '':
                    try:
                        num = int(input_s[0:2], 16)
                    except ValueError:
                        QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                        return None
                    input_s = input_s[2:].strip()
                    send_list.append(num)
                input_s = bytes(send_list)

            self.ftm_switch_ser.write(input_s)
        else:
            pass

    # send data
    def data_send_cmd(self, str_cmd):
        if self.ser.isOpen():
            input_s = str_cmd
            if input_s != "":
                input_s = input_s.strip()
                send_list = []
                while input_s != '':
                    try:
                        num = int(input_s[0:2], 16)
                    except ValueError:
                        QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                        return None
                    input_s = input_s[2:].strip()
                    send_list.append(num)
                input_s = bytes(send_list)

            self.ser.write(input_s)
        else:
            pass

    # some_test
    def some_test_func(self):
        self.excel = excel.ExcelTool()
        self.excel.excel_init()
        list = ["TMI遍历 STA band3", 'PASS', 'great']
        self.excel.excel_write(list)
        ''''
        self.timer = QTimer(self)  # init timer
        self.timer.timeout.connect(self.fa.test_case)
        self.timer.start(30*1000)  # start timer
        '''

    # read file test
    def readfile_test(self):
        config = configparser.ConfigParser()
        config_file = ".\config\cert_config.ini"
        try:
            config.read(config_file, encoding="utf-8")
        except Exception:
            print("error")
        print(config.sections())
        if config.has_option("cli_config", "s1_serial_port"):
            print(config.get("cli_config", "s1_serial_port"))
        if config.has_option("tt_config", "s2_serial_port"):
            print(config.get("tt_config", "s2_serial_port"))

    def test_start(self):
        self.tree.tw.table_statistics()

    def test_stop(self):
        self.fa.sig_gen.close_signal_generator()
        self.fa.auto_close()

    def log_display(self, str):
        # get test cursor
        textCursor = self.textBrowser.textCursor()
        # move cursor to end
        self.textBrowser.moveCursor(textCursor.End)

        self.textBrowser.insertPlainText(str)

    def pbar_set(self, int):
        self.pbar.setValue(int)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
