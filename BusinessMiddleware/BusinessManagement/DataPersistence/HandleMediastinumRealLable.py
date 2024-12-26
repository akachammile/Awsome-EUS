import os, time, shutil
from collections import deque
# from BusinessMiddleware.BusinessManagement.BaseThread import BaseThread
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigMediastinum import MediastinumConstants
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigMediastinum import ConfigMediastinum
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigMap import ConfigMap
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigQC import ConfigQC
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigCommon import ConfigCommon

from BusinessMiddleware.BusinessManagement.DataPersistence.PancreasUtils import PancreasUtils

class HandleMediastinumRealLable():

    def __init__(self) -> str:
        # super.__init__(self)
        
        self.queueMax = 30
        self.currentEusTargetList = deque(maxlen=self.queueMax)  # 部位缓存
        self.newCurrentEusTargetList = deque(maxlen=self.queueMax)  # 30帧内部位的缓存
        self.haveCheckStationTow = False
        self.modelQcCount = 1
        self.probThresh = 0.25
        # self.currentUser = ""
        self.currentNavTable = ["0"] * 17
        self.currentNavTableStr = ""
        self.sendCurrentNavTableStr = True
        self.pancreasUtils = PancreasUtils()

        # 导航统计条
        self.navLine = [""] * 12
        self.statisticsLine = [""] * 12
        self.labelReal = [False] * 12
        self.lastTempTav = [0] * 12
        self.lastLastTempTav = [0] * 12
        self.tempNavTable = [0] * 12

        # 时间
        self.updateNavTime = time.time()
        self.updateEusTargetTime = time.time()
        self.updateWordTime = time.time()
        self.updateTableTime = time.time()
        self.lastUpdateCheckTime = time.time()

        self.modelTableHead = "AOA,LCC,AZ,DA,PA,LA,AA,IVC,SVC,RA,LV,INV"
        self.stationInstruction = [
            "距门齿35-40cm看到肝内下腔静脉稍左旋看到右心（RA）并看到其分支SVC（10R 站LN）和IVC（第9站LN），稍退镜并左旋镜身，约距门齿27-32cm看到左心房（LA）",
            "继续左旋，看到肺动脉（PA），位于左心房（LA）和肺动脉（PA）之间的即为隆突下间隙（第7站LN）",
            "向右旋转180°看到降主动脉DA（第8站LN），沿DA左旋看到脐静脉AZ",
            "沿DA退镜至约距门齿25-27cm，沿DA右旋90°看到AP窗（第4，5，6站LN）",
            "沿主动脉弓退镜至距门齿23-25cm稍左旋看到LSC（第2L站LN）,LCC及LJV（第1，3A站LN）"]
        self.currentStation = 0
        self.newCurrentStation = 0
        self.currentStatisticIndex = time.time()

        self.historyNavTable = self.getInitHistoryTable()
        self.firstCheckOrNot = self.getInitHistoryRow()

        
    
    def initPatient(self):
        self.historyNavTable = self.getInitHistoryTable()
        self.firstCheckOrNot = self.getInitHistoryRow()
        self.historyChkIndex = 0
        self.curWebShortcutImgs = []
        self.curBezierUrl = ""              
        self.curStraightScatterUrl = ""
        self.currentStation = 0
        self.currentStatisticIndex = time.time()
        self.currentCheckTime = False
        self.sendCurrentNavTableStr = True


    def handleFrameCache(self
                        ,frameContent:list
                        ,navLine:list
                        ,statisticsLine:list
                        ,labelReal:list):
        
        for i in range(len(frameContent)):
            fn_content = frameContent[i]
            fn_content_arr = fn_content.split("^")
            label = int(fn_content_arr[3])
            prob = float(fn_content_arr[4])

            if prob < self.probThresh:
                continue

            coordinates_info = fn_content_arr[5].split(",")
            x = coordinates_info[0]
            y = coordinates_info[1]
            w = int(coordinates_info[2])
            h = int(coordinates_info[3])

            area = str(w * h)
            t = time.time() - self.currentStatisticIndex

            navLine[label] = "_".join([fn_content_arr[3], x, y, area])
            statisticsLine[label] = "_".join([str(t), x, y, area])
            labelReal[label] = True

        return navLine, statisticsLine, labelReal
        
    def handlePredictInfo(self, patientId:str, frameContent: list):
        self.CurrentCheckTime = True  # checked user
        self.FirstCheckPatient = True # 没有用户不会更新
        # if self.currentUser == "" | self.currentUser != patientId:
        #     # initPatient()
        #     self.currentUser = patientId
        #     self.currentCheckTime = True  # checked user
        #     self.firstCheckPatient = True # 没有用户不会更新
        #     self.lastTempTav = []*12
        #     self.lastLastTempTav = self.lastTempTav
        self.lastUpdateCheckTime = time.time()
        # currentNavTable = ["0"] * 12
        navLine, statisticsLine, navTableCache = self.handleFrameCache(frameContent, self.navLine, self.statisticsLine, self.labelReal)
        if (time.time() - self.updateNavTime) * 1000 > 1000 and self.sendCurrentNavTableStr == True:
            currentNavTable = ["0"] * 12
            # currentNavTable = self.handleRealLabelPart(labelReal)

            for i in range(len(navTableCache)):
                # 判断条件，根据累加值与阈值对 current_nav_table 赋值
                if (self.lastTempTav[i] + self.lastTempTav[i] + self.tempNavTable[i]) > self.modelQcCount:
                    currentNavTable[i] = MediastinumConstants.NAV_CHECKED
                else:
                    currentNavTable[i] = MediastinumConstants.NAV_EMPTY


            self.lastLastTempTav = self.lastTempTav
            self.lastTempTav = self.tempNavTable
            if (currentNavTable[MediastinumConstants.IVC] == MediastinumConstants.NAV_CHECKED or
                currentNavTable[MediastinumConstants.SVC] == MediastinumConstants.NAV_CHECKED or
                currentNavTable[MediastinumConstants.RA] == MediastinumConstants.NAV_CHECKED):
                 self.newCurrentStation = 0
            elif (currentNavTable[MediastinumConstants.LA] == MediastinumConstants.NAV_CHECKED or
                currentNavTable[MediastinumConstants.AA] == MediastinumConstants.NAV_CHECKED):
                 self.newCurrentStation = 1
            elif (currentNavTable[MediastinumConstants.AZ] == MediastinumConstants.NAV_CHECKED or
                currentNavTable[MediastinumConstants.DA] == MediastinumConstants.NAV_CHECKED):
                 self.newCurrentStation = 2
            elif currentNavTable[MediastinumConstants.AOA] == MediastinumConstants.NAV_CHECKED or\
                (currentNavTable[MediastinumConstants.LPA] == MediastinumConstants.NAV_CHECKED and\
                  currentNavTable[MediastinumConstants.RPA] == MediastinumConstants.NAV_CHECKED):
                 self.newCurrentStation = 3
            elif (currentNavTable[MediastinumConstants.LCC] == MediastinumConstants.NAV_CHECKED or
                currentNavTable[MediastinumConstants.INV] == MediastinumConstants.NAV_CHECKED):
                 self.newCurrentStation = 4
            self.currentNavTableStr = "[" + ",".join(map(str, self.currentNavTable)) + "]"
            self.pancreasUtils.AppendRecord(patientId, self.modelTableHead, ",".join(statisticsLine))
            self.updateNavTime = time.time()
            self.tempNavTable = [] * 12

            if (time.time() - self.updateEusTargetTime) * 1000 > 1 * 1000:
                if len(navLine) > 0:
                    self.currentEusTargetList.append(navLine)
                self.updateEusTargetTime = time.time()

    def makeCopyAndGetRecord(self, patientId, basePath):
        tmpUri = self.pancreasUtils.sort_files(basePath, name="_tmp_")
        
        if len(tmpUri) > 2:
            self.del_files(basePath, "_tmp_", 2)
            self.del_files(basePath, "strsca", 2)
            self.del_files(basePath, "bezier", 2)
            
        srcPath = self.pancreasUtils.getRecordPath(basePath)
        dstPath = self.pancreasUtils.getTempRecordPath(basePath)

        if os.path.isfile(srcPath):
            shutil.copy(srcPath, dstPath)
        else:
            with open(dstPath, 'w') as f:
                pass

        inOutPath = patientId + "|"  + dstPath + "|" + basePath

        return self.currentEusTargetList, inOutPath

    def del_files(self, base, search, left_num):
        tmp_uris = self.pancreasUtils.sort_files(base, search)

        # 删除多余的文件，保留 `left_num` 个最新的文件
        for i in range(len(tmp_uris) - left_num):
            tmp_file = tmp_uris[i]
            try:
                os.remove(os.path.join(base, tmp_file))
            except Exception as e:
                continue

    def ShowCurrentStageWord(self):
        if self.newCurrentStation == ConfigMap.Station.STATION_NONE:
            return str(self.newCurrentStation) + "|&nbsp"
        return str(self.newCurrentStation + 1) + "|" + self.stationInstruction[self.newCurrentStation]
    
    def ShowCurrentNavTable(self):
        currentNavTableStr = self.currentNavTableStr
        self.CurrentNavTableStr = ""
        self.SendCurrentNavTableStr = True
        return currentNavTableStr

    def handleQC(self, patientId:str, fn_content:list):

        for content in fn_content:
            fn_content_arr = content.split("^")
            arr = fn_content_arr[4].split(patientId)

            if ConfigQC.SCREENSHOT_RAW == ConfigCommon.ScreenshotRaw:
                url = self.pancreasUtils.getRecordPath(patientId) + arr[1]
            elif ConfigQC.SCREENSHOT_PREDICT == ConfigQC.SCREENSHOT_RAW:
                url = self.pancreasUtils.getRecordPath(patientId) + arr[1]

            index = 0
            if len(self.curWebShortcutImgs) > 4:
                index = 1

            self.curWebShortcutImgs = self.curWebShortcutImgs[index:] + [url]

    def handleStatisticChart(self, urlList:list, statisticPath:str):
        base = self.pancreasUtils.getWebPatientPath(statisticPath)
        if urlList:
            for fn in urlList:
                url = base + "/" + fn
                if "bezier" in fn:
                    self.curBezierUrl = url
                if "strsca" in fn:
                    self.curStraightScatterUrl = url
            return self.curBezierUrl, self.curStraightScatterUrl
        else:
            return "",""

    def handleNavigation(self):
            
            if time.time() - self.updateTableTime > 1:
                self.matchingHistoricalData(self.currentEusTargetList)
                self.historyNavTableStr = "[" + ",".join(map(str, self.historyNavTable)) + "]"
            
            self.updateTableTime = time.time()

    def matchingHistoricalData(self, historicalData:list):
        matchingWindowSizeRow = 10
        station1 = [MediastinumConstants.IVC, MediastinumConstants.SVC, MediastinumConstants.RA]
        station2 = [MediastinumConstants.LPA, MediastinumConstants.RPA, MediastinumConstants.LA, MediastinumConstants.AA]
        station3 = [MediastinumConstants.AZ, MediastinumConstants.DA]
        station4 = [MediastinumConstants.AOA, MediastinumConstants.LPA, MediastinumConstants.RPA]
        station5 = [MediastinumConstants.LCC, MediastinumConstants.INV]
        navTableWin = self.getInitHistoryRow()
        chkBgnIndex = self.historyChkIndex
        rowCount = 0
        tmpCurrentStation = 0
        
        for line in historicalData:
            if rowCount < chkBgnIndex:
                rowCount += 1
                continue
            
            line_arr = line

            for entry in line_arr:
                tmp_label_str = entry.split(",")[0]
                if "_" in tmp_label_str:
                    label = tmp_label_str.split("_")[0]
                    try:
                        tmp_label = int(label)
                        navTableWin[tmp_label] = True
                    except ValueError:
                        continue

            if (rowCount - self.historyChkIndex) % matchingWindowSizeRow == 0 or len(historicalData) - rowCount < matchingWindowSizeRow:
                for station_group, station_constant in [
                    (station1, MediastinumConstants.STATION1),
                    (station2, MediastinumConstants.STATION2),
                    (station3, MediastinumConstants.STATION3),
                    (station4, MediastinumConstants.STATION4),
                    (station5, MediastinumConstants.STATION5),
                ]:
                    for n in station_group:
                        if navTableWin.get(n, False):
                            self.historyNavTable[n] = MediastinumConstants.NAV_CHECKED
                        if self.historyNavTable.get(n) != MediastinumConstants.NAV_CHECKED:
                            if self.currentStation > station_constant:
                                self.historyNavTable[n] = MediastinumConstants.NAV_NOT_CHECK
                            else:
                                self.historyNavTable[n] = MediastinumConstants.NAV_NOT_CHK_YET

                if all(self.historyNavTable.get(station) == MediastinumConstants.NAV_CHECKED for station in station1):
                    tmpCurrentStation = MediastinumConstants.STATION1
                elif all(self.historyNavTable.get(station) == MediastinumConstants.NAV_CHECKED for station in station2):
                    tmpCurrentStation = MediastinumConstants.STATION2
                elif all(self.historyNavTable.get(station) == MediastinumConstants.NAV_CHECKED for station in station3):
                    tmpCurrentStation = MediastinumConstants.STATION3
                elif all(self.historyNavTable.get(station) == MediastinumConstants.NAV_CHECKED for station in station4):
                    tmpCurrentStation = MediastinumConstants.STATION4
                elif all(self.historyNavTable.get(station) == MediastinumConstants.NAV_CHECKED for station in station5):
                    tmpCurrentStation = MediastinumConstants.STATION5

                navTableWin = self.getInitHistoryRow()
                self.currentStation = tmpCurrentStation
            
            if rowCount > chkBgnIndex:
                chkBgnIndex += 1
            rowCount += 1
        
        self.historyChkIndex = chkBgnIndex

    def getInitHistoryTable(self):
        return ["0"] * 12
    
    def getInitHistoryRow(self):
        return [False] * 12


                    








