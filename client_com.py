import socket
import threading
import uuid
import client_pro
import time
import RSAClass
import AESCipher
class Client_com():
    '''
    constructor
    '''
    def __init__(self, server_ip, server_port, msg_q):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_on = False
        self.msg_q = msg_q
        self.my_socket = None
        self.mac = ':'.join(
            ['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]).upper()
        self.rsa_obj = RSAClass.RSAClass()
        self.rsa_pub_key = self.rsa_obj.get_public_key_pem()
        self.sym_key = ""
        self.aes_obj = None
        threading.Thread(target=self._main_loop).start()
        threading.Thread(target=self._recv_loop).start()
        #threading.Thread(target=self._ping).start()



    def _main_loop(self):
        '''
        the main loop that recv and put the msg in queue
        :return:
        '''
        while True:
            while not self.server_on:
                # creating the socket
                self.my_socket = socket.socket()
                print("1 ", self.server_on)
                try:
                    #try connecting
                    self.my_socket.connect((self.server_ip, self.server_port))
                    self.send(client_pro.build_mac(self.mac))
                    self.send(client_pro.build_key(self.rsa_pub_key))
                    #self.send(self.rsa_pub_key)
                except Exception as e:
                    print("connect error: ",str(e))
                    pass
                else:
                    self.server_on = True
                    print("11 ", self.server_on)

    def _recv_loop(self):
        count = 0
        while True:
            while self.server_on:
                print("3", self.server_on)
                try:
                    #recv the data
                    data_len = self.my_socket.recv(4).decode()
                    print(data_len)
                    data = self.my_socket.recv(int(data_len)).decode()
                except Exception as e:
                    print("recv data client_com", str(e))
                    self.server_on = False
                    self.my_socket.close()
                else:
                    print(data)
                    #put in q
                    if data[:2] == "11":
                        self.sym_key = data[2:]
                        print(self.sym_key)
                        #self.aes_obj = AESCipher.AESCipher(self.sym_key)
                    elif data != "":
                        if count == 0:
                            self.aes_obj = AESCipher.AESCipher(self.sym_key)
                            count += 1
                        data_dec = self.aes_obj.decrypt(data)
                        self.msg_q.put(data_dec)

                    print("client recv: ", data)
    #
    # def _ping(self):
    #     while True:
    #         #print("ping ", self.server_on)
    #         if self.server_on:
    #             self.send("ping")
    #         time.sleep(1.0)


    def send(self, msg):
        '''
        send the msg to the server
        :param msg: the msg to send
        :return:
        '''
        try:
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
        return self.my_socket





