import shutil
import os,sys,string,datetime,time
import socket
import tarfile
import glob
import telnetlib
import re
import threading
from time import sleep,ctime,gmtime,strftime


class thread(threading.Thread):
    def __init__(self, num, interval,bpath):  
    	threading.Thread.__init__(self)  
    	self.thread_num = num  
    	self.interval = interval
    	self.thread_stop = False
    	self.bpath = bpath
        
    def run(self):
        def getdirsize(dir):  
           size = 0.0  
           for root, dirs, files in os.walk(dir):  
              size += sum([os.path.getsize(os.path.join(root, name)) for name in files])  
           return size
        
        sleep(30)
        flag = True
        while(flag == True):
            kitSize1 = getdirsize(self.bpath)
            print self.bpath
            print kitSize1
            sleep(60)
            kitSize2 = getdirsize(self.bpath)
            print kitSize2
            speed = float(kitSize2 - kitSize1)/60.0/1024
            print speed
            speedlog = 'The Downloading Speed is ' + str(speed) + 'kb/s'
            dlog.writelog(speedlog,logPath)
            if speed == 0.0:
                flag = False

    def stop(self):
    	self.thread_stop = True



class Build:
    def getLastestBuild(self,path):
        buildList = os.listdir(path)
        #print buildList
        ftime = []
        for folder in buildList:
            
            ftime.append(os.path.getctime(os.path.join(path,folder)))
            
            
        ftime_temp = ftime[:]
       
        ftime_temp.sort()
        ftime_temp.reverse()
        timeMax = ftime_temp[0]
        timeMaxIndex = ftime.index(timeMax)
        return buildList[timeMaxIndex]

    def delOldestBuild(self,path,rpath):
        kitList = os.listdir(path)
        kitList.remove('installog.txt')
        kitList.remove('installversion.txt')
        kitList.remove('Integration10.2.5000.275')
        kitList.remove('Integration10.2.5001.156')
        kitList.remove('Integration10.2.5002.78')
        kitList.remove('Integration10.2.5003.83')
        kitList.remove('Integration10.2.5003.63')
        ftime = []
        for folder in kitList:
            
            ftime.append(os.path.getctime(os.path.join(path,folder)))
         
        ftime_temp = ftime[:]
        ftime_temp.sort()
        kitDel = ftime_temp[0]
        kitDelIndex = ftime.index(kitDel)
        delKitName = kitList[kitDelIndex]
        print os.path.join(path,delKitName)
        shutil.rmtree(os.path.join(path,delKitName)) #delete the local builds 
        shutil.rmtree(os.path.join(rpath,delKitName)) # delete the remote buils
       


    def download(self,folder,spath,dpath): 
        try:
            src = os.path.join(os.path.join(os.path.join(os.path.join(spath,folder),'winx64h'),'compressed'),'bisrvr')
            dst = os.path.join(os.path.join(os.path.join(os.path.join(dpath,folder),'winx64h'),'compressed'),'bisrvr')
            t = thread(1,1,dst)
            t.start()
            dlog.writelog('Start downloading',logPath)
            shutil.copytree(src,dst,524288000)
            t.stop()
        except:
            print 'copy failed'
            shutil.rmtree(os.path.join(dpath,folder))
            sys.exit(0)
        #return

    def setversion(self,version,versionfile,verlog):
        version_handler = open(versionfile,'wb')
        version_handler.write(version)
        version_handler.close()
        version_handler = open(verlog,'a')
        version_handler.write('\n'+version)
        version_handler.close()

    def getversion(self,versionfile):
        version_handler = open(versionfile,'rb')
        instversion = version_handler.readline()
        version_handler.close()
        return instversion

    
    def copy2vm(self,src,dis):
        srcFolder = os.listdir(src)
        disFolder = os.listdir(dis)
        srcFolder.remove('installog.txt')
        srcFolder.remove('installversion.txt')
        dlog.writelog('Start copying to VM',logPath)
        if len(disFolder) == 0:
            for targetFile in srcFolder:
                shutil.copytree(os.path.join(src,targetFile),os.path.join(dis,targetFile),524288000)
        else:
            for filename in disFolder:
                srcFolder.remove(filename)
            targetFolder = srcFolder  # list.remove() return nothing
            for targetFile in targetFolder:
                #print os.path.join(src,targetFile)
                #print os.path.join(dis,targetFile)
                shutil.copytree(os.path.join(src,targetFile),os.path.join(dis,targetFile),524288000)
        return

	
		

class ZIP:
    def creat_uzippath(self,agrm1):
        os.makedirs(agrm1)
        
    def extract_file(self,zippath,uzippath):
        try:
            print 'start unzipping'
            dlog.writelog('Start unzipping',logPath)
            tar = tarfile.open(zippath)
            names = tar.getnames()
            for name in names:
                tar.extract(name,path= uzippath)
            tar.close()
        except:
            dlog.writelog('unZip failed',logPath)
            print 'unZip failed'
            sys.exit(0)
            return
        print 'unzip completely'
        dlog.writelog('unZip completely',logPath)


