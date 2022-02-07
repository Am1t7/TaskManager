import controller
import psutil # http://code.google.com/p/psutil/
import wx
import threading
from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
import webbrowser
from googlesearch import search
from limits import Limits
from DB import DB
import uuid


########################################################################
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
class MainPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        self.limit = Limits()
        self.frame = parent
        self.currentSelection = None
        self.gui_shown = False
        self.procs = []
        self.bad_procs = []
        self.sort_col = 0

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

        #endProcBtn = wx.Button(self, label="End Process")
        #endProcBtn.Bind(wx.EVT_BUTTON, self.onKillProc)

        #infoProcBtn = wx.Button(self, label = "Info")
        #infoProcBtn.Bind(wx.EVT_BUTTON, self.onOpenInfo)

        limitProcBtn = wx.Button(self, label = "Set Limits")
        limitProcBtn.Bind(wx.EVT_BUTTON, self.onOpenLimit)

        #button_sizer.Add(endProcBtn, 0, wx.ALIGN_RIGHT | wx.ALL, 0)
        #button_sizer.Add(infoProcBtn, 0, wx.ALIGN_LEFT | wx.ALL, 0)
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

    #----------------------------------------------------------------------
    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.procmonOlv.ScreenToClient(pos)
        self.procmonOlv.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetText()
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
        frame = LimitsFrame(self.limit)
        panel = LimitsPanel(self,self.limit)
        '''
        dlg = wx.TextEntryDialog(frame, 'CPU:', 'Set CPU Limit')
        dlg.SetValue("")
        if dlg.ShowModal() == wx.ID_OK:
            print('You entered: %s\n' % dlg.GetValue())
        dlg.Destroy()
        '''

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
        if not self.timer.IsRunning():
            self.timer.Start(15000)

########################################################################
class LimitsFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, limit_obj):
        """Constructor"""
        wx.Frame.__init__(self, None, title="PyProcMon", size=(400, 400))
        panel = LimitsPanel(self,limit_obj)


class LimitsPanel(wx.Panel):
    def __init__(self, parent, limit_obj):
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        self.limit = limit_obj
        self.db = DB()

        # the main sizer
        b_sizer = wx.BoxSizer(wx.VERTICAL)

        # cpu
        cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        cpu_text = wx.StaticText(self, 1, label="CPU:  ")
        self.cpuField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        cpu_box.Add(cpu_text, 0, wx.ALL, 5)
        cpu_box.Add(self.cpuField, 0, wx.ALL, 5)


        # mem
        memory_box = wx.BoxSizer(wx.HORIZONTAL)
        memory_text = wx.StaticText(self, 1, label="Memory: ")
        self.memField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        memory_box.Add(memory_text, 0, wx.ALL, 5)
        memory_box.Add(self.memField, 0, wx.ALL, 5)

        # disk
        disk_box = wx.BoxSizer(wx.HORIZONTAL)
        disk_text = wx.StaticText(self, 1, label="Disk: ")
        self.diskField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        disk_box.Add(disk_text, 0, wx.ALL, 5)
        disk_box.Add(self.diskField, 0, wx.ALL, 5)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        applyBtn = wx.Button(self, wx.ID_ANY, label="Apply",size = (200, 60))
        applyBtn.Bind(wx.EVT_BUTTON, self.handle_limits)
        btnBox.Add(applyBtn, 0, wx.ALL, 5)

        b_sizer.Add(cpu_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(memory_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.Add(disk_box, 0, wx.CENTER | wx.ALL, 5)
        b_sizer.AddSpacer(30)
        b_sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        self.SetSizer(b_sizer)
        self.Layout()
        self.Show()

    def handle_limits(self, event):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)for ele in range(0, 8 * 6, 8)][::-1])
        mac = mac.upper()
        # extract username and password
        cpu = self.cpuField.GetValue()
        mem = self.memField.GetValue()
        disk = self.diskField.GetValue()
        if self.db.mac_exist(mac):
            if cpu == "":
                cpu = 100.0
                self.db.update_limits_details("cpu", cpu)
            if mem == "":
                mem = 1000.0
                self.db.update_limits_details("mem", mem)
            if disk == "":
                disk = 1000.0
                self.db.update_limits_details("disk", disk)
        else:
            if cpu == "":
                cpu = 100.0
            if mem == "":
                mem = 1000.0
            if disk == "":
                disk = 1000.0
            self.db.add_limits(mac, cpu, mem, disk)
        print("in apply")
        self.limit.update_limits(cpu, mem, disk)






class MainFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="PyProcMon", size=(1024, 768))
        panel = MainPanel(self)
        
        # set up the statusbar
        self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(4)
        self.StatusBar.SetStatusWidths([200, 200, 200, 200])

        # create a pubsub receiver
        #Publisher().subscribe(self.updateStatusbar, "update_status")
        pub.subscribe(self.updateStatusbar ,'update_status')
        
        self.Show()
        
    #----------------------------------------------------------------------
    def updateStatusbar(self, procsnum,totalcpu,totalmem, totaldisk):
        """"""
        procs=procsnum
        cpu=totalcpu
        mem = totalmem
        disk = totaldisk
        self.SetStatusText("Processes: %s" % procs, 0)
        self.SetStatusText("CPU Usage: %s" % cpu, 1)
        self.SetStatusText("Physical Memory: %s" % mem, 2)
        self.SetStatusText("Disk: %s" % disk, 3)

        

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
    
