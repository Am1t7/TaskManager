import client_com
import client_pro
import clientGraphic
import queue
import setting
import wx
import threading






def main_loop(msg_q, comm):
    while True:
        data = msg_q.get()
        msg = client_pro.break_msg(data)

        print("client recv ---------------------------",msg)




msg_q = queue.Queue()
comm = client_com.Client_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
threading.Thread(target=main_loop, args=(msg_q,comm,)).start()


app = wx.App(False)
frame = clientGraphic.MainFrame()
app.MainLoop()