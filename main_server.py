import server_com
import server_pro
import serverGraphic
import queue
import setting
import wx
import threading






def main_loop():
    while True:
        data = msg_q.get()
        msg = server_pro.break_msg(data)



msg_q = queue.Queue()
comm = server_com.server_com(setting.SERVER_IP,setting.SERVER_PORT,msg_q)
threading.Thread(target=main_loop).start()


app = wx.App(False)
frame = serverGraphic.ServerFrame()
app.MainLoop()