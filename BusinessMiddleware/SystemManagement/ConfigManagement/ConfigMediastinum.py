class ConfigMediastinum:
    REGIONS = {
        "AOA": 0,  # 主动脉弓 (Aortic Arch)
        "LCC": 1,  # 左锁骨下动脉 (Left Common Carotid Artery)
        "AZ": 2,   # 奇静脉 (Azygos Vein)
        "DA": 3,   # 胸主动脉 (Descending Aorta)
        # "PA": 4, # 肺动脉 (Pulmonary Artery)
        "LPA":4,   # 左肺动脉 (Left Pulmonary Artery)
        "RPA":5,   # 右肺动脉 (Right Pulmonary Artery)
        "LA": 6,   # 左心房 (Left Atrium)
        "AA": 7,   # 升主动脉 (Ascending Aorta)
        "IVC": 8,  # 下腔静脉 (Inferior Vena Cava)
        "SVC": 9,  # 上腔静脉 (Superior Vena Cava)
        "RA": 10,   # 右心房 (Right Atrium)
        "LV": 11,  # 左心室 (Left Ventricle)
        "INV": 12, # 入侵 (Invasion)
    }

    STATIONS = {
        
    }

class ConfigMediastinumQC:
    thProb = 0.25

class MediastinumConstants:
    NAV_EMPTY = "0"
    NAV_NOT_CHK_YET = "1"
    NAV_CHECKED = "2"
    NAV_NOT_CHECK = "3"


    AOA  = 0

    LCC = 1
    AZ = 2
    DA = 3
    # PA = 4
    LPA=4
    RPA=5
    LA = 6
    AA = 7
    IVC = 8
    SVC = 9
    RA = 10
    LV = 11

    INV = 12

    STATION1 = 0
    STATION2 = 1
    STATION3 = 2
    STATION4 = 3
    STATION5 = 4


