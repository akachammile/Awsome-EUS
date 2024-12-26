# cython: language_level=3
import os
from datetime import datetime


class UserBase:
    def __init__(self, isDebug, userSaveBaseDir:str, currentCheckType:str):
        self.isDebug = isDebug
        self.saveBaseDir = userSaveBaseDir # D:\user
        self.currentCheckType = currentCheckType

        self.qcPath = ""  # qc路径
        self.patientId = ""
        self.today = datetime.now().strftime("%Y%m%d")
        self.statisticPath = "" # static路径
        self.currentUserPath = None
        self._CreateUser()

    def ResetAll(self):
        self.checkType = "bi"
        self.qcPath = ""  # qc路径
        self.today = "" # 当日
        self.statisticPath = "" # static路径
        self.currentUserPath = None

    def GetCurrentCheckType(self):
        return self.currentCheckType

    def SetCurrentCheckType(self, currentCheckType):
        self.currentCheckType = currentCheckType

    def _CreateUser(self):
        self.patientId = str(datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + self.currentCheckType)
        self.currentUserPath = os.path.join(self.saveBaseDir, str(self.today), self.patientId)
        self.qcPath = os.path.join(self.currentUserPath, "QC")
        self.statisticPath = os.path.join(self.currentUserPath, "Statistic")


        if not os.path.isdir(self.currentUserPath):
            os.makedirs(self.currentUserPath)

        if not os.path.exists(self.qcPath):
            os.makedirs(self.qcPath, exist_ok=True)

        if not os.path.exists(self.statisticPath):
            os.makedirs(self.statisticPath, exist_ok=True)

    # def ExitUser(self):
    #     self._SaveCheckedData() # 保存：UserInfo.json

    # def _SaveCheckedData(self):
    #     raise NotImplemented

    # def _SaveCheckedInfo(self):
    #     raise NotImplemented

    # def _SaveCheckedScore(self):
    #     raise NotImplemented

    # def GetQCStatisticInfo(self):
    #     raise NotImplemented