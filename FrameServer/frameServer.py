#!/usr/bin/env python3
import os
import sys
import time
import http.server
import platform
from socketserver import ThreadingMixIn
from io import StringIO
import re


__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "philokey"
__home_page__ = ""


def init_server():
    print("init server")
    try:
        adr = sys.argv[2]
    except Exception as e:
        print('-------->> Warning: Address is not given, will use local server ')
        adr = ''

    try:
        port = int(sys.argv[3])
    except Exception as e:
        print('-------->> Warning: Port is not given, will use deafult port: 8080 ')
        port = 8080

    if not 1024 < port < 65535:  port = 8080

    print('-------->> Now, listening at port ' + str(port) + ' ...')
    if adr == '':
        print('-------->> You can visit the URL:     http://127.0.0.1:' +str(port))
    print("")
    return (adr, port)


def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def modification_date(filename):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(filename)))


class FrameHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "FrameHTTP/" + __version__

    def do_GET(self):
        buf = bytes("Server is working", encoding='utf-8')
        self.send_response(200)
        self.send_header("Welcome", "Contect")
        self.end_headers()
        self.wfile.write(buf)

    def do_POST(self):
        r, info, fname = self.save_post_data()
        baseDir = '/Users/philokey/Practice/AnnotationTool'
        execDir = os.path.join(baseDir, 'Storyboard/Storyboard')
        cmd = execDir + ' ' + fname
        print(cmd)
        os.system(cmd)
        # result_dir = os.path.join(baseDir, 'result', fname.split('/')[-1] + '.txt')
        # print(result_dir)
        result_dir = '/Users/philokey/test.txt'
        f = open(result_dir, 'r')

        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        length = 0
        if f:
            for i in f.readlines():
                _w = i.encode("utf-8")
                length += len(_w)
                self.wfile.write(_w)
            f.close()
        print(length)
        self.send_header("Content-Length", str(length))
    def save_post_data(self):
        baseDir = '/Users/philokey/Practice/AnnotationTool/data'

        boundary = self.headers['Content-Type'].split("=")[1]
        boundary = bytes(boundary, encoding='utf-8')
        remain_bytes = int(self.headers['content-length'])
        print(self.headers)
        # for i in self.rfile:
        #     print (i)
        line = self.rfile.readline()
        remain_bytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary", "")
        line = self.rfile.readline()

        remain_bytes -= len(line)

        # 获取文件名
        print("line................",line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', str(line))
        if not fn:
            return (False, "Can't find out file name...","")
        else:
            fn = fn[0]
        while os.path.exists(os.path.join(baseDir, fn)):
            fn = "_" + fn  #去重
        fn = os.path.join(baseDir, fn)

        # 有个\n\r 读掉
        line = self.rfile.readline()
        remain_bytes -= len(line)

        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?","")

        pre_line = self.rfile.readline()
        remain_bytes -= len(pre_line)
        while remain_bytes > 0:
            line = self.rfile.readline()
            remain_bytes -= len(line)
            if boundary in line:
                pre_line = pre_line[0:-1]

                if (pre_line).endswith(b'\r'):
                    #print("!!!!!!!!")
                    pre_line = pre_line[0:-1]
                #print(pre_line)
                out.write(pre_line)
                out.close()
                return (True, "File '%s' upload success!" % fn, fn)
            else:
                out.write(pre_line)
                pre_line = line
        return (False, "Unexpect Ends of data.", fn)


class ThreadingServer(ThreadingMixIn, http.server.HTTPServer):
    pass


if __name__ == '__main__':
    serveraddr = init_server()
    httpd = ThreadingServer(serveraddr, FrameHTTPRequestHandler)
    httpd.serve_forever()

