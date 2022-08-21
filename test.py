# 这是一个测试文件
from PIL import Image
import os

from ocrtext import OcrHandle

filt_path = os.path.abspath(__file__)
father_path = os.path.abspath(os.path.dirname(filt_path) + os.path.sep + ".")

test1 = os.path.join(father_path, "testimg/1.png")
img = Image.open(test1)
img = img.convert("RGB")


print(OcrHandle.predictText(img,white_list="9"))


test2 = os.path.join(father_path, "testimg/2.png")
img = Image.open(test2)
img = img.convert("RGB")

print(OcrHandle.findText(img,white_list="好"))
res,draw = OcrHandle.findText(img,white_list="好",is_draw=True)
