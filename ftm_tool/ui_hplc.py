# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_hplc.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1293, 923)
        self.smoe_test = QtWidgets.QPushButton(Form)
        self.smoe_test.setGeometry(QtCore.QRect(330, 10, 75, 23))
        self.smoe_test.setObjectName("smoe_test")
        self.treeWidget = QtWidgets.QTreeWidget(Form)
        self.treeWidget.setGeometry(QtCore.QRect(10, 80, 349, 571))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.tableWidget = QtWidgets.QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(360, 80, 921, 571))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.pushButton_start = QtWidgets.QPushButton(Form)
        self.pushButton_start.setGeometry(QtCore.QRect(30, 40, 111, 31))
        self.pushButton_start.setObjectName("pushButton_start")
        self.open_button = QtWidgets.QPushButton(Form)
        self.open_button.setGeometry(QtCore.QRect(20, 10, 145, 23))
        self.open_button.setObjectName("open_button")
        self.close_button = QtWidgets.QPushButton(Form)
        self.close_button.setGeometry(QtCore.QRect(170, 10, 145, 23))
        self.close_button.setObjectName("close_button")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(10, 660, 1271, 251))
        self.textBrowser.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.textBrowser.setFocusPolicy(QtCore.Qt.NoFocus)
        self.textBrowser.setObjectName("textBrowser")
        self.pbar = QtWidgets.QProgressBar(Form)
        self.pbar.setGeometry(QtCore.QRect(580, 42, 551, 31))
        self.pbar.setProperty("value", 24)
        self.pbar.setTextVisible(True)
        self.pbar.setObjectName("pbar")
        self.lcdNumber = QtWidgets.QLCDNumber(Form)
        self.lcdNumber.setGeometry(QtCore.QRect(350, 42, 151, 31))
        self.lcdNumber.setObjectName("lcdNumber")
        self.smoe_test.raise_()
        self.tableWidget.raise_()
        self.treeWidget.raise_()
        self.pushButton_start.raise_()
        self.open_button.raise_()
        self.close_button.raise_()
        self.textBrowser.raise_()
        self.pbar.raise_()
        self.lcdNumber.raise_()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.smoe_test.setText(_translate("Form", "some_test"))
        self.pushButton_start.setText(_translate("Form", "Start"))
        self.open_button.setText(_translate("Form", "初始化设备"))
        self.close_button.setText(_translate("Form", "冻结设备"))
        self.pbar.setFormat(_translate("Form", "%p%"))
