# _*_  coding:utf-8 _*_
#    redis未授权检测脚本 单线程版
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
#       python.exe ./redisOneThread.py
#

import redis,time
from func_timeout import func_set_timeout
import func_timeout


file="./url.txt"
success_save_filename="./success_redisOneThread.txt"
redis_row_list=[]
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
#发送检测漏洞语句reds.info
def redisSendFifo():
    for line in redis_row_list:
        print("准备检测："+line[0])
        try:
            r=checkTimeOut(line)
            if "redis_build_id" in r:
                writefile(success_save_filename,line[0]+":"+line[1]+"\n")
                print(line[0]+":"+line[1]+" 存在未授权漏洞")
        except func_timeout.exceptions.FunctionTimedOut:
            writefile("./chaoshi.txt",line[0]+":"+line[1]+"\n")
            print('执行函数超时')
            
        
#真正发送检测函数
@func_set_timeout(5)#设定函数超执行时间_
def checkTimeOut(line):
    try:
        r=redis.Redis(host=line[0], port=line[1], db=0,socket_connect_timeout=3)
        return r.info()
    except :
        return "error"
#主函数
if __name__ == '__main__':

    readfile(file)
    redisSendFifo()
    
    