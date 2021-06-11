import numpy as np
import cv2,time,random

def show(name):
    '''展示圈出来的位置'''
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def _tran_canny(image):
    """消除噪声"""
    return cv2.Canny(image, 50, 150)


def detect_boximg(image_path,block):
    """detect displacement"""
    # 读取三个图片
    img_bg_box = cv2.imread("/Users/chenyun/Projects/ocrtext/TS_Test_Script/box.jpg", 0)
    img_bg_slider = cv2.imread("/Users/chenyun/Projects/ocrtext/TS_Test_Script/slider.jpg", 0)
    image = cv2.imread(image_path, 0)
    
    # 做预处理 高斯模糊
    image = cv2.GaussianBlur(image, (3, 3), 0)
    w, h = image.shape[::-1]  # 宽
    image = image[0:h, block:w-block]
    w = w - block*2

    img_find_box = image[80:360, 0:w]
    img_find_slider = image[400:450, 0:w]

    # 查找滑块匹配度
    res = cv2.matchTemplate(_tran_canny(img_bg_slider), _tran_canny(img_find_slider), cv2.TM_CCOEFF_NORMED)

    # 获取最佳匹配的X轴
    _, _, _, max_loc = cv2.minMaxLoc(res)
    slider_x, _ = max_loc  # 获取x,y位置坐标


    # 查找灰色框匹配度
    score = cv2.matchTemplate(_tran_canny(img_bg_box), _tran_canny(img_find_box), cv2.TM_CCOEFF_NORMED)

    # 找出分数大于0.1的值
    high_score_arr = np.argwhere(score > 0.1)
    
    # 这些值中,y出现频率最高的
    count_y = np.bincount(high_score_arr[:,0])  # 列出y值的频次
    slider_y = np.argmax(count_y)        # y值出现最多的
    print(slider_x,slider_y)
    return slider_x,slider_y,score


def Compare_boximg(image_path):
    # 检测需要匹配的图形
    block = 15
    box_w,box_h = 62,72

    slider_x,slider_y,score = detect_boximg(image_path,block)
    image = cv2.imread(image_path, 0)
    w, h = image.shape[::-1]  # 宽
    image = image[80:h, block:w-block]
    w = w - block*2
    # 截取需要匹配的图片
    img_slider_box = image.copy()[slider_y:slider_y+box_h, slider_x:slider_x+box_w]

    img_slider_box = cv2.GaussianBlur(img_slider_box, (3, 3), 0)

    # 截取要识别的区块为长条形
    img_find_box = image[slider_y:slider_y+box_h,0:w]
    avg = img_find_box.mean()

    # img_find_box = cv2.GaussianBlur(img_find_box, (3, 3), 0)
    # 把滑块图区域变成黑色
    for y in range(0,box_h):
        for x in range(slider_x - 5,slider_x + box_w + 5):  #多处理5个像素
            img_find_box[y,x] = random.randint(0,255)
    
    # 找出分数大于0.5,并且赛选出y的值
    mid_score_arr = np.argwhere(score > 0.05)
    mask = np.argwhere(mid_score_arr[:,0] == slider_y)
    
    # 处理完全不像box的图片区域
    xlist = mid_score_arr[mask][:,0][:,1]
    count = 0
    for x in range(w-box_w):
        if x in xlist:
            count = x + box_w
        if x > count:
            for y in range(0,box_h):
                img_find_box[y,x] = random.randint(0,255)
                # img_find_box[y,x] = 0

    res = cv2.matchTemplate(cv2.Canny(img_slider_box, 50, 150), cv2.Canny(img_find_box, avg*0.4, avg*1.2), cv2.TM_CCOEFF_NORMED)
    print(avg)
    
    # 计算最佳返回
    reslist_x = []
    for i in range(w):
        _, _, _, max_loc = cv2.minMaxLoc(res)
        x, _ = max_loc
        if (res[0][x] == 0) or len(reslist_x)>=3:
            break
        if abs(x - slider_x) > box_w + 25:
            reslist_x.append(x+block)
        res[0][x] = 0

    slider_x = slider_x + block

    for i in range(len(reslist_x)-1):
        if abs(reslist_x[i]-reslist_x[i+1]) <= 3:
            return slider_x,reslist_x[i]
    return slider_x,reslist_x[0]

if __name__ == '__main__':
    # pass
    t1 = time.time()
    # bg = "/Users/chenyun/Projects/ocrtext/TS_Test_Script/4.png"
    # slider_x,box_x = Compare_boximg(bg)

    # showimg = cv2.imread(bg)
    # cv2.line(showimg, (slider_x, 70), (slider_x,360), (0,0,0), 2)
    # cv2.line(showimg, (box_x, 70), (box_x,360), (255,23,140), 2)
    # show(showimg)

    import os
    work_dir = "/Users/chenyun/Downloads/B/"
    for parent, dirnames, filenames in os.walk(work_dir):
            for filename in filenames:
                file_path = os.path.join(parent, filename)
                
                slider_x,box_x = Compare_boximg(file_path)

                #展示结果
                showimg = cv2.imread(file_path)
                cv2.line(showimg, (slider_x, 70), (slider_x,360), (0,0,0), 2)
                cv2.line(showimg, (box_x, 70), (box_x,360), (255,23,140), 2)
                show(showimg)

    print(time.time()-t1)
    # print(top_left)
