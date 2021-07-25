# _*_  coding:utf-8 _*_
#    redis未授权检测脚本 多线程版
#   使用环境；
#   1.Python 3.8.10
#   2.python安装redis和func_timeout
#
#       windows环境：管理员身份
#                    pip3 install func_timeout
#                    pip3 install redis
#       Linux环境：  sudo easy_install redis  
#                    sudo easy_install func_timeout
#=========================================================
#       使用命令
#       url.txt导入的目标,格式为 IP:端口 示例 119.45.56.123:6379
#       python.exe ./redisManyThread.py
#

import redis
import threading
import math
import time
from func_timeout import func_set_timeout
import func_timeout



file="./url.txt" #导入的目标，格式为 IP：端口 示例 119.45.56.123:6379
thread_num=20 #默认线程数量
socket_timeout=6 #默认超时时间6秒
success_save_filename="./success.txt" #存在未授权漏洞的目标
timeout_save_filename="./timeout.txt" #因网络太卡，检测超时的目标IP，需要人工复查

thread_slit=0 #每一条线程处理数据量(勿动)
redis_row_list=[] #从文件读入内存的列表(勿动)

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        # print ("开启线程： " + self.name+"时间:"+str(time.time()))
        try:
            redisSendFifo(self.threadID)
        except :
            print("超时线程ID："+self.name)

#按行读取文本
def readfile(file):
    file = open(file) 
    while 1:
      lines = file.readlines(100000)
      if not lines:
        break
      for line in lines:
        list2 = line.replace("\n", "").split(":", 1)
        redis_row_list.append(list2)
    file.close()
#将存在漏洞的数据保存到文件
def writefile(filename,context):
    fo = open(filename, "a")
    fo.write(context)
    fo.close()
#发送检测漏洞 reds.info
def redisSendFifo(threadID):
    
    redis_block_list=redis_row_list[(threadID-1)*thread_slit:threadID*thread_slit] # 多线程处理同个list，原理跟数据库手动分页差不多
    for line in redis_block_list:
        try:
            r=checkTimeOut(line)
            if "redis_build_id" in r:
                writefile(success_save_filename,line[0]+":"+line[1]+"\n")
                print(line[0]+":"+line[1]+" 存在未授权漏洞")
        except :
            writefile(timeout_save_filename,line[0]+":"+line[1]+"\n")
            print('检测超时：'+line[0]+":"+line[1])

#真正发送检测函数
@func_set_timeout(socket_timeout)#设定函数超执行时间_
def checkTimeOut(line):
    try:
        r=redis.Redis(host=line[0], port=line[1], db=0,socket_connect_timeout=socket_timeout)
        data=r.info()
        return data
    except :
        return "error"
#主函数
if __name__ == '__main__':
    s_time = time.time()
    readfile(file)
    thread_slit=math.ceil(len(redis_row_list)/thread_num)
    thread_list=[] #线程列表
    for i in range(1,thread_num+1):
        thread_tmp=myThread(i,"thread-"+str(i),i)#创建新线程
        thread_tmp.start()#开始执行线程
        thread_list.append(thread_tmp)#将创建的线程加入到线程列表，方便管理
    
    # 等待所有线程完成
    for t in thread_list:
        t.join()
    print ("全部检测完成，存在漏洞的目标会被保存在当前目录"+success_save_filename+"文件")
    print ("因网络太卡，检测超时的目标IP，保存在当前目录"+timeout_save_filename+"文件")
    
    e_time = time.time()
    writefile(success_save_filename,"use {:.5}s".format(e_time-s_time)+"\n")
    print("use {:.5}s".format(e_time-s_time))
    