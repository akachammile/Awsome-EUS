# cython: language_level=3
import queue
import traceback
import time
import json
import threading

from threading import RLock

from websocket_server import WebsocketServer # pip install websocket_server

from BusinessMiddleware.SystemManagement.ConfigManagement.ConfigWebSocket import ConfigWebSocket


class WebSocketManagement():
    def __init__(self, logFile, port):
        self.logFile = logFile
        self.WebSocketThread = None
        self.lock = RLock()
        self.clients = [] # 所有连过来的客户端，这里只用于base64的图像发送
        self.cls_pc = []
        self.cls_live = []
        self.cls_qc_cut = []
        self.cls_qc_statistics = []
        self.cls_nav_assosiate = []
        self.queue_WSMsg = queue.Queue() # 工作站发来的信息
        self.queue_qc_cut = queue.Queue()
        self.queue_qc_statistic = queue.Queue()
        self.queue_qc_nav = queue.Queue()
        self.port = port


        # ######调试消息通信用#######
        self.ui_msg = ""
        self.pc_extened_msg = ""
        self.mobile_msg = ""

    def _RunServer(self):
        self._Reset()
        self.server = WebsocketServer(host=ConfigWebSocket.WEBSOCKET_SERVER_IP, port=self.port)
        self.server.set_fn_new_client(self._NewClient)
        self.server.set_fn_message_received(self._MsgRecv)
        self.server.set_fn_client_left(self._ClientLeft)
        self.server.run_forever()

    def Start(self):
        self.WebSocketThread = threading.Thread(target=self._RunServer, args=())
        self.WebSocketThread.daemon = True
        self.WebSocketThread.start()
        print("websocket通信启动")
    
    def _Reset(self):
        self.clients.clear()
        with self.queue_WSMsg.mutex:
            self.queue_WSMsg.queue.clear()
      
    
    def _writeLog(self,msg):
        logStr = time.strftime("%Y-%m-%d,%H:%M:%S", time.localtime(time.time())) + " | "+msg+"\n"
        self.logFile.write(logStr)
        self.logFile.flush()

    def _Send(self, client, message):
        if client in self.clients:
            try:
                self.server.send_message(client, message)
            except:
                err_msg = f"send error:{traceback.format_exc()}"
                print(err_msg)
                #self._writeLog(err_msg)
    
    def _NewClient(self, client, server):
        msg_connect = f'new client connected: {client["address"]}'
        #self._writeLog(msg_connect)
        with self.lock:
            self.clients.append(client)

    def _MsgRecv(self, client, server, message):
        # msg = f'received {client["address"]} message: {message}'
        try:
            if "start" in message: #工作站发来的心跳信息
                pass
            else:
                if isinstance(message, str):
                    if "start" not in message and "bi" in message or "me" in message:
                        # 进入 WSMsg 队列
                        self.queue_WSMsg.put(message)

                    elif "live" in message and client not in self.cls_live:
                        # 进入 cls_live 队列
                        self.cls_live.append(client)

                    elif "qc" in message and "shortcut" in message and client not in self.cls_qc_cut:
                        # 进入 cls_qc_cut 队列
                        self.cls_qc_cut.append(client)

                    elif "qc" in message and "statistics" in message and client not in self.cls_qc_statistics:
                        # 进入 cls_qc_statistics 队列
                        self.cls_qc_statistics.append(client)

                    elif "nav" in message or "check_time" in message and client not in self.cls_nav_assosiate:
                        # 进入 cls_nav_assosiate 队列
                        self.cls_nav_assosiate.append(client)

                  
                        # 其余情况，确保消息正确放入其他队列
                    if "qc" in message and "shortcut" in message and "bi" in message or "me" in message:
                            self.queue_qc_cut.put(message)
                    elif "qc" in message and "statistics" in message:
                            self.queue_qc_statistic.put(message)
                    elif "nav" in message or "check_time" in message and  "bi" in message or "me" in message:
                            self.queue_qc_nav.put(message)

                  

        except:
            err_msg = f"error:{traceback.format_exc()}"
            print(err_msg)
            #self._writeLog(err_msg)
        finally:
            self._Send(client,"ok")

    def _ClientLeft(self, client, server):
        msg_disconnect = f'client disconnected: {client["address"]}'
        if client in self.clients:
            self.clients.remove(client)
        
        if client in self.cls_qc_cut:
            self.cls_qc_cut.remove(client)

        if client in self.cls_qc_statistics:
            self.cls_qc_statistics.remove(client)
        
        if client in self.cls_nav_assosiate:
            self.cls_nav_assosiate.remove(client)
        
        if client in self.cls_live:
            self.cls_live.remove(client)
        
        
        
        
       
    
    # 工作站发送来的信息
    def GetWSMsg(self):
        if not self.queue_WSMsg.empty():#判断是否为空
            msg = self.queue_WSMsg.get() #取出消息
        else:
            msg = {}
        return msg
    
    def GetQCutMsg(self):
        if not self.queue_qc_cut.empty():
            msg = self.queue_qc_cut.get()
        else:
            msg = {}
        return msg
    
    def GetStatisticMsg(self):
        if not self.queue_qc_statistic.empty():
            msg = self.queue_qc_statistic.get()
        else:
            msg = {}
        return msg
    
    def GetNavMsg(self):
        if not self.queue_qc_nav.empty():
            msg = self.queue_qc_nav.get()
        else:
            msg = {}
        return msg
    

    def SendMsgtoLive(self,str_msg):
        """
        向服务端发送消息
        """
        for client in self.cls_live:
            self._Send(client,str_msg)

    def SendMsgtoQCut(self, str_msg):
        """
        向服务端发送消息
        """
        for client in self.cls_qc_cut:
            self._Send(client,str_msg)


    def SendMsgtoQcStatistic(self, str_msg):
        for client in self.cls_qc_statistics:
            self._Send(client, str_msg)

    def SendMsgtoNav(self, str_msg):
        for client in self.cls_nav_assosiate:
            self._Send(client, str_msg)
     

  


