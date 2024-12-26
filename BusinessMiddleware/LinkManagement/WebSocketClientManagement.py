# cython: language_level=3
import socket,os
import threading
import traceback


class SocketManagement:
    def __init__(self, ip='127.0.0.1', port=9523):
        try:
            self.server_ip = ip
            self.server_port = port
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self.lock = threading.Lock()
            self.udp.bind(('', 9530))
        except:
            print(f"绑定udp地址异常：{ip}:{port}")
            traceback.print_exc()

    def SendMessage(self, info):
        try:
            self.udp.sendto(info.encode('utf8'), (self.server_ip, self.server_port))
        except:
            print(f"发送udp信息异常：{info}")
            traceback.print_exc()

    def RecMessage(self):
        try:
            urlList = []
            img_uris, addrf = self.udp.recvfrom(1024)
            content = img_uris.decode('utf8')
            if content.__contains__("|"):
                urls = content.split("|")
                with self.lock:  # 使用锁保护对共享变量的访问
                    self.patient_id = urls[0]
                    bezier_name = urls[1]
                    straight_name = urls[2]
                    urlList.append(bezier_name)
                    urlList.append(straight_name)
            return urlList
        except:
            print("接受udp信息异常")
            traceback.print_exc()
