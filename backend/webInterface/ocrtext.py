import time

from model import  OcrHandle
import tornado.web
import tornado.gen
import tornado.httpserver
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
from config import dbnet_max_size
from backend.tools.np_encoder import NpEncoder
from backend.tools import log

import logging,json,base64,re

logger = logging.getLogger(log.LOGGER_ROOT_NAME + '.' +__name__)

ocrhandle = OcrHandle()
class OcrText(tornado.web.RequestHandler):
    # 接口方法
    def get(self):
        self.set_status(404)
        self.write("404 : Please use POST")

    @tornado.gen.coroutine
    def post(self):

        start_time = time.time()        
        # 接受参数
        img_up = self.request.files.get('file', None)
        img_base64 = self.get_argument('base64', None)
        box_list = self.get_argument('boxlist', None)
        color_list = self.get_argument('colorlist', None)
        white_list = self.get_argument('whitelist', None)
        compress_size = self.get_argument('compress', None)
        is_draw = self.get_argument('isdraw', None)
        # is_draw = True

        # listhex = [0xf6f502,0xc4bc06,0xffff01,0xebe803]
        # listhex = [["0xd8d0c8","0xfaf8f8","0xb0a297","0xebe9e8","0xffffff"]]
        # listhex = [["0xe9d635","0xebd834","0x988c21","0xead733","0xb9a12f","0xcccf69"],["0x69ac5e","0x75fe8c","0x2a5b32"]]
        # [["0xef0b09","0xdf1412","0xc12520","0x8b2015"]]
        # [[240,447,333,468],[393,328,474,347],[310,271,413,294],[313,254,403,272]]
        
        # [[11,100,227,127],[11,128,226,156],[11,152,227,186],[11,183,227,212],[11,210,227,240],[10,241,226,268]]

        self.set_header('content-type', 'application/json')

        # 检查图片是否上传
        if img_up is not None and len(img_up) > 0:
            img_up = img_up[0]
            img = Image.open(BytesIO(img_up.body))
            img = img.convert("RGB")
        elif img_base64 is not None and len(img_up) > 0:
            img_base64 = re.sub('^data:image/.+;base64,', '', img_base64)
            img_base64 = base64.b64decode(img_base64)
            img = Image.open(BytesIO(img_base64))
            pass
        else:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '没有传入图像'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '没有传入图像'}, cls=NpEncoder))
            return

        # 检查参数是否正确
        param_err = white_list is not None and not isinstance(white_list,str)

        if box_list is not None and not param_err:
            try:
                box_list = json.loads(box_list)
                param_err = not isinstance(box_list,list) or not isinstance(box_list[0],list)
            except:
                param_err = True
        
        if color_list is not None and not param_err:
            try:
                color_list = json.loads(color_list)
                param_err = not isinstance(color_list,list)
            except:

                param_err = True

        img_w, img_h = img.size
        if compress_size is not None and not param_err:
            try:
                short_size = int(compress_size)
            except:
                param_err = True
        else:
            short_size = min(img_w, img_h)
            if short_size > 960:
                short_size = 960
    
        if param_err:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '参数有误,请检查参数'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '参数有误,请检查参数'}, cls=NpEncoder))
            return

        # 检查压缩比是否正确
        if short_size < 64:
            short_size = 64
        short_size = 32 * (short_size//32)
        if max(img_w, img_h) * (short_size * 1.0 / min(img_w, img_h)) > dbnet_max_size:
            self.set_status(400)
            logger.error(json.dumps({'code': 400, 'msg': '图片reize后长边过长，请调整短边尺寸'}, cls=NpEncoder))
            self.finish(json.dumps({'code': 400, 'msg': '图片reize后长边过长，请调整短边尺寸'}, cls=NpEncoder))
            return

        res,img_draw = ocrhandle.text_predict(img,short_size,box_list,color_list,white_list,is_draw)
        speed_time = round(time.time() - start_time, 2)

        if img_draw:
            draw = ImageDraw.Draw(img_draw)
            colors = ['red', 'green', 'blue', "purple"]
            for i, r in enumerate(res):
                _, rect = r
                x1,y1,x2,y2 = rect

                size = max(min(x2-x1,y2-y1) // 2 , 20 )

                myfont = ImageFont.truetype("fs_GB2312.ttf", size=size)
                fillcolor = colors[i % len(colors)]
                draw.text((x1, y1 - size ), str(i+1), font=myfont, fill=fillcolor)

                for xy in [(x1, y1, x2, y1), (x2, y1, x2, y2 ), (x2 , y2 , x1, y2), (x1, y2, x1, y1)]:
                    draw.line(xy=xy, fill=colors[i % len(colors)], width=2)

            output_buffer = BytesIO()
            img_draw.save(output_buffer, format='JPEG')
            byte_data = output_buffer.getvalue()
            img_detected_b64 = base64.b64encode(byte_data).decode('utf8')

            log_info = {
                'ip': self.request.remote_ip,
                'return': res,
                'time': time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())),
                'speed_time': speed_time
            }
            logger.info(json.dumps(log_info, cls=NpEncoder))

            self.finish(json.dumps(
                {'code': 200, 'msg': '成功',
                'words': res,
                'speed_time': speed_time,
                'img_detected': 'data:image/jpeg;base64,' + img_detected_b64
                },
                cls=NpEncoder))
        else:
            log_info = {
                'ip': self.request.remote_ip,
                'return': res,
                'time': time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time())),
                'speed_time': speed_time
            }
            logger.info(json.dumps(log_info, cls=NpEncoder))
            
            self.finish(json.dumps(
                {'code': 200, 'msg': '成功',
                'words': res,
                'speed_time': speed_time,
                },
                cls=NpEncoder))

        
        return
