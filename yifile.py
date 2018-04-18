import urllib
from PIL import Image
import http.cookiejar
import os
import re
from pytesser3 import *
import time
import io
import urllib.request
import urllib.response
import datetime
import zipfile
import threading

class yifile:
    filepage = ""
    pagefilename = ""
    pagefilesize = ""
    filelink = ""
    filename = ""
    filesize = 0
    downloadfolder = ""
    filepath = ""
    downloadsize = 0
    unzippath = ""
    timecost = 0
    starttime = ""
    downloadtime = ""
    unziptime = ""
    endtime = ""
    status = 0
    __cookie = http.cookiejar.CookieJar()
    __fileid = 0
    __fileaction = ""
    __codelink = "https://www.yifile.com/includes/imgcode.inc.php?verycode_type=2"
    __codeurl = "https://www.yifile.com/ajax.php"

    def __init__(self, url):
        self.filepage = url
        self.__fileaction = "yifile_down"

    def __getyifilePage(self):
        req = urllib.request.Request(self.filepage)
        req.add_header('accept',
                       'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
        req.add_header('accept-language', 'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4,zh-CN;q=0.2')
        req.add_header('cache-control', 'max-age=0')
        req.add_header('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36' +
                       ' (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        rep = urllib.request.urlopen(req)
        return rep.read().decode()

    def getyifilePageInfo(self):
        pagecode = self.__getyifilePage()
        p = re.compile('<span id="FileSize">.*?</span>')
        s = p.findall(pagecode)[0]
        self.pagefilesize = s[s.find(">") + 1: s.rfind("<")]
        p = re.compile('<span id=\"FileName\".*?</span>')
        n = p.findall(pagecode)[0]
        self.pagefilename = n[n.find(">") + 1: n.rfind("<")]
        return self.pagefilesize, self.pagefilename

    def __getYifileID(self):
        p = re.compile('action=yifile_down&file_id=[0-9]*[0-9][0-9]')
        # para = p.findall(self.__filePageCode)[0]
        para = p.findall(self.__getyifilePage())[0]
        return para[para.rfind("=") + 1:para.__len__()]

    def __get_bin_table(threshold=140):
        """
        获取灰度转二值的映射table
        :param threshold:
        :return:
        """
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        return table

    def __getVeryCode(self):
        vreq = urllib.request.Request(self.__codelink)
        vreq.add_header('accept',
                        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
        vreq.add_header('accept-language', 'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4,zh-CN;q=0.2')
        vreq.add_header('cache-control', 'max-age=0')
        vreq.add_header('user-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36' +
                        ' (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.__cookie))
        response = opener.open(vreq)
        data_stream = io.BytesIO(response.read())
        pil_image = Image.open(data_stream)
        pil_image = pil_image.convert('L')
        threshold = 140
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        image = pil_image.point(table, '1')
        return image

    def __verycodeModify(self, verycode):
        rep = {'0': 'o',
               '\n': '',
               ']': '1',
               '/': 'i',
               '\\': 'i',
               ' ': '',
               '|': 'i'
            }
        verycode.strip()
        for r in rep:
            verycode = verycode.replace(r, rep[r])
        if len(verycode) < 4:
            verycode = verycode.zfill(4)
        print(verycode)
        return verycode.lower()

    def getYifileLink(self, trytimes=0):
        # self.__filePageCode = self.__getYifilePageHtml()
        self.__fileid = self.__getYifileID()
        verified = 0
        if trytimes <= 0:
            trytimes = 1
        for i in range(trytimes):
            verycode = image_to_string(self.__getVeryCode())
            verycode = self.__verycodeModify(verycode)
            postdata = {
                'action': self.__fileaction,
                'file_id': self.__fileid,
                'verycode': verycode
            }
            postheader = {
                'accept': 'text/plain, */*; q=0.01',
                # 'accept-encoding': 'gzip, deflate, br',
                # 'accept-language': 'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4,zh-CN;q=0.2',
                'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,zh-CN;q=0.6',
                'content-length': 47,
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36' +
                #              ' (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                'origin': 'https://www.yifile.com',
                'referer': self.filepage
            }
            print(postdata)
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.__cookie))
            req = urllib.request.Request(url=self.__codeurl, data=urllib.parse.urlencode(postdata).encode(), headers=postheader, method='POST')
            response = opener.open(req)
            s = response.read()
            result = s.split("|".encode())
            print(result)
            if result[0] == b'true':
                self.filelink = result[1].decode()
                self.filename = self.filelink.split('/')[-1]
                verified = 1
                break
            time.sleep(1)
        return verified

    def continueDownloading(self, uptcallback=None):
        print("start continue downloading " + self.filename + "\t" + yifile.formatFileSize(self.downloadsize) + "\\" + yifile.formatFileSize(self.filesize))
        if self.downloadsize == self.filesize:
            if self.filepath.find('.downloading') >= 0:
                os.rename(self.filepath, self.downloadfolder + "\\" + self.filename)
                self.filepath = self.downloadfolder + "\\" + self.filename
            self.status = 2
            print("\n download finished " + self.filename + "\t" + yifile.formatFileSize(
                self.downloadsize) + "\\" + yifile.formatFileSize(self.filesize))
            return self.status
        if self.getYifileLink(10) == 1:
            r = 'bytes=' + str(self.downloadsize) + '-'
            header = {'Range': r}
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.__cookie))
            req = urllib.request.Request(url=self.filelink, data=None,
                                         headers=header, method='GET')
            rep = opener.open(req)
            file_size = rep.headers["Content-Length"]
            f = open(self.filepath, 'ab+')
            start = time.time()
            file_size_dl = 0
            block_sz = 8192
            uptcounter = 0
            t = self.timecost
            self.status = 1
            try:
                while True:
                    buffer = rep.read(block_sz)
                    if not buffer:
                        break
                    file_size_dl += len(buffer)
                    self.downloadsize += len(buffer)
                    f.write(buffer)
                    end = time.time()
                    time.sleep(0.2)
                    self.timecost = round((end - start)) + t
                    # self.timecost += t
                    if uptcounter == 100:
                        uptcallback(self)
                        uptcounter = 0
                    speed = int(self.downloadsize / self.timecost)
                    print("%s:%.2f%% %s/%s %s S %s/S     " % (
                        self.filename, float(self.downloadsize) / float(self.filesize) * 100,
                        yifile.formatFileSize(self.downloadsize), yifile.formatFileSize(self.filesize),
                        str(self.timecost), yifile.formatFileSize(speed)), end="\r")
                    uptcounter += 1
                f.close()
                self.status = 2
                os.rename(self.filepath, self.downloadfolder + "\\" + self.filename)
                self.filepath = self.downloadfolder + "\\" + self.filename
                print("\n download finished " + self.filename + "\t" + yifile.formatFileSize(
                    self.downloadsize) + "\\" + yifile.formatFileSize(self.filesize))
                return self.status
            except Exception as e:
                self.status = 1
                print("\n")
                print("download error: " + str(e))
                return self.status
            finally:
                if not f.closed:
                    f.close()
        else:
            return 0

    def startdownload(self, uptcallback=None):
        if self.getYifileLink(10) == 1:
            print("start downloading " + self.filename + "\t" + yifile.formatFileSize(self.filesize))
            if os.path.exists(self.downloadfolder + "\\" + self.filename):
                self.filename = time.strftime('%Y%m%d%H%M%S') + self.filename
            self.filepath = self.downloadfolder + "\\" + self.filename + ".downloading"
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.__cookie))
            headers = {}
            req = urllib.request.Request(url=self.filelink, data=None,
                                         headers=headers, method='GET')
            rep = opener.open(req)
            self.filesize = rep.headers["Content-Length"]
            if uptcallback:
                uptcallback(self)
            f = open(self.filepath, "wb+")
            start = time.time()
            file_size_dl = 0
            block_sz = 8192
            uptcounter = 0
            self.downloadtime = str(datetime.datetime.now())
            try:
                while True:
                    buffer = rep.read(block_sz)
                    if not buffer:
                        break
                    file_size_dl += len(buffer)
                    self.downloadsize = file_size_dl
                    f.write(buffer)
                    self.status = 1
                    end = time.time()
                    time.sleep(0.2)
                    self.timecost = round((end - start))
                    if self.timecost < 1:
                        self.timecost = 1
                    if uptcounter == 100:
                        uptcallback(self)
                        uptcounter = 0
                    speed = int(file_size_dl / self.timecost)
                    print("%s:%.2f%% %s/%s %s S %s/S     " % (
                        self.filename, float(self.downloadsize) / float(self.filesize) * 100,
                        yifile.formatFileSize(self.downloadsize), yifile.formatFileSize(self.filesize),
                        str(self.timecost), yifile.formatFileSize(speed)), end="\r")
                    uptcounter += 1
                f.close()
                self.status = 2
                os.rename(self.filepath, self.downloadfolder + "\\" + self.filename)
                self.filepath = self.downloadfolder + "\\" + self.filename
                print("\n download finished " + self.filename + "\t" + yifile.formatFileSize(
                    self.downloadsize) + "\\" + yifile.formatFileSize(self.filesize))
                return self.status
            except Exception as e:
                self.status = 1
                print("\n")
                print("download error: " + str(e))
                if str(e).find("WinError 10054") > 0:
                    return -1
                return self.status
            finally:
                if not f.closed:
                    f.close()
        else:
            return 0



    def formatFileSize(size):
        size = float(size)
        if (size >= 1024) and (size <= 1024 * 1024):
            f = "%.2f KB" % (float(size) / 1024)
        elif (size >= 1024 * 1024) and (size < 1024 * 1024 * 1024):
            f = "%.2f MB" % (float(size) / 1024 / 1024)
        elif size >= (1024 * 1024 * 1024):
            f = "%.2f GB" % (float(size) / 1024 / 1024 / 1024)
        else:
            f = "%d Bytes" % size
        return f