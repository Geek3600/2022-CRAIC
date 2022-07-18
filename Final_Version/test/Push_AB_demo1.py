#!/usr/bin/python 
# -*- coding: utf-8 -*
import socket
import rospy
import time
import subprocess
from subprocess import PIPE, Popen
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseActionResult


storage_cache_1 = "B1M1SetCmd;1;-50;170;-35;0;1#"
storage_cache_2 = "B1M1SetCmd;1;0;170;-35;0;1#"
storage_cache_3 = "B1M1SetCmd;1;50;170;-35;0;1#"
storage_cache_4 = "B1M1SetCmd;1;-50;220;-35;0;1#"
storage_cache_5 = "B1M1SetCmd;1;0;220;-35;0;1#"
storage_cache_6 = "B1M1SetCmd;1;50;220;-35;0;1#"

storage_cache_coordinate_A = [storage_cache_1, storage_cache_2, storage_cache_3]
storage_cache_coordinate_B = [storage_cache_4, storage_cache_5, storage_cache_6 ]

A_label = "0"
B_label = "1"

A_nums = 3
B_nums = 3



def deal_with_apriltag_info(apriltag_bunble_info, label_1= None, label_2= None,option="coordinate"):
    
    # 提取返回指令中包含的全部坐标信息
    str = apriltag_bunble_info[18:-1]
    
    
    # 有星号，说明至少检测到了两个二维码；无星号但有逗号，说明只检测到一个二维码
    while str.find("*") != -1 or str.find(",") != -1:
           
        # 有星号，有两个以上坐标的情况
        if str.find("*") != -1: 
            
            # 星号的索引用来做数字定位
            index = str.find("*")
            
            # 提第一个二维码的完整信息，括号去掉，同时把这个二维码抹掉
            info = str[1:index-1]
            str = str[index+1:]
            
            # 先提取二维码的编号
            index_second_comma = info.rfind(",")   
            apriltag_label = info[index_second_comma+1:]
            
            # 判断是否为A或B，不是直接跳过
            if apriltag_label != label_1 or apriltag_label != label_2:
                x_coordinate = None
                y_coordinate = None
                apriltag_label = None
                continue
            # 判断A是否已经抓够
            elif apriltag_label == label_1 and label_2 == "yes":
                x_coordinate = None
                y_coordinate = None
                apriltag_label = None
                continue
            # 判断B是否已经抓够
            elif apriltag_label == label_1 and label_2 == "yes":
                x_coordinate = None
                y_coordinate = None
                apriltag_label = None
                continue

            # 再提取坐标    
            index_first_comma = info.find(",")
            x_coordinate = info[:index_first_comma]
            y_coordinate = info[index_first_comma+1:index_second_comma]
            break
              
        # 只有一个坐标的情况
        elif str.find(",") != -1:
            
            info = str[1:-1]
            # str = ""
            
            # 先提取信息内的编号（字符串类型）
            index_second_comma = info.rfind(",")   
            apriltag_label = info[index_second_comma+1:]
            # 判断是否为A或B，不是直接跳过
            if apriltag_label != label_1 or apriltag_label != label_2:
                x_coordinate = None
                y_coordinate = None
                apriltag_label = None
                continue
            # 判断A是否已经抓够
            elif apriltag_label == label_1 and A_isfull == label_2:
                x_coordinate = None
                y_coordinate = None
                apriltag_label = None
                continue
            # 判断B是否已经抓够
            elif apriltag_label == label_1 and B_isfull == label_2:
                x_coordinate = None
                y_coordinate = None
                apriltag_label = None
                continue

            # 再提取坐标    
            index_first_comma = info.find(",")
            x_coordinate = info[:index_first_comma]
            y_coordinate = info[index_first_comma+1:index_second_comma]
            break
      
    #选择返回值，返回的一定是A或B的方块的info
    if option == "label":
        return apriltag_label
    elif option == "coordinate+label":
        return x_coordinate, y_coordinate, apriltag_label
    else:
        return x_coordinate, y_coordinate  


