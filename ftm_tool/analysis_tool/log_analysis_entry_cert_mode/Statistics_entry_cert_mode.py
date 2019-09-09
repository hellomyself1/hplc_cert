# !/usr/bin/python
#import re

class read_file_and_handle:

    def __init__(self, filename):
        self.file = None
        self.filename = filename
        self.start_flag = 0
        self.cert_lines = 0
        self.err_flag = 0

    def read_file(self):
        try:
            self.file = open(self.filename, 'r')
            for line in self.file:
                str_p = line.strip()
                if str_p.find('oard_id') > 0:
                    self.start_flag += 1
                    if self.start_flag != 1 and self.cert_lines == 0:
                        print(str_p)
                        self.err_flag += 1
                    self.cert_lines = 0
                    continue

                if str_p.find('enter cert mode') > 0:
                    self.cert_lines += 1
                    continue
            self.file.close()
        except:
            print("open file fail!")

if __name__ == "__main__":

    file_name = ".\session_2019_09_09_Serial-COM9-173044 - 副本.log"
    f = read_file_and_handle(file_name)
    f.read_file()
    print('all test times:%d' % f.start_flag)
    print('error times:%d' % f.err_flag)
