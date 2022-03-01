import controller
import psutil # http://code.google.com/p/psutil/
import wx
import threading
from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
import webbrowser
from googlesearch import search
from clientDB import DB
import client_pro


########################################################################
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
class MainPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent, send_q):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        self.currentSelection = None
        self.gui_shown = False
        self.procs = []
        self.bad_procs = []
        self.sort_col = 0
        self.q = send_q
        self.db = DB()

        self.col_w = {"name":175,
                      "pid":50,
                      "exe":300,
                      "user":175,
                      "cpu":60,
                      "mem":75,
                      "disk":75}

        self.procmonOlv = ObjectListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.procmonOlv.Bind(wx.EVT_LIST_COL_CLICK, self.onColClick)
        self.procmonOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        #self.procmonOlv.Select

        #pop up menu
        self.popupmenu = wx.Menu()
        for text in "Info,End Task".split(","):
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.procmonOlv.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)



        self.procmonOlv.EnableSorting()

        self.setProcs()

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        limitProcBtn = wx.Button(self, label = "Set Limits")
        limitProcBtn.Bind(wx.EVT_BUTTON, self.onOpenLimit)
        button_sizer.Add(limitProcBtn, 0, wx.ALIGN_CENTER | wx.ALL, 0)


        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.procmonOlv, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(mainSizer)

        # check for updates every 15 seconds
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update("")
        self.setProcs()

        self.procmonOlv.Show()

        # create a pubsub receiver
        pub.subscribe(self.updateDisplay ,'update')
        pub.subscribe(self.on_kill_proc_server, 'kill')
        pub.subscribe(self.limits_from_server, 'update_limits')
        pub.subscribe(self.ban_from_server, 'ban')
        pub.subscribe(self.display_opening_ban_proc, 'open_ban')


    #----------------------------------------------------------------------
    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.procmonOlv.ScreenToClient(pos)
        self.procmonOlv.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetItemLabel()
        if text == "Info":
            threading.Thread(target =self.onOpenInfo).start()
        elif text == "End Task":
            self.onKillProc()


    def onColClick(self, event):
        """
        Remember which column to sort by, currently only does ascending
        """
        self.sort_col = event.GetColumn()

    #----------------------------------------------------------------------
    def onKillProc(self):
        """
        Kill the selected process by pid
        """
        obj = self.procmonOlv.GetSelectedObject()
        try:
            pid = int(obj.pid)
            p = psutil.Process(pid)
            p.terminate()
            self.update("")
        except Exception as e:
            pass
    def on_kill_proc_server(self, pid):
        try:
            p = psutil.Process(pid)
            p.terminate()
            self.update("")
        except Exception as e:
            pass

    def onOpenInfo(self):
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

    def onOpenLimit(self,event):
        frame = LimitsFrame()
        panel = LimitsPanel(self)

        frame.Show()
    #----------------------------------------------------------------------
    def onSelect(self, event):
        """
        Gets called when an item is selected and helps keep track of
        what item is selected
        """
        item = event.GetItem()
        itemId = item.GetId()
        self.currentSelection = itemId

    #----------------------------------------------------------------------
    def setProcs(self):
        """
        Updates the ObjectListView widget display
        """
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
            #ColumnDefn("description", "left", 200, "desc")
            ]
        self.procmonOlv.SetColumns(cols)
        self.procmonOlv.SetObjects(self.procs)
        #self.procmonOlv.SortBy(self.sort_col)
        if self.currentSelection:
            self.procmonOlv.Select(self.currentSelection)
            self.procmonOlv.SetFocus()

        for i in self.bad_procs:
            self.procmonOlv.SetItemTextColour(i, wx.RED)
            self.procmonOlv.Refresh()
        self.procmonOlv.SortBy(self.sort_col)
        self.gui_shown = True

    #----------------------------------------------------------------------
    def update(self, event):
        """
        Start a thread to get the pid information
        """
        print ("update thread started!")
        self.timer.Stop()
        controller.ProcThread()

    #----------------------------------------------------------------------
    def updateDisplay(self, procs, bad_procs):
        """
        Catches the pubsub message from the thread and updates the display
        """
        print ("thread done, updating display!")
        self.procs = procs
        self.bad_procs = bad_procs
        self.setProcs()
        self.q.put(procs)
        #self.q.put(bad_procs)
        #self.q.put(client_pro.build_done())
        if not self.timer.IsRunning():
            self.timer.Start(15000)

    def limits_from_server(self, type, value):
        if type == "CPU":
            self.db.update_cpu_value(float(value))
        if type == "Memory":
            self.db.update_mem_value(float(value))
        if type == "Disk":
            self.db.update_disk_value(float(value))


    def ban_from_server(self, mac, soft):
        self.db.add_ban(mac, soft)


    def display_opening_ban_proc(self, name, procs):
        print("here")
        for p in procs:
            if name == p.name:
                try:
                    psutil.Process(int(p.pid)).terminate()
                    #self.update("")
                except Exception as e:
                    pass
        self.update("")
        wx.MessageBox(f'{name} is banned!!!', 'Warning', wx.ICON_WARNING | wx.OK)




