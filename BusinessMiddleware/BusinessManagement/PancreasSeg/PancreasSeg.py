# cython: language_level=3
import os
# import sys
from datetime import datetime
import time
import traceback
import queue
from ultralytics.utils import ops
import numpy as np
# import torch
# import cv2

from BusinessMiddleware.BusinessManagement.BaseThread import BaseThread
from BusinessMiddleware.BusinessManagement.DataPersistence.HandlePancerasRealLable import HandlePancerasRealLable 
from AIService.AIService.Service.PancreasSeg.Pancreas_Seg import Pancreas_Seg as AIService
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigPancreas import ConfigPancreasQC, ConfigPancreas
from BusinessMiddleware.BusinessManagement.DataPersistence.PancreasUtils import PancreasUtils



class PancreasSeg(BaseThread):
    def __init__(self, isDebug:bool, isDrawFlag, logFile, saveImageThreadHandle, udpHandler, detModelPath:str, deviceId:str):
        super(PancreasSeg, self).__init__()
        self.isDebug = isDebug
        self.isDrawFlag = isDrawFlag
        self.pancerasResultHandler = HandlePancerasRealLable()
        self.updServer = udpHandler
        self.pancreaUtils = PancreasUtils()

        # self.;ab
        self.logFile = logFile
        self.saveImageThreadHandle = saveImageThreadHandle
        self.currentFrame = None
        self.annotatedFrame = None
        self.thProb = ConfigPancreasQC.thProb # 手术器械出现阈值(最小概率)
        # 部位分割模型
        self.aiServiceDet = AIService(detModelPath,deviceId)
        self.classList = ConfigPancreas.EUS_BI_QC
        

        self.qcPath = ""
        self.staticPath = ""
        self.patientId = ""
        self.rowPath = ""
        self.predPath = ""
        self.mode = ""
        self.predResult = ""
        self.atama = ""
        self.kubi = ""
        self.nav =""
        self.outPath = ""
        self.today = ""
        
        self.originFrameQueue = queue.Queue(maxsize=10)#原始视频帧队列
        self.imgPathQueue = queue.Queue(maxsize=300)
        self.det_time = 0
        self.lastWriteTime = 0
        self.imageSaveDir = None
        self.count = 0
        self.curBezierUrl = ""
        self.curStraightScatterUrl = ""
        
    
    def _Reset(self):
        self.det_time = 0
        self.lastWriteTime = 0
        self.imageSaveDir = None
        self.currentFrame = None
        self.annotatedFrame = None
        with self.originFrameQueue.mutex:
            self.originFrameQueue.queue.clear()

    def _WriteLog(self, msg:str):
        logStr = time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime(time.time())) + " | "
        self.logFile.write(logStr + msg +"\n")
        self.logFile.flush()

    def SetCurrentFrame(self, currentframe):
        if self.originFrameQueue.full():#如果满了就取出一个
            self.originFrameQueue.get()
        self.originFrameQueue.put(currentframe)
    
    def setPatientInfo(self, qcPath:str, staticPath:str, patientId:str, today:str):
        self.qcPath = qcPath
        self.staticPath = staticPath
        self.patientId = patientId
        self.today = today
        self.pancerasResultHandler.setPathInfo(self.staticPath, self.today)

    def setMsg(self, atama:str, kubi:str):
        self.atama = atama
        self.kubi = kubi
      

    def getStreamFrame(self):
        return self.annotatedFrame
        

    def getQcImgPath(self):
        return self.rowPath, self.predPath
    
    def getStatisticPath(self):
        return self.curBezierUrl, self.curStraightScatterUrl
    
    def getStationTips(self):
        return self.pancerasResultHandler.ShowCurrentStageWord()
    
    def getNavCurTable(self):
        return self.pancerasResultHandler.ShowCurrentNavTable()
    
    def getPredInfo(self):
        return self.predResult
    

    def _HandleStatic(self, urlList:str) -> str:
        self.curBezierUrl, self.curStraightScatterUrl = self.pancerasResultHandler.handleStatisticChart(urlList, self.staticPath)
        return self.curBezierUrl, self.curStraightScatterUrl

    def _HandleTime(self) -> str:
        if True:
            firstCheckTime = time.time()
            self.pancerasResultHandler.CurrentCheckTime = False
        elapsed = int((time.time() - firstCheckTime))
        elapsedStr = str(elapsed)
        if self.pancerasResultHandler.FirstCheckPatient:
            if (time.time() - self.pancerasResultHandler.LastUpdateCheckTime) < 60:
                return elapsedStr
            else:
                return ""
        else:
            return ""


    
    def _HandleNav(self, targetList:list):
        infoList = []
        for result in targetList:
            self.count += 1
            cls, prob, bbox, _ = result
            x, y, w, h = bbox
            info = f"{self.count}" + "^"+ "03^01"+"^"+ f"{cls}" + "^" + f"{prob}" + "^" + f"{x},{y},{w},{h}"
            infoList.append(info)
        self.pancerasResultHandler.handlePredictInfo(self.patientId, infoList)
        self.pancerasResultHandler.handleNavigation()


    def _HandleRecord(self):
        self.nav, self.outPath = self.pancerasResultHandler.makeCopyAndGetRecord(self.patientId, self.staticPath)
        if self.nav:
            self.updServer.SendMessage(self.outPath)



    def _DrawTarget(self, frame, annotatedFrame, targetList:list):
        if len(targetList) > 0:
            drawframe = frame.copy()
            labelList = []
            infoList = []

            for result in targetList:
                self.count += 1
                cls, prob, bbox, _ = result
                x, y, w, h = bbox
                info = f"{self.count}" + "^"+ "03^01"+"^"+f"{cls}"+"^"+ f"{prob}" + "^" + f"{x},{y},{w},{h}"
                label = self.classList[cls]
                labelList.append(label)  # 将格式化后的标签加入列表
                infoList.append(info)
                
            subFolder = os.path.join(self.qcPath, ",".join(labelList))
            


            if not os.path.exists(subFolder):
                os.makedirs(subFolder, exist_ok=True)
            
            originImgDir = "raw_" + ",".join(labelList) + "-" + str(int(time.time())) + ".jpg"
            maskImgDir = "pred_" + ",".join(labelList) + "-" + str(int(time.time())) + ".jpg"


            subFolderTxtDir = ",".join(labelList) + "-"+ str(int(time.time())) + ".txt" 
            savePredInfoTxt = os.path.join(subFolder, subFolderTxtDir)
            with open(savePredInfoTxt, "a") as f:
                for i in infoList:
                    f.write(i)
                    f.write("\n")
            
            saveOriginImgName = os.path.join(subFolder, originImgDir)
            saveMarkImgName = os.path.join(subFolder, maskImgDir)
            self.saveImageThreadHandle.SetInput(drawframe, saveFullPath = saveOriginImgName)
            self.saveImageThreadHandle.SetInput(annotatedFrame, saveFullPath = saveMarkImgName)

            self.rowPath = saveOriginImgName.replace("D:\\eus", "user")
            self.predPath = saveMarkImgName.replace("D:\\eus", "user")
            # self.imgPathQueue.put(UdpMsgtoQcCut)
            # print(self.imgPathQueue.qsize())
            
        
   

    def run(self):
        while self.loopFlag:
            # 检查是否重置
            if self.resetFlag:
                self._Reset()
                self.resetFlag = False
                continue
            
            threadStartTime = time.time()
            predResult=[]
            if not self.originFrameQueue.empty():
                currentFrame = self.originFrameQueue.get()
                predResult, annotatedFrame = self.aiServiceDet.getResult(currentFrame)
                self.annotatedFrame = annotatedFrame
                self.predResult = predResult
                self._DrawTarget(currentFrame, annotatedFrame, predResult)


            threadExecuteTime = time.time() - threadStartTime  # 单位：秒
            if len(predResult) > 0 and time.time() - self.lastWriteTime >= 5:  #间隔5s保存一次文件
                self.lastWriteTime = time.time()
                logStr = "线程耗时:%.4f,[" % threadExecuteTime
                for result in predResult:#
                    logStr += f"({result[0]},{result[1]},{result[2]})"
                logStr += f"],胆胰计数:{self.count}"
                self._WriteLog(logStr)
            
            threadSleepTime = self.sleepTime - threadExecuteTime
            if threadSleepTime > 0:
                time.sleep(threadSleepTime)

