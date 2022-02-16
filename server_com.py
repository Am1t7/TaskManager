import socket
import threading
import select
import wx
from pubsub import pub

class server_com():
    '''
    constructor
    '''
    def __init__(self, server_ip, server_port, msg_q):

        self.my_socket = socket.socket()
        self.server_ip = server_ip
        self.server_port = server_port
        self.msg_q = msg_q
        self.open_clients = {}
        threading.Thread(target=self._main_loop).start()



    def _get_ip_by_socket(self, socket):
        '''

        :param socket: the client socket
        :return: the ip that addressed to this socket
        '''
        ip = None
        for soc in self.open_clients.keys():
            if soc == socket:
                ip = self.open_clients[soc]
                break
        return ip

    def _get_socket_by_ip(self, ip):
        '''

        :param ip: the client ip
        :return: the socket that addressed to this ip
        '''
        socket = None
        for soc in self.open_clients.keys():
            if self.open_clients[soc] == ip:
                socket = soc
                break
        return socket


    def _main_loop(self):
        '''
        the main loop that recv msg and put it in the q and handles the clients
        :return:
        '''
        self.my_socket.bind((self.server_ip,self.server_port))
        self.my_socket.listen(3)

        while True:

            rlist, wlist, xlist = select.select(list(self.open_clients.keys()) + [self.my_socket], list(self.open_clients.keys()), [], 0.3)

            for current_socket in rlist:
                if current_socket is self.my_socket:
                    # new client
                    client, address = self.my_socket.accept()
                    print(f'{address[0]} - connected')
                    self.open_clients[client] = address[0]

                else:
                    try:
                        #recv data
                        data_len = current_socket.recv(4).decode()
                        data = current_socket.recv(int(data_len)).decode()
                    except Exception as e:
                        print("server com - main loop" , str(e))
                        self._disconnect_user(current_socket)
                    else:
                        if data != "":
                            #put in q
                            self.msg_q.put((self._get_ip_by_socket(current_socket),data))
                        else:
                            self._disconnect_user(current_socket)




    def _disconnect_user(self, current_socket):
        print(f"{self.open_clients[current_socket]} - disconnected")
        del self.open_clients[current_socket]
        current_socket.close()
        wx.CallAfter(pub.sendMessage, 'del')

    def send_msg(self, ip, msg):
        soc = self._get_socket_by_ip(ip)
        if soc:
            try:
                soc.send((str(len(msg)).zfill(4)).encode())
                soc.send(str(msg).encode())
            except Exception as e:
                print("serv_com send msg: ",str(e))
                pass






