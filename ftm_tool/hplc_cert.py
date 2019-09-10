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
from ui_demo_1 import Ui_Form
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
        self.user = ftm_cmd.ftm_tool(self.record_log)
        self.auto = ftm_auto.ftm_auto(self.tree.tw, self.signal_txt_emit, self.switch_send_cmd,
                                      self.user, self.record_log,
                                      self.lcdNumber, self.signal_pbar_emit)
        self.switch_ser = serial.Serial()

    def init(self):

        self.lcdNumber.setDigitCount(8)
        self.lcdNumber.setSegmentStyle(QLCDNumber.Flat)
        self.lcdNumber.display('00:00:00')
        self.lcdNumber.setStyleSheet("border: 0.1px solid black; color: green; background: silver;")
        self.pbar.setValue(0)

        # 打开串口按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭串口按钮
        self.close_button.clicked.connect(self.port_close)

        self.hwq_cfg.clicked.connect(self.hwq_cfg_func)

        self.pushButton_start.clicked.connect(self.test_start)

        # 连接发射函数
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
            self.user.start_thread(self.ser)
            # set tx data callback
            self.user.ftm_tx_data_fun(self.data_send_cmd)

            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)

    def power_on_serial_port_open(self):
        if self.config.has_option("switch_config", "s3_serial_port"):
            self.switch_ser.port = self.config.get("switch_config", "s3_serial_port")
        if self.config.has_option("switch_config", "s3_baudrate"):
            self.switch_ser.baudrate = int(self.config.get("switch_config", "s3_baudrate"))
        if self.config.has_option("switch_config", "s3_bytesize"):
            self.switch_ser.bytesize = int(self.config.get("switch_config", "s3_bytesize"))
        if self.config.has_option("switch_config", "s3_stopbits"):
            self.switch_ser.stopbits = int(self.config.get("switch_config", "s3_stopbits"))
        if self.config.has_option("switch_config", "s3_parity"):
            self.switch_ser.parity = self.config.get("switch_config", "s3_parity")

        self.record_log(debug_leave.LOG_DEBUG, 'power on serial config ' + self.switch_ser.port +
                        ' %s' % self.switch_ser.baudrate + ' %s' % self.switch_ser.bytesize +
                        ' %s' % self.switch_ser.stopbits + ' ' + self.switch_ser.parity)

        if self.switch_ser.isOpen():
            self.record_log(debug_leave.LOG_DEBUG, "power on serial open successed")

        try:
            self.switch_ser.open()
            self.record_log(debug_leave.LOG_ERROR, "power on serial open successed!")
        except:
            QMessageBox.critical(self, "Port Error", "power on串口不能被打开！")
            self.record_log(debug_leave.LOG_ERROR, "power on 串口不能被打开！")
            return None

    # open serial
    def port_open(self):
        # cli serial port open
        self.cli_serial_port_open()
        # power on serial port open
        self.power_on_serial_port_open()
        # tt serial port open
        self.auto.tt_ser_open()
        # lp serial port open
        self.auto.lp_ser_open()
        # att control serial port open
        self.auto.sig_gen.att_control_ser_open()
        # open signal generator
        #self.auto.sig_gen.open_signal_generator()

    # 关闭串口
    def port_close(self):
        try:
            self.user.stop_thread()
            self.auto.stop_thread()
            self.ser.close()
            self.switch_ser.close()
            self.auto.tt_ser.close()
            self.auto.att_control_ser.close()
        except:
            self.record_log(debug_leave.LOG_ERROR, "关闭串口出错！")
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)

    # 上下电发送命令
    def switch_send_cmd(self, str_cmd):
        if self.switch_ser.isOpen():
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

            self.switch_ser.write(input_s)
        else:
            pass

    # 发送命令
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

    # hwq_cfg
    def hwq_cfg_func(self):
        #self.auto.auto_ftm_set_self_band(0, 0)
        #self.auto.auto_init_ftm(0, 0)
        #self.auto.auto_ftm_rx_config()
        self.auto.auto_ftm_tx_test_pkt(4)


        '''
        self.timer = QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.auto.test_case)  # 计时结束调用operate()方法
        self.timer.start(20*1000)  # 设置计时间隔并启动
        '''


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

    def log_display(self, str):
        # 获取到text光标
        textCursor = self.textBrowser.textCursor()
        # 滚动到底部
        self.textBrowser.moveCursor(textCursor.End)

        self.textBrowser.insertPlainText(str)

    def pbar_set(self, int):
        self.pbar.setValue(int)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())
