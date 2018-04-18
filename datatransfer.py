import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect("C:\\Users\\ShSctIT\\PycharmProjects\\yifileDownloader\\db\\data.sqlite3.bak")
    conn1 = sqlite3.connect("C:\\Users\\ShSctIT\\PycharmProjects\\yifileDownloader\\db\\data.sqlite3")
    sql = "select * from filelist"
    c = conn.execute(sql)
    rows = c.fetchall()
    for r in rows:
        filepage = r[0]
        print(filepage)
        pagefilename = r[1]
        print(pagefilename)
        pagefilesize = r[2]
        print(pagefilesize)
        if r[3]:
            filelink = r[3]
        else:
            filelink = ""
        if r[4]:
            filename = r[4]
        else:
            filename = ""
        if r[5]:
            filesize = r[5]
        else:
            filesize = 0
        if r[6]:
            filepath = r[6]
        else:
            filepath = ""
        if r[7]:
            downloadfolder = r[7]
        else:
            downloadfolder = ""
        if r[8]:
            downloadsize = r[8]
        else:
            downloadsize = 0
        if r[9]:
            unzippath = r[9]
        else:
            unzippath = ""
        if r[10]:
            timecost = r[10]
        else:
            timecost = 0
        print(str(timecost))
        starttime = r[11]
        if r[12]:
            downloadtime = r[12]
        else:
            downloadtime = ""
        if r[15]:
            status = r[15]
        else:
            status = 0
        sql = "insert into filelist (filepage, pagefilename,pagefilesize,filelink,filename,filesize,filepath,downloadfolder,downloadsize,unzippath,timecost,starttime,downloadtime,status) VALUES ('" + \
              str(filepage) + "','" + str(pagefilename) + "','" + str(
            pagefilesize) + "','" + str(filelink) + "','" + str(filename) + "'," + str(
            filesize) + ",'" + str(filepath) + "','" + str(downloadfolder) + "'," + str(
            downloadsize) + ",'" + str(unzippath) + "'," + str(timecost) + ",'" + str(starttime) + "','" + str(downloadtime) + "'," + str(status) + ")"
        print(sql)
        # conn1.execute(sql)
        # conn1.commit()
    conn.close()
    conn1.close()
