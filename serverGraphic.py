import wx
from pubsub import pub
from ObjectListView import ObjectListView, ColumnDefn
import threading
import webbrowser
from googlesearch import search
import server_pro
from serverDB import DB
import hashlib
import wx.lib.scrolledpanel as scrolled


chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'


class ServerFrame(wx.Frame):
    def __init__(self,parent=None,send_q=None,mac=None):
        '''
        constructor
        :param parent:
        :param send_q: the send msg q
        :param mac: the client mac address
        '''
        super(ServerFrame, self).__init__(parent, title="Server", size=(1024,768) ,style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)
        # create status bar
        self.CreateStatusBar()
        self.StatusBar.SetStatusText("By: Amit Finder")
        # creating the main panel
        main_panel = MainPanel(self,send_q, mac)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)

        self.Bind(wx.EVT_CLOSE, self._when_closed)

        self.SetSizer(box)
        self.Layout()
        self.Show()

    def _when_closed(self, event):
        '''
        closing the server
        :param event:
        :return:
        '''
        self.DestroyChildren()
        self.Destroy()
        wx.CallAfter(pub.sendMessage, 'close_sr', )



class TaskFrame(wx.Frame):

    #---------------------------------------------------------------------
    def __init__(self, mac, send_q):
        '''
        constructor
        :param mac: the client mac address
        :param send_q: the send msg q
        '''
        wx.Frame.__init__(self, None, title=mac, size=(1024, 768))
        panel = TaskPanel(self, send_q, mac)
        #creating a status bar
        self.CreateStatusBar()
        self.mac = mac
        self.StatusBar.SetFieldsCount(4)
        self.StatusBar.SetStatusWidths([200, 200, 200, 200])

        pub.subscribe(self.updateStatusbar, f'{self.mac}update_status_server')


    def updateStatusbar(self, procsnum,totalcpu,totalmem, totaldisk):
        '''
        creating the status bar
        :param procsnum: the total number of processes that runs on the pc
        :param totalcpu: the total cpu usage of all the processes
        :param totalmem: the total memory usage of all the processes
        :param totaldisk: the total disk usage of all the processes
        :return:
        '''
        procs=procsnum
        cpu=totalcpu
        mem = totalmem
        disk = totaldisk
        #set the statusbar text
        self.SetStatusText("Processes: %s" % procs, 0)
        self.SetStatusText("CPU Usage: %s" % cpu, 1)
        self.SetStatusText("Physical Memory: %s" % mem, 2)
        self.SetStatusText("Disk: %s" % disk, 3)

class MainPanel(wx.Panel):
    def __init__(self, parent, send_q, mac):
        '''
        constructor
        :param parent: the frame
        :param send_q: the queue to send msg
        :param mac: the mac address
        '''
        wx.Panel.__init__(self, parent, size=(1024, 768))
        self.frame = parent
        m_box = wx.BoxSizer()

        # creating all the screen panels
        self.login = LoginPanel(self)
        self.pc = PcPanel(self, send_q)
        self.task = TaskPanel(self, send_q, mac)

        # adding all the screen panels to the sizer
        m_box.Add(self.login,0,wx.EXPAND,0)
        m_box.Add(self.pc,0,wx.EXPAND,0)
        m_box.Add(self.task,0,wx.EXPAND,0)

        #showing the screen
        self.login.Show()
        self.SetSizer(m_box)
        self.Layout()

