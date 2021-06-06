from config import *
from crnn import CRNNHandle

from utils import get_hsv_range,sorted_boxes
from PIL import Image
import numpy as np
from dbnet.dbnet_infer import DBNET
# import copy

import cv2

class  OcrHandle(object):
    def __init__(self):
        self.text_handle = DBNET(model_path)
        self.crnn_handle = CRNNHandle(crnn_model_path)
    
    def text_predict(self,img,short_size,box_list,color_list,white_list,is_draw):
        # 识别数据处理
        results = []
        img = np.asarray(img).astype(np.uint8)
        if color_list:
            count = 1
            img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
            for color in color_list:
                hsvLower,hsvUpper = get_hsv_range(color)
                # 处理红色
                if hsvLower[0] <= 10 and hsvUpper[0] >= 156:
                    red1_Lower = np.array([0, hsvLower[1], hsvLower[2]])
                    red1_Upper = np.array([10,hsvUpper[1],hsvUpper[2]])
                    red2_Lower = np.array([156, hsvLower[2], hsvLower[2]])
                    red2_Upper = np.array([180,hsvUpper[1],hsvUpper[2]])
                    if count == 1:
                        mask = cv2.inRange(img, red1_Lower,red1_Upper)
                        mask = cv2.bitwise_or(mask,cv2.inRange(img, red2_Lower,red2_Upper))
                    else:
                        mask = cv2.bitwise_or(mask,cv2.inRange(img, red1_Lower,red1_Upper))
                        mask = cv2.bitwise_or(mask,cv2.inRange(img, red2_Lower,red2_Upper))
                else:
                    if count == 1:
                        mask = cv2.inRange(img, hsvLower,hsvUpper)
                    else:
                        mask = cv2.bitwise_or(mask,cv2.inRange(img, hsvLower,hsvUpper))
                count += 1
            img = cv2.bitwise_and(img,img, mask=mask)
            img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

        if not box_list:
            tmp_box_list, _ = self.text_handle.process(img,short_size=short_size)
            tmp_box_list = sorted_boxes(np.array(tmp_box_list))
            for box in tmp_box_list:
                left = int(np.min(box[:, 0]))
                top = int(np.min(box[:, 1]))
                right = int(np.max(box[:, 0]))
                bottom = int(np.max(box[:, 1]))
                img_crop = img[top:bottom, left:right, :].copy()

                img_height, img_width = img_crop.shape[0:2]
                if img_height * 1.0 / img_width >= 1.5:
                    img_crop = np.rot90(img_crop)

                img_crop = Image.fromarray(img_crop).convert("RGB")
                simPred = self.crnn_handle.predict_rbg(img_crop, white_list)
                if simPred.strip() != '':
                    results.append([simPred,[left,top,right,bottom]])
        else:
            for box in box_list:
                left,top,right,bottom = box
                img_crop = img[top:bottom, left:right, :].copy()

                img_height, img_width = img_crop.shape[0:2]
                if img_height * 1.0 / img_width >= 1.5:
                    img_crop = np.rot90(img_crop)
                
                img_crop = Image.fromarray(img_crop).convert("RGB")
                simPred = self.crnn_handle.predict_rbg(img_crop, white_list)
                results.append([simPred,box])

        if is_draw is not None:
            img = Image.fromarray(img).convert("RGB")
            return results,img
        else:
            return results,None

if __name__ == "__main__":
    pass
