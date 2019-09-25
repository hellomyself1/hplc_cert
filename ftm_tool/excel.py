# -*- coding: utf-8 -*-
import xlsxwriter
import time
import os
import xlwt
import xlrd
from xlutils.copy import copy
from openpyxl import load_workbook
from macro_const import all_cert_case_value, DictCommandInfo

class ExcelTool:
    def __init__(self):
        self.filename = ''

    def exceltool(self):
        file_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        file_patch = '.\\LOG\\report'
        if not os.path.exists(file_patch):
            os.makedirs(file_patch)
        self.filename = file_patch + '\\hplc_report_' + file_time + '.xls'
        workbook = xlsxwriter.Workbook(self.filename)
        worksheet = workbook.add_worksheet(u'hplc_report')
        workbook.close()
        self.excel_init()

    def excel_style(self, font_height, align_h, align_v, bold=0, align_wrap=1, align_shri=0, pattern_color=None, borders_set=None):
        font = xlwt.Font()
        font.name = '宋体'
        font.height = font_height
        font.bold = bold
        # 设置单元格对齐方式
        alignment = xlwt.Alignment()
        # 0x01(左端对齐)、0x02(水平方向上居中对齐)、0x03(右端对齐)
        alignment.horz = align_h
        # 0x00(上端对齐)、 0x01(垂直方向上居中对齐)、0x02(底端对齐)
        alignment.vert = align_v
        # 1-自动换行,0-不自动换行
        alignment.wrap = align_wrap
        # 缩小字体填充
        alignment.shri = align_shri

        style = xlwt.XFStyle()
        style.font = font
        style.alignment = alignment

        if borders_set is not None:
            # 设置边框
            borders = xlwt.Borders()
            # 细实线:1，小粗实线:2，细虚线:3，中细虚线:4，大粗实线:5，双线:6，细点虚线:7
            # 大粗虚线:8，细点划线:9，粗点划线:10，细双点划线:11，粗双点划线:12，斜点划线:13
            borders.left = borders_set
            borders.right = borders_set
            borders.top = borders_set
            borders.bottom = borders_set
            borders.left_colour = 8
            borders.right_colour = 8
            borders.top_colour = 8
            borders.bottom_colour = 8
            style.borders = borders

        # 设置背景颜色的模式
        if pattern_color is not None:
            pattern_top = xlwt.Pattern()
            pattern_top.pattern = xlwt.Pattern.SOLID_PATTERN
            # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta,
            # 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , almost brown),
            # 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray, the list goes on...
            pattern_top.pattern_fore_colour = pattern_color
            style.pattern = pattern_top
        return style

    def keys_get_value(self, mydict, keys):
        for key, val in mydict.items():
            if key == keys:
                return val

    def excel_init(self):
        # 打开想要更改的excel文件
        old_excel = xlrd.open_workbook(self.filename)
        # 将操作文件对象拷贝，变成可写的workbook对象
        new_excel = copy(old_excel)
        # 获得第一个sheet的对象
        ws = new_excel.get_sheet(0)
        # set col width
        a_col = ws.col(0)
        a_col.width = 256*16
        b_col = ws.col(1)
        b_col.width = 256*14
        c_col = ws.col(2)
        c_col.width = 256*40
        d_col = ws.col(3)
        d_col.width = 256*20
        e_col = ws.col(4)
        e_col.width = 256*40
        # set row width
        tall_style = xlwt.easyxf('font:height 320')  # 14pt
        first_row = ws.row(0)
        first_row.set_style(tall_style)

        # 合并
        style = self.excel_style(20 * 14, 0x02, 0x01, 1, pattern_color=22, borders_set=1)
        ws.write_merge(0, 0, 0, 1, "测试大项", style)
        ws.write(0, 2, '测试项', style)
        ws.write(0, 3, '测试结果', style)
        ws.write(0, 4, '备注', style)

        # 协议一致性 sta/cco 测试项目个数
        pro_sta_cnt = all_cert_case_value.ROOT_PROTOCON_STA_MAX - all_cert_case_value.ROOT_PROTOCON_STA_CHILD - 1
        pro_cco_cnt = all_cert_case_value.ROOT_PROTOCON_CCO_MAX - all_cert_case_value.ROOT_PROTOCON_CCO_CHILD - 1
        performance_cnt = all_cert_case_value.ROOT_PERFORMANCE_MAX - all_cert_case_value.ROOT_PERFORMANCE_CHILD - 1

        for keys in DictCommandInfo.keys():
            if DictCommandInfo[keys] == all_cert_case_value.ROOT_PROTOCON:
                style = self.excel_style(20 * 14, 0x02, 0x01, 0, borders_set=1)
                start_idx = 1
                end_idx = pro_sta_cnt + pro_cco_cnt
                ws.write_merge(start_idx, end_idx, 0, 0, keys, style)

            elif DictCommandInfo[keys] == all_cert_case_value.ROOT_PROTOCON_STA_CHILD:
                style = self.excel_style(20 * 12, 0x02, 0x01, 0, borders_set=1)
                start_idx = 1
                end_idx = pro_sta_cnt
                ws.write_merge(start_idx, end_idx, 1, 1, keys, style)

            elif DictCommandInfo[keys] < all_cert_case_value.ROOT_PROTOCON_STA_MAX and DictCommandInfo[keys] > all_cert_case_value.ROOT_PROTOCON_STA_CHILD:
                val = self.keys_get_value(DictCommandInfo, keys)
                val -= all_cert_case_value.ROOT_PROTOCON_STA_CHILD
                # sta 协议一致性case
                style = self.excel_style(20 * 12, 0x01, 0x01, 0, borders_set=1)
                col = val
                row = 2
                ws.write(col, row, keys, style)

            elif DictCommandInfo[keys] == all_cert_case_value.ROOT_PROTOCON_CCO_CHILD:
                style = self.excel_style(20 * 12, 0x02, 0x01, 0, borders_set=1)
                start_idx = 1 + pro_sta_cnt
                end_idx = pro_sta_cnt + pro_cco_cnt
                ws.write_merge(start_idx, end_idx, 1, 1, keys, style)

            elif DictCommandInfo[keys] < all_cert_case_value.ROOT_PROTOCON_CCO_MAX and DictCommandInfo[keys] > all_cert_case_value.ROOT_PROTOCON_CCO_CHILD:
                # cco 协议一致性case
                val = self.keys_get_value(DictCommandInfo, keys)
                val -= all_cert_case_value.ROOT_PROTOCON_CCO_CHILD
                style = self.excel_style(20 * 12, 0x01, 0x01, 0, borders_set=1)
                col = pro_sta_cnt + val
                row = 2
                ws.write(col, row, keys, style)

            elif DictCommandInfo[keys] == all_cert_case_value.ROOT_PERFORMANCE_CHILD:
                style = self.excel_style(20 * 14, 0x02, 0x01, 0, borders_set=1)
                start_idx = pro_sta_cnt + pro_cco_cnt + 1
                end_idx = pro_sta_cnt + pro_cco_cnt + performance_cnt
                ws.write_merge(start_idx, end_idx, 0, 1, keys, style)

            elif DictCommandInfo[keys] < all_cert_case_value.ROOT_PERFORMANCE_MAX and DictCommandInfo[keys] > all_cert_case_value.ROOT_PERFORMANCE_CHILD:
                val = self.keys_get_value(DictCommandInfo, keys)
                val -= all_cert_case_value.ROOT_PERFORMANCE_CHILD
                # 性能测试
                style = self.excel_style(20 * 12, 0x01, 0x01, 0, borders_set=1)
                col = pro_sta_cnt + pro_cco_cnt + val
                row = 2
                ws.write(col, row, keys, style)

        ''''
        style = self.excel_style(20 * 14, 0x02, 0x01, 0)
        ws.write_merge(1, 40, 0, 0, "协议一致性", style)
        style = self.excel_style(20 * 12, 0x02, 0x01, 0)
        ws.write_merge(1, 20, 1, 1, "STA测试", style)
        ws.write_merge(21, 40, 1, 1, "CCO测试", style)
        style = self.excel_style(20 * 14, 0x02, 0x01, 0)
        ws.write_merge(42, 67, 0, 1, "通信性能", style)
        '''

        # 另存为excel文件，并将文件命名
        new_excel.save(self.filename)

    def excel_write(self, list):
        name, times, result, remark = list

        # 打开想要更改的excel文件
        old_excel = xlrd.open_workbook(self.filename, formatting_info=True)

        old_sheet = old_excel.sheet_by_name('hplc_report')
        # 获取有效行数
        row_max = old_sheet.nrows
        row_lid = 0
        for i in range(row_max):
            if old_sheet.cell_value(i, 2) == name:
                row_lid = i
                break

        # 将操作文件对象拷贝，变成可写的workbook对象
        new_excel = copy(old_excel)
        # 获得第一个sheet的对象
        ws = new_excel.get_sheet(0)
        if result == 'pass':
            style = self.excel_style(20 * 12, 0x02, 0x01, 0, pattern_color=3, borders_set=1)
        else:
            style = self.excel_style(20 * 12, 0x02, 0x01, 0, pattern_color=2, borders_set=1)
        ws.write(row_lid, 3, result, style)

        style = self.excel_style(20 * 12, 0x02, 0x01, 0, borders_set=1)
        ws.write(row_lid, 4, remark, style)

        # 另存为excel文件，并将文件命名
        new_excel.save(self.filename)



