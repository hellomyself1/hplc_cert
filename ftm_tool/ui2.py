# -*- coding: utf-8 -*-

import sys
import os
'''
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
'''
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
import queue
from macro_const import AllCertCaseValue, DictCommandInfo
import excel


class TreeWidgetClass:
    def __init__(self, treewidget, tablewidget, record_log):
        super(TreeWidgetClass, self).__init__()
        self.record_log = record_log
        self.tw, self.treeWidget, self.AllTestCase = None, None, None

        self.intiui(treewidget, tablewidget)

    def intiui(self, treewidget, tablewidget):
        # 初始化tablewidget模块
        self.tw = TableWidgetClass(tablewidget)

        self.treeWidget = treewidget
        # 设置列数
        self.treeWidget.setColumnCount(1)
        # 设置树形控件头部的标题
        self.treeWidget.setHeaderLabels(['测试用例'])
        self.treeWidget.setColumnWidth(0, 120)
        # 设置根节点
        self.AllTestCase = QTreeWidgetItem(self.treeWidget)
        self.AllTestCase.setText(0, '测试项')
        self.AllTestCase.setCheckState(0, Qt.Unchecked)

        item_protocon, item_sta_father, item_cco_father, item_prerf_father = None, None, None, None

        for value in DictCommandInfo.keys():
            # print(value)
            # print(DictCommandInfo[value])
            if DictCommandInfo[value] == AllCertCaseValue.ROOT_PROTOCON:
                item_protocon = QTreeWidgetItem(self.AllTestCase)
                item_protocon.setText(0, value)
                item_protocon.setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] == AllCertCaseValue.ROOT_PROTOCON_STA_CHILD:
                item_sta_father = QTreeWidgetItem(item_protocon)
                item_sta_father.setText(0, value)
                item_sta_father.setCheckState(0, Qt.Unchecked)
            elif AllCertCaseValue.ROOT_PROTOCON_STA_CHILD < DictCommandInfo[value] < \
                    AllCertCaseValue.ROOT_PROTOCON_STA_MAX:
                item_sta_child = QTreeWidgetItem(item_sta_father)
                item_sta_child.setText(0, value)
                item_sta_child.setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] == AllCertCaseValue.ROOT_PROTOCON_CCO_CHILD:
                item_cco_father = QTreeWidgetItem(item_protocon)
                item_cco_father.setText(0, value)
                item_cco_father.setCheckState(0, Qt.Unchecked)
            elif AllCertCaseValue.ROOT_PROTOCON_CCO_CHILD < DictCommandInfo[value] < \
                    AllCertCaseValue.ROOT_PROTOCON_CCO_MAX:
                item_cco_child = QTreeWidgetItem(item_cco_father)
                item_cco_child.setText(0, value)
                item_cco_child.setCheckState(0, Qt.Unchecked)
            elif DictCommandInfo[value] == AllCertCaseValue.ROOT_PERFORMANCE_CHILD:
                item_prerf_father = QTreeWidgetItem(self.AllTestCase)
                item_prerf_father.setText(0, value)
                item_prerf_father.setCheckState(0, Qt.Unchecked)
            elif AllCertCaseValue.ROOT_PERFORMANCE_CHILD < DictCommandInfo[value] < \
                    AllCertCaseValue.ROOT_PERFORMANCE_MAX:
                item_perf_child = QTreeWidgetItem(item_prerf_father)
                item_perf_child.setText(0, value)
                item_perf_child.setCheckState(0, Qt.Unchecked)

        # 节点全部展开
        self.treeWidget.expandAll()

        # self.treeWidget.itemClicked.connect(self.handlechanged)
        self.treeWidget.itemChanged.connect(self.handlechanged)

    def handlechanged(self, item, column):
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


class TableWidgetClass(QWidget):
    signal2 = pyqtSignal(list)

    def __init__(self, tablewidget):
        # noinspection PyArgumentList
        super(TableWidgetClass, self).__init__()
        self.tableWidget = None
        self.initui(tablewidget)
        self.twrowcnt = 0
        self.handle_queue = queue.Queue(maxsize=100)
        # 连接发射函数
        self.signal2.connect(self.table_set_item)
        # excel
        self.excel = excel.ExcelTool()

    def signal2emit(self, list_info):
        self.signal2.emit(list_info)  # 朝connect的函数发射一个tuple

    def initui(self, tablewidget):
        layout = QHBoxLayout()

        self.tableWidget = tablewidget
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        # 字体颜色（红色）
        # self.tableWidget.item(1, 0).setForeground(QColor("red"))
        # self.tableWidget.item(1, 1).setBackground(QColor("red"))
        # newItem = QTableWidgetItem('hellomsss')
        # self.tableWidget.setItem(1, 0, newItem)
        # print(self.tableWidget.item(1, 0).text())
        # self.tableWidget.item(1, 0).setForeground(QColor("black"))
        # self.tableWidget.item(1, 0).setBackground(QColor("red"))

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

        # noinspection PyArgumentList
        layout.addWidget(self.tableWidget)

        # self.setLayout(layout)

    def table_append(self, str_info):
        if str_info == 'CCO测试项' or str_info == 'STA测试项' or str_info == '协议一致性' \
                or str_info == '通信性能测试':
            return
        item = self.tableWidget.findItems(str_info, Qt.MatchExactly)
        if not item:
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            newitem = QTableWidgetItem(str_info)
            self.tableWidget.setItem(row, 0, newitem)

    def table_remove(self, str_info):
        item = self.tableWidget.findItems(str_info, Qt.MatchExactly)
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

    def table_get_row(self, str_info):
        item = self.tableWidget.findItems(str_info, Qt.MatchExactly)
        if not item:
            row = self.tableWidget.rowCount()
            return row

    def table_set_item(self, list_info):
        f_str = list_info[0]
        exe_time = list_info[1]
        result = list_info[2]
        remarks = list_info[3]
        item = self.tableWidget.findItems(f_str, Qt.MatchExactly)
        # print("ttttttttttt")
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
                    newitem = QTableWidgetItem(f_str)
                    self.tableWidget.setItem(row, idx, newitem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
                elif idx == 1:
                    newitem = QTableWidgetItem(exe_time)
                    self.tableWidget.setItem(row, idx, newitem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
                elif idx == 2:
                    newitem = QTableWidgetItem(result)
                    self.tableWidget.setItem(row, idx, newitem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
                elif idx == 3:
                    newitem = QTableWidgetItem(remarks)
                    self.tableWidget.setItem(row, idx, newitem)
                    # set red
                    self.tableWidget.item(row, idx).setBackground(QColor(bcolor))
        self.excel.excel_write(list_info)
