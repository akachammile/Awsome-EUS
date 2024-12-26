import os
from datetime import datetime
from BusinessMiddleware.BusinessManagement.DataPersistence.PancreasUtils import PancreasUtils


class CreateUser(object):
    def __init__(self
                , userPath:str = "D:/eus"
                , staticPath:str = "Statistic"
                , qcPath:str = "QC"
               ) -> None:
            
            self.userPath = userPath
            self.qcPath = qcPath
            self.statisticPath = staticPath

            self.today = datetime.now().strftime("%Y%m%d")
            self.patient = ""
            self.baseDir = ""

    def resetAll(self):
        self.userPath = ""
        self.baseDir = ""
        self.qcPath = ""
        self.statisticPath = ""
        self.socreFile = ""
        self.jsonFile = ""
        self.today = ""
        self.patient = ""


   
    def getFilePath(self) -> list:
        return self.qcPath, self.statisticPath, self.patient, self.baseDir

            
        
    def createUserpath(self, checkType:str) -> list:
        patientId = str(datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + checkType)
        baseDir = os.path.join(self.userPath, str(self.today), patientId)
        fullQcPath = os.path.join(baseDir, self.qcPath)
        fullStatisticPath = os.path.join(baseDir, self.statisticPath)
    


        if not os.path.exists(baseDir):
            os.makedirs(baseDir, exist_ok=True)

        if not os.path.exists(self.qcPath):
            os.makedirs(self.qcPath, exist_ok=True)

        if not os.path.exists(self.statisticPath):
            os.makedirs(self.statisticPath, exist_ok=True)
        
        PancreasUtils().setStaticBasePath(fullStatisticPath)
        return baseDir ,fullQcPath,fullStatisticPath, patientId

        # if not os.path.exists(self.socreFile):
        #     with open(self.socreFile, "w") as file:
        #         pass

        # if not os.path.exists(self.jsonFile):
        #     with open(self.jsonFile, "w") as file:
        #         pass
        

        

        

        