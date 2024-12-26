import os, time, shutil
from collections import deque
# from BusinessMiddleware.BusinessManagement.BaseThread import BaseThread
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigPancreas import PancreasConstants, ConfigPancreas
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigMap import ConfigMap
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigQC import ConfigQC
from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigCommon import ConfigCommon
from BusinessMiddleware.BusinessManagement.DataPersistence.PancreasUtils import PancreasUtils

class HandlePancerasRealLable():

    def __init__(self) -> str:
        # super.__init__(self)
        self.currentNavTable = ["0"] * 17
        self.tempNavTable = [0] * 17
        self.queueMax = 30
        # self.saveImageThreadHandle = saveImageThreadHandle
        self.currentEusTargetList = deque(maxlen=self.queueMax)  # 部位缓存
        self.newCurrentEusTargetList = deque(maxlen=self.queueMax)  # 30帧内部位的缓存
        self.historyNavTableStr = ""
        self.haveCheckStationTow = False
        self.modelQcCount = 1
        self.probThresh = 0.25
        self.currentUser = ""
        self.currentNavTableStr = ""
        self.sendCurrentNavTableStr = True
        self.pancreasUtils = PancreasUtils()
        self.historyChkIndex = 0
        self.statisticPath = ""
        self.today = ""
        self.CurrentCheckTime = False
        self.FirstCheckPatient = False
        

        self.count = 0

        # 图像列表
        self.curWebShortcutImgs = []
        self.curBezierUrl = ""
        self.curStraightScatterUrl = ""
        self.newCurrentStation = 0

        # 历史列表
        self.historyNavTable = self.getInitHistoryTable()
        # self.firstCheckOrNot = self.getInitHistoryRow()


        # 导航统计条
        self.navLine = [""] * 23
        self.statisticsLine = [""] * 23
        self.labelReal = [False] * 23

        # 时间
        self.updateNavTime = time.time()
        self.updateEusTargetTime = time.time()
        self.updateWordTime = time.time()
        self.updateTableTime = time.time()
        self.LastUpdateCheckTime = time.time()

        self.modelTableHead = "S4,PB,SV,SA,LK,PT,AO,CA,SMA,GB,S,PV,CBD,SMV,UP,LAD,PH,MPD,CONFLUENCE,PN,GBNECK,S3,S2"
        self.stationInstruction = [
            "进入贲门，右旋进镜找寻腹主动脉、腹腔干及肠系膜上动脉，边退镜边右旋，看到胰体、主胰管、左肾，继续左旋看到胰尾、脾脏，稍进镜，并沿着脾动静脉左旋镜身看到汇合区，稍左旋沿着主胰管回到汇合区，边退镜、边稍左旋可进入肝门区。镜身回正后，观察胆囊",
            "进镜至球部，看到门静脉，镜身稍右旋看到胆总管中段，继续右旋并进镜观察胆总管下段、胰体、胰管，然后沿着胆总管左旋并稍退镜观察胆总管上段、胆囊颈部、底部",
            "进镜至降段，顺时针旋转看到腹主动脉，顺时针旋转并缓慢回撤内镜，在主动脉右侧看到勾突，继续退镜的过程中看到胆总管、胰管、乳头"]
        self.currentStation = 0
        self.newCurrentStation = 0
        self.currentStatisticIndex = time.time()

    
    def setPathInfo(self, statisticPath, today):
        self.statisticPath = statisticPath
        self.today = today


    def handleRealLabelPart(self, frameResult:list):
        if frameResult[PancreasConstants.S3] or frameResult[PancreasConstants.S2]:
            self.currentNavTable[PancreasConstants.LIVERS2S3PART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.AO] or frameResult[PancreasConstants.CA]:
            self.currentNavTable[PancreasConstants.CAPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.PB] or frameResult[PancreasConstants.SA] or frameResult[PancreasConstants.SV]:
            self.currentNavTable[PancreasConstants.PBPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.LK]:
            self.currentNavTable[PancreasConstants.LKPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.PT] or frameResult[PancreasConstants.S]:
            self.currentNavTable[PancreasConstants.PTSPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.LAD]:
            self.currentNavTable[PancreasConstants.LADPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.CONFLUENCE] and self. haveCheckStationTow:
            self.currentNavTable[PancreasConstants.CONFLUENCE1PART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.PH] or frameResult[PancreasConstants.CBD] or frameResult[PancreasConstants.MPD]:
            self.currentNavTable[PancreasConstants.PHPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.PN] or frameResult[PancreasConstants.MPD]:
            self.currentNavTable[PancreasConstants.PNPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.PV] or frameResult[PancreasConstants.CBD]:
            self.currentNavTable[PancreasConstants.PVPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.S4]:
            self.currentNavTable[PancreasConstants.LIVERS4PART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.GB]:
            self.currentNavTable[PancreasConstants.GB1PART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.CBD] or frameResult[PancreasConstants.PV]:
            self.currentNavTable[PancreasConstants.CBDPVPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.CONFLUENCE] or frameResult[PancreasConstants.CBD] or frameResult[PancreasConstants.PH]:
            self.currentNavTable[PancreasConstants.CONFLUENCE2PART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.GBNECK]:
            self.currentNavTable[PancreasConstants.GB2PART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.SMV] or frameResult[PancreasConstants.SMA] or frameResult[PancreasConstants.UP]:
            self.currentNavTable[PancreasConstants.UPPART] = PancreasConstants.NAV_CHECKED
        elif frameResult[PancreasConstants.CBD] or frameResult[PancreasConstants.MPD]:
            self.currentNavTable[PancreasConstants.PAPILLAPART] = PancreasConstants.NAV_CHECKED

        for i in range(len(self.currentNavTable)):
            if self.currentNavTable[i] == PancreasConstants.NAV_CHECKED:
                self.tempNavTable[i] = 1
                if len(self.newCurrentEusTargetList) > 30:
                    self.newCurrentEusTargetList.popleft()
                self.newCurrentEusTargetList.append(i)

        len_of_list = len(self.newCurrentEusTargetList)
        real_count = 0
        for m in self.newCurrentEusTargetList:
            if self.tempNavTable[m] > 0:
                self.tempNavTable[m] += 1
            real_count += 1

            if real_count == len_of_list:
                for i, value in enumerate(self.tempNavTable):
                    if value > self.modelQcCount:
                        self.currentNavTable[i] = PancreasConstants.NAV_CHECKED
                    else:
                        self.currentNavTable[i] = PancreasConstants.NAV_EMPTY

        return self.currentNavTable
    
    def handleFrameCache(self, frameContent:list, navLine:list, statisticsLine:list, labelReal:list):
        for i in range(len(frameContent)):
            fn_content = frameContent[i]
            #predInfo =['1^03^01^01^0.28^0.62^0.33^0.1^0.13'; 
            #          ['15^03^01^1^0.6525^80,881,212,455 ]
		    #seq，environment，model type(01 classification)，label，probability，x,y,w,h
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
            t = int(time.time()) - int(self.currentStatisticIndex)

            navLine[label] = "_".join([fn_content_arr[3], x, y, area])
            statisticsLine[label] = "_".join([str(t), x, y, area])
            labelReal[label] = True

        return navLine, statisticsLine, labelReal

    def handlePredictInfo(self, patientId:str, frameContent: list):
        self.CurrentCheckTime = True  # checked user
        self.FirstCheckPatient = True # 没有用户不会更新
        # if self.currentUser == "" | self.currentUser != patientId:
        #     # initPatient()
        #     CurPatientId = patientId
        #     CurrentCheckTime = True  # checked user
        #     FirstCheckPatient = True # 没有用户不会更新
        self.LastUpdateCheckTime = time.time()
        currentNavTable = ["0"] * 12
        navLine, statisticsLine, labelReal = self.handleFrameCache(frameContent, self.navLine, self.statisticsLine, self.labelReal)
        if (time.time() - self.updateNavTime) * 1000 > 1000 and self.sendCurrentNavTableStr == True:
            currentNavTable = self.handleRealLabelPart(labelReal)
            station_1 = list(ConfigPancreas.STATIONS.values())

            station_1_cnt = 0
            for i, ivalue in enumerate(currentNavTable):
                if ivalue == PancreasConstants.NAV_CHECKED:
                    for jvalue in station_1:
                        if i == jvalue:
                            station_1_cnt += 1

            if station_1_cnt > 2:
                #FIXME
                self.newCurrentStation = ConfigMap.Station.STATION_1
            elif (currentNavTable[PancreasConstants.CBDPVPART] == PancreasConstants.NAV_CHECKED or
                currentNavTable[PancreasConstants.CONFLUENCE2PART] == PancreasConstants.NAV_CHECKED) or \
                (currentNavTable[PancreasConstants.GB2PART] == PancreasConstants.NAV_CHECKED and
                currentNavTable[PancreasConstants.CONFLUENCE2PART] == PancreasConstants.NAV_CHECKED):
                self.newCurrentStation = ConfigMap.Station.STATION_2
                self.haveCheckStationTow = False
            elif currentNavTable[PancreasConstants.UPPART] == PancreasConstants.NAV_CHECKED or \
                currentNavTable[PancreasConstants.PAPILLAPART] == PancreasConstants.NAV_CHECKED:
                self.newCurrentStation = ConfigMap.Station.STATION_3

            self.currentNavTableStr = "[" + ",".join(map(str, currentNavTable)) + "]"
            path = self.pancreasUtils.getRecordPath(self.statisticPath)
            self.pancreasUtils.AppendRecord(self.modelTableHead, ",".join(statisticsLine), path)
            self.updateNavTime = time.time()

            self.navLine = [""] * 23
            self.statisticsLine = [""] * 23
            self.labelReal = [False] * 23
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
            # Update "currentStation", "historyNavTable", "historyChkIndex"
            self.matchingHistoricalData(self.currentEusTargetList)
            self.historyNavTableStr = "[" + ",".join(map(str, self.historyNavTable)) + "]"
        
        self.updateTableTime = time.time()

    def matchingHistoricalData(self, historicalData:list):
        matchingWindowSizeRow = 10

        station1 = [PancreasConstants.LIVERS2S3PART, PancreasConstants.CAPART, PancreasConstants.PBPART,
                    PancreasConstants.LKPART, PancreasConstants.PTSPART, PancreasConstants.LADPART,
                    PancreasConstants.CONFLUENCE1PART, PancreasConstants.PHPART,
                    PancreasConstants.PNPART, PancreasConstants.PVPART,
                    PancreasConstants.LIVERS4PART, PancreasConstants.GB1PART]

        station2 = [PancreasConstants.CBDPVPART, PancreasConstants.CONFLUENCE2PART,
                    PancreasConstants.GB2PART]

        station3 = [PancreasConstants.UPPART, PancreasConstants.PAPILLAPART]
        
        labelRealTable = [False] * 23
        navTableWin = self.getInitHistoryRow()
        
        chkBgnIndex = self.historyChkIndex
        rowCount = 0
        tmpCurrentStation = 0
        
        for i in historicalData:
            # skip handled data
            if rowCount < chkBgnIndex:
                rowCount += 1
                continue
            
            line_arr = i
            
            for j in range(len(line_arr)):
                tmp_label_str = line_arr[j].split(",")[0]
                if "_" in tmp_label_str:
                    label = tmp_label_str.split("_")[0]
                    try:
                        tmp_label = int(label)
                        labelRealTable[tmp_label] = True
                    except ValueError:
                        continue
            
            current_nav_table = self.handleRealLabelPart(labelRealTable)
            
            for i in range(len(current_nav_table)):
                if current_nav_table[i] == PancreasConstants.NAV_CHECKED:
                    navTableWin[i] = True
            
            if (rowCount - self.historyChkIndex) % matchingWindowSizeRow == 0 or len(historicalData) - rowCount < matchingWindowSizeRow:
                for n in range(len(station1)):
                    if navTableWin[station1[n]]:
                        self.historyNavTable[station1[n]] = PancreasConstants.NAV_CHECKED
                    if self.historyNavTable[station1[n]] != PancreasConstants.NAV_CHECKED:
                        if self.currentStation > ConfigMap.Station.STATION_1:
                            self.historyNavTable[station1[n]] = PancreasConstants.NAV_NOT_CHECK
                        else:
                            self.historyNavTable[station1[n]] = PancreasConstants.NAV_NOT_CHK_YET
                
                if all(self.historyNavTable[station] == PancreasConstants.NAV_CHECKED for station in [
                    PancreasConstants.LIVERS2S3PART, PancreasConstants.CAPART, PancreasConstants.PBPART,
                    PancreasConstants.LKPART, PancreasConstants.PTSPART, PancreasConstants.LADPART,
                    PancreasConstants.CONFLUENCE1PART, PancreasConstants.PHPART, PancreasConstants.PNPART,
                    PancreasConstants.PVPART, PancreasConstants.LIVERS4PART, PancreasConstants.GB1PART]):
                    tmpCurrentStation =  ConfigMap.Station.STATION_1
                
                for n in range(len(station2)):
                    if navTableWin[station2[n]]:
                        self.historyNavTable[station2[n]] = PancreasConstants.NAV_CHECKED
                    if self.historyNavTable[station2[n]] != PancreasConstants.NAV_CHECKED:
                        if self.currentStation > ConfigMap.Station.STATION_2:
                            self.historyNavTable[station2[n]] = PancreasConstants.NAV_NOT_CHECK
                        else:
                            self.historyNavTable[station2[n]] = PancreasConstants.NAV_NOT_CHK_YET
                
                if all(self.historyNavTable[station] == PancreasConstants.NAV_CHECKED for station in [
                    PancreasConstants.CBDPVPART, PancreasConstants.CONFLUENCE2PART, PancreasConstants.GB2PART]):
                    tmpCurrentStation = ConfigMap.Station.STATION_2
                
                for n in range(len(station3)):
                    if navTableWin[station3[n]]:
                        self.historyNavTable[station3[n]] = PancreasConstants.NAV_CHECKED
                    if self.historyNavTable[station3[n]] != PancreasConstants.NAV_CHECKED:
                        if self.currentStation > ConfigMap.Station.STATION_3:
                            self.historyNavTable[station3[n]] = PancreasConstants.NAV_NOT_CHECK
                        else:
                            self.historyNavTable[station3[n]] = PancreasConstants.NAV_NOT_CHK_YET
                
                if self.historyNavTable[PancreasConstants.UPPART] == PancreasConstants.NAV_CHECKED and \
                self.historyNavTable[PancreasConstants.PAPILLAPART] == PancreasConstants.NAV_CHECKED:
                    tmpCurrentStation = ConfigMap.Station.STATION_3
                
                navTableWin = self.getInitHistoryRow()
                self.currentStation = tmpCurrentStation
            
            if rowCount > chkBgnIndex:
                chkBgnIndex += 1
            
            rowCount += 1
        
        self.historyChkIndex = chkBgnIndex


    def getInitHistoryTable(self):
        return ["0"] * 17
    
    def getInitHistoryRow(self):
        return [False] * 17






                    








