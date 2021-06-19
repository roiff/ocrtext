import tornado.web
import tornado.gen
import tornado.httpserver
import json
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
import time

from backend.tools.np_encoder import NpEncoder
from backend.tools import log
import logging


logger = logging.getLogger(log.LOGGER_ROOT_NAME + '.' +__name__)

class Qrcode(tornado.web.RequestHandler):
    # 接口方法
    def get(self):
        self.set_status(404)
        self.write("404 : Please use POST")

    @tornado.gen.coroutine
    def post(self):

        start_time = time.time()        
        # 接受参数
        img_up = self.request.files.get('file', None)

        self.set_header('content-type', 'application/json')

        # 检查图片是否上传
        if img_up is not None and len(img_up) > 0:
            img_up = img_up[0]['body']
            img = cv2.imdecode(np.frombuffer(img_up, np.uint8),0)

        else:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '没有传入图像'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '没有传入图像'}, cls=NpEncoder))
            return

        res = []
        barcodes = pyzbar.decode(img)
        for barcode in barcodes:
            barcodeData = barcode.data.decode("UTF8")
            barcodeType = barcode.type
            res.append([barcodeData,barcodeType])
        
        speed_time = round(time.time() - start_time, 2)
        log_info = {
            'ip': self.request.remote_ip,
            'return': res,
            'time': time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())),
            'speed_time': speed_time
        }
        logger.info(json.dumps(log_info, cls=NpEncoder))
        
        self.finish(json.dumps(
            {'code': 200, 'msg': '成功',
            'res': res,
            'speed_time': speed_time,
            },
            cls=NpEncoder))

        return
