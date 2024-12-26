# cython: language_level=3
from threading import Thread,RLock


class BaseThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.loopFlag = True
        self.sleepTime = 0.005
        self.resetFlag = False
        self.lock = RLock()

    #一定要在join后调用一下，重置flag为false 
    # (因为类在未置为None时，第二次调用start启动线程会报线程已启动的错误。)
    def clear(self):
        self._is_stopped = False
        self._started.clear()
        self._delete() # 注意：VSCODE有bug，在调试模式下此步会卡死

    def ResetAll(self):
        with self.lock:
            self.resetFlag = True

    def _Reset(self):
        raise NotImplemented

    def SetLoopFlag(self, flag:bool):
        with self.lock:
            self.loopFlag = flag

    def Exit(self):
        with self.lock:
            self.loopFlag = False
        self._Reset()

    def SetSleepTime(self, sleepTime:float):
        self.sleepTime = sleepTime
