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

def adjust_move(x_adjust, y_adjust, label):
    
    
    X = int(float(x_adjust))
    
    if X > 85:
        cmd = "rostopic pub /check std_msgs/String 'angule true 12 0.5 5'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()
        x_adjust, y_adjust = get_adjust_coordinate(label)

    elif X < -85:
        cmd = "rostopic pub /check std_msgs/String 'angule true -12 0.5 5'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()
        x_adjust, y_adjust = get_adjust_coordinate(label)    

    Y = int(float(y_adjust))
    if Y > -200:
        y_offset = (Y + 200) / 1000.0
        y_offset = str( y_offset)
        cmd = "rostopic pub /check std_msgs/String 'line true " + y_offset + " 0.2 0.01'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        res.terminate()
        x_adjust, y_adjust = get_adjust_coordinate(label)
	
    elif Y < -300:
        y_offset = (300 + Y) / 1000.0
        y_offset = str( y_offset)
        cmd = "rostopic pub /check std_msgs/String 'line true "+ y_offset +" 0.2 0.01'"
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2.5)
        res.terminate()
        x_adjust, y_adjust = get_adjust_coordinate(label)
    x_adjust = str(float(x_adjust)-4)
    y_adjust = str(float(y_adjust)-14)
    
    return x_adjust, y_adjust