class LoginPanel(wx.Panel):
    def __init__(self, parent):
        '''
        constructor
        :param parent: the frame
        '''
        wx.Panel.__init__(self, parent, size=(1024, 768))
        self.frame = parent
        self.gui_shown = False
        self.db = DB()

        # the main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        # username
        username_box = wx.BoxSizer(wx.HORIZONTAL)
        name_text = wx.StaticText(self, 1, label="Username: ")
        self.userField = wx.TextCtrl(self, -1, name="Enter name",size=(150, -1))
        username_box.Add(name_text, 0, wx.ALL, 5)
        username_box.Add(self.userField, 0, wx.ALL, 5)
        name_text.SetFont(font)

        # password
        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, -1, "Password: ")
        font = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        passText.SetFont(font)

        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size = (150, -1))

        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0, wx.ALL, 5)

        # login button
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="Login", size = (200, 60))
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)


        # add all elements to sizer
        sizer.AddSpacer(50)
        sizer.Add(username_box, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        #showing the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Show()


    def handle_login(self, event):
        '''
        check the login details
        :param event:
        :return:
        '''
        # extract username and password
        username = self.userField.GetValue()
        password = self.passField.GetValue()
        #check if username and password are valid
        if(self.db.username_exist(username) and self.db.pass_exist(hashlib.md5(str(password).encode()).hexdigest())):
            self.Hide()
            self.frame.pc.Show()
        else:
            wx.MessageBox("not valid!!!", "Erorr", wx.OK)


class PcPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, send_q):
        '''
        constructor
        :param parent: the frame
        :param send_q: the queue sor sending messages
        '''
        scrolled.ScrolledPanel.__init__(self, parent, -1, size=(1024, 768))
        self.frame = parent
        #the sizers
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.scr_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.scr_sizer.Add(self.row_sizer)
        self.pc_sizer = wx.BoxSizer(wx.VERTICAL)
        self.pc_objects = {}
        #the button
        self.pcImg = wx.Image("pc.png", wx.BITMAP_TYPE_ANY)
        self.pcImg.Rescale(100, 100)
        self.pcBmp = wx.Bitmap(self.pcImg)
        self.pcBtn = None
        self.mac_string = None
        self.is_del = False

        self.macText = None
        self.q = send_q


        self.SetBackgroundColour(wx.WHITE)
        pub.subscribe(self.add_pc, 'add')
        pub.subscribe(self.del_pc, 'del')
        #show the screen
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Hide()


    def add_pc(self, mac, pass_limit, created):
        '''
        adding pc to the connected pc view
        :param mac: the mac address of the pc
        :return:
        '''
        #check if already added
        if created == False:
            #creating the pc logo button
            self.pcBtn = wx.BitmapButton(self, wx.ID_ANY, bitmap=self.pcBmp, size=wx.DefaultSize, name=mac)
            self.pcBtn.Bind(wx.EVT_BUTTON, self.handle_pc)

            #create the text with the mac address
            self.macText = wx.StaticText(self, -1, str(mac))
            font = wx.Font(11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            self.macText.SetFont(font)
            self.mac_string = mac
            #check if there are more than 7 pc in a row
            if len(self.row_sizer.GetChildren()) == 7:
                self.row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.pc_sizer = wx.BoxSizer(wx.VERTICAL)
                self.pc_sizer.Add(self.pcBtn, 0, wx.ALL, 5)
                self.pc_sizer.Add(self.macText, 0, wx.ALL, 5)
                self.row_sizer.Add(self.pc_sizer)
                self.scr_sizer.Add(self.row_sizer)
            else:
                self.pc_sizer = wx.BoxSizer(wx.VERTICAL)
                self.pc_sizer.Add(self.pcBtn, 0, wx.ALL, 5)
                self.pc_sizer.Add(self.macText, 0, wx.ALL, 5)
                self.row_sizer.Add(self.pc_sizer, 0, wx.LEFT, 5)

                self.pc_objects[mac] = [self.pcBtn, self.macText]
        #for passed limits pc
        elif created and pass_limit == False:
            self.macText.SetBackgroundColour(wx.WHITE)
        elif created and pass_limit == True:
            self.macText.SetBackgroundColour(wx.RED)

        #show screen
        self.SetSizer(self.scr_sizer)
        self.SetupScrolling()
        self.Layout()

        self.is_del = False


    def del_pc(self, mac):
        '''
        deleting a pc from the connected pc
        :param mac: the mac address of the pc
        :return:
        '''
        btn, txt = self.pc_objects[mac]
        btn.Destroy()
        txt.Destroy()
        del self.pc_objects[mac]
        self.Layout()

    def handle_pc(self, event):
        '''
        when a pc gets pressed
        :param event:
        :return:
        '''
        mac = event.GetEventObject().GetName()
        frame = TaskFrame(mac, self.q)
        panel = TaskPanel(self, self.q, mac)
        #put in message q
        self.q.put((mac,server_pro.build_start()))
        frame.Show()



class TaskPanel(wx.Panel):
    def __init__(self, parent, send_q, mac):
        '''
        constructor
        :param parent: the frame
        :param send_q: the send messages q
        :param mac: the pc mac address
        '''
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        self.currentSelection = None
        self.gui_shown = False
        self.procs = []
        self.bad_procs = []
        self.sort_col = 0
        self.q = send_q
        self.mac = mac
        self.db = DB()

        self.col_w = {"name":175,
                      "pid":50,
                      "exe":300,
                      "user":175,
                      "cpu":60,
                      "mem":75,
                      "disk":75}

        #creating the list view object
        self.procmonOlv = ObjectListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.procmonOlv.Bind(wx.EVT_LIST_COL_CLICK, self.onColClick)
        self.procmonOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)

        #pop up menu
        self.popupmenu = wx.Menu()
        for text in "Info,End Task".split(","):
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.procmonOlv.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

        # set the task to display
        self.setProcs()
        # the sizer for the buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # set the "set limits" button
        limitProcBtn = wx.Button(self, label = "Set Limits")
        limitProcBtn.Bind(wx.EVT_BUTTON, self.onOpenLimit)
        button_sizer.Add(limitProcBtn, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # set the "ban process" button
        banProcBtn = wx.Button(self, label = "Ban Process")
        banProcBtn.Bind(wx.EVT_BUTTON, self.onBanProcess)
        button_sizer.Add(banProcBtn, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # set the "unban process" button
        unbanProcBtn = wx.Button(self, label = "Unban Process")
        unbanProcBtn.Bind(wx.EVT_BUTTON, self.onUnbanProcess)
        button_sizer.Add(unbanProcBtn, 0, wx.ALIGN_CENTER | wx.ALL, 0)

        # set the "shutdown pc" button
        shutProcBtn = wx.Button(self, label = "Shutdown Pc")
        shutProcBtn.Bind(wx.EVT_BUTTON, self.onshutpc)
        button_sizer.AddSpacer(550)
        button_sizer.Add(shutProcBtn, 0, wx.ALIGN_RIGHT | wx.ALL, 0)

        # set the "close system" button
        closeProcBtn = wx.Button(self, label = "Close System")
        closeProcBtn.Bind(wx.EVT_BUTTON, self.onclosesys)
        button_sizer.Add(closeProcBtn, 0, wx.RIGHT | wx.ALL, 0)

        #set the main sizer and adds the buttons
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.procmonOlv, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)


        # check for updates every 15 seconds
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update("")
        self.setProcs()
        flag = f"{self.mac}update_server"
        pub.subscribe(self.updateDisplay_server, flag )
        self.SetSizer(mainSizer)
        self.procmonOlv.Show()

    def OnShowPopup(self, event):
        '''
        get the current position for the pop up menu
        '''
        pos = event.GetPosition()
        pos = self.procmonOlv.ScreenToClient(pos)
        self.procmonOlv.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        '''
        open the pop up menu and does an action according to what selected
        '''
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetItemLabel()
        if text == "Info":
            threading.Thread(target=self.onOpenInfo).start()
        elif text == "End Task":
            self.onKillProc()

    def onColClick(self, event):
        '''
        Remember which column to sort by
        '''
        self.sort_col = event.GetColumn()

        # ----------------------------------------------------------------------

    def onKillProc(self):
        '''
        puts in q a message to kill process in the client pc
        '''
        obj = self.procmonOlv.GetSelectedObject()
        self.q.put((self.mac, server_pro.build_close_proc(obj.pid)))

    def onOpenInfo(self):
        '''
        open info on google to a selected process
        '''
        global chrome_path
        obj = self.procmonOlv.GetSelectedObject()
        try:
            name = obj.name
        except Exception as e:
            pass
        else:
            # to search
            query = name
            for j in search(query, tld="co.in", num=1, stop=1, pause=2):
                webbrowser.get(chrome_path).open(j)


    def onSelect(self, event):
        '''
        Gets called when an item is selected and helps keep track of what item is selected
        '''
        item = event.GetItem()
        itemId = item.GetId()
        self.currentSelection = itemId


    def onOpenLimit(self,event):
        '''
        open a window to set limits
        '''
        frame = LimitsFrame(self.mac, self.q)
        panel = LimitsPanel(self,self.mac, self.q)
        frame.Show()

    def onBanProcess(self, event):
        '''
        gets called when want to ban process
        '''
        #dialog to enter process name to ban
        dlg = wx.TextEntryDialog(self, 'Process name: ', 'Ban Process')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            self.db.add_ban(self.mac, dlg.GetValue())
            #put in send messages queue
            self.q.put((self.mac, server_pro.build_ban_proc(dlg.GetValue())))
        dlg.Destroy()

    def onUnbanProcess(self, event):
        '''
        gets called when want to unban process
        '''
        # dialog to enter process name to ban
        dlg = wx.TextEntryDialog(self, 'Process name: ', 'Unban Process')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            self.db.delete_ban_proc(self.mac, dlg.GetValue())
            # put in send messages queue
            self.q.put((self.mac, server_pro.build_unban_proc(dlg.GetValue())))
        dlg.Destroy()

    def onshutpc(self,event):
        '''
        gets called when want to shutdown a user pc
        '''
        # put in send messages queue
        self.q.put((self.mac, server_pro.build_close_pc()))

    def onclosesys(self, event):
        '''
        gets called when want to close a user system
        '''
        # put in send messages queue and closing the system
        self.q.put((self.mac , server_pro.build_close_sys()))
        self.frame.Destroy()

    def setProcs(self):
        '''
        Updates the ObjectListView display
        '''
        cw = self.col_w
        # change column widths as necessary
        if self.gui_shown:
            cw["name"] = self.procmonOlv.GetColumnWidth(0)
            cw["pid"] = self.procmonOlv.GetColumnWidth(1)
            cw["exe"] = self.procmonOlv.GetColumnWidth(2)
            cw["user"] = self.procmonOlv.GetColumnWidth(3)
            cw["cpu"] = self.procmonOlv.GetColumnWidth(4)
            cw["mem"] = self.procmonOlv.GetColumnWidth(5)
            cw["disk"] = self.procmonOlv.GetColumnWidth(6)

        cols = [
            ColumnDefn("name", "left", cw["name"], "name"),
            ColumnDefn("pid", "left", cw["pid"], "pid"),
            ColumnDefn("exe location", "left", cw["exe"], "exe"),
            ColumnDefn("username", "left", cw["user"], "user"),
            ColumnDefn("cpu", "left", cw["cpu"], "cpu"),
            ColumnDefn("mem", "left", cw["mem"], "mem"),
            ColumnDefn("disk", "left", cw["disk"], "disk")
            ]
        #sets the task display
        self.procmonOlv.SetColumns(cols)
        self.procmonOlv.SetObjects(self.procs)
        if self.currentSelection:
            self.procmonOlv.Select(self.currentSelection)
            self.procmonOlv.SetFocus()
        #check if there are bad procs
        for i in self.bad_procs:
            self.procmonOlv.SetItemTextColour(i, wx.RED)
            self.procmonOlv.Refresh()
        self.procmonOlv.SortBy(self.sort_col)
        self.gui_shown = True

    def updateDisplay_server(self, procs,bad_procs):
        '''
        get the pubsub from the mainserver and updates the task display
        :param procs: list of the processes
        :param bad_procs: list of the processes that passed limits
        :return:
        '''
        self.procs = procs
        self.bad_procs = bad_procs
        #check if process passed limit
        if len(bad_procs) != 0:
            wx.CallAfter(pub.sendMessage, 'add', mac="0", pass_limit=True, created=True)
        else:
            wx.CallAfter(pub.sendMessage, 'add', mac="0", pass_limit=False, created=True)
        self.setProcs()
        if not self.timer.IsRunning():
            self.timer.Start(15000)

class LimitsFrame(wx.Frame):
    def __init__(self, mac, send_q):
        '''
        constructor
        :param mac: the mac address
        :param send_q: the queue for sending messages
        '''
        wx.Frame.__init__(self, None, title="Set Limits", size=(400, 400))
        panel = LimitsPanel(self, mac, send_q)


class LimitsPanel(wx.Panel):
    def __init__(self, parent, mac, send_q):
        '''
        constructor
        :param parent: the frame
        :param mac: the mac address
        :param send_q: the queue for sending messages
        '''
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        self.db = DB()
        self.mac = mac
        self.q = send_q
        # the main sizer
        b_sizer = wx.BoxSizer(wx.VERTICAL)

        # the cpu input box
        cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        before_cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        cpu_text = wx.StaticText(self, 1, label="CPU:  ")
        before_cpu = wx.StaticText(self, 1, label=f"CPU limit: {self.db.get_cpu_limits_value(self.mac)}")
        self.cpuField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        cpu_box.Add(cpu_text, 0, wx.ALL, 5)
        before_cpu_box.Add(before_cpu, 0, wx.ALL, 5)
        cpu_box.Add(self.cpuField, 0, wx.ALL, 5)


        # the memory input box
        memory_box = wx.BoxSizer(wx.HORIZONTAL)
        before_memory_box = wx.BoxSizer(wx.HORIZONTAL)
        memory_text = wx.StaticText(self, 1, label="Memory: ")
        before_mem = wx.StaticText(self, 1, label=f"Memory limit: {self.db.get_mem_limits_value(self.mac)}")
        self.memField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        memory_box.Add(memory_text, 0, wx.ALL, 5)
        before_memory_box.Add(before_mem,0,wx.ALL,5)
        memory_box.Add(self.memField, 0, wx.ALL, 5)

        # the disk input box
        disk_box = wx.BoxSizer(wx.HORIZONTAL)
        before_disk_box = wx.BoxSizer(wx.HORIZONTAL)
        disk_text = wx.StaticText(self, 1, label="Disk: ")
        before_disk = wx.StaticText(self, 1, label=f"Disk limit: {self.db.get_disk_limits_value(self.mac)}")
        self.diskField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        disk_box.Add(disk_text, 0, wx.ALL, 5)
        disk_box.Add(self.diskField, 0, wx.ALL, 5)
        before_disk_box.Add(before_disk,0,wx.ALL,5)

        # the apply button
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        applyBtn = wx.Button(self, wx.ID_ANY, label="Apply",size = (200, 60))
        applyBtn.Bind(wx.EVT_BUTTON, self.handle_limits)
        btnBox.Add(applyBtn, 0, wx.ALL, 5)

        # adding to the size
        b_sizer.Add(cpu_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(before_cpu_box,0,wx.CENTER | wx.ALL,5)
        b_sizer.Add(memory_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(before_memory_box,0,wx.CENTER | wx.ALL,5)
        b_sizer.Add(disk_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(before_disk_box,0,wx.CENTER | wx.ALL,5)
        b_sizer.AddSpacer(30)
        b_sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        #show on screen
        self.SetSizer(b_sizer)
        self.Layout()
        self.Show()

    def handle_limits(self, event):
        '''
        update the limits to the database
        '''
        # extract limits
        cpu = self.cpuField.GetValue()
        mem = self.memField.GetValue()
        disk = self.diskField.GetValue()
        #updates the database and put it in the send messages q
        if cpu != "":
            self.db.update_cpu_value(cpu)
            self.q.put((self.mac, server_pro.build_set_limits("CPU", str(cpu))))
        if mem != "":
            self.db.update_mem_value(mem)
            self.q.put((self.mac, server_pro.build_set_limits("Memory", str(mem))))
        if disk != "":
            self.db.update_disk_value(disk)
            self.q.put((self.mac, server_pro.build_set_limits("Disk", str(disk))))
        self.frame.Close()



if __name__ == '__main__':
    app = wx.App(False)
    frame = ServerFrame()
    app.MainLoop()