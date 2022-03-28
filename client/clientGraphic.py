from client import controller
import psutil
import wx
import threading
from ObjectListView import ObjectListView, ColumnDefn
from pubsub import pub
import webbrowser
from googlesearch import search
from client.clientDB import DB
import os

chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
class MainPanel(wx.Panel):
    '''
    the main panel that display the process that runs on the pc
    '''
    def __init__(self, parent, send_q):
        '''
        the main panel
        :param parent: the frame
        :param send_q: the send messages
        '''
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
        # set the list of the tasks to display
        self.procmonOlv = ObjectListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.procmonOlv.Bind(wx.EVT_LIST_COL_CLICK, self.onColClick)
        self.procmonOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)

        # pop up menu
        self.popupmenu = wx.Menu()
        for text in "Info,End Task".split(","):
            item = self.popupmenu.Append(-1, text)
            self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.procmonOlv.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)


        # sort the tasks
        self.procmonOlv.EnableSorting()
        # set the task to display
        self.setProcs()

        # the sizer for the buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # set the "set limits" button
        limitProcBtn = wx.Button(self, label = "Set Limits")
        limitProcBtn.Bind(wx.EVT_BUTTON, self.onOpenLimit)
        button_sizer.Add(limitProcBtn, 0, wx.ALIGN_CENTER | wx.ALL, 0)


        #  the main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.procmonOlv, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(mainSizer)

        #  check for updates every 15 seconds
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update("")
        self.setProcs()

        self.procmonOlv.Show()

        # pubsub receivers
        pub.subscribe(self.updateDisplay ,'update')
        pub.subscribe(self.on_kill_proc_server, 'kill')
        pub.subscribe(self.limits_from_server, 'update_limits')
        pub.subscribe(self.ban_from_server, 'ban')
        pub.subscribe(self.display_opening_ban_proc, 'open_ban')
        pub.subscribe(self.unban_from_server, 'del_ban')
        pub.subscribe(self.shut_pc, 'shut')
        pub.subscribe(self.close_sys, 'close')
        pub.subscribe(self.update_first, 'start')

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
            threading.Thread(target =self.onOpenInfo).start()
        elif text == "End Task":
            self.onKillProc()


    def onColClick(self, event):
        '''
        Remember which column to sort by
        '''
        self.sort_col = event.GetColumn()

    def onKillProc(self):
        '''
        Kill the selected process by id
        '''
        obj = self.procmonOlv.GetSelectedObject()
        try:
            pid = int(obj.pid)
            p = psutil.Process(pid)
            p.terminate()
            self.update("")
        except Exception as e:
            pass
    def on_kill_proc_server(self, pid):
        '''
        kill a process that sent from the server
        '''
        try:
            p = psutil.Process(pid)
            p.terminate()
            self.update("")
        except Exception as e:
            pass

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
            #  to search
            query = name
            for j in search(query, tld="co.in", num=1, stop=1, pause=2):
                webbrowser.get(chrome_path).open(j)

    def onOpenLimit(self,event):
        '''
        open a window to set limits
        '''
        frame = LimitsFrame()
        panel = LimitsPanel(self)

        frame.Show()
    # ----------------------------------------------------------------------
    def onSelect(self, event):
        '''
        Gets called when an item is selected and helps keep track of what item is selected
        '''
        item = event.GetItem()
        itemId = item.GetId()
        self.currentSelection = itemId

    # ----------------------------------------------------------------------
    def setProcs(self):
        '''
        Updates the ObjectListView display
        '''
        cw = self.col_w
        #  change column widths as necessary
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
        self.procmonOlv.SetColumns(cols)
        self.procmonOlv.SetObjects(self.procs)
        if self.currentSelection:
            self.procmonOlv.Select(self.currentSelection)
            self.procmonOlv.SetFocus()

        for i in self.bad_procs:
            self.procmonOlv.SetItemTextColour(i, wx.RED)
            self.procmonOlv.Refresh()
        self.procmonOlv.SortBy(self.sort_col)
        self.gui_shown = True

    # ----------------------------------------------------------------------
    def update(self, event):
        '''
        Start a thread to get processes information
        :param event:
        :return:
        '''
        print ("update thread started!")
        self.timer.Stop()
        controller.ProcThread()

    def update_first(self):
        '''
        update the process display
        :return:
        '''
        self.update("")

    # ----------------------------------------------------------------------
    def updateDisplay(self, procs, bad_procs):
        '''
        Catches the pubsub message and updates the display
        :param procs: the current procs on the pc
        :param bad_procs: procs that break limits
        :return:
        '''
        self.procs = procs
        self.bad_procs = bad_procs
        self.setProcs()
        # put the procs in q to send to server
        self.q.put(procs)
        if not self.timer.IsRunning():
            self.timer.Start(15000)

    def limits_from_server(self, type, value):
        '''
        get limits from server and updates them to the client
        :param type: the type of limit
        :param value: what to update to
        :return:
        '''
        if type == "CPU":
            self.db.update_cpu_value(float(value))
        if type == "Memory":
            self.db.update_mem_value(float(value))
        if type == "Disk":
            self.db.update_disk_value(float(value))


    def ban_from_server(self, mac, soft):
        '''
        add a ban software to the database
        :param mac: the pc mac address
        :param soft: software name
        :return:
        '''
        self.db.add_ban(mac, soft)

    def unban_from_server(self, mac, soft):
        '''
        delete a software from the banned software
        :param mac: the mac address
        :param soft: software name
        :return:
        '''
        self.db.delete_ban_proc(mac, soft)


    def display_opening_ban_proc(self, name, procs):
        '''
        check if the proc is banned, closing the proc and displays message
        :param name: the name of the process
        :param procs: list of the processes in the pc
        :return:
        '''
        for p in procs:
            if name == p.name:
                try:
                    # close the process
                    psutil.Process(int(p.pid)).terminate()
                except Exception as e:
                    pass
        # updating the processes display
        self.update("")
        wx.MessageBox(f'{name} is banned!!!', 'Warning', wx.ICON_WARNING | wx.OK)

    def shut_pc(self):
        '''
        shutting the pc
        '''
        os.system('shutdown -s')

    def close_sys(self):
        '''
        closing the software
        '''
        self.frame.Destroy()

