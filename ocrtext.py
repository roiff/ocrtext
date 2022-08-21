from PIL import Image,ImageDraw,ImageFont
from config import *
from crnn import CRNNHandle
from utils import sorted_boxes
import numpy as np
from dbnet.dbnet_infer import DBNET

text_handle = DBNET(model_path)
crnn_handle = CRNNHandle(crnn_model_path)

class  OcrHandle(object):

    def predictText(img,white_list=None):
        # 文字识别
        return crnn_handle.predict_rbg(img, white_list)

    def findText(img,white_list=None,is_draw=None,compress_size=None):
        # 查找文字
        img = np.asarray(img).astype(np.uint8)
        img_w = img.shape[0]
        img_h = img.shape[1]
        short_size = min(img_w, img_h)
        if compress_size:
            try:
                short_size = int(compress_size)
            except:
                print("compress_size必须是整数")

        if short_size < 64:
            short_size = 64
        short_size = 32 * (short_size//32)
        if max(img_w, img_h) * (short_size * 1.0 / min(img_w, img_h)) > dbnet_max_size:
            print('图片reize后长边过长，请调整短边尺寸')
            return

        results = []
        tmp_box_list, _ = text_handle.process(img,short_size=short_size)
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
            simPred = crnn_handle.predict_rbg(img_crop, white_list)
            if simPred.strip() != '':
                results.append([simPred,[left,top,right,bottom]])

        if is_draw:
            img = Image.fromarray(img).convert("RGB")
            draw = ImageDraw.Draw(img)
            colors = ['red', 'green', 'blue', "purple"]
            for i, r in enumerate(results):
                _, rect = r
                x1,y1,x2,y2 = rect

                size = max(min(x2-x1,y2-y1) // 2 , 20 )

                myfont = ImageFont.truetype("fs_GB2312.ttf", size=size)
                fillcolor = colors[i % len(colors)]
                draw.text((x1, y1 - size ), str(i+1), font=myfont, fill=fillcolor)

                for xy in [(x1, y1, x2, y1), (x2, y1, x2, y2 ), (x2 , y2 , x1, y2), (x1, y2, x1, y1)]:
                    draw.line(xy=xy, fill=colors[i % len(colors)], width=2)

            return results,draw
        else:
            return results


if __name__ == "__main__":
    pass
