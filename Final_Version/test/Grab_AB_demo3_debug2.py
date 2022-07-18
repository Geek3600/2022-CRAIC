#!/usr/bin/python
#_*_ coding: utf_8 -*

import rospy
import socket
import time
import sys
import subprocess
from subprocess import PIPE, Popen
from move_base_msgs.msg import MoveBaseActionResult
from std_msgs.msg import String
# from apriltag_ros.msg import AprilTagDetectionArray

# 暂存位坐标
storage_cache_1 = "B1M1SetCmd;1;-50;170;-35;0;1#"
storage_cache_2 = "B1M1SetCmd;1;0;170;-35;0;1#"
storage_cache_3 = "B1M1SetCmd;1;50;170;-35;0;1#"
storage_cache_4 = "B1M1SetCmd;1;-50;220;-35;0;1#"
storage_cache_5 = "B1M1SetCmd;1;0;220;-35;0;1#"
storage_cache_6 = "B1M1SetCmd;1;50;220;-35;0;1#"

storage_cache_coordinate_A = [storage_cache_1, storage_cache_2, storage_cache_3]
storage_cache_coordinate_B = [storage_cache_4, storage_cache_5, storage_cache_6 ]

storage_cache_coordinate_A_copy = [storage_cache_1, storage_cache_2, storage_cache_3]
storage_cache_coordinate_B_copy = [storage_cache_4, storage_cache_5, storage_cache_6 ]

A_nums = 3
B_nums = 3 

# 存储弹出的暂存区指令
A_storage_pos = ""
B_storage_pos = ""

# AB方块的编号
A_label = "0"
B_label = "1"

def debug():
    arm_move(option="goto_obervation_pos")
    time.sleep(1)
    arm_move(option="go_home")
    time.sleep(1)    



# 二维码信息处理，同时检测是否是AB，
# 可能出现没有的情况(提取坐标和编号，根据参数来选择返回值是坐标还是二维码编号，或者三者都要)
def deal_with_apriltag_info(apriltag_bunble_info, option="coordinate"):
    
    global A_nums
    global B_nums

    # 提取返回指令中包含的全部坐标信息
    str = apriltag_bunble_info[18:-1]
    
    x_coordinate = None
    y_coordinate = None
    apriltag_label = None
   
    # 只要有逗号，就说明检测到了二维码，就要进行筛查
    while str.find(",") != -1:
        
        # 有星号，有两个以上坐标的情况
        if str.find("*") != -1: 
            
            # 星号的索引用来做数字定位
            index = str.find("*")
            
            # 提第一个二维码的完整信息，括号去掉，同时把这个二维码抹掉
            info = str[1:index-1]
            str = str[index+1:]
            
            # 先提取二维码的编号
            index_of_second_comma = info.rfind(",")   
            apriltag_label = info[index_of_second_comma+1:]
            

            # 判断是否为A或B，不是直接跳过
            if apriltag_label != A_label and apriltag_label != B_label:                             
                continue
            
            # 判断A是否已经抓够
            elif apriltag_label == A_label and A_nums == 0:
                continue
            
            # 判断B是否已经抓够
            elif apriltag_label == B_label and B_nums == 0:              
                continue

            # 再提取坐标    
            index_of_first_comma = info.find(",")
            x_coordinate = info[:index_of_first_comma]
            y_coordinate = info[index_of_first_comma+1:index_of_second_comma]
            break
              
        # 只有一个坐标的情况
        elif str.find(",") != -1:
            
            info = str[1:-1]
            str = ""
            
            # 先提取信息内的编号（字符串类型）
            index_of_second_comma = info.rfind(",")   
            apriltag_label = info[index_of_second_comma+1:]
            
            # 判断是否为A或B，不是直接跳过
            if apriltag_label != A_label and apriltag_label != B_label:                
                continue

            # 判断A是否已经抓够
            elif apriltag_label == A_label and A_nums == 0:              
                continue

            # 判断B是否已经抓够
            elif apriltag_label == B_label and B_nums == 0:
                continue

            # 再提取坐标    
            index_of_first_comma = info.find(",")
            x_coordinate = info[:index_of_first_comma]
            y_coordinate = info[index_of_first_comma+1:index_of_second_comma]
            break
    
   
    #选择返回值，返回的一定是A或B的方块的info
    if option == "label":
        return apriltag_label
    elif option == "coordinate+label":
        return x_coordinate, y_coordinate, apriltag_label
    else:
        return x_coordinate, y_coordinate  


