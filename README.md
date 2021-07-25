# yang-redis
#redis 未授权检测 单线程 多线程 one many  thread
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
#
#
#
#
# 效果5分钟跑完1万条。线程20最适合，默认20线程，如线程太多，CPU带不动，检测效果会更差。