########################################################################
class LimitsFrame(wx.Frame):
    """"""

    #---------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Set Limits", size=(400, 400))
        panel = LimitsPanel(self)


class LimitsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        self.db = DB()
        # the main sizer
        b_sizer = wx.BoxSizer(wx.VERTICAL)

        # cpu
        cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        before_cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        cpu_text = wx.StaticText(self, 1, label="CPU:  ")
        before_cpu = wx.StaticText(self, 1, label=f"CPU limit: {self.db.get_cpu_limits_value()}")
        self.cpuField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        cpu_box.Add(cpu_text, 0, wx.ALL, 5)
        before_cpu_box.Add(before_cpu, 0, wx.ALL, 5)
        cpu_box.Add(self.cpuField, 0, wx.ALL, 5)


        # mem
        memory_box = wx.BoxSizer(wx.HORIZONTAL)
        before_memory_box = wx.BoxSizer(wx.HORIZONTAL)
        memory_text = wx.StaticText(self, 1, label="Memory: ")
        before_mem = wx.StaticText(self, 1, label=f"Memory limit: {self.db.get_mem_limits_value()}")
        self.memField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        memory_box.Add(memory_text, 0, wx.ALL, 5)
        before_memory_box.Add(before_mem,0,wx.ALL,5)
        memory_box.Add(self.memField, 0, wx.ALL, 5)

        # disk
        disk_box = wx.BoxSizer(wx.HORIZONTAL)
        before_disk_box = wx.BoxSizer(wx.HORIZONTAL)
        disk_text = wx.StaticText(self, 1, label="Disk: ")
        before_disk = wx.StaticText(self, 1, label=f"Disk limit: {self.db.get_disk_limits_value()}")
        self.diskField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        disk_box.Add(disk_text, 0, wx.ALL, 5)
        disk_box.Add(self.diskField, 0, wx.ALL, 5)
        before_disk_box.Add(before_disk,0,wx.ALL,5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        applyBtn = wx.Button(self, wx.ID_ANY, label="Apply",size = (200, 60))
        applyBtn.Bind(wx.EVT_BUTTON, self.handle_limits)
        btnBox.Add(applyBtn, 0, wx.ALL, 5)

        b_sizer.Add(cpu_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(before_cpu_box,0,wx.CENTER | wx.ALL,5)
        b_sizer.Add(memory_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(before_memory_box,0,wx.CENTER | wx.ALL,5)
        b_sizer.Add(disk_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(before_disk_box,0,wx.CENTER | wx.ALL,5)
        b_sizer.AddSpacer(30)
        b_sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        self.SetSizer(b_sizer)
        self.Layout()
        self.Show()

    def handle_limits(self, event):
        # extract limits
        cpu = self.cpuField.GetValue()
        mem = self.memField.GetValue()
        disk = self.diskField.GetValue()

        if cpu != "":
            self.db.update_cpu_value(cpu)
        if mem != "":
            self.db.update_mem_value(mem)
        if disk != "":
            self.db.update_disk_value((disk))
        self.frame.Close()






class MainFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, send_q):
        """Constructor"""
        wx.Frame.__init__(self, None, title="PyProcMon", size=(1024, 768))
        panel = MainPanel(self, send_q)
        
        # set up the statusbar
        self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(4)
        self.StatusBar.SetStatusWidths([200, 200, 200, 200])


        # create a pubsub receiver
        pub.subscribe(self.updateStatusbar ,'update_status')
        
        self.Show()
        
    #----------------------------------------------------------------------
    def updateStatusbar(self, procsnum,totalcpu,totalmem, totaldisk):
        """"""
        procs=procsnum
        cpu=totalcpu
        mem = totalmem
        disk = totaldisk
        #self.q.put(client_pro.build_total(procsnum,totalcpu,totalmem,totaldisk))
        self.SetStatusText("Processes: %s" % procs, 0)
        self.SetStatusText("CPU Usage: %s" % cpu, 1)
        self.SetStatusText("Physical Memory: %s" % mem, 2)
        self.SetStatusText("Disk: %s" % disk, 3)

        

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
    