# 机械臂移动函数，可选择功能
# TODO 去暂存区的部分还不够通用，里面是直接内定AB坐标的
def arm_move( x=None, y=None, apriltag_label=None, option="goto_grab_pos"):
    
    global storage_cache_coordinate_A
    global storage_cache_coordinate_B
    global A_nums
    global B_nums
    global A_storage_pos
    global B_storage_pos
    

    # 去暂存区,放一个方块，就抹掉一个位置
    if option == "goto_storage_pos": 

        if apriltag_label == A_label:
            send_data_for_goto_storage_pos = storage_cache_coordinate_A[0]
            tcp_socket.send(send_data_for_goto_storage_pos.encode())
            recvData_for_goto_storage_pos = tcp_socket.recv(1024) 

            
            # 抹去位置，保存每次弹出的位置指令，用于后面的数量校验
            # 注意这里要把另一个设置为None,这样可以很简单地就能知道最近一次弹出的是哪个方块
            # A_storage_pos = storage_cache_coordinate_A.pop(0)
            # B_storage_pos = None
            storage_cache_coordinate_A.pop(0)            
            A_nums -= 1
            
           
              
        elif apriltag_label == B_label:
            send_data_for_goto_storage_pos = storage_cache_coordinate_B[0]
            tcp_socket.send(send_data_for_goto_storage_pos.encode())
            recvData_for_goto_storage_pos = tcp_socket.recv(1024) 

            
            # 与上面一样
            # B_storage_pos = storage_cache_coordinate_B.pop(0)
            # A_storage_pos = None
            storage_cache_coordinate_B.pop(0)           
            B_nums -= 1


    # 去抓取位
    elif option == "goto_grab_pos": 
        send_data_for_goto_grab_pos = "B1M1SetCmd;1;-33;-180;1#"
        index = send_data_for_goto_grab_pos.find("1;") 
       
        # 利用切片将传来的二维码坐标参数插入指令中,使其完整
        send_data_for_goto_grab_pos = send_data_for_goto_grab_pos[:index+2] + x + ";" + y + send_data_for_goto_grab_pos[index+1:]
        tcp_socket.send(send_data_for_goto_grab_pos.encode())
        recvData_for_goto_grab_pos = tcp_socket.recv(1024) 

    
    # 去Home位 
    elif option == "go_home":
        send_data_for_arm_move = "B1M1SetCmd;1;0;230;70;0;1#"
        tcp_socket.send(send_data_for_arm_move.encode())
        recvData_for_go_home = tcp_socket.recv(1024) 


    # 去观察位
    elif option == "goto_obervation_pos":
        send_data_for_goto_obervation_pos ="B1M1SetCmd;1;0;-253;150;-180;1#"
        tcp_socket.send(send_data_for_goto_obervation_pos.encode())
        recvData_for_goto_obervation_pos = tcp_socket.recv(1024) 


# 气泵功能函数，可选择
def deflate_or_inhale(option="inhale"):
    # 吸气
    if option == "inhale":
        send_data_for_inhale = "B1M1Pump;1#"
        tcp_socket.send(send_data_for_inhale.encode())
        recvData_for_inhale = tcp_socket.recv(1024) 

    # 放气
    elif option == "deflate":
        send_data_for_deflate = "B1M1Pump;0#"
        tcp_socket.send(send_data_for_deflate.encode())
        recvData_for_deflate = tcp_socket.recv(1024) 