class LimitsFrame(wx.Frame):
    '''
    the frame for the set limits option
    '''
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Set Limits", size=(400, 400))
        panel = LimitsPanel(self)
        # adding icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("tm.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)


class LimitsPanel(wx.Panel):
    '''
    the pannel for the set limits option
    '''
    def __init__(self, parent):
        '''
        constructor
        :param parent: the frame
        '''
        wx.Panel.__init__(self, parent=parent)
        self.frame = parent
        # set the database
        self.db = DB()
        #  the main sizer
        b_sizer = wx.BoxSizer(wx.VERTICAL)

        #  the cpu input box
        cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        before_cpu_box = wx.BoxSizer(wx.HORIZONTAL)
        cpu_text = wx.StaticText(self, 1, label="CPU:  ")
        before_cpu = wx.StaticText(self, 1, label=f"CPU limit: {self.db.get_cpu_limits_value()}")
        self.cpuField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        cpu_box.Add(cpu_text, 0, wx.ALL, 5)
        before_cpu_box.Add(before_cpu, 0, wx.ALL, 5)
        cpu_box.Add(self.cpuField, 0, wx.ALL, 5)


        #  the memory input box
        memory_box = wx.BoxSizer(wx.HORIZONTAL)
        before_memory_box = wx.BoxSizer(wx.HORIZONTAL)
        memory_text = wx.StaticText(self, 1, label="Memory: ")
        before_mem = wx.StaticText(self, 1, label=f"Memory limit: {self.db.get_mem_limits_value()}")
        self.memField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        memory_box.Add(memory_text, 0, wx.ALL, 5)
        before_memory_box.Add(before_mem,0,wx.ALL,5)
        memory_box.Add(self.memField, 0, wx.ALL, 5)

        #  the disk input box
        disk_box = wx.BoxSizer(wx.HORIZONTAL)
        before_disk_box = wx.BoxSizer(wx.HORIZONTAL)
        disk_text = wx.StaticText(self, 1, label="Disk: ")
        before_disk = wx.StaticText(self, 1, label=f"Disk limit: {self.db.get_disk_limits_value()}")
        self.diskField = wx.TextCtrl(self, -1, name="",size=(150, -1))
        disk_box.Add(disk_text, 0, wx.ALL, 5)
        disk_box.Add(self.diskField, 0, wx.ALL, 5)
        before_disk_box.Add(before_disk,0,wx.ALL,5)

        # the apply button
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        applyBtn = wx.Button(self, wx.ID_ANY, label="Apply",size = (200, 60))
        applyBtn.Bind(wx.EVT_BUTTON, self.handle_limits)
        btnBox.Add(applyBtn, 0, wx.ALL, 5)

        # adding to the sizer
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
        '''
        update the limits to the database
        '''
        #  extract limits
        cpu = self.cpuField.GetValue()
        mem = self.memField.GetValue()
        disk = self.diskField.GetValue()
        # update the database
        if cpu != "":
            self.db.update_cpu_value(cpu)
        if mem != "":
            self.db.update_mem_value(mem)
        if disk != "":
            self.db.update_disk_value((disk))
        self.frame.Close()






class MainFrame(wx.Frame):
    '''
    the main frame for the display of the processes that runs on pc
    '''
    def __init__(self, send_q):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Share My Task", size=(1024, 768))
        panel = MainPanel(self, send_q)
        
        #  set up the statusbar
        self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(4)
        self.StatusBar.SetStatusWidths([200, 200, 200, 200])
        self.Bind(wx.EVT_CLOSE, self._when_closed)
        #  create a pubsub receiver
        pub.subscribe(self.updateStatusbar ,'update_status')

        # adding icon
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap("tm.png", wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        
        self.Show()

    def updateStatusbar(self, procsnum,totalcpu,totalmem, totaldisk):
        '''
        updating the details of the procs status bar
        :param procsnum: how many procs
        :param totalcpu: the total cpu usage of all the procs
        :param totalmem: the total memory usage of all the procs
        :param totaldisk: the total disk usage of all the procs
        :return:
        '''
        procs=procsnum
        cpu=totalcpu
        mem = totalmem
        disk = totaldisk
        self.SetStatusText("Processes: %s" % procs, 0)
        self.SetStatusText("CPU Usage: %s" % cpu, 1)
        self.SetStatusText("Physical Memory: %s" % mem, 2)
        self.SetStatusText("Disk: %s" % disk, 3)

    def _when_closed(self, event):
        '''
        if the client has been closed destroy him and close him
        :param event:
        :return:
        '''

        self.DestroyChildren()
        self.Destroy()
        wx.CallAfter(pub.sendMessage, 'close_cl', )

        

# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
    
