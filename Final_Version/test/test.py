# str = "(39.434628,-300.490356,0)*(-3.318930,-325.067261,3)*(24.600719,-225.225098,21)"
# count = 0
# A_label = "0"
# B_label = "1"
# A_nums = 3
# B_nums = 3
# while str.find(",") != -1:
        
#         # 有星号，有两个以上坐标的情况
#         if str.find("*") != -1: 
            
#             # 星号的索引用来做数字定位
#             index = str.find("*")
            
#             # 提第一个二维码的完整信息，括号去掉，同时把这个二维码抹掉
#             info = str[1:index-1]
#             str = str[index+1:]
            
#             # 先提取二维码的编号
#             index_of_second_comma = info.rfind(",")   
#             apriltag_label = info[index_of_second_comma+1:]

#             # 判断是否为A或B，不是直接跳过
#             if apriltag_label != A_label and apriltag_label != B_label:               
#                 continue
            
#             # 判断A是否已经抓够
#             elif apriltag_label == A_label and A_nums == 0:
#                 continue
            
#             # 判断B是否已经抓够
#             elif apriltag_label == B_label and B_nums == 0:              
#                 continue

#             # 再提取坐标    
#             index_of_first_comma = info.find(",")
#             x_coordinate = info[:index_of_first_comma]
#             y_coordinate = info[index_of_first_comma+1:index_of_second_comma]
#             break
              
#         # 只有一个坐标的情况
#         elif str.find(",") != -1:
            
#             info = str[1:-1]
#             str = ""
            
#             # 先提取信息内的编号（字符串类型）
#             index_of_second_comma = info.rfind(",")   
#             apriltag_label = info[index_of_second_comma+1:]
            
#             # 判断是否为A或B，不是直接跳过
#             if apriltag_label != A_label and apriltag_label != B_label:                
#                 continue

#             # 判断A是否已经抓够
#             elif apriltag_label == A_label and A_nums == 0:              
#                 continue

#             # 判断B是否已经抓够
#             elif apriltag_label == B_label and B_nums == 0:
#                 continue

#             # 再提取坐标    
#             index_of_first_comma = info.find(",")
#             x_coordinate = info[:index_of_first_comma]
#             y_coordinate = info[index_of_first_comma+1:index_of_second_comma]
#             break

# print(x_coordinate, y_coordinate)


# print(count)
i = 0
a = [1,2]
def add(a, b):
    global i
    print(a,b)
    if i == 10:
        return    
    return add(a, b)

add(i+1, 2)