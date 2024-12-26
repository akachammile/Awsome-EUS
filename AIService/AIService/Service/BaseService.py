# cython: language_level=3
import queue
import os

import tinyaes

class BaseService:
    def __init__(self, inputQueueSize):
        # 输入队列
        self.inputQueueSize = inputQueueSize
        self.inputQueue = queue.Queue(maxsize=self.inputQueueSize)
        # 输出结果
        self.resultList = []
        self.resultUpdateFlag = False
        self.saveImgDir = None #测试用
        self.imgHandle = None #测试用

    def ResetAll(self):
        self._ResetResult()
        with self.inputQueue.mutex:
            self.inputQueue.queue.clear()

    def SetInput(self, curInput):
        raise NotImplementedError

    def GetResult(self):
        result = []
        if self.resultUpdateFlag:
            result = self.resultList.copy()
            self._ResetResult()
        return result

    def _ResetResult(self):
        self.resultList.clear()
        self.resultUpdateFlag = False

    def _Predict(self):
        raise NotImplementedError

    def _getCudaIndex(self):
        list_gpu_index = os.popen("nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits").read().rstrip().splitlines()
        cuda_index=-1
        if len(list_gpu_index) == 1:
            index,free_size=list_gpu_index[0].split(",")
            cuda_index = int(index.strip())
        else:
            gpu_free_size = 0 #剩余显存
            for i in list_gpu_index:
                index,free_size=i.split(",")
                if int(free_size.strip()) > gpu_free_size: #查找剩余显存多的显卡
                    gpu_free_size = int(free_size.strip())
                    cuda_index = int(index.strip())
            if gpu_free_size < 2*1024: #因模型推理及其他程序也会占用显存，故需要预留至少2G
                cuda_index = -1
        
            # ###临时测试######
            # index0,free_size0 = list_gpu_index[0].split(",")
            # index1,free_size1 = list_gpu_index[1].split(",")
            # if int(free_size0.strip()) > int(free_size1.strip()):
            #     cuda_index = int(index0.strip())
            # else:
            #     cuda_index = int(index1.strip())
            # #####

        return cuda_index

    def _decryptModel(self, modelPath:str, deviceId:str)->bytes:
        file_data = b""
        with open(modelPath,"rb") as fr:
            file_data = fr.read()
        psw = deviceId
        iv = deviceId[::-1] #字符串反转
        obj_aes=tinyaes.AES(psw.encode("utf-8"),iv.encode("utf-8"))
        de_text=obj_aes.CTR_xcrypt_buffer(file_data)
        return de_text

    ##测试用
    def SetSaveImgHandle(self,saveImgDir,imgHandle):
        self.saveImgDir = saveImgDir
        self.imgHandle = imgHandle