# cython: language_level=3
import time
import queue

import cv2
# import numpy as np

from BusinessMiddleware.BusinessManagement.BaseThread import BaseThread


class SaveImage(BaseThread):
    """
    存图片线程
    """
    def __init__(self, saveImgSize:str):
        super(SaveImage, self).__init__()
        self.saveImgSize = saveImgSize #1280_1080
        # self.threadPostFile = None
        #手术器械搜集截图时，器械出现5秒以上很容易就满，所以需要设置大一些
        self.imageInfoQueue = queue.Queue(maxsize=300) # 最大大约 300kb*300 ~=90Mb

    def _Reset(self):
        with self.imageInfoQueue.mutex:
            self.imageInfoQueue.queue.clear()

    def SetSaveImgSize(self, saveImgSize:str):
        self.saveImgSize = saveImgSize 

    # #设置上传图像线程
    # def SetPostFileHandle(self, threadPostFile):
    #     self.threadPostFile = threadPostFile

    def SetInput(self, frame, saveFullPath:str):
        if self.imageInfoQueue.full():
            self.imageInfoQueue.get()
        self.imageInfoQueue.put((frame, saveFullPath))

    def _resizeImg(self, image):
        ####更改保存图像大小#######
        img_height,img_width = image.shape[:2] #高,宽
        if f"{img_width}_{img_height}" != self.saveImgSize:
            width_new,height_new = self.saveImgSize.split("_")
            img = cv2.resize(image, (int(width_new),int(height_new)), interpolation=cv2.INTER_CUBIC)
        else:
            img = image
        return img

    def _SaveImg(self, bytes_data, imageFullPath:str):
        with open(imageFullPath,"wb") as fw:
            fw.write(bytes_data)

    def run(self):
        while self.loopFlag:
            # 检查是否重置
            if self.resetFlag:
                self._Reset()
                self.resetFlag = False
            threadStartTime = time.time()
            if not self.imageInfoQueue.empty():
                image, imageFullPath = self.imageInfoQueue.get()
                img = self._resizeImg(image)
                #cv2.imencode将图片格式转换(编码)成流数据，赋值到内存缓存中;主要用于图像数据格式的压缩，方便网络传输
                #'.jpg'表示将图片按照jpg格式编码。
                # params = [cv2.IMWRITE_JPEG_QUALITY, 95]  # ratio=95, 取值范围为0~100(默认值95)，数值越小，压缩比越高，图片质量损失越严重
                result, imgencode = cv2.imencode('.jpg', img)
                if result:
                    bytes_img = imgencode.tobytes() #将numpy矩阵转换成bytes形式
                    self._SaveImg(bytes_img, imageFullPath)
                    # if self.threadPostFile and (imageFullPath.upper().replace("\\","/").find("DR/DISEASE") > 0 \
                    #                             or imageFullPath.upper().find("QC") > 0):
                    #     self.threadPostFile.SetInput(bytes_img,imageFullPath)

            threadExecuteTime = time.time() - threadStartTime  # 单位：秒

            # 线程休眠
            threadSleepTime = self.sleepTime - threadExecuteTime
            if threadSleepTime > 0:
                time.sleep(threadSleepTime)
