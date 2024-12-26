# cython: language_level=3
import os
# import sys
import datetime
import time
import traceback
import queue
from BusinessMiddleware.BusinessManagement.BaseThread import BaseThread
from BusinessMiddleware.BusinessManagement.DataPersistence.HandleMediastinumRealLable import HandleMediastinumRealLable 
from AIService.AIService.Service.MediastinumSeg.Mediasttinum_Seg import Mediasttinum_Seg as AIService
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigMediastinum import ConfigMediastinumQC


class MediastinumSeg(BaseThread):
    def __init__(self, isDebug:bool, isDrawFlag, logFile, saveImageThreadHandle, udpHandler, detModelPath:str, deviceId:str):
        super(MediastinumSeg, self).__init__()
        self.isDebug = isDebug
        self.isDrawFlag = isDrawFlag
        self.mediastinumResultHandler = HandleMediastinumRealLable()
        self.updServer = udpHandler
        self.logFile = logFile
        self.saveImageThreadHandle = saveImageThreadHandle
        self.thProb = ConfigMediastinumQC.thProb # 手术器械出现阈值(最小概率)
        # 目标检测模型
        self.aiServiceDet = AIService(detModelPath,deviceId)

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
        self.det_time = 0
        self.count = 0
        self.lastWriteTime = 0
        self.imageSaveDir = None
        self.annotatedFrame = None
        self.isHaveTool = False  # 是否有器械

        
        
    
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
        self.logFile.write(logStr+msg+"\n")
        self.logFile.flush()

    def SetCurrentFrame(self, currentframe,):
        # 设置AI service的输入
        if self.originFrameQueue.full():#如果满了就取出一个
            self.originFrameQueue.get()
        self.originFrameQueue.put(currentframe)

    def setPatientInfo(self, qcPath:str, staticPath:str, patientId:str, today:str):
        self.qcPath = qcPath
        self.staticPath = staticPath
        self.patientId = patientId
        self.today = today
        self.mediastinumResultHandler.setPathInfo(self.staticPath, self.today)
    
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
        return self.mediastinumResultHandler.ShowCurrentStageWord()
    
    def getNavCurTable(self):
        return self.mediastinumResultHandler.ShowCurrentNavTable()
    
    def getPredInfo(self):
        return self.predResult
    
    def _HandleStatic(self, urlList:str) -> str:
        self.curBezierUrl, self.curStraightScatterUrl = self.mediastinumResultHandler.handleStatisticChart(urlList, self.staticPath)
        return self.curBezierUrl, self.curStraightScatterUrl

    def _HandleTime(self) -> str:
        if self.mediastinumResultHandler.CurrentCheckTime:
            firstCheckTime = time.time()
            self.mediastinumResultHandler.CurrentCheckTime = False
        elapsed = int((time.time() - firstCheckTime))
        elapsedStr = str(elapsed)
        if self.mediastinumResultHandler.FirstCheckPatient:
            if (time.time() - self.mediastinumResultHandler.lastUpdateCheckTime) < 60:
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
        self.mediastinumResultHandler.handlePredictInfo(self.patientId, infoList)
        self.mediastinumResultHandler.handleNavigation()


    def _HandleRecord(self):
        self.nav, self.outPath = self.mediastinumResultHandler.makeCopyAndGetRecord(self.patientId, self.staticPath)
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
    

 
   

    def run(self):
        while self.loopFlag:
            # 检查是否重置
            if self.resetFlag:
                self._Reset()
                self.resetFlag = False
                continue
            
            threadStartTime = time.time()
            predResult=[]
            try:
                if not self.originFrameQueue.empty():
                    currentFrame = self.originFrameQueue.get()
                    predResult, annotatedFrame = self.aiServiceDet.getResult(currentFrame)
                    self.annotatedFrame = annotatedFrame
                    self._DrawTarget(currentFrame, annotatedFrame, predResult)
            except:
                self._WriteLog(traceback.format_exc())

            threadExecuteTime = time.time() - threadStartTime  # 单位：秒
            if len(predResult) > 0 and time.time() - self.lastWriteTime >= 5:  #间隔5s保存一次文件
                self.lastWriteTime = time.time()
                logStr = "线程耗时:%.4f,[" % threadExecuteTime
                for result in predResult:# [(cls, prob, bbox),(cls, prob, bbox)]
                    logStr += f"({result[0]},{result[1]},{result[2]})"
                logStr += f"],手术器械:{self.isHaveTool}"
                self._WriteLog(logStr)
            
            # print("threadExecuteTime" + str(threadExecuteTime))
            threadSleepTime = self.sleepTime - threadExecuteTime
            if threadSleepTime > 0:
                time.sleep(threadSleepTime)

