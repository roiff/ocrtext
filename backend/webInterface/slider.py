import time,random

import tornado.web
import tornado.gen
import tornado.httpserver
import json
import numpy as np
import cv2
import os

from backend.tools.np_encoder import NpEncoder
from backend.tools import log
import logging

logger = logging.getLogger(log.LOGGER_ROOT_NAME + '.' +__name__)

current_path = os.path.dirname(__file__)

class Slider(tornado.web.RequestHandler):
    # 接口方法
    def get(self):
        self.set_status(404)
        self.write("404 : Please use POST")

    def detect_boximg(self,image,block):
        """detect displacement"""
        # 读取三个图片
        img_bg_box = cv2.imread(os.path.join(current_path, "sliderimg/box.jpg"), 0)
        img_bg_slider = cv2.imread(os.path.join(current_path, "sliderimg/slider.jpg"), 0)
        # image = cv2.imread(image_path, 0)
        
        # 做预处理 高斯模糊
        image = cv2.GaussianBlur(image, (3, 3), 0)
        w, h = image.shape[::-1]  # 宽
        image = image[0:h, block:w-block]
        w = w - block*2

        img_find_box = image[80:360, 0:w]
        img_find_slider = image[400:450, 0:w]

        # 查找滑块匹配度
        res = cv2.matchTemplate(cv2.Canny(img_bg_slider, 50, 150), cv2.Canny(img_find_slider, 50, 150), cv2.TM_CCOEFF_NORMED)

        # 获取最佳匹配的X轴
        _, _, _, max_loc = cv2.minMaxLoc(res)
        slider_x, _ = max_loc  # 获取x,y位置坐标


        # 查找灰色框匹配度
        score = cv2.matchTemplate(cv2.Canny(img_bg_box, 50, 150), cv2.Canny(img_find_box, 50, 150), cv2.TM_CCOEFF_NORMED)

        # 找出分数大于0.1的值
        high_score_arr = np.argwhere(score > 0.1)
        
        # 这些值中,y出现频率最高的
        count_y = np.bincount(high_score_arr[:,0])  # 列出y值的频次
        slider_y = np.argmax(count_y)        # y值出现最多的

        return slider_x,slider_y,score


    def Compare_boximg(self,image):
        # 检测需要匹配的图形
        block = 15
        box_w,box_h = 62,72

        slider_x,slider_y,score = self.detect_boximg(image.copy(),block)

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

    @tornado.gen.coroutine
    def post(self):

        start_time = time.time()        
        # 接受参数
        img_up = self.request.files.get('file', None)

        self.set_header('content-type', 'application/json')

        # 检查图片是否上传
        if img_up is not None and len(img_up) > 0:
            img_up = img_up[0]['body']
            img = cv2.imdecode(np.frombuffer(img_up, np.uint8), 0)

        else:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '没有传入图像'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '没有传入图像'}, cls=NpEncoder))
            return

        res = []

        start_x,end_x = self.Compare_boximg(img)
        speed_time = round(time.time() - start_time, 2)
        log_info = {
            'ip': self.request.remote_ip,
            'return': [start_x,end_x],
            'time': time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())),
            'speed_time': speed_time
        }
        logger.info(json.dumps(log_info, cls=NpEncoder))
        
        self.finish(json.dumps(
            {'code': 200, 'msg': '成功',
            'res': [start_x,end_x],
            'speed_time': speed_time,
            },
            cls=NpEncoder))

        return
