# cython: language_level=3
# -*- coding: utf-8 -*-
import os
import sys
import traceback
import time
import json
import cv2
import numpy as np
import socket



from BusinessMiddleware.BusinessManagement.Utils.MessageParse import MessageParse
from BusinessMiddleware.BusinessManagement.UserManagement.CreateUser import CreateUser
from BusinessMiddleware.BusinessManagement.UserManagement.UserBase import UserBase
from BusinessMiddleware.BusinessManagement.DataPersistence.SaveImage import SaveImage
from BusinessMiddleware.BusinessManagement.MediastinumSeg.MediastinumSeg import MediastinumSeg
from BusinessMiddleware.BusinessManagement.DataPersistence.PancreasUtils import PancreasUtils
from BusinessMiddleware.BusinessManagement.PancreasSeg.PancreasSeg import PancreasSeg
from BusinessMiddleware.LinkManagement.WebSocketServerManagement import WebSocketManagement
from BusinessMiddleware.LinkManagement.WebSocketClientManagement import SocketManagement

from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigWebSocket import ConfigWebSocket
from BusinessMiddleware.BusinessManagement.CheckModeStream.CheckModeStream import CheckModeStream




class MainService(object):
    def __init__(self, configs:dict):

        self.defaultCheckType = configs["checkType"] # 检查类型
        self.isDrawFlag = True
        self.userPath = configs["userPath"] # 
        self.videoPath = configs["videoPath"] # 播放视频文件路径
        self.msgParseUtil = MessageParse(configs["userPath"])
        self.pancreasUtils = PancreasUtils()
        self.qcCutMsg = {}
        self.qcStatisticMsg = {}
        self.navMsg = {}
        self.UDPSockeCsv = SocketManagement()

      
        # 胆胰/纵膈模型路径
        self.modelPathDRMediasttinumSeg = configs["modelPathDRMediasttinumSeg"]
        self.modelPathDRPancerasSeg = configs["modelPathDRPancerasSeg"]

        self.patientId = ""
        self.qcPath = ""
        self.staticPath = ""
        self.baseDir = ""
        self.currentCheckType = ""
        self.currentUser = None
        self.writeFlag = False


        self.hospitalName = configs["hospitalName"]
        self.room = configs["room"]
        self.defaultCheckType = configs["checkType"]
        self.userSaveBaseDir = configs["userSaveBaseDir"]

        self.saveImgSize = configs["saveImgSize"]
        
        # 视频设置
       
        self.offsetX = configs["offsetX"]
        self.offsetY = configs["offsetY"]
        self.cropWidth = configs["cropWidth"] 
        self.cropHeight = configs["cropHeight"] 
        self.originFrameWidth = configs["originFrameWidth"] 
        self.originFrameHeight = configs["originFrameHeight"]
        # self.drawDRRectType = configs["drawDRRectType"] # 病变画框类型，0：四边形，1：多边形
        
        
        
        self.isDebug = True
        self.isShowVideo = True
        self.currentFrameIndex = 0
        self.watchThreadStartTime = time.time() 
        self.watchThreadErrorCount = 0 
        self.isStopCapVideoFlag = True 
        
        self.logDir = os.path.join(self.userSaveBaseDir, "log") # InitAllLog内部会自动判断并创建子文件夹
        
        if len(self.saveImgSize.split("_")) != 2:
            self.saveImgSize = f"{self.cropWidth}_{self.cropHeight}"

     

        # logfile
        self.InitAllLog()
        self.InitAllSockets()
        self.InitAllThreads()
        self.ResetCurrentUser()
        self.currentCheckType = self.defaultCheckType #当前检查类型更新
        self.dict_ui_msg = {} # 测试用
        self.last_x,self.last_y,self.last_w,self.last_h = 0,0,0,0 # 测试用
        
    def GetInput(self):
        videoFrameSumLen = -1
        videoFps = -1
        if self.videoPath == '0' or self.videoPath == '1' or self.videoPath == '2' or self.videoPath == '3':
            videoCapture = cv2.VideoCapture(int(self.videoPath), cv2.CAP_DSHOW)
            self.isShowVideo = False
        else:
            if not os.path.isfile(self.videoPath):
                return False,None,videoFrameSumLen,videoFps
            videoCapture = cv2.VideoCapture(self.videoPath)
            # cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            videoFrameSumLen = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
            videoFps = int(videoCapture.get(cv2.CAP_PROP_FPS))
            self.isShowVideo = True
 
        # 读摄像头时，需要重新设置宽高与fps，因为opencv默认读摄像头的宽、高、fps为640、480、0
        videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, self.originFrameWidth)
        videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.originFrameHeight)
        videoCapture.set(cv2.CAP_PROP_FPS, 25)
        if not videoCapture.isOpened():
            #self._writeLog("视频打开异常，程序自动退出")
            return False, videoCapture, videoFrameSumLen, videoFps
        return True, videoCapture, videoFrameSumLen, videoFps

    def StartService(self):
        """
        主循环
        :return:
        """
        res, videoCapture, videoFrameSumLen, videoFps = self.GetInput()
        cv2.namedWindow('video', cv2.WND_PROP_FULLSCREEN)
        cv2.moveWindow('video', 0, 0)
        cv2.createTrackbar("processbar", "video", 0, videoFrameSumLen, lambda x: x)
        cv2.setWindowProperty('video', cv2.WINDOW_GUI_NORMAL, cv2.WINDOW_GUI_NORMAL)
        pos = 0
        if not res:
            self.ResetAllThreads()
            self.ResetCurrentUser()
            self.ExitAllThreads()
            sys.exit(1)


        try:
            while videoCapture.isOpened():
                curPlayStartTime = cv2.getTickCount()
                

                if not self.WatchAllThreads():
                    break

                if  self.currentFrameIndex == pos:
                    self.currentFrameIndex += 1
                    cv2.setTrackbarPos("processbar", "video",  self.currentFrameIndex)
                else:
                    pos = cv2.getTrackbarPos("processbar", "video")
                    self.currentFrameIndex = pos
                    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, pos)

                capReturn, originFrame = videoCapture.read()
                if not capReturn:
                    break
                
                currentFrame = originFrame[self.offsetY : self.offsetY + self.cropHeight,self.offsetX : self.offsetX + self.cropWidth]
                
                # opencv 画框测试用
                if self.isShowVideo:
                    drawFrame = currentFrame.copy() # 画框
                else:
                    drawFrame = None
        
                # 接收记录H5页面消息，
                wsMsg = self.WebSocketServer.GetWSMsg()
                self.qcCutMsg = self.WebSocketServer.GetQCutMsg()
                self.qcStatisticMsg = self.WebSocketServer.GetStatisticMsg()
                self.navMsg = self.WebSocketServer.GetNavMsg()
                self.wsMsg = wsMsg
                self.StartPancreaThreads()
                self.StartMediastinumThreads()
                self.threadPancreas.SetCurrentFrame(currentFrame)
                
 
               
                if self.currentCheckType == "bi":
                    self.StopMediastinumThreads()
                    self.CreateUser()
                    annotatedFrame = self.threadPancreas.getStreamFrame()
                    self.threadPancreas.setPatientInfo(self.currentUser.qcPath
                                                       ,self.currentUser.statisticPath
                                                       ,self.currentUser.patientId
                                                       ,self.currentUser.today)
                    self.pancreasUtils.setStaticBasePath(self.currentUser.statisticPath)
                    self.threadCheckModeStream.setCurrentFrame(annotatedFrame)
                    
                    

                    if self.qcCutMsg:
                        info = self.threadPancreas.getPredInfo()
                        self.threadPancreas._HandleNav(info)
                        atama, kubi = "qc", "shortcut"
                        rowPath, predPath = self.threadPancreas.getQcImgPath() #获得画出的画图和截图
                        UdpMsgtoQcCut = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{rowPath}|{predPath}<$2>"
                        self.WebSocketServer.SendMsgtoQCut(UdpMsgtoQcCut)
        

                    if self.qcStatisticMsg:
                        self.threadPancreas._HandleRecord()
                        urlList = self.UDPSockeCsv.RecMessage()
                        atama, kubi = "qc", "statistics"
                        curBezierUrl, curStraightScatterUrl = self.threadPancreas._HandleStatic(urlList)
                        UdpMsgtotatistic = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{curBezierUrl}|{curStraightScatterUrl}<$2>"
                        self.WebSocketServer.SendMsgtoQcStatistic(UdpMsgtotatistic)

                    if self.navMsg:
                        msgFromH5 = self.msgParseUtil.msgParse(self.navMsg)
                        atama, patientId, kubi = msgFromH5.get("msg"), msgFromH5.get("patientId"), msgFromH5.get("mode")
                        if atama == "nav":
                            if kubi == "word":
                                describe = self.threadPancreas.getStationTips()
                                UdpMsgtoNavStationTips = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{describe}<$2>"
                                self.WebSocketServer.SendMsgtoNav(UdpMsgtoNavStationTips)

                            elif kubi == "current":
                                curTable = self.threadPancreas.getNavCurTable()
                                UdpMsgtoNavStation = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{curTable}<$2>"
                                self.WebSocketServer.SendMsgtoNav(UdpMsgtoNavStation)

                            elif kubi == "check_time":
                                elasped = self.threadPancreas._HandleTime()
                                UdpMsgtoNavStation = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{elasped}<$2>"
                                self.WebSocketServer.SendMsgtoNav(UdpMsgtoNavStation)
                            

                else:
                    self.StartPancreaThreads()
                    self.CreateUser()
                    annotatedFrame = self.threadPancreas.getStreamFrame()
                    self.threadPancreas.setPatientInfo(self.currentUser.qcPath
                                                       ,self.currentUser.statisticPath
                                                       ,self.currentUser.patientId
                                                       ,self.currentUser.today)
                    self.pancreasUtils.setStaticBasePath(self.currentUser.statisticPath)
                    self.threadCheckModeStream.setCurrentFrame(annotatedFrame)
                    
                    

                    if self.qcCutMsg:
                        info = self.threadPancreas.getPredInfo()
                        self.threadPancreas._HandleNav(info)
                        atama, kubi = "qc", "shortcut"
                        rowPath, predPath = self.threadPancreas.getQcImgPath() #获得画出的画图和截图
                        UdpMsgtoQcCut = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{rowPath}|{predPath}<$2>"
                        self.WebSocketServer.SendMsgtoQCut(UdpMsgtoQcCut)
        

                    if self.qcStatisticMsg:
                        self.threadMediasttinum._HandleRecord()
                        urlList = self.UDPSockeCsv.RecMessage()
                        atama, kubi = "qc", "statistics"
                        curBezierUrl, curStraightScatterUrl = self.threadPancreas._HandleStatic(urlList)
                        UdpMsgtotatistic = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{curBezierUrl}|{curStraightScatterUrl}<$2>"
                        self.WebSocketServer.SendMsgtoQcStatistic(UdpMsgtotatistic)

                    if self.navMsg:
                        msgFromH5 = self.msgParseUtil.msgParse(self.navMsg)
                        atama, patientId, kubi = msgFromH5.get("msg"), msgFromH5.get("patientId"), msgFromH5.get("mode")
                        if atama == "nav":
                            if kubi == "word":
                                describe = self.threadPancreas.getStationTips()
                                UdpMsgtoNavStationTips = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{describe}<$2>"
                                self.WebSocketServer.SendMsgtoNav(UdpMsgtoNavStationTips)

                            elif kubi == "current":
                                curTable = self.threadPancreas.getNavCurTable()
                                UdpMsgtoNavStation = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{curTable}<$2>"
                                self.WebSocketServer.SendMsgtoNav(UdpMsgtoNavStation)

                            elif kubi == "check_time":
                                elasped = self.threadPancreas._HandleTime()
                                UdpMsgtoNavStation = f"<$1>{atama}<$$>{self.currentUser.patientId}<$$>{kubi}<$$>{elasped}<$2>"
                                self.WebSocketServer.SendMsgtoNav(UdpMsgtoNavStation)



                    # 计算主线程计算耗时
                curPlayDuration = int((cv2.getTickCount() - curPlayStartTime) / cv2.getTickFrequency() * 1000)  # 单位：毫秒
                    # 每600帧输出一次log
                if (self.currentFrameIndex % 600) == 0:
                        #self._writeLog(f" 主循环耗时: {curPlayDuration} ms", False)
                        # 写入log后重新计算耗时
                    curPlayDuration = int((cv2.getTickCount() - curPlayStartTime) / cv2.getTickFrequency() * 1000)  # 单位：毫秒
                    
                    # 显示视频帧
                # self._ShowVideo(originFrame,drawFrame,videoCapture)
                cv2.imshow("video", drawFrame)

                #     # 控制帧显示速率，如果是视频则以视频FPS为基准，如果是直播，则直播最快不超过30FPS
                # if videoFps > 0:
                #     waitKeyTime = int((1000. / videoFps) - curPlayDuration)
                # else:
                #     waitKeyTime = 33 - curPlayDuration  # 如果比30FPS快，则固定30FPS
                # if waitKeyTime < 1:
                #     waitKeyTime = 1
                key = cv2.waitKey(1)
                if key == 27: #esc
                    break
        except KeyboardInterrupt: #按下Ctrl+C
            print("用户按压Ctrl+C,程序退出")
            #self._writeLog("用户按压Ctrl+C,程序退出")
        except:
            traceback.print_exc()
            print(traceback.print_exc())
            #self._writeLog(f"主循环异常！！，程序退出\n{traceback.format_exc()}")
        finally:
            #self._writeLog("主循环结束，程序退出")
            self.ResetAllThreads()
            self.ResetCurrentUser()
            self.ExitAllThreads()
            videoCapture.release()
            cv2.destroyAllWindows()
            sys.exit(1)

    def CreateUser(self):
        if self.currentCheckType == "bi" and self.currentUser is None:
            self.currentUser = UserBase(True, self.userPath, self.currentCheckType)
        else:
            pass


    
    def InitAllSockets(self):
        self.WebSocketServer = WebSocketManagement(self.logWebsocket, port=ConfigWebSocket.WEBSOCKET_SERVER_NAVQC_PORT)  # 实例化
        self.WebSocketServerLive = WebSocketManagement(self.logWebsocket, port=ConfigWebSocket.WEBSOCKET_SERVER_LIVE_PORT)
        

    def InitAllThreads(self):
        
       
        #########################启动公用线程##############################
        self.WebSocketServer.Start()
        self.WebSocketServerLive.Start()
        # 开启公用线程
        # 启动胆胰/纵膈检查线程
        self.threadSaveImage = SaveImage(self.saveImgSize)
        self.threadMediasttinum = MediastinumSeg(self.isDebug
                                          ,self.isDrawFlag
                                          ,self.logDRColo
                                          ,self.threadSaveImage
                                          ,self.UDPSockeCsv
                                          ,self.modelPathDRMediasttinumSeg   
                                          ,"dick1")
        
        self.threadPancreas = PancreasSeg(self.isDebug
                                          ,self.isDrawFlag
                                          ,self.logDRColo
                                          ,self.threadSaveImage
                                          ,self.UDPSockeCsv
                                          ,self.modelPathDRPancerasSeg   
                                          ,"dick1")
        self.threadCheckModeStream = CheckModeStream(self.logWebsocket, self.WebSocketServerLive)
        self.threadSaveImage.start()
        self.threadCheckModeStream.start()
        #self._writeLog("~~~公用线程启动运行")
        self.watchThreadStartTime = time.time() #重置线程监控起始时间

    # 纵膈相关的线程 启动
    def StartMediastinumThreads(self):
        if not self.threadMediasttinum.is_alive():
            self.threadMediasttinum.SetLoopFlag(True)
            self.threadMediasttinum.start()  #纵膈线程启动
        #self._writeLog("~~~纵膈相关 启动完毕")
        self.watchThreadStartTime = time.time() #重置线程监控起始时间
        
    # 胆胰相关的线程 启动
    def StartPancreaThreads(self):
        if not self.threadPancreas.is_alive():
            self.threadPancreas.SetLoopFlag(True)
            self.threadPancreas.start()
        #self._writeLog("~~~胆胰线程 启动完毕")
        self.watchThreadStartTime = time.time() #重置线程监控起始时间

    # 纵膈相关的线程 停止
    def StopMediastinumThreads(self):
        if self.threadMediasttinum.is_alive():
            self.threadMediasttinum.Exit()
            self.threadMediasttinum.join()
            self.threadMediasttinum.clear()
        #self._writeLog("~~~停止纵膈相关所有线程完毕")
    
    # 胆胰相关的线程 停止
    def StopPancreaThreads(self):
        if self.threadPancreas.is_alive():
            self.threadPancreas.Exit()
            self.threadPancreas.join()
            self.threadPancreas.clear()
        #self._writeLog("~~~停止胆胰相关所有线程完毕")

    # 纵膈相关的线程 重置
    def ResetMediastinumThreads(self):
        self.threadMediasttinum.ResetAll() #纵膈质控线程
        #self._writeLog("~~~重置纵膈镜相关所有线程完毕")

    # 胆胰相关的线程 重置
    def ResetPancreaThreads(self):
        self.threadPancreas.ResetAll() #胆胰质控线程
        #self._writeLog("~~~重置胆胰镜相关所有线程完毕")
    
    # 重置所有线程
    def ResetAllThreads(self):
        # #####公用线程#######
        # 体内外检查类型线程
        self.threadSaveImage.ResetAll()
        
        #self._writeLog("~~~重置公共所有线程完毕")
        
        # ########纵膈相关的线程#################
        self.ResetMediastinumThreads()
        
        # ########胆胰相关的线程#################
        self.ResetPancreaThreads()
       

    # 退出所有线程
    def ExitAllThreads(self):
        # #####公用线程#######
        if self.threadSaveImage.is_alive():
            self.threadSaveImage.Exit()
            self.threadSaveImage.join()
            self.threadSaveImage.clear()
    
        
        ######胆胰相关线程#######
        self.StopPancreaThreads()

        #self._writeLog("~~~停止所有线程完毕")

        # 关闭所有日志文件
        self.CloseAllLog()

    # 监控所有线程
    def WatchAllThreads(self):
        isAllThreadsOk = True
        #10秒检查一次线程是否停止(因为线程全部启动完毕需要5秒以上)
        if 0 <=  time.time() - self.watchThreadStartTime < 10:
            return isAllThreadsOk
        self.watchThreadStartTime = time.time() #大于5秒重置时间

        # 公共线程监控
        if not self.threadSaveImage.is_alive():
            isAllThreadsOk = False
            #self._writeLog("threadSaveImage 异常退出")
        
      
        # 纵膈镜相关线程监控
       
        if not self.threadMediasttinum.is_alive():
            isAllThreadsOk = False
            #self._writeLog("纵膈相关线程监控 异常退出") 
        
                
        # 胆胰镜相关线程监控
       
        if not self.threadPancreas.is_alive():# 质控线程监控
            isAllThreadsOk = False
            #self._writeLog("胆胰镜相关线程监控 异常退出")
        
        # 失败三次退出程序
        if not isAllThreadsOk:
            self.watchThreadErrorCount = self.watchThreadErrorCount + 1

        else:
            self.watchThreadErrorCount = 0 #线程启动成功就重置
        if self.watchThreadErrorCount > 3: #失败大于3次退出程序
            return False
        # print("watchThreadErrorCount:",self.watchThreadErrorCount)
        return True
    
    # 重置当前用户
    def ResetCurrentUser(self):
        self.currentCheckType = ""
        self.patientId = "" # 用户名（胆胰纵膈切换时需要保存一下）
        self.currentUser = None
        

        # 与工作站连通
        self.wsMsg = {}  # 用于存放工作站发送的患者信息
        self.WebSocketServer._Reset() 
        #self._writeLog("重置当前用户信息完毕")

    # 初始化所有log
    def InitAllLog(self):
        todayTimeStr = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        today_path = os.path.join(self.logDir, todayTimeStr)
        if not os.path.isdir(today_path):
            os.makedirs(today_path)
        self.logMain = open(os.path.join(today_path, todayTimeStr + "_log_Main.txt"), "a+", encoding="UTF-8")
        self.logInOutStomachColo = open(os.path.join(today_path, todayTimeStr + "_log_InOutStomachColo.txt"), "a+", encoding="UTF-8")
        self.logCheckTypeStomachColo = open(os.path.join(today_path, todayTimeStr + "_log_CheckTypeStomachColo.txt"), "a+", encoding="UTF-8")
        self.logSPSurgicalTool = open(os.path.join(today_path, todayTimeStr + "_log_SPSurgicalTool.txt"), "a+", encoding="UTF-8")
        
        #胆胰相关log
        self.logQCStomach = open(os.path.join(today_path, todayTimeStr + "_log_QCStomach.txt"), "a+", encoding="UTF-8")
        self.logDRStomach = open(os.path.join(today_path, todayTimeStr + "_log_DRStomach.txt"), "a+", encoding="UTF-8")

        #纵膈相关log
        self.logQCColo = open(os.path.join(today_path, todayTimeStr + "_log_QCColo.txt"), "a+", encoding="UTF-8")
        self.logDRColo = open(os.path.join(today_path, todayTimeStr + "_log_DRColo.txt"), "a+", encoding="UTF-8")
        self.logPostFile = open(os.path.join(today_path, todayTimeStr + "_log_PostFile.txt"), "a+", encoding="UTF-8")
        self.logWebsocket = open(os.path.join(today_path, todayTimeStr + "_log_Websocket.txt"), "a+", encoding="UTF-8")
        
        
            
    def CloseAllLog(self):
        #胆胰相关
        self.logQCStomach.close()
        self.logDRStomach.close()
        #纵膈相关
        self.logQCColo.close()
        self.logDRColo.close()
        self.logPostFile.close()
        self.logWebsocket.close()
        #公用
        self.logSPSurgicalTool.close()
        self.logInOutStomachColo.close()
        self.logCheckTypeStomachColo.close()
        self.logMain.close()

    def _WriteLog(self, logInfo:str, isPrint=True):
        logMainStr = time.strftime("%Y-%m-%d,%H:%M:%S, ", time.localtime(time.time()))
        self.logMain.write(logMainStr + logInfo+ "\n")
        self.logMain.flush()
        # 既要打印又处于debug模式时才会真正打印信息
        if isPrint and self.isDebug:
            print(logMainStr + logInfo)
    

    # def nothing(self, emp):
    #     pass

    
    
    # def _ShowVideo(self,originFrame,drawFrame, videoPicture):
    #     #注意：画的框并不精确，因为病变结果列表是把多张图预测的结果组合在一起返回的
    #     if True:
    #         cv2.namedWindow('video', cv2.WND_PROP_FULLSCREEN)
    #         cv2.moveWindow('video', 0, 0)
    #         total_frame =  videoPicture.get(cv2.CAP_PROP_FRAME_COUNT)
    #         cv2.createTrackbar("processbar", "video", 0, int(total_frame), lambda x: print(x))
    #         cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    #         # 显示内容
    #         displayFrame = np.zeros_like(originFrame)
    #         displayFrame[self.offsetY:self.offsetY + self.cropHeight,
    #                     self.offsetX:self.offsetX + self.cropWidth, ...] = drawFrame
    #         cv2.imshow("video", displayFrame)

