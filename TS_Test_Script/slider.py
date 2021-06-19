import numpy as np
import cv2,time,random
import os,json
from matplotlib import pyplot as plt

# 可调式的一些常量
# 边距(背景图之外的距离)
IMAGE_TOP = 70
IMAGE_LEFT = 7

# 背景图宽 
BG_IMG_MARGIN = 5
BG_IMG_H = 290 - 2 * BG_IMG_MARGIN
BG_IMG_W = 576 - 2 * BG_IMG_MARGIN

SLIDER_IMG_H = 55
SLIDER_MARGIN_TOP = 40 + BG_IMG_H + 2 * BG_IMG_MARGIN

# 框框高高(扣去的圆角)
BOX_IMG_H = 72
BOX_IMG_W = 60

# 边缘检测亮度范围
BRIGHT_LOW = 0.3
BRIGHT_HIGH = 1

def show(name):
    '''展示圈出来的位置'''
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def detect(image_path,showit):
    # 读取背景图
    img_bg = cv2.imread(image_path, 0)
    # 截取要查找的滑块背景部分,并做高斯处理
    y1 = IMAGE_TOP + SLIDER_MARGIN_TOP
    y2 = y1 + SLIDER_IMG_H
    x1 = IMAGE_LEFT
    x2 = x1 + BG_IMG_W + 2 * BG_IMG_MARGIN
    img_gb_slider = img_bg[y1:y2,x1:x2]
    # img_gb_slider = cv2.GaussianBlur(img_gb_slider, (3, 3), 0)

    # 读取滑块图
    img_find = cv2.imread("/Users/chenyun/Projects/ocrtext/TS_Test_Script/slider.jpg", 0)
    # img_find = cv2.GaussianBlur(img_find, (3, 3), 0)

    # 滑块匹配度
    score = cv2.matchTemplate(cv2.Canny(img_find, 50, 150), cv2.Canny(img_gb_slider, 50, 150), cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(score)
    start_x, _ = max_loc
    start_x = start_x + x1

    # 截取要查找图背景部分,并做高斯处理(比原图会小一点)
    y1 = IMAGE_TOP + BG_IMG_MARGIN 
    y2 = y1 + BG_IMG_H
    x1 = IMAGE_LEFT + BG_IMG_MARGIN 
    x2 = x1 + BG_IMG_W
    img_bg = img_bg[y1:y2,x1:x2]
    img_bg = cv2.GaussianBlur(img_bg, (3, 3), 0)
    bg_bright_avg = img_bg.mean()
    
    slider_x = start_x - x1  #查找到x需要变化一下
    if slider_x < 0:
        slider_x = 0

    # 读取灰框图
    img_find = cv2.imread("/Users/chenyun/Projects/ocrtext/TS_Test_Script/box.jpg", 0)
    # 第一次查找黑框匹配度
    score = cv2.matchTemplate(cv2.Canny(img_find, 50, 150), cv2.Canny(img_bg, bg_bright_avg*BRIGHT_LOW, bg_bright_avg), cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(score)
    _, box_y = max_loc

    # 再次截取图像范围,以查找第二个框:
    y1 = box_y
    y2 = y1 + BOX_IMG_H + 15
    x1 = 0 
    x2 = x1 + BG_IMG_W
    img_bg = img_bg[y1:y2,x1:x2]
    bg_bright_avg = img_bg.mean()

    score = cv2.matchTemplate(cv2.Canny(img_find, 50, 150), cv2.Canny(img_bg, bg_bright_avg*0.2, bg_bright_avg), cv2.TM_CCOEFF_NORMED)
    box_list = []
    while True:
        _, _, _, max_loc = cv2.minMaxLoc(score)
        x,y = max_loc
        if score[y][x] == -100:
            break
        xend = x + BOX_IMG_W + 11
        if x not in range(slider_x - BOX_IMG_W - 20,slider_x + BOX_IMG_W + 20) and xend + 3 < BG_IMG_W:
            diffs = (img_bg[y,x-3] + img_bg[y,x-2]) - (img_bg[y,x+3] + img_bg[y,x+2])
            diffe = (img_bg[y,xend+3] + img_bg[y,xend+2]) - (img_bg[y,xend-3] + img_bg[y,xend-2])
            if diffs > 15 and diffe > 15:
                if len(box_list) < 1:
                    box_list.append(x)
                elif abs(x - box_list[0])>BOX_IMG_W + 20:
                    box_list.append(x)
                    break
        score[y][x] = -100

    # 截取对比图
    y1 = 2
    y2 = y1 + BOX_IMG_H
    x1 = slider_x
    x2 = x1 + BOX_IMG_W
    img_find = img_bg[y1:y2,x1:x2]
    find_bright_avg = img_find.mean()

    if len(box_list) == 2:
        x1 = box_list[0]
        x2 = x1 + BOX_IMG_W
        box1_img = img_bg[y1:y2,x1:x2]
        x1 = box_list[1]
        x2 = x1 + BOX_IMG_W
        box2_img = img_bg[y1:y2,x1:x2]
        
        avg1 = box1_img.mean()
        avg2 = box2_img.mean()
        
        for y in range(0,BOX_IMG_H):
            for x in range(0,BOX_IMG_W):
                box1_img[y,x] = box1_img[y,x] * find_bright_avg/avg1
                box2_img[y,x] = box2_img[y,x] * find_bright_avg/avg2

        bring_low = find_bright_avg * BRIGHT_LOW
        bring_high = find_bright_avg * BRIGHT_HIGH
        score1 = cv2.matchTemplate(cv2.Canny(img_find, bring_low, bring_high), cv2.Canny(box1_img, bring_low, bring_high), cv2.TM_CCOEFF_NORMED)
        score2 = cv2.matchTemplate(cv2.Canny(img_find, bring_low, bring_high), cv2.Canny(box2_img, bring_low, bring_high), cv2.TM_CCOEFF_NORMED)
        if score1[0][0] == 1:
            end_x = box_list[1] + BG_IMG_MARGIN + IMAGE_LEFT
            title5 = "2"
        elif score2[0][0] == 1:
            end_x = box_list[0] + BG_IMG_MARGIN + IMAGE_LEFT
            title5 = "1"
        elif score1[0][0] >= score2[0][0]:
            end_x = box_list[0] + BG_IMG_MARGIN + IMAGE_LEFT
            title5 = "1"
        else:
            end_x = box_list[1] + BG_IMG_MARGIN + IMAGE_LEFT
            title5 = "2"

        box_score1 = str(score1[0][0])
        box_score2 = str(score2[0][0])
    else:
        box1_img = np.zeros((BOX_IMG_H, BOX_IMG_W), np.uint8)
        box2_img = box1_img
        end_x = 0
        box_score1 = "-1"
        box_score2 = "-1"
        box_list.append(0)
        box_list.append(0)
        title5 = "2"

    # 展示图片
    if showit:
        showimg = cv2.imread(image_path)

        cv2.rectangle(img_bg, (box_list[0], 0), (box_list[0]+BOX_IMG_W, BOX_IMG_H), (255,255,255),2)
        cv2.rectangle(img_bg, (box_list[1], 0), (box_list[1]+BOX_IMG_W, BOX_IMG_H), (255,255,255),2)

        cv2.line(showimg, (start_x, IMAGE_TOP), (start_x,450), (0,0,0), 3)
        cv2.line(showimg, (end_x, IMAGE_TOP), (end_x,450), (255,23,140), 3)

        
        titles = [title5,box_score1,box_score2,title5,image_path[-14:]]
        images = [img_find,box1_img,box2_img,img_bg,showimg]
        for i in range(len(images)):
            if i == 4:
                # plt.figure(figsize=(5,5))
                images[i] = images[i][...,::-1]
            plt.subplot(2,3,i+1),plt.imshow(images[i],cmap='gray', vmin=0, vmax=255)
            plt.title(titles[i])
            plt.xticks([]),plt.yticks([])
        plt.show()

    return start_x,end_x

if __name__ == '__main__':
    t1 = time.time()

    work_dir = "/Users/chenyun/Downloads/B/"
    conti = True
    for parent, dirnames, filenames in os.walk(work_dir):
            for filename in filenames:
                # if filename == "1623319855.png":
                #     conti = True
                # else:
                #     conti = False
                if conti:
                    print(filename)
                    file_path = os.path.join(parent, filename)
                    slider_x,box_x = detect(file_path,False)

                    # 展示结果
                    showimg = cv2.imread(file_path)
                    showimg = showimg[70:450,0:576]
                    cv2.line(showimg, (slider_x, 0), (slider_x,450), (0,0,0), 2)
                    cv2.line(showimg, (box_x, 0), (box_x,450), (255,23,140), 2)
                    show(showimg)

    # current_path = os.path.dirname(__file__)
    # Filediff = os.path.join(current_path, "res_diff.json")
    # with open(Filediff, 'r') as json_file_diff:
    #     data = json.load(json_file_diff)
    # for name in data.keys():
    #     file_path = os.path.join(work_dir, name + ".png")
    #     # print(file_path)
    #     slider_x,box_x = detect(file_path,True)

    print(time.time()-t1)
    # print(top_left)
