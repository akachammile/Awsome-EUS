#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import traceback
import time
import base64

import cv2

from BusinessMiddleware.BusinessManagement.BaseThread import BaseThread



class CheckModeStream(BaseThread):
    def __init__(self, logWebsocket, websocketStream):
        super().__init__()
        self.frame = None
        self.logFile = logWebsocket
        self.WebSocketServerCheckMode = websocketStream

    def _Reset(self):
        self.frame = None
    
    def _WriteLog(self, msg):
        logStr = time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime(time.time())) + " | "
        self.logFile.write(logStr+msg+"\n")
        self.logFile.flush()

    def setCurrentFrame(self, frame):
        self.frame = frame

    def streaming(self):
        try:
            if self.frame is not None:
                self.WebSocketServerCheckMode
                currentFrame = cv2.resize(self.frame, (600, 480))
                _, buffer = cv2.imencode(".jpg", currentFrame)
                frame_data = base64.b64encode(buffer.tobytes()).decode("utf-8")
                self.WebSocketServerCheckMode.SendMsgtoLive(str_msg = frame_data)
                self.frame = None
        except:
            self._WriteLog(f"Send base64 img error:{traceback.format_exc()}")
        

    def run(self):
        while self.loopFlag:
            # 检查是否重置
            if self.resetFlag:
                self._Reset()
                self.resetFlag = False
            threadStartTime = time.time()
            self.streaming()
            # threadExecuteTime = time.time() - threadStartTime
            # threadSleepTime = self.sleepTime - threadExecuteTime
            # if threadSleepTime > 0:
            #     time.sleep(threadSleepTime)
            # print(time.time()-threadStartTime)
            time.sleep(0.04)
        