class HTML:
    def txt2json(self,path):
        targetPath="C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.2\\htdocs\\installog.json"
        sourPath = path
        file_handler = open(sourPath,'rt')
        buildList = file_handler.readlines()
        buildList.reverse()
        file_handler.close()
        jsonlist = []
        for x in buildList:
            buildtmp = x.split("\n")
            build = buildtmp[0]
            build = build.strip()
            if x == buildList[0]:
                jsonele = '[' + "{" + '"id":' + str(buildList.index(x)) + ',' + '"text"' + ':' + '"' + build + '"' + "}" + ','
            if x == buildList[len(buildList)-1]:
                jsonele = "{" + '"id":' + str(buildList.index(x)) + ',' + '"text"' + ':' + '"' + build + '"' + "}" + ']'
            if x != buildList[0] and x != buildList[len(buildList)-1]:
                jsonele = "{" + '"id":' + str(buildList.index(x)) + ',' + '"text"' + ':' + '"' + build + '"' + "}" + ','
            jsonlist.append(jsonele + '\r\n')
        jsonname = targetPath
        file_handler2 = open(jsonname, 'wb')
        file_handler2.writelines(jsonlist)
        file_handler2.close()
    	
    def getcmplst(self,insversion,sourcedir):
        cmplstdir = sourcedir + '\\winx64h\\versions.ini'
        file_handler = open(cmplstdir,'rb')
        cmplst = file_handler.readlines()
        file_handler.close()
        targetdir= "C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.2\\htdocs\\" + insversion + '.txt'
        file_handler2 = open(targetdir,'wb')
        file_handler2.writelines(cmplst)
        file_handler2.close()

    def creathtml(self,insversion,verlogdir):

        html1 = ['<html>\n', '\t<body>\n', '\t\t<h1>IBM Cognos Componet List</h1>\n', '\t\t<hr />\n', '\t\t<p>\n']
        html3 =[]
        html2 = ['\t\t</p>\n', '\t\t</body>\n', '</html>']

        file_handler = open(verlogdir,'r')
        version = file_handler.readlines()
        file_handler.close()

        for every_version in version:
            link = '\t\t\t<p><a href="/'+ every_version.rstrip('\n') +'.txt" target="_blank">' + every_version.rstrip('\n') + '\t\t</a></p> \r'

            html3.append(link)
            print(html3)

        #html3.append('\t\t\t<a href="/'+ insversion +'.txt" target="_blank">' + insversion + '</a> \r')
        html = html1 + html3 + html2
        htmldir = "C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.2\\htdocs\\cmplst.html"
        file_handler = open(htmldir,'wb')
        
        print(html)
        file_handler.writelines(html)
        file_handler.close()

class Log:
    def writelog(self,log,logpath):
        path = logpath
        currentime = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        file_handler = open(path,'ab')
        file_handler.writelines(currentime + ' '+ log + '\n')
        file_handler.close()
		

		

if __name__ == '__main__':

    spath = "\\\sottbuild1f.ottawa.ibm.com\\danube\\cdsets\\danubecdset"
    dpath = "C:\installbuilds"
    insVer = 'installversion.txt'
    insVerPath = os.path.join(dpath,insVer)
    insLog = 'installog.txt'
    insLogPath = os.path.join(dpath,insLog)
    vmPath = "//9.110.82.16/installbuilds"
    logPath = "C:\\Aaron\\python\\downloadinglog.txt"
    try:
        dlog = Log()
        b = Build()
        bname = b.getLastestBuild(spath)
        dlog.writelog(bname,logPath)
        zipPath = os.path.join(os.path.join(dpath,bname),'builds')
        print bname
        pattern = re.compile(r'Integration10.2.6100')
        match = pattern.match(bname)
        if match:
            if bname != b.getversion(insVerPath):
                b.download(bname,spath,dpath)
                b.setversion(bname,insVerPath,insLogPath)
            else:
                print 'the build exist'
                sys.exit(0)
        else:
            print 'the build is not vaild'
            sys.exit(0)
        tarBuildFilePath = glob.glob(os.path.join(dpath,bname)+"/*/*/*/*.tar.gz")[0]
        b.copy2vm(dpath,vmPath)
        z = ZIP()
        z.creat_uzippath(zipPath)
        z.extract_file(tarBuildFilePath,zipPath)

        h = HTML()
        h.getcmplst(bname,zipPath)
        h.txt2json(insLogPath)
        b.delOldestBuild(dpath,vmPath)
    except Exception,e:
        emessage = str(e)
        dlog.writelog(emessage,logPath)

    
