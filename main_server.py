import server_com
import server_pro
import serverGraphic
import queue
import setting
import wx
import threading
from pubsub import pub
import setting




used_port = [setting.SERVER_PORT]

def get_port():
    pass

def main_loop(msg_q, comm):
    while True:
        data = msg_q.get()
        msg = server_pro.break_msg(data)

        if msg[0] == "02":
            wx.CallAfter(pub.sendMessage, 'add', mac = str(msg[1]))
            port = get_port()
            comm = server_com.server_com(setting.SERVER_IP, port, msg_q)
            #build...(port)
            # sne msg

        elif msg[0] == "01":
            pass

        print("------------------------------------",msg)



msg_q = queue.Queue()
comm = server_com.server_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
threading.Thread(target=main_loop, args=(msg_q,comm,)).start()


app = wx.App(False)
frame = serverGraphic.ServerFrame()
app.MainLoop()