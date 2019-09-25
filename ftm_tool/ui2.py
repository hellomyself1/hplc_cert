# -*- coding: utf-8 -*-
import sys
import os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
import queue
from macro_const import all_cert_case_value, DictCommandInfo
import excel

class treeWidget_class:
    def __init__(self, treeWidget, tableWidget, record_log):
        super(treeWidget_class, self).__init__()
        self.record_log = record_log

        self.member = all_cert_case_value()
        self.intiUI(treeWidget, tableWidget)

    def intiUI(self, treeWidget, tableWidget):
        # 初始化tablewidget模块
        self.tw = tableWidget_class(tableWidget)

        self.treeWidget = treeWidget
        # 设置列数
        self.treeWidget.setColumnCount(1)
        # 设置树形控件头部的标题
        self.treeWidget.setHeaderLabels(['测试用例'])
        self.treeWidget.setColumnWidth(0, 120)
        # 设置根节点
        self.AllTestCase = QTreeWidgetItem(self.treeWidget)
        self.AllTestCase.setText(0, '测试项')
        self.AllTestCase.setCheckState(0, Qt.Unchecked)

        #  初始化数组
        self.tree_list = [0 for i in range(self.member.TREE_MAX)]
        #print(self.tree_list)

        for value in DictCommandInfo.keys():
            #print(value)
            #print(DictCommandInfo[value])
            if DictCommandInfo[value] == self.member.ROOT_PROTOCON:
                self.tree_list[self.member.ROOT_PROTOCON] = QTreeWidgetItem(self.AllTestCase)
                self.tree_list[self.member.ROOT_PROTOCON].setText(0, value)
                self.tree_list[self.member.ROOT_PROTOCON].setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] == all_cert_case_value.ROOT_PROTOCON_STA_CHILD:
                self.tree_list[DictCommandInfo[value]] = QTreeWidgetItem(self.tree_list[self.member.ROOT_PROTOCON])
                self.tree_list[DictCommandInfo[value]].setText(0, value)
                self.tree_list[DictCommandInfo[value]].setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] < self.member.ROOT_PROTOCON_STA_MAX and DictCommandInfo[value] > self.member.ROOT_PROTOCON_STA_CHILD:
                self.tree_list[DictCommandInfo[value]] = QTreeWidgetItem(self.tree_list[self.member.ROOT_PROTOCON_STA_CHILD])
                self.tree_list[DictCommandInfo[value]].setText(0, value)
                self.tree_list[DictCommandInfo[value]].setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] == all_cert_case_value.ROOT_PROTOCON_CCO_CHILD:
                self.tree_list[DictCommandInfo[value]] = QTreeWidgetItem(self.tree_list[self.member.ROOT_PROTOCON])
                self.tree_list[DictCommandInfo[value]].setText(0, value)
                self.tree_list[DictCommandInfo[value]].setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] < self.member.ROOT_PROTOCON_CCO_MAX and DictCommandInfo[value] > self.member.ROOT_PROTOCON_CCO_CHILD:
                self.tree_list[DictCommandInfo[value]] = QTreeWidgetItem(self.tree_list[self.member.ROOT_PROTOCON_CCO_CHILD])
                self.tree_list[DictCommandInfo[value]].setText(0, value)
                self.tree_list[DictCommandInfo[value]].setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] == all_cert_case_value.ROOT_PERFORMANCE_CHILD:
                self.tree_list[DictCommandInfo[value]] = QTreeWidgetItem(self.AllTestCase)
                self.tree_list[DictCommandInfo[value]].setText(0, value)
                self.tree_list[DictCommandInfo[value]].setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] < self.member.ROOT_PERFORMANCE_MAX and DictCommandInfo[value] > self.member.ROOT_PERFORMANCE_CHILD:
                self.tree_list[DictCommandInfo[value]] = QTreeWidgetItem(self.tree_list[self.member.ROOT_PERFORMANCE_CHILD])
                self.tree_list[DictCommandInfo[value]].setText(0, value)
                self.tree_list[DictCommandInfo[value]].setCheckState(0, Qt.Unchecked)

        # 节点全部展开
        self.treeWidget.expandAll()

        #self.treeWidget.itemClicked.connect(self.handleChanged)
        self.treeWidget.itemChanged.connect(self.handleChanged)

    def handleChanged(self, item, column):
        count = item.childCount()
        if item.checkState(column) == Qt.Checked:
            if count == 0:
                self.tw.table_append(item.text(0))
            for f in range(count):
                if item.child(f).checkState(0) != Qt.Checked:
                    item.child(f).setCheckState(0, Qt.Checked)
                    self.tw.table_append(item.child(f).text(0))

        if item.checkState(column) == Qt.Unchecked:
            if count == 0:
                self.tw.table_remove(item.text(0))
            for f in range(count):
                if item.child(f).checkState != Qt.Unchecked:
                    item.child(f).setCheckState(0, Qt.Unchecked)
                    self.tw.table_remove(item.text(0))

