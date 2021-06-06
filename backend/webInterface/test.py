import numpy as np
import cv2
import os
import time


# import matplotlib.pyplot as plt

t1 = time.time()
image = '/Users/chenyun/Projects/ocrtext/backend/webInterface/QQ20210601-0.png'
# sdff = '/Users/chenyun/Projects/ocrtext/backend/webInterface/mark1/hhh.png'
# image = "20200602141811.jpeg"
savefile = 'mark1'
# image = os.listdir(image_file)
save_image = os.path.join(savefile, image)
save_image_sub = os.path.join(savefile,"sub.png")
print(save_image)
 
#设定颜色HSV范围，假定为红色
redLower = np.array([26, 199, 232])
redUpper = np.array([27, 200, 255])

#读取图像
img = cv2.imread(image)
# print(img.shape)
cv2.imshow('image', img)
# cv2.waitKey(0)
#将图像转化为HSV格式
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# print(hsv.shape)
#去除颜色范围外的其余颜色
mask = cv2.inRange(hsv, redLower, redUpper)
 
# 二值化操作
ret, binary = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)

#膨胀操作，因为是对线条进行提取定位，所以腐蚀可能会造成更大间隔的断点，将线条切断，因此仅做膨胀操作
kernel = np.ones((5, 5), np.uint8)
dilation = cv2.dilate(binary, kernel, iterations=1)

# cv2.imwrite(save_image, dilation)
 
#获取图像轮廓坐标，其中contours为坐标值，此处只检测外形轮廓
_, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

mask = np.zeros([img.shape[0], img.shape[1]], dtype=np.uint8)
dd = []
if len(contours) > 0:
  #cv2.boundingRect()返回轮廓矩阵的坐标值，四个值为x, y, w, h， 其中x, y为左上角坐标，w,h为矩阵的宽和高
  boxes = [cv2.boundingRect(c) for c in contours]
  for box in boxes:
    x, y, w, h = box
    if w >= 10 and h>=10:
      mask[y:y+h, x:x+w] = 255
      print(w,h)
      dd.append(img[y:y+h, x:x+w])
      # cv2.imwrite(save_image_sub, np.hstack(dd))
    #绘制矩形框对轮廓进行定位
    # cv2.rectangle(img, (x, y), (x+w, y+h), (153, 153, 0), 2)
    #将绘制的图像保存并展示
    # cv2.imwrite(save_image, img)
    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
cv2.imwrite(save_image_sub, np.vstack(dd))
image = cv2.add(img, np.zeros(np.shape(img), dtype=np.uint8), mask=mask)
cv2.imwrite(save_image, image)
# cv2.imwrite('/Users/chenyun/Projects/ocrtext/backend/webInterface/mark1/hhh.png', image)

print(time.time()-t1)