# 微调小车位置
def adjust_car_pos(x_adjust, y_adjust, apriltag_label):
    
    
    x_adjust = int(float(x_adjust))    
    
    if x_adjust > 85:# 如果车子偏左
       
        cmd = "rostopic pub /check std_msgs/String 'angule true 12 0.5 5'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()
        
        apriltag_bunble_info = check_apriltag()
        x_adjust, y_adjust, apriltag_label = deal_with_apriltag_info(apriltag_bunble_info, option="coordinate+label")
        
    elif x_adjust < -85:# 如果车子偏右
        
        cmd = "rostopic pub /check std_msgs/String 'angule true -12 0.5 5'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()
       
        apriltag_bunble_info = check_apriltag()
        x_adjust, y_adjust, apriltag_label = deal_with_apriltag_info(apriltag_bunble_info, option="coordinate+label")

    
    y_adjust = int(float(y_adjust))
    
    x_grab = "0"
    y_grab = "0"

    if y_adjust > -200: # 如果车子靠放置台太近
        y_offset = (y_adjust + 200)/1000.0 # 正值
        y_offset = str(y_offset)
        
        cmd = cmd = "rostopic pub /check std_msgs/String 'line true " + y_offset + " 0.2 0.01'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        res.terminate()
        
        apriltag_bunble_info = check_apriltag()
        x_grab, y_grab, apriltag_label = deal_with_apriltag_info(apriltag_bunble_info, option="coordinate+label")     
    
    elif y_adjust < -300: # 如果车子靠放置台太远
        y_offset = (y_adjust + 300)/1000.0 # 负值
        y_offset = str(y_offset)
        
        cmd = "rostopic pub /check std_msgs/String 'line true " + y_offset + " 0.2 0.01'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        res.terminate()
        
        apriltag_bunble_info = check_apriltag()
        x_grab, y_grab, apriltag_label = deal_with_apriltag_info(apriltag_bunble_info, option="coordinate+label")     
    
    return x_grab, y_grab, apriltag_label

# 相机检测二维码
def check_apriltag():
   
    send_data_for_checking_apriltag = "B1M1GetAdjustPose;1#"
    tcp_socket.send(send_data_for_checking_apriltag.encode())  
    recvData_for_checking_apriltag = tcp_socket.recv(1024)
    

    return recvData_for_checking_apriltag


# # 检测暂存区方块的数量，以及检测A、B各自的抓取量，并修正可能发生的空抓错误
# def check_numbers_of_blocks():
    
#     global storage_cache_coordinate_A
#     global storage_cache_coordinate_B
#     global A_nums
#     global B_nums
#     global A_storage_pos
#     global B_storage_pos

#     calculate_block_nums = (3 - A_nums) + (3 - B_nums) 

#     # 相机拍摄暂存区方块二维码
#     recvData_of_block_apriltag = check_apriltag()
    
#     # 一个方块都没有
#     if recvData_of_block_apriltag.find(",") == -1:
#         real_block_nums = 0
#     # 至少有一个
#     elif recvData_of_block_apriltag.find(",") != -1:
#         real_block_nums = recvData_of_block_apriltag.count('*') + 1
    
#     # 抓够就结束，由于我的设计，只要抓够6个，就一定是3个A，3个B
#     if real_block_nums == 6:
#         return "finished"


#     # 如果没抓够，就检测暂存区还差哪几个，因为AB位置是固定的
#     # 检测相机检测到的 “真实方块数量” 和 “机械臂外部计数得到的数量” 是否一致，用于修正
#     # 问题：万一是一致的，但是AB的数量是错的，最终加和恰好正确的呢?
#     # TODO(HuaYang Yuan): 在没有假设的情况下，如何检测真实方块数量中有A、B各自的数量？
   
#     # 一致则说明没有出现抓空的现象 ，
#     # elif real_block_nums == calculate_block_nums:  

#     #     pass
    
#     if real_block_nums != calculate_block_nums:   
#         '''
#         不一致则说明出现抓空的现象
#         my idea: 由于我的设定, A、B方块各自放到暂存区的顺序是固定的(都是从左往右依次放置), 
#                  而且每次抓取完之后都会进行一次暂存区的数量检查,
#                  所以空抓的现象会在放完之后被立刻发现, 我只需要把刚刚(也就是
#                  空抓)弹出的暂存区指令再给他放回去以及计数加回1就ok了 
#         '''
#         # 检测最近一次弹出的(也就是空抓空放的方块)的是A还是B

#         # 如果是A，则A_storage_pos不是None, B_storage_pos是None
#         if B_storage_pos != None:
#             storage_cache_coordinate_A.insert(0,B_storage_pos)
#            
#                
#             B_nums += 1
#         # 如果是B，则B_storage_pos不是None, A_storage_pos是None
#         elif A_storage_pos != None:
#             storage_cache_coordinate_B.insert(0,A_storage_pos)
#             if A_nums == 0:
#                 A_nums = "not"
#             A_nums += 1
#     return "not finished"



