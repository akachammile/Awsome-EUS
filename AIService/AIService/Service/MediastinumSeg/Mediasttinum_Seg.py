# cython: language_level=3
import time
import io

import numpy as np
import torch
# import cv2

from ultralytics import YOLO

# from AIService.AIService.Service.AIModel import YOLOV8
from AIService.AIService.Service.BaseService import BaseService
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigMediastinum import ConfigMediastinum


class Mediasttinum_Seg(BaseService):
    def __init__(self, modelPath:str, deviceId:str):
        self.modelPath = modelPath
        self.deviceId = deviceId
        self.batchSize = 1 # 1
        self.classCount = 2
        super().__init__(self.batchSize)
        self.inputImgSize = 640
        self.thNMSIou = 0.6
        self.confThres = 0.2
        self.list_classes=list(ConfigMediastinum.REGIONS.values())
        # 加载模型
        cuda_index = self._getCudaIndex()
        if cuda_index < 0:
            print("!!!!!! 显存已使用完毕，将使用cpu模式")
            self.device=torch.device("cpu")
        else:
            self.device=torch.device("cuda",cuda_index)
        
        # ONNX模型需要在初始化时先提前预测一次
        if self.modelPath.endswith(".onnx"):
            self.model = YOLO(self.modelPath,task="segment")
            self._preInference()
        elif self.modelPath.endswith(".pt"):
            self.model = YOLO(self.modelPath,task="segment")
       

    # 预测一次空白图
    def _preInference(self):
        time_beg = time.time()
        blank_image = np.zeros((self.inputImgSize, self.inputImgSize, 3), np.uint8)
        self.model.predict(blank_image,
            imgsz=self.inputImgSize,classes=self.list_classes,device=self.device,
            verbose=False,conf=self.confThres,iou=self.thNMSIou,half=False)
        predict_time = time.time()-time_beg
        print(f"Init inference blank image: {predict_time:.2f}s")

    
    def getResult(self, currentFrame):
        results = self.model.predict(currentFrame,
            imgsz=self.inputImgSize,classes=self.list_classes,device=self.device,
            verbose=False,conf=self.confThres,iou=self.thNMSIou,half=False)
        detResultList = []
        r = results[0]
        annotatedFrame = r.plot()
        if len(r.boxes) > 0:
            boxes = r.boxes.xyxy
            clses = r.boxes.cls
            probs = r.boxes.conf
            masks = r.masks.xy
            for j in range(len(boxes)):
                box = boxes[j]
                cls = clses[j]
                prob = probs[j]
                mask = masks[j]
                leftTopX = int(box[0].item())  # 矩形框左上角x坐标
                leftTopY = int(box[1].item())  # 矩形框左上角y坐标
                rightBottomX = int(box[2].item())  # 矩形框右下角x坐标
                rightBottomY = int(box[3].item())  # 矩形框右下角y坐标
                bbox = [leftTopX, leftTopY, rightBottomX, rightBottomY]
                # mask = []
                cls = int(cls.item())
                prob = round(prob.item(), 2)
                detResultList.append((cls, prob, bbox, mask))
        return detResultList, annotatedFrame
    


 