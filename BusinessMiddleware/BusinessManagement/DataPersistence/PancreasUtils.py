import os 
import csv

from datetime import datetime
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigCommon import ConfigCommon
 
class PancreasUtils:

    def __init__(self):
        self.staticPath = ""
        self.writeHeadFlag = False
        self.timeStamp = datetime.now().strftime("%Y%m%d%H%M%S")


    def setStaticBasePath(self, staticPath:str):
        self.staticPath = staticPath

    
    def getTempRecordPath(self, basePath):
        # fileName = "_tmp_" + self.timeStamp + "_" + "ai_pred_record.csv"
        fileName = "_tmp_" +  datetime.now().strftime("%Y%m%d%H%M%S") + "_" + "ai_pred_record.csv"
        filePath = basePath + "\\" + fileName
        # if not os.path.exists(filePath):
        #     os.makedirs(filePath)
        with open(filePath, "w") as f:
            pass
        return filePath
    

    def getWebPatientPath(self, basePath:str) -> str:
        webPath = basePath.replace("D:\\eus", "user")
        return webPath


    def getRecordPath(self, basePath):
        return basePath + "\\" +  "ai_pred_record.csv"
    

    def sort_files(self, path, name=""):
        try:
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return []
        if name:
            files = [f for f in files if name in f]

        files_with_time = []
        for file in files:
            file_path = os.path.join(path, file)
            file_mtime = os.path.getmtime(file_path)
            files_with_time.append((file, file_mtime))

        files_with_time.sort(key=lambda x: x[1], reverse=True)
        sorted_files = [file for file, _ in files_with_time]

        return sorted_files



    def AppendRecord(self, modelClassNames, lineStr, filePath):
        try:
            with open(filePath, 'a', encoding='utf-8') as file:
                if not self.writeHeadFlag:
                    try:
                        column_names = modelClassNames.split(',')
                        file.write(','.join(column_names) + "\r\n")  # 写入列名，并加换行符
                        self.writeHeadFlag = True
                    except Exception as err:
                        print(f"错误{filePath}: {err}")
                
                try:
                    file.write("\r\n" + lineStr)
                except Exception as err:
                    print(f"错误")
        except Exception as err:
            print(f"错误 {filePath}: {err}")