# 视觉抓取，data可查看为导航结果
def visual_grab(data):
   
    global A_nums
    global B_nums
    
    # 若成功到达目的地
    if data.status.status == 3:
       
    	# 设置机械臂速度
        send_data_for_arm_speed = "B1M1SetPTPPrm;200;200;1#"
        tcp_socket.send(send_data_for_arm_speed.encode())
        recvData_for_arm_speed = tcp_socket.recv(1024) 

        # 开始进行抓取循环
        while A_nums != 0 and B_nums != 0:
            
            # 每次抓之前，先查看暂存区的方块数量
            # if check_numbers_of_blocks() == "finished":
            #     pub.publish("Push_AB")
            #     rospy.signal_shutdown("tasked finished")
            #     break
                        

                # 去观察位（无参）
                arm_move(option="goto_obervation_pos")
                time.sleep(2.5)

                # 看二维码,返回看到的二维码信息，用于调整位置
                apriltag_coordinate_for_adjust = check_apriltag()
               
                # 二维码信息处理，同时筛出A或B信息
                x_adjust, y_adjust, apriltag_label = deal_with_apriltag_info(apriltag_coordinate_for_adjust, option="coordinate+label")
               
                # 如果码放台1的AB已经抓完，就退出,去码放台2
                # TODO 这里的时间可以想办法优化一下，能不能减少码放台1的AB抓完前的的一次观察步骤，或者说把这个观察步骤换顺序
                if x_adjust == None and y_adjust == None:
                    return 
                
                # 微调小车位置（有参）
                x_grab, y_grab, apriltag_label = adjust_car_pos(x_adjust, y_adjust, apriltag_label)
                time.sleep(1)
               

                # 去抓取位
                arm_move(x=x_grab, y=y_grab, apriltag_label =apriltag_label,  option="goto_grab_pos")
                time.sleep(1)
                
                # 吸气
                deflate_or_inhale(option="inhale")
                time.sleep(1)

                # 回到观察位（抬高机械臂）
                arm_move(option="goto_obervation_pos")
                time.sleep(1)
                
                # 回home位
                arm_move(option="go_home")
                time.sleep(1)

                # 去暂存区
                arm_move(apriltag_label=apriltag_label, option="goto_storage_pos")
                time.sleep(1)

                # 放气
                deflate_or_inhale(option="deflate")
                time.sleep(0.5)

                # 回home位（抬高）
                arm_move(option="go_home")
                time.sleep(1)
        
        
        pub.publish("PushAB")
        rospy.signal_shutdown("Grab_AB finished")


# 监听导航结果
def listen_navigation_result():
    rospy.Subscriber('move_base/result', MoveBaseActionResult, visual_grab)


# 导航到目标点
def navigation(target): 
     # 发送导航指令    
    send_data_for_navi = "B1GotoTarget;" + target + "#" 
    tcp_socket.send(send_data_for_navi.encode())
    recvData_for_navi = tcp_socket.recv(1024)   
        
    
        
    
           
'''
Greb_AB.py

初始化配置：
    1.初始化ros节点
    2.打开tcp
    3.打开话题(创建publisher发布导航结果,subscriber接受导航结果)
移动操作：
    1.导航到码放台1
    2.监听导航结果,是否到位
    3.视觉抓取(循环)
        1.检测暂存区方块数量，
        （假设每次抓的都对，只出现抓空的情况）
        1.机械臂去观察位(设置观察位坐标)
        2.查看二维码位置(用于微调小车位置)
        3.微调小车的位置
        4.再次查看二维码的位置(用于抓取)
        5.去抓取位
        6.吸气
        7.回到观察位
        8.回到home位
        9.用抓取位去到暂存位
        10.放气
        10.再回到home位
   
'''


if __name__ == '__main__':
    
    # 创建TCP连接
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server_addr = ("192.168.31.200", 9093)
    tcp_socket.connect(server_addr)
    
    # 初始化ros节点
    rospy.init_node('Grab_AB', anonymous=True) 
    pub = rospy.Publisher("taker", String, queue_size=10)
    # 导航到码放台1 
    
    
    # 导航到码放台1
    navigation("1")
   
    # 监听导航结果话题,在回调函数中进行视觉抓取(主要的函数)
    listen_navigation_result()
    
    # # 导航到码放台2
    # navigation("2")
    # # 监听导航结果话题,在回调函数中进行视觉抓取(主要的函数)
    # listen_navigation_result()

    rospy.spin()

 


