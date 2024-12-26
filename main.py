# -*- coding: utf-8 -*-
import os
import yaml
import argparse

from BusinessMiddleware.MainService import MainService as start_service
# from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigInOutCheckType import ConfigCheckType
# from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigProduct import ConfigProduct, ConfigVersion,ConfigAIModelType


def load_config(config_path):
    """
    加载 YAML 配置文件
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"错误: 配置文件 {config_path} 未找到！")
        exit(1)
    except yaml.YAMLError as e:
        print(f"错误: 无法解析 YAML 文件 {config_path}！\n{e}")
        exit(1)

def main():

    config_file_path = r'BusinessMiddleware\SystemManagement\ConfigManagement\Conf\Pancreas.yaml'
    # 加载配置文件
    config = load_config(config_file_path)
    saveImgSize = f"200_200"
    offsetX = 200 # olympus(CV-290)
    # offsetX = 340 # fuji(EC-600)
    # offsetX = 55 # fuji(EG-760R)
    # offsetX = 660 # aohua(AQ-300)
    # offsetX = 310 # kaili(HD-580)
    offsetY = 0
    cropWidth = 1280 # kaili(HD-580) 1300
    cropHeight = 1080

    originWidth = 1920 #信号源输入图像宽
    originHeight = 1080 #信号源输入图像高

    # 定义命令行参数解析器
    parser = argparse.ArgumentParser(description="AI 视频处理应用")

    # 添加参数，每个参数都设置默认值和帮助信息
    parser.add_argument("--checkType", type=str, default="bi",help="检查类型胆胰（bi）/纵膈（me）")
    parser.add_argument("--userPath", type=str, default=r"D:\eus", help="信息存储地址")
    parser.add_argument("--videoPath", type=str, default=r"D:\video\danyi.mp4",help="视频存储路径")
    
    parser.add_argument("--modelPathDRPancerasSeg", type=str, default=r"D:\4_all_project\Python_project\EUS\Model\yolov8l-seg-danyi-20240715.onnx",help="胆胰模型路径")
    parser.add_argument("--modelPathDRMediasttinumSeg", type=str, default=r"D:\4_all_project\Python_project\EUS\Model\yolov8l-seg-zongge-20240715.onnx",help="纵膈模型路径")
    parser.add_argument("--room", type=str, default="诊间一",help="诊间")
    parser.add_argument("--userSaveBaseDir", type=str, default="D//user",help="存储位置")
    parser.add_argument("--saveImgSize", type=str, default=saveImgSize,help="存储位置")

    parser.add_argument("--offsetX", type=int, default=offsetX, help="画面左上角坐标X的起始偏移量")
    parser.add_argument("--offsetY", type=int, default=offsetY, help="画面左上角坐标Y的起始偏移量")
    parser.add_argument("--cropWidth", type=int, default=cropWidth, help="截取画面的宽度")
    parser.add_argument("--cropHeight", type=int, default=cropHeight, help="截取画面的高度")
    parser.add_argument("--originFrameWidth", type=int, default=originWidth, help="原始视频画面的宽度")
    parser.add_argument("--originFrameHeight", type=int, default=originHeight, help="原始视频画面的高度")




    parser.add_argument("--sendType", type=int, default=config.get('monitor', {}).get('send.type', 0),help="发送类型：0=HTTP，1=UDP，2=TCP，3=串口HTTP，4=串口UDP，5=串口TCP")
    parser.add_argument("--deviceType", type=int, default=config.get('monitor', {}).get('device.type', 2),help="设备类型：0=消化内镜AI，1=膀胱内镜AI，2=超声内镜")
    parser.add_argument("--devicePackage", type=str, default=config.get('monitor', {}).get('device.package', 'eus'),help="设备程序包：消化=ge；EUS=eus")
    parser.add_argument("--bboxState", type=int, default=config.get('monitor', {}).get('bbox.state', 0),help="包围框状态：0=截图显示，1=截图不显示，2=实时显示，3=实时不显示")
    parser.add_argument("--hardVer", type=str, default=config.get('monitor', {}).get('hard.ver', '01000000'),help="硬件版本号")
    parser.add_argument("--softVer", type=str, default=config.get('monitor', {}).get('soft.ver', '04000000'),help="软件版本号")
    parser.add_argument("--hospitalName", type=str, default=config.get('monitor', {}).get('hospital.name', ''),help="医院名称")
    parser.add_argument("--sectionName", type=str, default=config.get('monitor', {}).get('section.name', ''),help="科室名称")
    parser.add_argument("--commAddr", type=str, default=config.get('monitor', {}).get('comm.addr', ''),help="通信地址")
    parser.add_argument("--AIModelPath", type=str, default=config.get('aipt', {}).get('model.target_name', ''),help="AI 模型路径")
    parser.add_argument("--AIQcPath", type=str, default=config.get('aiqc', {}).get('model.qc_name', ''),help="AI 模型路径")
    parser.add_argument("--AIEnvPath", type=str, default=config.get('aiev', {}).get('model.env_name', ''),help="AI 模型路径")
    parser.add_argument("--socketPort", type=int, default=config.get('server', {}).get('socket.port', 7080),help="Socket 服务端口号")
    parser.add_argument("--webPort", type=int, default=config.get('server', {}).get('web.port', 8080),help="Web 服务端口号")
    parser.add_argument("--screenWidth", type=int, default=config.get('local', {}).get('screen.width', 640),help="屏幕宽度")
    parser.add_argument("--screenHeight", type=int, default=config.get('local', {}).get('screen.height', 640),help="屏幕高度")
    parser.add_argument("--maxTasksPerSec", type=int, default=config.get('local', {}).get('max.task.per.sec', 40),help="每秒最大任务处理数量")
    parser.add_argument("--monitorInterval", type=int, default=config.get('monitor', {}).get('monitor.soft.alive.interval', 5), help="监控软件进程存活时间间隔（单位：秒）")

    # 解析命令行参数
    args = parser.parse_args().__dict__


    start_service(args).StartService()



if __name__ == "__main__":
    main()
