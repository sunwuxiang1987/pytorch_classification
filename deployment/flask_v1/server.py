# -*- coding:utf-8 -*-
# @time :2020.04.05
# @IDE : pycharm
# @author :lxztju
# @github : https://github.com/lxztju

import io
from PIL import Image
from flask import Flask, request, jsonify

import torch
import json
import time
import cfg

from transform import get_test_transform

# with open('label.json', 'rb') as f:
#     nm  = json.load(f)

mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]
input_size = 300

app = Flask(__name__)


@app.route("/predict")
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}
    # print(data)

    # ensure an image was properly uploaded to our endpoint

    # print("Hello")
    if request.args.get("image"):
        # print("world")
        now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
        # read the image in PIL format

        # image = request.files["image"].read()

        image_path = request.args.get("image")
        image = Image.open(image_path).convert('RGB')
        # image.save(now + '.jpg')
        # preprocess the image and prepare it for classification
        img = get_test_transform(mean, std, input_size)(image).unsqueeze(0)

        # classify the input image and then initialize the list
        # of predictions to return to the client

        out = model(img.cuda())
        # print(out)
        pred_label = torch.max(out, 1)[1].item()
        # print(pred_label)

        data["predictions"] = cfg.LABEL_ID_NAME[pred_label]
        # data["predictions"].append(str(pred_label))

        # indicate that the request was a success
        data["success"] = True
        print(data)

    # return the data dictionary as a JSON response
    return "success"


def load_checkpoint(filepath):
    checkpoint = torch.load(filepath)
    model = checkpoint['model']  # 提取网络结构
    model.load_state_dict(checkpoint['model_state_dict'])  # 加载网络权重参数
    for parameter in model.parameters():
        parameter.requires_grad = False
    model.eval()
    return model


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading Pytorch model and Flask starting server..."
           "please wait until server has fully started"))
    num_classes = cfg.NUM_CLASSES
    checkpoint_path = cfg.TRAINED_MODEL
    model = load_checkpoint(checkpoint_path)
    print('..... Finished loading model! ......')
    app.run(host='0.0.0.0', port=5000, debug=True)
