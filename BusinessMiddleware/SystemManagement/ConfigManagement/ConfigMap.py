class ConfigMap:
    class Station:
        STATION_NONE = -1
        STATION_1 = 0
        STATION_2 = 1
        STATION_3 = 2
    

    class Part:
        LIVERS2S3PART = 0
        CAPART = 1
        PBPART = 2
        LKPART = 3
        PTSPART = 4
        LADPART = 5
        CONFLUENCE1PART = 6
        PHPART = 7
        PNPART = 8
        PVPART = 9
        LIVERS4PART = 10
        GB1PART = 11
        CBDPVPART = 12
        CONFLUENCE2PART = 13
        GB2PART = 14
        UPPART = 15
        PAPILLAPART = 16

    class Navigation:
        ATAMA_NAV = "nav"
        KUBI_NAV_WORD = "word"
        KUBI_NAV_CURRENT_TABLE = "current"
        KUBI_NAV_HISTORY_TABLE = "history"
        ATAMA_QC = "qc"
        KUBI_QC_SHORTCUT = "shortcut"
        KUBI_QC_STATISTICS = "statistics"
        ATAMA_LIVE = "live"
        KUBI_LIVE_RESOLUTION = "resolution"
        KUBI_LIVE_CHECK_TIME = "check_time"

    class NavigationStatus:
        EMPTY = "0"       # 空
        NOT_CHK_YET = "1" # 还没有检查
        CHECKED = "2"     # 已检查
        NOT_CHECK = "3"   # 漏检查

 