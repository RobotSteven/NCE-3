#coding=utf-8
__author__ = 'zhm'
from win32com import client as wc
import os
import time
import random
import MySQLdb
import re
def wordsToHtml(dir):
#批量把文件夹的word文档转换成html文件
 #金山WPS调用，抢先版的用KWPS，正式版WPS
 word = wc.Dispatch('KWPS.Application')
 for path, subdirs, files in os.walk(dir):
  for wordFile in files:
   wordFullName = os.path.join(path, wordFile)
   #print "word:" + wordFullName
   doc = word.Documents.Open(wordFullName)
   wordFile2 = unicode(wordFile, "gbk")
   dotIndex = wordFile2.rfind(".")
   if(dotIndex == -1):
    print '********************ERROR: 未取得后缀名！'
   fileSuffix = wordFile2[(dotIndex + 1) : ]
   if(fileSuffix == "doc" or fileSuffix == "docx"):
    fileName = wordFile2[ : dotIndex]
    htmlName = fileName + ".html"
    htmlFullName = os.path.join(unicode(path, "gbk"), htmlName)
    # htmlFullName = unicode(path, "gbk") + "\\" + htmlName
    print u'生成了html文件：' + htmlFullName
    doc.SaveAs(htmlFullName, 8)
    doc.Close()
 word.Quit()
 print ""
 print "Finished!"
def html_add_to_db(dir):
#将转换成功的html文件批量插入数据库中。
 conn = MySQLdb.connect(
  host='localhost',
  port=3306,
  user='root',
  passwd='root',
  db='test',
  charset='utf8'
  )
 cur = conn.cursor()
 for path, subdirs, files in os.walk(dir):
  for htmlFile in files:
   htmlFullName = os.path.join(path, htmlFile)
   title = os.path.splitext(htmlFile)[0]
   targetDir = 'D:/files/htmls/'
   #D:/files为web服务器配置的静态目录
   sconds = time.time()
   msconds = sconds * 1000
   targetFile = os.path.join(targetDir, str(int(msconds))+str(random.randint(100, 10000)) +'.html')
   htmlFile2 = unicode(htmlFile, "gbk")
   dotIndex = htmlFile2.rfind(".")
   if(dotIndex == -1):
    print '********************ERROR: 未取得后缀名！'
   fileSuffix = htmlFile2[(dotIndex + 1) : ]
   if(fileSuffix == "htm" or fileSuffix == "html"):
    if not os.path.exists(targetDir):
     os.makedirs(targetDir)
    htmlFullName = os.path.join(unicode(path, "gbk"), htmlFullName)
    htFile = open(htmlFullName,'rb')
    #获取网页内容
    htmStrCotent = htFile.read()
    #找出里面的图片
    img=re.compile(r"""<img\s.*?\s?src\s*=\s*['|"]?([^\s'"]+).*?>""",re.I)
    m = img.findall(htmStrCotent)
    for tagContent in m:
     imgSrc = unicode(tagContent, "gbk")
     imgSrcFullName = os.path.join(path, imgSrc)
     #上传图片
     imgTarget = 'D:/files/images/whzx/'
     img_sconds = time.time()
     img_msconds = sconds * 1000
     targetImgFile = os.path.join(imgTarget, str(int(img_msconds))+str(random.randint(100, 10000)) +'.png')
     if not os.path.exists(imgTarget):
      os.makedirs(imgTarget)
     if not os.path.exists(targetImgFile) or(os.path.exists(targetImgFile) and (os.path.getsize(targetImgFile) != os.path.getsize(imgSrcFullName))):
      tmpImgFile = open(imgSrcFullName,'rb')
      tmpWriteImgFile = open(targetImgFile, "wb")
      tmpWriteImgFile.write(tmpImgFile.read())
      tmpImgFile.close()
      tmpWriteImgFile.close()
      htmStrCotent=htmStrCotent.replace(tagContent,targetImgFile.split(":")[1])
    if not os.path.exists(targetFile) or(os.path.exists(targetFile) and (os.path.getsize(targetFile) != os.path.getsize(htmlFullName))):
     #用iframe包装转换好的html文件。
     iframeHtml='''
     <script type="text/javascript" language="javascript">
      function iFrameHeight() {
       var ifm= document.getElementById("iframepage");
       var subWeb = document.frames ? document.frames["iframepage"].document:ifm.contentDocument;
       if(ifm != null && subWeb != null) {
        ifm.height = subWeb.body.scrollHeight;
       }
      }
     </script>
     <iframe src='''+targetFile.split(':')[1]+'''
      marginheight="0" marginwidth="0" frameborder="0" scrolling="no" width="765" height=100% id="iframepage" name="iframepage" onLoad="iFrameHeight()" ></iframe>
     '''
     tmpTargetFile = open(targetFile, "wb")
     tmpTargetFile.write(htmStrCotent)
     tmpTargetFile.close()
     htFile.close()
     try:
      # 执行
      sql = "insert into common_article(title,content) values(%s,%s)"
      param = (unicode(title, "gbk"),iframeHtml)
      cur.execute(sql,param)
     except:
      print "Error: unable to insert data"
 cur.close()
 conn.commit()
 # 关闭数据库连接
 conn.close()
if __name__ == '__main__':
 # wordsToHtml('Lesson_01.docx')
 # html_add_to_db('Lesson_01.html')
 wordsToHtml('/')
 html_add_to_db('/')