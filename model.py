from config import *
from crnn import CRNNHandle

class  OcrHandle(object):
    def __init__(self):
        self.crnn_handle = CRNNHandle(crnn_model_path)

    def text_predict_no_detect(self,img,white_list):
        return self.crnn_handle.predict_rbg_whitelist(img, white_list)


if __name__ == "__main__":
    pass
