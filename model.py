from config import *
from crnn import CRNNHandle

from utils import sorted_boxes, get_rotate_crop_image
from PIL import Image
import numpy as np
import copy
from dbnet.dbnet_infer import DBNET
import traceback

class  OcrHandle(object):
    def __init__(self):
        self.text_handle = DBNET(model_path)
        self.crnn_handle = CRNNHandle(crnn_model_path)

    def crnnRecWithBox(self,im, boxes_list,score_list,white_list):
        """
        crnn模型，ocr识别
        @@model,
        @@converter,
        @@im:Array
        @@text_recs:text box
        @@ifIm:是否输出box对应的img

        """
        results = []
        boxes_list = sorted_boxes(np.array(boxes_list))

        count = 1
        for index, (box ,score) in enumerate(zip(boxes_list,score_list)):

            tmp_box = copy.deepcopy(box)
            partImg_array = get_rotate_crop_image(im, tmp_box.astype(np.float32))


            partImg = Image.fromarray(partImg_array).convert("RGB")

            if not is_rgb:
                partImg = partImg.convert('L')

            try:
                if white_list:
                    simPred = self.crnn_handle.predict_rbg_whitelist(partImg,white_list)  ##识别的文本
                elif is_rgb:
                    simPred = self.crnn_handle.predict_rbg(partImg)  ##识别的文本
                else:
                    simPred = self.crnn_handle.predict(partImg)  ##识别的文本
            except Exception as e:
                print(traceback.format_exc())
                continue

            if simPred.strip() != '':
                results.append([tmp_box,simPred,score])
                count += 1

        return results


    def text_predict(self,img,short_size,white_list):
        boxes_list, score_list = self.text_handle.process(np.asarray(img).astype(np.uint8),short_size=short_size)
        result = self.crnnRecWithBox(np.array(img), boxes_list,score_list,white_list)

        return result

    def text_predict_no_detect(self,img,white_list):
        return self.crnn_handle.predict_rbg_whitelist(img, white_list)


if __name__ == "__main__":
    pass
