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
# from apriltag_ros.msg import AprilTagDetectionArray
from adjust_move import adjust_move

storage_cache_1="B1M1SetCmd;1;-60;160;-35;0;1#"
storage_cache_2="B1M1SetCmd;1;-10;160;-35;0;1#"
storage_cache_3="B1M1SetCmd;1;40;160;-35;0;1#"
storage_cache_4="B1M1SetCmd;1;-60;220;-35;0;1#"
storage_cache_5="B1M1SetCmd;1;-10;220;-35;0;1#"
storage_cache_6="B1M1SetCmd;1;40;220;-35;0;1#"
storage_cache_coordinate = [storage_cache_1, storage_cache_2, storage_cache_3, storage_cache_4, storage_cache_5, storage_cache_6]


# AB 的标签
A_label = "0"
B_label = "1"

B_nums = 3
A_nums = 3

# 气泵吸气
def inhale():
    # 吸气
    send_data_for_inhale = "B1M1Pump;1#"
    tcp_socket.send(send_data_for_inhale.encode())
    recvData_for_inhale = tcp_socket.recv(1024)
    
    time.sleep(0.5)

# 去观察位
def goto_obervation_pos():

    # 去观察位
    send_data_for_goto_observation_pos = "B1M1SetCmd;1;0;-243;80;-180;1#" 
    tcp_socket.send(send_data_for_goto_observation_pos.encode())
    recvData_for_goto_observation_pos = tcp_socket.recv(1024)
    
# 去home位
def go_home():
    send_data_for_go_home = "B1M1SetCmd;1;0;200;150;0;1#" 
    tcp_socket.send(send_data_for_go_home.encode())
    recvData_for_go_home = tcp_socket.recv(1024)

# 抬高机械臂
def lift():
    send_data17 = "B1M1SetCmd;1;0;230;70;0;1#" 
    tcp_socket.send(send_data17.encode())
    recvData = tcp_socket.recv(1024)
    time.sleep(0.5)

# 去抓取位
def goto_grab_pos(x_grab, y_grab):
    
    send_data_for_goto_grab_pos = "B1M1SetCmd;1;-28;-180;1#"
    index = send_data_for_goto_grab_pos.find("1;")
    send_data_for_goto_grab_pos = send_data_for_goto_grab_pos[:index+2] + x_grab + ";" + y_grab + send_data_for_goto_grab_pos[index+1:]  
    tcp_socket.send(send_data_for_goto_grab_pos.encode())
    recvData_for_goto_grab_pos = tcp_socket.recv(1024)
    time.sleep(1)

#去暂存位
def goto_storage_pos(storage_cache_coordinate):
    # 去暂存区
    send_data_for_goto_storage_pos = storage_cache_coordinate
    tcp_socket.send(send_data_for_goto_storage_pos.encode())
    recvData_for_goto_storage_pos = tcp_socket.recv(1024)
    
# 气泵放气
def deflate():
     # 放气
    send_data_for_deflate = "B1M1Pump;0#"
    tcp_socket.send(send_data_for_deflate.encode())
    recvData_for_deflate = tcp_socket.recv(1024)
    time.sleep(0.5)

# 抓取
def Grab(x_grab, y_grab, storage_cache_coordinate):

    goto_grab_pos(x_grab,y_grab)

    inhale()

    goto_obervation_pos()
    time.sleep(0.5)

    go_home()
    time.sleep(0.5)

    goto_storage_pos(storage_cache_coordinate)
    time.sleep(3)

    deflate()

    go_home()
    time.sleep(1)
    
def check_apriltag():
   
    send_data_for_check_apriltag = "B1M1GetAdjustPose;1#"
    tcp_socket.send(send_data_for_check_apriltag.encode()) 
    recvData_for_check_apriltag = tcp_socket.recv(1024)
    print(recvData_for_check_apriltag)
    return recvData_for_check_apriltag

def navigation(target):
    send_data_for_navi = "B1GotoTarget;" + target + "#" 
    tcp_socket.send(send_data_for_navi.encode())
    recvData_for_navi = tcp_socket.recv(1024)

