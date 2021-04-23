import os

filt_path = os.path.abspath(__file__)
father_path = os.path.abspath(os.path.dirname(filt_path) + os.path.sep + ".")

# crnn参数
crnn_lite = True
model_path = os.path.join(father_path, "models/dbnet.onnx")
is_rgb = True
crnn_model_path = os.path.join(father_path, "models/crnn_lite_lstm.onnx")

