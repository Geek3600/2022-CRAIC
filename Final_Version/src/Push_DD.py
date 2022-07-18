#!/usr/bin/python 
# -*- coding: utf-8 -*
import socket
import rospy 
import time
import sys
import subprocess
from subprocess import Popen,PIPE
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseActionResult 

storage_cache_1="B1M1SetCmd;1;-50;160;-35;0;1#"

storage_cache_coordinate = [storage_cache_1]

Push_label = "21" 

# 看二维码
def check_apriltag():
   
    send_data_for_check_apriltag = "B1M1GetAdjustPose;1#"
    tcp_socket.send(send_data_for_check_apriltag.encode()) 
    recvData_for_check_apriltag = tcp_socket.recv(1024)
    return recvData_for_check_apriltag
# 导航
def navigation(target):
    send_data_for_navi = "B1GotoTarget;" + target + "#" 
    tcp_socket.send(send_data_for_navi.encode())
    recvData_for_navi = tcp_socket.recv(1024)
# 吸气
def inhale():
    # 吸气
    send_data_for_inhale = "B1M1Pump;1#"
    tcp_socket.send(send_data_for_inhale.encode())
    recvData_for_inhale = tcp_socket.recv(1024)
    time.sleep(0.5)
# 放气
def deflate():
     # 放气
    send_data_for_deflate = "B1M1Pump;0#"
    tcp_socket.send(send_data_for_deflate.encode())
    recvData_for_deflate = tcp_socket.recv(1024)
    time.sleep(0.5)
# 去home位
def go_home():
   
    send_data_for_go_home= "B1M1SetCmd;1;0;200;100;0;1#" 
    tcp_socket.send(send_data_for_go_home.encode())
    time.sleep(1)

# 去暂存位
def goto_storage_pos(storage_cache_coordinate):
    # 去暂存区
    send_data_for_goto_storage_pos = storage_cache_coordinate
    tcp_socket.send(send_data_for_goto_storage_pos.encode())
    recvData_for_goto_storage_pos = tcp_socket.recv(1024)
# 去放置位
def goto_push_pos():
    send_data_for_goto_push_pos = "B1M1SetCmd;1;0;-300;50;-180;1#" 
    tcp_socket.send(send_data_for_goto_push_pos.encode())
    time.sleep(2.3)
# 提取二维码信息

def deal_with_apriltag(apriltag_bundle_info, apriltag_label):
    str = apriltag_bundle_info[18:-1]
    
    if str=="":
        return 0

    while str.find('*') != -1:
        index = str.find('*')
        info = str[1:index-1]

        if info[-3:-1] == apriltag_label:
            return info
        
        str = str[index+1: ]

    if str[-3:-1] == apriltag_label:
        return str[1:-1]
    else:
        return 0

# 去观察位
def goto_obervation_pos():

    # 去观察位
    send_data_for_goto_observation_pos = "B1M1SetCmd;1;0;-243;120;-180;1#" 
    tcp_socket.send(send_data_for_goto_observation_pos.encode())
    recvData_for_goto_observation_pos = tcp_socket.recv(1024)

# 微调位置    
def adjust_move(x_adjust, y_adjust):
    
    
    X = int(float(x_adjust))
    
    if X > 85:
        cmd = "rostopic pub /check std_msgs/String 'angule true 12 0.5 5'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()

    elif X < -85:
        cmd = "rostopic pub /check std_msgs/String 'angule true -12 0.5 5'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()

    Y = int(float(y_adjust))
    if Y > -200:
        y_offset = (Y + 200) / 1000.0
        y_offset = str( y_offset)
        cmd = "rostopic pub /check std_msgs/String 'line true " + y_offset + " 0.2 0.01'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()
    
	
    elif Y < -300:
        y_offset = (300 + Y) / 1000.0
        y_offset = str( y_offset)
        cmd = "rostopic pub /check std_msgs/String 'line true "+ y_offset +" 0.2 0.01'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()

# 放置函数
def goto_push(storage_cache_coordinate):
    
    go_home()
    goto_storage_pos(storage_cache_coordinate)
    time.sleep(2.5)
    inhale()
    go_home()
    goto_push_pos()
    deflate()
    go_home()

# 导航到位的回调函数
def callback(data):
    
   
    if data.status.status == 3:
        
        # # 去观察位
        # goto_obervation_pos()
        # time.sleep(2)
        # #看二维码
        # recvData_for_check_apriltag = check_apriltag()
        
        # # 提取二维码信息
        # apriltag_info = deal_with_apriltag(recvData_for_check_apriltag, Push_label)
        
        # # 提取二维码坐标
        # index_first_comma = apriltag_info.find(',') 
        # x_adjust = apriltag_info[ :index_first_comma-1]
        # index_second_comma = apriltag_info.rfind(',') 
        # y_adjust = apriltag_info[index_first_comma + 1 : index_second_comma]
       
        # # 微调位置
        # adjust_move(x_adjust, y_adjust)
        time.sleep(2)
        # 开始放置
        
        goto_push(storage_cache_coordinate[0])
            

    pub.publish("GrabDD")
    rospy.signal_shutdown("task finished")

# 监听导航结果
def listen_navi_result():
    
    rospy.Subscriber('move_base/result', MoveBaseActionResult, callback) 
    
# 监听到任务开始的回调函数
# def callback_for_task_begin(msg):
    
#     if msg.data == "PushD":
#         navigation("D")  
#         listen_navi_result()


if __name__ == '__main__': 
    
    # TCP连接
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server_addr = ("192.168.31.200", 9093)
    tcp_socket.connect(server_addr) 
    
    #初始化ros结点
    rospy.init_node('PushD', anonymous=True)
    pub = rospy.Publisher('taker', String, queue_size = 100)
    
    
    # 监听任务是否开始
    # rospy.Subscriber("taker", String, callback_for_task_begin)
    navigation("D")  
    listen_navi_result()

    rospy.spin()




   




