import socket
import threading
import select
import RSAClass
import string as string_c
import random
from server import server_pro
import AESCipher

class server_com():
    '''
    responsible for the communication  with the client
    '''
    def __init__(self, server_ip, server_port, msg_q):
        '''
        constructor
        :param server_ip: the server ip
        :param server_port: the port
        :param msg_q: the q of the msg
        '''
        self.my_socket = socket.socket()
        self.server_ip = server_ip
        self.server_port = server_port
        self.msg_q = msg_q
        self.open_clients = {}
        self.key_lst = []
        self.aes_obj = None
        self.running = True
        self.socket_key = {}
        # start the main loop thread
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

    def gen_key(self):
        '''

        :return: the generated key
        '''
        #  string that contains all the letters + all the digits
        st_all = string_c.ascii_letters + "123456789"
        string = ''

        #  randomizing a 16 char long string
        for i in range(16):
            char = random.choice(st_all)
            string += char

        #  checking if the string isn't being used already as a symetric key
        if string in self.key_lst:
            return self.gen_key()

        else:
            #  if it isn't being used , add to the symetric key list and return the key
            self.key_lst.append(string)
            return string

    def stop_threads(self):
        '''
        stopping the threads
        :return:
        '''
        self.running = False
    def _main_loop(self):
        '''
        the main loop that recv msg and put it in the q and handles the clients
        :return:
        '''
        count = 0
        sym_key = ""
        self.my_socket.bind((self.server_ip,self.server_port))
        self.my_socket.listen(3)

        while self.running:
            rlist, wlist, xlist = select.select(list(self.open_clients.keys()) + [self.my_socket], list(self.open_clients.keys()), [], 0.3)
            for current_socket in rlist:
                if current_socket is self.my_socket:
                    #  new client
                    client, address = self.my_socket.accept()
                    print(f'{address[0]} - connected')
                    self.open_clients[client] = address[0]
                else:
                    try:
                        # recv data
                        data_len = current_socket.recv(4).decode()
                        data = current_socket.recv(int(data_len)).decode()
                    except Exception as e:
                        self._disconnect_user(current_socket)
                    else:
                        if data != "" and data[:2] != "04":
                            # put in q
                            self.msg_q.put((self._get_ip_by_socket(current_socket),data))
                        # check if the data is the key
                        elif data[:2] == "04":
                            # get the key
                            cl_pub_key = data[2:]
                            self.socket_key[current_socket] = cl_pub_key
                            # sending encrypted key
                            if count == 0:
                                sym_key = self.gen_key()
                                self.aes_obj = AESCipher.AESCipher(sym_key)
                                count += 1
                            enc_sym_key = RSAClass.encrypt_msg(sym_key, self.socket_key[current_socket])
                            self.send_msg(self._get_ip_by_socket(current_socket), server_pro.build_key(enc_sym_key))
                        else:
                            self._disconnect_user(current_socket)




    def _disconnect_user(self, current_socket):
        '''
        check if pc has disconnected
        :param current_socket:
        :return:
        '''
        print(f"{self.open_clients[current_socket]} - disconnected")
        self.msg_q.put((self._get_ip_by_socket(current_socket), "del"))
        del self.open_clients[current_socket]
        current_socket.close()

    def send_msg(self, ip, msg):
        '''
        sending a msg
        :param ip: the ip of the pc
        :param msg: the msg
        :return:
        '''
        # getting the socket
        soc = self._get_socket_by_ip(ip)
        if type(msg) == str:
            msg = msg.encode()

        if soc:
            # check if its not a swiching keys
            if msg[:2] != b'11':
                msg = self.aes_obj.encrypt(msg)
            try:
                soc.send((str(len(msg)).zfill(4)).encode())
                soc.send(msg)
            except Exception as e:
                pass
        else:
            print("no soc")






