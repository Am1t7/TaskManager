import socket
import threading
import uuid
from client import client_pro
import RSAClass
import AESCipher
class Client_com():
    def __init__(self, server_ip, server_port, msg_q):
        '''
        constructor
        :param server_ip: the ip of the server pc
        :param server_port: the port to communicate
        :param msg_q: the q of the messages
        '''
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_on = False
        self.msg_q = msg_q
        self.my_socket = None
        self.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]).upper() #the mac addres of the pc
        self.rsa_obj = RSAClass.RSAClass()
        self.rsa_pub_key = self.rsa_obj.get_public_key_pem().decode()
        self.sym_key = None
        self.running = True
        # starting the threads
        threading.Thread(target=self._main_loop).start()
        threading.Thread(target=self._recv_loop).start()


    def stop_threads(self):
        '''
        stop the threads
        :return:
        '''
        self.running = False
    def _main_loop(self):
        '''
        the main loop that recv and put the msg in queue
        :return:
        '''
        while self.running:
            while not self.server_on and self.running:
                # creating the socket
                self.my_socket = socket.socket()
                print("1 ", self.server_on)
                try:
                    #try connecting
                    self.my_socket.connect((self.server_ip, self.server_port))
                    #send mac
                    self.send(client_pro.build_mac(self.mac))
                    #sending key
                    self.send(client_pro.build_key(self.rsa_pub_key))
                except Exception as e:
                    print("connect error: ",str(e))
                    pass
                else:
                    self.server_on = True

    def _recv_loop(self):
        '''
        recv the msg from the server
        :return:
        '''
        while self.running:
            while self.server_on and self.running:
                try:
                    #recv the data
                    data_len = self.my_socket.recv(4).decode()
                    data = self.my_socket.recv(int(data_len))
                except Exception as e:
                    print("recv data client_com", str(e))
                    self.server_on = False
                    self.my_socket.close()
                else:
                    if data != "" and data[:2] != b"11":
                        data = data.decode()
                        data_dec = self.sym_key.decrypt(data)
                        self.msg_q.put(data_dec)
                    #check if the data is the switched key
                    elif data[:2] == b"11":
                        sym_key = data[2:]
                        sym_key = self.rsa_obj.decrypt_msg(sym_key).decode()
                        self.sym_key = AESCipher.AESCipher(sym_key)

    def send(self, msg):
        '''
        send the msg to the server
        :param msg: the msg to send
        :return:
        '''
        try:
            #sending the msg
            self.my_socket.send((str(len(msg)).zfill(4)).encode())
            self.my_socket.send(str(msg).encode())
        except Exception as e:
            print("send msg client_com: ",str(e))
            self.server_on = False
            self.my_socket.close()


    def get_mac(self):
        '''
        getting the mac address
        :return:
        '''
        return self.mac

    def get_socket(self):
        '''
        getting the socket
        :return:
        '''
        return self.my_socket





