from queue import Queue


class InfoAnalysis:
    def __init__(self) -> None:
        self.resultList = {}
        self.infoQueue = Queue(max=30)

    def getInfoQueue(self):
        return self.infoQueue

    def setInfo2Queue(self, message):
        if self.infoQueue.full():
            self.infoQueue.get()
        self.infoQueue.put(message)

    def startInfoAnalysis(self):
        if not self.infoQueue.empty():
            analysisInfo = self.infoQueue.get()
            if "|" in analysisInfo:
                result = analysisInfo.split("|")
                if len(result) != 3:
                    return
                if result:
                    deviceId = result[0]
                    self.resultList.update({"deviceId": deviceId})
                    if len(result[1]) > 10:
                        imgInfos = result[1].split(";")
                        self.resultList.update({"imageInfo": imgInfos})

                    if len(result[2]) > 10:
                        predInfos = result[2].split(";")
                        self.resultList.update({"predInfos": predInfos})
