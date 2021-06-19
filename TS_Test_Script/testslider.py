import requests
import base64
import time
from matplotlib import pyplot as plt
import cv2
import os
import json

current_path = os.path.dirname(__file__)
File = os.path.join(current_path, "res_data.json")
Filediff = os.path.join(current_path, "res_diff.json")
Data = {}
Datadiff = {}
# print(Data)
countt = 0

def base64encode(path):
    with open(path,"rb") as f:
        base64_data = base64.b64encode(f.read())
        return base64_data.decode()

def other(path):
    t1 = time.time()
    url = "http://121.5.124.90/member/xiong_member.php"
    data = {
        'name':'185261',
        'item':'g',
        'be64': base64encode(path)
        }
    res = requests.post(url,data=data)
    x1 = res.json()["起点"]
    x2 = res.json()["终点"]
    return x1,x2,time.time()-t1

def my(path):
    t1 = time.time()
    url = "http://192.168.10.139:8099/api/slider/"
    files = {
        'file':open(path, 'rb')
        }
    res = requests.post(url,files=files)
    x1 = res.json()["res"][0]
    x2 = res.json()["res"][1]
    return x1,x2,time.time()-t1

def view(path,name):
    global Data,countt,Datadiff
    img_my=cv2.imread(path)
    img_my = cv2.cvtColor(img_my, cv2.COLOR_BGR2RGB)
    img_other = img_my.copy()
    h = 360

    if name in Data.keys():
        my_x1 = Data[name][0] or 0
        my_x2 = Data[name][1] or 0
        my_t = Data[name][2] or 0
        # if Data[name][6] == 3:
        #     my_x1,my_x2,my_t = my(path)
        #     Data[name][0] = my_x1
        #     Data[name][1] = my_x2
        #     Data[name][2] = my_t
        #     Data[name][6] = 4

        other_x1 = Data[name][3] or 0
        other_x2 = Data[name][4] or 0
        other_t = Data[name][5] or 0
        # saveinfo()
    else:
        my_x1,my_x2,my_t = my(path)
        other_x1,other_x2,other_t = other(path)
        Data[name] = [my_x1,my_x2,my_t,other_x1,other_x2,other_t]
        saveinfo()

    defr = 10
    
    # if not(abs(my_x1 - other_x1) < defr and abs(my_x2-other_x2) < defr):
    if defr:
        Datadiff[name] = Data[name]
        cv2.line(img_my, (my_x1,0),(my_x1,h), (0,0,0), 3)
        cv2.line(img_my, (my_x2,0),(my_x2,h), (140,23,255), 3)
        cv2.line(img_other, (other_x1,0),(other_x1,h), (0,0,0), 3)
        cv2.line(img_other, (other_x2,0),(other_x2,h), (140,23,255), 3)

        titles = ['fy: '+ str(my_t),'js: ' + str(other_t)]
        images = [img_my, img_other]
        for i in range(2):
            plt.subplot(1,2,i+1),plt.imshow(images[i])
            plt.title(titles[i])
            plt.xticks([]),plt.yticks([])
        countt = countt + 1
        print("次数:" + str(countt))
        plt.show()

def getinfo():
    global Data,File
    with open(File, 'r') as json_file_r:
        Data = json.load(json_file_r)

def saveinfo():
    global Data,File
    with open(File, 'w') as json_file_w:
        json.dump(Data, json_file_w)

def savediff():
    global Datadiff,Filediff
    with open(Filediff, 'w') as json_file_diff:
        json.dump(Datadiff, json_file_diff)

if __name__ == '__main__':
    if os.path.isfile(File):
        getinfo()
    
    countf = 1
    work_dir = "/Users/chenyun/Downloads/B/"
    for parent, dirnames, filenames in os.walk(work_dir):
            for filename in filenames:
                if filename[0] != ".":
                    file_path = os.path.join(parent, filename)
                    filename = filename[:-4]
                    print(countf,filename)
                    view(file_path,filename)
                    countf += 1

    savediff()
    saveinfo()
