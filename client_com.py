import socket
import threading
import select

class Client_com():
    def __init__(self, server_ip, server_port, msg_q):
        self.server_ip = server_ip
        self.server_port = server_port
        self.msg_q = msg_q
        self.my_socket = None
        threading.Thread(target=self._main_loop).start()



    def _main_loop(self):
        self.my_socket = socket.socket()
        server_on = False
        while not server_on:
            try:
                self.my_socket.connect((self.server_ip, self.server_port))
            except Exception as e:
                print("connect error: ",str(e))
                pass
            else:
                server_on = True
        while True:
            try:
                data_len = self.my_socket.recv(4).decode()
                data = self.my_socket.recv(int(data_len)).decode()
            except Exception as e:
                print("recv data client_com", str(e))
                break
            else:
                self.msg_q.put(data)

    def send(self, msg):
        try:
            self.my_socket.send(str(len(msg)).encode())
            self.my_socket.send(str(msg).encode())
        except Exception as e:
            print("senf msg client_com: ",str(e))
            pass