def arm_move( x=None, y=None, apriltag_label=None, option="goto_grab_pos"):
    
    global storage_cache_coordinate_A
    global storage_cache_coordinate_B
   
    
    # 去暂存区,放一个方块，就抹掉一个位置
    if option == "goto_storage_pos": 

        if apriltag_label == A_label:
            send_data_for_goto_storage_pos = storage_cache_coordinate_A[0]
            tcp_socket.send(send_data_for_goto_storage_pos.encode())
            
            storage_cache_coordinate_A.pop(0)
            A_nums -=1 
        
        
        elif apriltag_label == B_label:
            send_data_for_goto_storage_pos = storage_cache_coordinate_B[0]
            tcp_socket.send(send_data_for_goto_storage_pos.encode())
   
            storage_cache_coordinate_B.pop(0)
            B_nums -= 1
            
    # 去抓取位
    elif option == "goto_grab_pos": 
        send_data_for_goto_grab_pos = "B1M1SetCmd;1;-33;-180;1#"
        index_of_1 = send_data_for_goto_grab_pos.find("1") 
    
        # 利用切片将传来的二维码坐标参数插入指令中,使其完整
        send_data_for_goto_grab_pos = send_data_for_goto_grab_pos[:index_of_1+2] + x + ";" + y + send_data_for_goto_grab_pos[index_of_1+1:]
        tcp_socket.send(send_data_for_goto_grab_pos.encode())
        
    
    # 去Home位 
    elif option == "go_home":
        send_data_for_arm_move = "B1M1SetCmd;1;0;230;70;0;1#"
        tcp_socket.send(send_data_for_arm_move.encode())
        

    # 去观察位
    elif option == "goto_obervation_pos":
        send_data_for_arm_move ="B1M1SetCmd;1;0;-253;150;-180;1#"
        tcp_socket.send(send_data_for_arm_move.encode())



def deflate_or_inhale(option="inhale"):
    # 吸气
    if option == "inhale":
        send_data_for_inhale = "B1M1Pump;1#"
        tcp_socket.send(send_data_for_inhale.encode())
        
    # 放气
    elif option == "deflate":
        send_data_for_deflate = "B1M1Pump;0#"
        tcp_socket.send(send_data_for_deflate.encode())

# 将放置方块到盒子的步骤全部封装起来
def push(label):
    arm_move(apriltag=label, option="goto_storage_pos")
    time.sleep(1)
    deflate_or_inhale("inhale")
    arm_move(option="go_home")
    time.sleep(0.5)
    arm_move(option="goto_observation_pos")
    time.sleep(1)
    deflate_or_inhale("deflate")
    arm_move(option="go_home")
    time.sleep(0.5)



def visual_push(data):
    if data.status.status == 3:
        send_data_for_arm_speed = "B1M1SetPTPPrm;200;200;1#"
        tcp_socket.send(send_data_for_arm_speed.encode())

        # TODO 位置微调,可能不用

        while A_nums != 0 and B_nums != 0:
            push(A_label)
            push(B_label)
        

    pub.Publisher("GrabAC")
    rospy.signal_shutdown("Push_AB finished")   




# 导航到目标点
def navigation(target): 
     # 发送导航指令    
    send_data_for_navi = "B1GotoTarget;" + target + "#" 
    tcp_socket.send(send_data_for_navi.encode())
        
# 监听导航结果
def listen_navigation_result():
    rospy.Subscriber('move_base/result', MoveBaseActionResult, visual_push)

# 由话题消息引起
def callback(msg):
    if msg.data == "PushAB":
        navigation("AB")
        listen_navigation_result()

    
if __name__ == '__main__':
   
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server_addr = ("192.168.31.200", 9093)
    tcp_socket.connect(server_addr)
    
    
    rospy.init_node('Push_AB', anonymous=True) 
    pub = rospy.Publisher('taker', String, queue_size = 10)
    rospy.Subscriber('taker', String, callback)
    

    rospy.spin()