

import time
from model import  OcrHandle
import tornado.web
import tornado.gen
import tornado.httpserver
from PIL import Image
from io import BytesIO
import json

from backend.tools.np_encoder import NpEncoder
from backend.tools import log
import logging

logger = logging.getLogger(log.LOGGER_ROOT_NAME + '.' +__name__)

ocrhandle = OcrHandle()


request_time = {}
now_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))

class OcrText(tornado.web.RequestHandler):
    '''
    接口方法
    '''
        
    def get(self):
        self.set_status(404)
        self.write("404 : Please use POST")

    @tornado.gen.coroutine
    def post(self):
        '''

        :return:
        报错：
        400 没有请求参数

        '''
        start_time = time.time()
        global now_time
        global request_time
        img_up = self.request.files.get('file', None)
        box_list = json.loads(self.get_argument('boxarr', None))
        white_list = self.get_argument('whitelist', None)

        self.set_header('content-type', 'application/json')

        if img_up is not None and len(img_up) > 0:
            img_up = img_up[0]
            img = Image.open(BytesIO(img_up.body))
            img = img.convert("RGB")
        else:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '没有传入参数'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '没有传入参数'}, cls=NpEncoder))
            return
        
        time_now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
        time_day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        if time_day != now_time:
            now_time = time_day
            request_time = {}

        if isinstance(box_list,dict):
            res = {}
            for k,v in box_list.items():
                img_sub = img.crop((v[0],v[1],v[2],v[3]))
                res[k] = ocrhandle.text_predict_no_detect(img_sub,white_list)
        elif isinstance(box_list,list):
            res = []
            for v in box_list:
                img_sub = img.crop((v[0],v[1],v[2],v[3]))
                res.append(ocrhandle.text_predict_no_detect(img_sub,white_list))

        log_info = {
            'ip': self.request.remote_ip,
            'return': res,
            'time': time_now,
            'speed_time': round(time.time() - start_time, 2)
        }
        logger.info(json.dumps(log_info, cls=NpEncoder))
        self.finish(json.dumps(
            {'code': 200, 'msg': '成功',
             'words': res,
            },
            cls=NpEncoder))
        return
