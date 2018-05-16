import configparser
import sqlite3
import os
import yifile
import datetime
import time

class inifile:
    __configpath = ""
    yifilelist = ""
    downloadpath = ""
    datasource = ""

    def __init__(self, confile):
        if os.path.exists(confile):
            self.__configpath = confile
            config = configparser.ConfigParser()
            config.read(self.__configpath)
            self.yifilelist = config.get("yifiletool", "yifilelist")
            self.downloadpath = config.get("yifiletool", "downloadpath")
            if not os.path.exists(self.downloadpath):
                os.mkdir(self.downloadpath)
            self.datasource = config.get("yifiletool", "datasource")
            if os.path.exists(self.datasource):
                if os.path.isfile(self.datasource):
                    pass
                else:
                    raise FileExistsError(self.datasource + " is NOT a file")
            else:
                p, f = os.path.split(self.datasource)
                if not os.path.exists(p):
                    os.mkdir(p)
            self.__initDB()
        else:
            raise FileNotFoundError("Init file does NOT exist")

    def __initDB(self):
        conn = sqlite3.connect(self.datasource)
        sql = "select * from sqlite_master where type = 'table' and tbl_name = 'filelist'"
        c = conn.execute(sql)
        if c.fetchall().__len__() < 1:
            # sql = "CREATE TABLE filelist (filepage text primary key,pagefilename text,pagefilesize text,filelink text,filename text,filesize integer,filepath text,downloadfolder text,downloadsize INTEGER , unzippath text, timecost INTEGER,starttime text,downloadtime text, unziptime text,endtime text,status integer)"
            sql = "s"
            conn.execute(sql)
            conn.commit()
        conn.close()

def getyifileList(yifilelistfile):
    list = []
    if os.path.exists(yifilelistfile):
        f = open(yifilelistfile)
        line = f.readline()
        while line:
            info = line.split("\t")
            if info[0].find("https://www.yifile.com/file/") < 0:
                continue
            else:
                list.append(info[0].replace('\n', ''))
            line = f.readline()
        f.close()
        return list
    else:
        return list
        # raise FileNotFoundError(yifilelistfile + " does NOT exist")

def insertYifile(page, size, name):
    conn = sqlite3.connect(config.datasource)
    sql = "select * from filelist where filepage = '" + page + "' or pagefilesize = '" + size + "'"
    c = conn.execute(sql)
    if c.fetchall().__len__() < 1:
        sql = "insert into filelist (filepage, pagefilename,pagefilesize,downloadfolder,starttime,status) VALUES ('" + page + "','" + name + "','" + size + "','" + config.downloadpath + "','" + getdatetime() + "',0)"
        conn.execute(sql)
        conn.commit()
    conn.close()

def formatFileSize(size):
    size = float(size)
    if (size >= 1024) and (size <= 1024 * 1024):
        f = "%.2f KB" % (float(size) / 1024)
    elif (size >= 1024 * 1024) and (size < 1024 * 1024 * 1024):
        f = "%.2f MB" % (float(size) / 1024 / 1024)
    elif (size >= (1024 * 1024 * 1024)):
        f = "%.2f GB" % (float(size) / 1024 / 1024 / 1024)
    else:
        f = "%d Bytes" % (size)
    return f

def getdatetime():
    return str(datetime.datetime.now())

def getdownloadinglist():
    list = []
    sql = "select filepage, pagefilename, pagefilesize, filelink, filename, filesize, filepath, downloadsize, timecost,downloadfolder,status from filelist where status = 1 order by starttime "
    conn = sqlite3.connect(config.datasource)
    c = conn.execute(sql)
    rows = c.fetchall()
    for r in rows:
        y = yifile.yifile(r[0])
        y.pagefilename = r[1]
        y.pagefilesize = r[2]
        y.filelink = r[3]
        y.filename = r[4]
        y.filesize = r[5]
        y.filepath = r[6]
        y.downloadsize = r[7]
        y.timecost = r[8]
        y.downloadfolder = r[9]
        y.status = r[10]
        if os.path.exists(y.filepath):
            if y.downloadsize == os.path.getsize(y.filepath):
                list.append(y)
            else:
                y.downloadsize = os.path.getsize(y.filepath)
                sql = "update filelist set downloadsize = " + str(y.downloadsize) + " where filepage = '" + y.filepage + "'"
                conn.execute(sql)
                conn.commit()
                list.append(y)
        else:
            sql = "update filelist set status = 0 where filepage = '" + y.filepage + "'"
            conn.execute(sql)
            conn.commit()
    conn.close()
    return list

def getdownloadlist():
    list = []
    sql = "select filepage from filelist where status = 0 order by starttime "
    # sql = "select filepage from filelist where status < 2 order by status DESC , starttime "
    conn = sqlite3.connect(config.datasource)
    c = conn.execute(sql)
    rows = c.fetchall()
    for r in rows:
        list.append(r[0])
    conn.close()
    return list

def uptyifileinfo(yifile):
    sql = "update filelist set filelink = '" + yifile.filelink + "',filename = '" + yifile.filename + "',filesize = " + str(
        yifile.filesize) + ",filepath = '" + yifile.filepath + "',downloadsize = " + str(yifile.downloadsize) + ",timecost = " + str(
        yifile.timecost) + ",status = " + str(yifile.status)
    if yifile.downloadtime:
        sql += ",downloadtime = '" + yifile.downloadtime + "'"
    if yifile.unziptime:
        sql += ",unziptime = '" + yifile.unziptime + "'"
    if yifile.endtime:
        sql += ",endtime = '" + yifile.endtime + "'"
    sql += " where filepage = '" + yifile.filepage + "'"
    conn = sqlite3.connect(config.datasource)
    conn.execute(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("application start")
    mainpath = os.path.abspath(os.curdir)
    ini = mainpath + "\\main.ini"
    config = inifile(ini)
    yifilelist = getyifileList(config.yifilelist)
    print("get config")
    for y in yifilelist:
        yi = yifile.yifile(y)
        yi.getyifilePageInfo()
        insertYifile(yi.filepage, yi.pagefilesize, yi.pagefilename)
    print("insert yifile initial info")
    list = getdownloadinglist()
    print("get downloading yifile data" + "\t" + str(list.__len__()))
    for l in list:
        while l.status != 2:
            if l.status == 2:
                break
            elif l.status == -1:
                l.continueDownloading(uptcallback=uptyifileinfo)
            elif l.status == 1:
                l.continueDownloading(uptcallback=uptyifileinfo)
            else:
                break
        # l.continueDownloading(uptcallback=uptyifileinfo)
        uptyifileinfo(l)
    list = getdownloadlist()
    print("get new yifile data" + "\t" + str(list.__len__()))
    for l in list:
        y = yifile.yifile(l)
        y.downloadfolder = config.downloadpath
        r = 0
        while r != 2:
            if r == 2:
                break
            elif r == -1:
                print(r)
                time.sleep(600)
                r = y.continueDownloading(uptcallback=uptyifileinfo)
            elif r == 1:
                print(r)
                r = y.continueDownloading(uptcallback=uptyifileinfo)
            elif r == 0:
                r = y.startdownload(uptcallback=uptyifileinfo)
            else:
                break
        # r = y.startdownload(uptcallback=uptyifileinfo)
        uptyifileinfo(y)


