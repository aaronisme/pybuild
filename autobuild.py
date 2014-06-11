import shutil
import os,sys,string,datetime,time
import socket
import tarfile
import glob
import telnetlib
import re

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



    def download(self,folder,spath,dpath): 
        try:
            src = os.path.join(os.path.join(os.path.join(os.path.join(spath,folder),'winx64h'),'compressed'),'bisrvr')
            dst = os.path.join(os.path.join(os.path.join(os.path.join(dpath,folder),'winx64h'),'compressed'),'bisrvr')
            shutil.copytree(src,dst)
            
        except:
            print 'copy failed'
            shutil.rmtree(os.path.join(dpath,folder))
            sys.exit(0)
        return

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
        if len(disFolder) == 0:
            for targetFile in srcFolder:
                shutil.copytree(os.path.join(src,targetFile),os.path.join(dis,targetFile))
        else:
            for filename in disFolder:
                srcFolder.remove(filename)
            targetFolder = srcFolder  # list.remove() return nothing
            for targetFile in targetFolder:
                #print os.path.join(src,targetFile)
                #print os.path.join(dis,targetFile)
                shutil.copytree(os.path.join(src,targetFile),os.path.join(dis,targetFile))
        return

	
		

class ZIP:
    def creat_uzippath(self,agrm1):
        os.makedirs(agrm1)
        
    def extract_file(self,zippath,uzippath):
        try:
            print 'start unzipping'
            tar = tarfile.open(zippath)
            names = tar.getnames()
            for name in names:
                tar.extract(name,path= uzippath)
            tar.close()
        except:
            print 'unZip failed'
            sys.exit(0)
            return
        print 'unzip completely'


class HTML:
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


		

		
	

if __name__ == '__main__':

    spath = ""
    dpath = "C:\installbuilds"
    insVer = 'installversion.txt'
    insVerPath = os.path.join(dpath,insVer)
    insLog = 'installog.txt'
    insLogPath = os.path.join(dpath,insLog)
    vmPath = ""
    b = Build()
    bname = b.getLastestBuild(spath)
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
    h.creathtml(bname,insLogPath)


    