class tableWidget_class(QWidget):
    signal2 = pyqtSignal(list)

    def __init__(self, tableWidget):
        super(tableWidget_class, self).__init__()
        self.initUI(tableWidget)
        self.twrowcnt = 0
        self.handle_queue = queue.Queue(maxsize=100)
        # 连接发射函数
        self.signal2.connect(self.table_set_item)
        # excel
        self.excel = excel.ExcelTool()

    def signal2emit(self, list):
        self.signal2.emit(list)  # 朝connect的函数发射一个tuple

    def initUI(self, tableWidget):
        layout = QHBoxLayout()

        self.tableWidget = tableWidget
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        # 字体颜色（红色）
        #self.tableWidget.item(1, 0).setForeground(QColor("red"))
        #self.tableWidget.item(1, 1).setBackground(QColor("red"))
        #newItem = QTableWidgetItem('hellomsss')
        #self.tableWidget.setItem(1, 0, newItem)
        #print(self.tableWidget.item(1, 0).text())
        #self.tableWidget.item(1, 0).setForeground(QColor("black"))
        #self.tableWidget.item(1, 0).setBackground(QColor("red"))

        # 设置头label
        self.tableWidget.setHorizontalHeaderLabels(['测试用例', '执行时间', '结果', '备注'])

        # 设置列宽度
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 130)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 400)

        # 优化3 将表格变为禁止编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 优化 4 设置表格整行选中
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.tableWidget)

        #self.setLayout(layout)

    def table_append(self, str):
        if str == 'CCO测试项' or str == 'STA测试项' or str == '协议一致性' \
                or str == '通信性能测试':
            return
        item = self.tableWidget.findItems(str, Qt.MatchExactly)
        if not item:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            newItem = QTableWidgetItem(str)
            self.tableWidget.setItem(row, 0, newItem)

    def table_remove(self, str):
        item = self.tableWidget.findItems(str, Qt.MatchExactly)
        if item:
            row = item[0].row()
            self.tableWidget.removeRow(row)

    def table_statistics(self):
        rowmax = self.tableWidget.rowCount()
        # set excel name
        self.excel.exceltool()

        for index in range(rowmax):
            item = self.tableWidget.item(index, 0).text()
            self.handle_queue.put(DictCommandInfo[item])
            self.signal2emit([item, '', 'white', ''])
        if self.handle_queue.empty():
            print("this is grade")

    def table_get_row(self, str):
        item = self.tableWidget.findItems(str, Qt.MatchExactly)
        if not item:
            row = self.tableWidget.rowCount()
            return row

    def table_set_item(self, list):
        f_str = list[0]
        exe_time = list[1]
        result = list[2]
        remarks = list[3]
        item = self.tableWidget.findItems(f_str, Qt.MatchExactly)
        #print("ttttttttttt")
        bcolor = ''
        if item:
            if result == 'pass':
                bcolor = 'green'
            elif result == 'white':
                bcolor = 'white'
                result = ''
            else:
                bcolor = 'red'
            row = item[0].row()
            for idx in range(4):
                if idx == 0:
                    newItem = QTableWidgetItem(f_str)
                    self.tableWidget.setItem(row, idx, newItem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
                elif idx == 1:
                    newItem = QTableWidgetItem(exe_time)
                    self.tableWidget.setItem(row, idx, newItem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
                elif idx == 2:
                    newItem = QTableWidgetItem(result)
                    self.tableWidget.setItem(row, idx, newItem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
                elif idx == 3:
                    newItem = QTableWidgetItem(remarks)
                    self.tableWidget.setItem(row, idx, newItem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
        self.excel.excel_write(list)