# 提取二维码信息
def deal_with_apriltag(apriltag_bundle_info, apriltag_label):
    str = apriltag_bundle_info[18:-1]
    
    if str=="":
	    return 0

    while str.find('*') != -1:
        index = str.find('*')
        info = str[1:index-1]

        if info[-1] == apriltag_label:
            return info
        
        str = str[index+1: ]

    if str[-2] == apriltag_label:
        return str[1:-1]
    else:
        return 0

# 看二维码 + 提取二维码信息中的坐标
def get_adjust_coordinate(label):
    
    # 看二维码
    recvData_for_check_apriltag = check_apriltag()
    apriltag_info = deal_with_apriltag(recvData_for_check_apriltag, label)

    if apriltag_info == 0:
        go_home()
        return

    index_first_comma = apriltag_info.find(',') 
    x = apriltag_info[ :index_first_comma-1]
    index_second_comma = apriltag_info.rfind(',') 
    y = apriltag_info[index_first_comma + 1 : index_second_comma]
    # x, y = adjust_move(x, y, label)
    return x, y



def set_arm_speed():
    send_data_for_arm_speed = "B1M1SetPTPPrm;200;200;1#"
    tcp_socket.send(send_data_for_arm_speed.encode())
    recvData_for_arm_speed = tcp_socket.recv(1024)


def goto_grab(label, storage_cache_coordinate):
   
    goto_obervation_pos()
    time.sleep(2.5)   

    recvData_for_check_apriltag = check_apriltag()
   
    apriltag_info = deal_with_apriltag(recvData_for_check_apriltag, label)
   
  
    #如果没看到二维码，结束
    if apriltag_info == 0:
        return 0

    # 看到就提取坐标
    index_first_comma = apriltag_info.find(',') 
    x = apriltag_info[ :index_first_comma-1]
    index_second_comma = apriltag_info.rfind(',') 
    y = apriltag_info[index_first_comma + 1 : index_second_comma]

    # 微调，加再看二维码
    x_grab, y_grab = adjust_move(x, y, label)
    
    # 抓+放，最后机械臂位于home位
    Grab(x_grab, y_grab, storage_cache_coordinate)


    return 1



def callback(data):
    
    global A_nums
    global B_nums
    if data.status.status == 3:
        # 设置机械臂速度
        set_arm_speed()
        
        i = 0
        mark_a = 1
        mark_b = 1

        while A_nums:
            mark_a = goto_grab(A_label, storage_cache_coordinate[i])
            if mark_a == 0:
                break
            else:
                i = i + 1 
                A_nums = A_nums - 1

        while B_nums:
            mark_b = goto_grab(B_label, storage_cache_coordinate[i])
            if mark_b == 0:
                break
            else:
                i = i + 1
                B_nums = B_nums - 1
            
        if mark_a == 0 or mark_b == 0:
            go_home()
            time.sleep(0.5)
            navigation("2")
            time.sleep(10)

            while A_nums:
                goto_grab(A_label, storage_cache_coordinate[i])
                i = i + 1
                A_nums = A_nums - 1
            while B_nums:
                goto_grab(B_label, storage_cache_coordinate[i])
                i = i + 1
                B_nums= B_nums - 1
            go_home()

        pub.publish("PushAB")
        rospy.signal_shutdown("task finished")
        
	
def listen_navi_result():
    
    rospy.Subscriber('move_base/result', MoveBaseActionResult, callback)
   
    
    
if __name__ == '__main__': 
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server_addr = ("192.168.31.200", 9093)
    tcp_socket.connect(server_addr)  
    rospy.init_node('CalibrateCamera', anonymous=True)
        
        
    goto_grab_pos("0","-220")
    time.sleep(8)
    goto_obervation_pos()
    time.sleep(2.5)
    x,y = get_adjust_coordinate(A_label)
    print(x,y)
    goto_grab_pos(x,y)

    rospy.spin()
    

    
    

    
