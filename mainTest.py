# # import os
# from datetime import datetime
# # userPath = r"D:\\user"
# # qcPath = "QC"
# today = datetime.now().strftime("%Y%m%d")
# basePath = datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+"bi"
# # qcPath = os.path.join(userPath, today, basePath ,qcPath)
# print(basePath)
# # import numpy as np

# # # import time
# # from ultralytics.utils import ops
# # bbox = np.array([361,990,97,114])
# # bbox = ops.xywh2xyxy(bbox)
# # # 获取当前时间的 Unix 时间戳（秒）
# # # timestamp = int(time.time())
# # print(bbox[..., 0], bbox)
# from BusinessMiddleware.BusinessManagement.PancreasSeg.PancreasSeg import PancreasSeg
# s = PancreasSeg()
# s.SetCurrentFrame(1)

import shutil

shutil.copy(r"Ztest1\1.csv", r"Ztest2\2.csv")

