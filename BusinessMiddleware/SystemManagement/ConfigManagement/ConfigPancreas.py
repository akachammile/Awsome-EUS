class ConfigPancreas:
    REGIONS = {
        "S4": 0,
        "PB": 1,
        "SV": 2,
        "SA": 3,
        "LK": 4,
        "PT": 5,
        "AO": 6,
        "CA": 7,
        "SMA": 8,
        "GB": 9,
        "S": 10,
        "PV": 11,
        "CBD": 12,
        "SMV": 13,
        "UP": 14,
        "LAD": 15,
        "PH": 16,
        "MPD": 17,
        "CONFLUENCE": 18,
        "PN": 19,
        "GBNECK": 20,
        "S3": 21,
        "S2": 22,
    }

    STATIONS = {
    "LIVERS2S3PART": 0,
    "CAPART": 1,
    "PBPART": 2,
    "LKPART": 3,
    "PTSPART": 4,
    "LADPART": 5,
    "CONFLUENCE1PART": 6,
    "PHPART": 7,
    "PNPART": 8,
    "PVPART": 9,
    "LIVERS4PART": 10,
    "GB1PART": 11,
    # "CBDPVPART": 12,
    # "CONFLUENCE2PART": 13,
    # "GB2PART": 14,
    # "UPPART": 15,
    # "PAPILLAPART": 16
}
    EUS_BI_QC = ["S4","PB","SV","SA","LK","PT","AO","CA","SMA","GB","S","PV","CBD","SMV","UP","LAD","PH","MPD","CONFLUENCE","PN","GBNECK","S3","S2"]


class ConfigPancreasQC:
    thProb = 0.25


class PancreasConstants:
    S4 = 0
    PB = 1
    SV = 2
    SA = 3
    LK = 4
    PT = 5
    AO = 6
    CA = 7
    SMA = 8
    GB = 9
    S = 10
    PV = 11
    CBD = 12
    SMV = 13
    UP = 14
    LAD = 15
    PH = 16
    MPD = 17
    CONFLUENCE = 18
    PN = 19
    GBNECK = 20
    S3 = 21
    S2 = 22
    
    NAV_EMPTY = "0"
    NAV_NOT_CHK_YET = "1"
    NAV_CHECKED = "2"
    NAV_NOT_CHECK = "3"
    
    

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
