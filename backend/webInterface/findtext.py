

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
from config import dbnet_max_size


class FindText(tornado.web.RequestHandler):
        
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
        short_size = 960
        img_up = self.request.files.get('file', None)
        white_list = self.get_argument('whitelist', None)
        compress_size = self.get_argument('compress', None)

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

        img = img.convert("RGB")
        
        time_now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
        time_day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        if time_day != now_time:
            now_time = time_day
            request_time = {}
        

        '''
        是否开启图片压缩
        默认为960px
        值为 0 时表示不开启压缩
        非 0 时则压缩到该值的大小
        '''
        res = []

        img_w, img_h = img.size
        if compress_size is not None:
            try:
                compress_size = int(compress_size)
                short_size = compress_size
            except ValueError as ex:
                res.append("短边尺寸参数类型有误，只能是int类型")
                self.finish(json.dumps({'code': 400, 'msg': 'compress参数类型有误，只能是int类型'}, cls=NpEncoder))
                return
        else:
            short_size = min(img_w, img_h)

        if short_size < 32:
            short_size = 32
    
        if short_size > 960:
            short_size = 960
        
        short_size = 32 * (short_size//32)

        if max(img_w, img_h) * (short_size * 1.0 / min(img_w, img_h)) > dbnet_max_size:
            res.append("图片reize后长边过长，请调整短边尺寸")
            self.finish(json.dumps({'code': 400, 'msg': '图片reize后长边过长，请调整短边尺寸'}, cls=NpEncoder))
            return

        res = ocrhandle.text_predict(img,short_size,white_list)

        log_info = {
            'ip': self.request.remote_ip,
            'return': res,
            'time': time_now,
            "short_size": short_size,
        }

        logger.info(json.dumps(log_info, cls=NpEncoder))

        self.finish(json.dumps(
            {'code': 200, 'msg': '成功',
             'words': res,
            },
            cls=NpEncoder))
        return
