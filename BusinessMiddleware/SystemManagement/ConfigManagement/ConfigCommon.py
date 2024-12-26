import os
import time
import configparser

class ConfigCommon:
    def __init__(self):
        self.DeviceType = ""
        self.DevicePackage = ""
        self.BboxState = ""
        self.HardVer = 0
        self.SoftVer = 0
        self.CommAddr = ""
        self.DeviceId = ""
        self.DeviceIdType = 0
        self.ThreadSleepTime = 1
        self.WebBasePath = ""
        self.ImgBasePath = ""
        self.VideoBasePath = ""
        self.ProactiveDeviceInfoTI = 1
        self.ProactiveDeviceStateTI = 1
        self.ProactiveDevicePathsTI = 1
        self.SocketAddr = "127.0.0.1"
        self.SocketPort = "7080"
        self.WebAddr = "127.0.0.1"
        self.WebPort = "7081"
        self.WSPort = "8082"
        self.LiveAddr = "127.0.0.1"
        self.LivePort = "80"
        self.FrameSize = 0
        self.LocalServerPort = "7075"
        self.MonitorPath = ""
        self.MonitorSoftName = ""
        self.MonitorSoftAliveTI = 1
        self.PatientDetailAddMonitorTI = 1
        self.MatchVideoAndPatientTI = 1
        self.ReadAllVideoTI = 1
        self.ReadAllTimeTI = 1
        self.ReadTodayBeforePatientTI = 1
        self.ReadTodayPatientTI = 1
        self.PatientFree = 1
        self.HelloTime = 1
        self.ModelTargetName = "eus20221026.wts"
        self.ModelQcName = ""
        self.ModelEnvName = ""
        self.AiIp = "127.0.0.1"
        self.AiInfoPort = "9521"
        self.AiLivePort = "9522"
        self.RIP = "127.0.0.1"
        self.RPort = "9523"
        self.MonitorH5LivePort = "9524"
        self.MonitorH5InfoPort = "9525"
        self.MonitorGuiLivePort = "9526"
        self.MonitorGuiInfoPort = "9527"
        self.ScreenX = 0
        self.ScreenY = 0
        self.ScreenWidth = 1920
        self.ScreenHeight = 1080
        self.ScreenshotRaw = 0
        self.ModelQcCount = 1
        self.ProbThreshold = 0.5
        self.config = None
        self.ScreenshotRaw = 0
        self.ScreenshotPredict = 1

    def load_config(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # 读取配置并设置类的属性
        self.DeviceType = self.config.get("monitor", "device.type")
        self.DevicePackage = self.config.get("monitor", "device.package")
        self.BboxState = self.config.get("monitor", "bbox.state")
        self.HardVer = int(self.config.get("monitor", "hard.ver"))
        self.SoftVer = int(self.config.get("monitor", "soft.ver"))
        self.CommAddr = self.config.get("monitor", "comm.addr")
        self.DeviceId = self.config.get("monitor", "device.id")
        self.DeviceIdType = int(self.config.get("monitor", "device.id.type"))
        
        # Logging the device ID
        print(f"设备编号为: {self.DeviceId}")
        
        self.LiveAddr = self.config.get("server", "live.addr")
        self.LivePort = self.config.get("server", "live.port")
        self.SocketAddr = self.config.get("server", "socket.addr")
        self.SocketPort = self.config.get("server", "socket.port")
        self.WebAddr = self.config.get("server", "web.addr")
        self.WebPort = self.config.get("server", "web.port")
        self.WSPort = self.config.get("local", "ws.port")
        
        # Frame size (integer)
        self.FrameSize = int(self.config.get("server", "frame.size"))
        
        # Paths
        self.ImgBasePath = self.config.get("local", "base.image.path")
        self.WebBasePath = self.config.get("local", "base.web.path")
        self.VideoBasePath = self.config.get("local", "base.video.path")
        
        # Calculating thread sleep time
        max_task_per_sec = int(self.config.get("local", "max.task.per.sec"))
        self.ThreadSleepTime = time.Duration(int(time.Second) / max_task_per_sec)
        
        # Local server port
        self.LocalServerPort = self.config.get("local", "local.server.port")
        
        # Monitor paths and software name
        self.MonitorPath = self.config.get("monitor", "monitor.path")
        self.MonitorSoftName = self.config.get("monitor", "monitor.soft.name")
        
        # Time intervals
        self.MonitorSoftAliveTI = self.get_time_val("monitor", "monitor.soft.alive.interval", time.Minute)
        self.ProactiveDeviceInfoTI = self.get_time_val("proactive", "device.info.time.interval", time.Minute)
        self.ProactiveDeviceStateTI = self.get_time_val("proactive", "device.state.time.interval", time.Minute)
        self.ProactiveDevicePathsTI = self.get_time_val("proactive", "device.paths.time.interval", time.Minute)
        self.MatchVideoAndPatientTI = self.get_time_val("proactive", "match.video.patient", time.Minute)
        self.PatientDetailAddMonitorTI = self.get_time_val("proactive", "patient.detail.add.monitor", time.Minute)
        
        # Patient time intervals
        self.ReadAllVideoTI = self.get_time_val("patient", "read.all.video", time.Minute)
        self.ReadAllTimeTI = self.get_time_val("patient", "read.all.time", time.Minute)
        self.ReadTodayBeforePatientTI = self.get_time_val("patient", "read.today.before.patient", time.Minute)
        self.ReadTodayPatientTI = self.get_time_val("patient", "read.today.patient", time.Minute)
        self.PatientFree = self.get_time_val("patient", "patient.free", time.Minute)
        self.HelloTime = self.get_time_val("patient", "hello.time", time.Second)
        
        # AI model details
        self.ModelTargetName = self.config.get("ai", "model.target.name")
        self.ModelQcName = self.config.get("ai", "model.qc.name")
        self.ModelEnvName = self.config.get("ai", "model.env.name")
        
        # AI threshold and ports
        self.ModelQcCount = int(self.config.get("ai", "model.qc.count"))
        self.ProbThreshold = float(self.config.get("monitor", "model.qc.ProbThreshold"))
        self.AiIp = self.config.get("ai", "ai.ip")
        self.AiInfoPort = self.config.get("ai", "ai.info.port")
        self.AiLivePort = self.config.get("ai", "ai.live.port")
        self.RIP = self.config.get("ai", "r.ip")
        self.RPort = self.config.get("ai", "r.port")
        self.MonitorH5LivePort = self.config.get("ai", "monitor.h5.live.port")
        self.MonitorH5InfoPort = self.config.get("ai", "monitor.h5.info.port")
        self.MonitorGuiLivePort = self.config.get("ai", "monitor.gui.live.port")
        self.MonitorGuiInfoPort = self.config.get("ai", "monitor.gui.info.port")

        # Screen settings
        self.ScreenX = int(self.config.get("local", "screen.x"))
        self.ScreenY = int(self.config.get("local", "screen.y"))
        self.ScreenWidth = int(self.config.get("local", "screen.width"))
        self.ScreenHeight = int(self.config.get("local", "screen.height"))
        self.ScreenshotRaw = int(self.config.get("local", "screenshot.raw"))
    
    def get_time_val(self, section, key, unit):
        value = self.config.get(section, key)
        return int(value) * unit

