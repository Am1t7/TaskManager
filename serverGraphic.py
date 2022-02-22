import wx
from pubsub import pub
from serverDB import DB
from ObjectListView import ObjectListView, ColumnDefn
import threading
import psutil
import webbrowser
from googlesearch import search


chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

class ServerFrame(wx.Frame):
    def __init__(self,parent=None):
        super(ServerFrame, self).__init__(parent, title="Server", size=(1024,768) ,style = wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)
        # create status bar
        self.CreateStatusBar(1)

        # creating the main panel
        main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()
        self.Show()





class MainPanel(wx.Panel):
    def __init__(self, parent):
        #wx.Panel.__init__(self, parent=parent)
        wx.Panel.__init__(self, parent, size=(1024, 768))

        self.frame = parent

        m_box = wx.BoxSizer()

        # creating all the screen panels
        self.login = LoginPanel(self)
        self.pc = PcPanel(self)
        self.task = TaskPanel(self)
        #self.stations = StationsPanel(self, self.frame)

        # adding all the screen panels to the sizers
        m_box.Add(self.login,0,wx.EXPAND,0)
        m_box.Add(self.pc,0,wx.EXPAND,0)
        m_box.Add(self.task,0,wx.EXPAND,0)
        #m_box.Add(self.stations,0,wx.EXPAND,0)

        self.login.Show()

        self.SetSizer(m_box)
        self.Layout()

class LoginPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(1024, 768))
        self.frame = parent
        self.gui_shown = False
        self.db = DB()

        # the main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # title
        title_image_box = wx.BoxSizer(wx.HORIZONTAL)

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
        #passText = wx.StaticText(self, 1, label="Password: ")
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
        sizer.Add(title_image_box, 0, wx.CENTER|wx.ALL, 5)
        sizer.AddSpacer(50)
        sizer.Add(username_box, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # subscribe to the answer of the login function
        #pub.subscribe(self.handle_login_ans, 'login_ans')

        self.SetSizer(sizer)
        self.Layout()
        self.Show()


    def handle_login(self, event):
        # extract username and password
        username = self.userField.GetValue()
        password = self.passField.GetValue()

        if(self.db.username_exist(username) and self.db.pass_exist(password)):
            self.Hide()
            self.frame.pc.Show()
        else:
            wx.MessageBox("not valid!!!", "Erorr", wx.OK)


class PcPanel(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(1024, 768))
        self.frame = parent

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.pc_box = wx.BoxSizer(wx.VERTICAL)
        self.pcImg = wx.Image("pc.png", wx.BITMAP_TYPE_ANY)
        self.pcImg.Rescale(100, 100)
        self.pcBmp = wx.Bitmap(self.pcImg)
        self.pcBtn = None


        self.macBox = wx.BoxSizer(wx.VERTICAL)
        self.macText = None

        #self.mainSizer.Add(self.pc_box, 0, wx.LEFT, 5)
        #self.mainSizer.Add(self.macBox,0,wx.LEFT,5)

        pub.subscribe(self.add_pc, 'add')
        pub.subscribe(self.del_pc, 'del')

        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Hide()


    def add_pc(self, mac):
        '''
        adding pc to the connected pc view
        :param mac: the mac address of the pc
        :return:
        '''
        #creating the pc logo button
        self.pcBtn = wx.BitmapButton(self, wx.ID_ANY, bitmap=self.pcBmp, size=wx.DefaultSize)
        self.pcBtn.Bind(wx.EVT_BUTTON, self.handle_pc)
        #create the text with the mac address
        self.macText = wx.StaticText(self, -1, str(mac))
        font = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.macText.SetFont(font)

        #adding to the sizers
        self.macBox.Add(self.macText, 0, wx.ALL, 5)

        self.pc_box.Add(self.pcBtn, 0, wx.ALL, 5)

        #adding to the main sizer
        self.mainSizer.Add(self.pc_box, 0, wx.LEFT, 5)
        self.mainSizer.Add(self.macBox,0,wx.LEFT,5)

        self.mainSizer.Layout()

    def del_pc(self):
        '''
        deleting a pc from the connecting pc
        :return:
        '''
        self.pc_box.Hide(self.pcBtn)
        self.pc_box.Detach(self.pcBtn)
        self.macBox.Hide(self.macText)
        self.macBox.Detach(self.macText)



    def handle_pc(self, event):
        self.Hide()
        self.frame.task.Show()



class TaskPanel(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(1024, 768))
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

        #limitProcBtn = wx.Button(self, label = "Set Limits")
        #limitProcBtn.Bind(wx.EVT_BUTTON, self.onOpenLimit)
        #button_sizer.Add(limitProcBtn, 0, wx.ALIGN_CENTER | wx.ALL, 0)


        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.procmonOlv, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(button_sizer, 0, wx.EXPAND|wx.ALL, 5)

       # self.SetSizer(mainSizer)

        # check for updates every 15 seconds
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update("")
        self.setProcs()

        pub.subscribe(self.updateDisplay_server, 'update_server')
        #self.procmonOlv.Show()
        #self.Layout()
        #self.Hide()
        self.SetSizer(mainSizer)
        self.Layout()
        self.Hide()

        #self.procmonOlv.Show()
        #self.Show()
        # ----------------------------------------------------------------------

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.procmonOlv.ScreenToClient(pos)
        self.procmonOlv.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        item = self.popupmenu.FindItemById(event.GetId())
        text = item.GetItemLabel()
        if text == "Info":
            threading.Thread(target=self.onOpenInfo).start()
        elif text == "End Task":
            self.onKillProc()

    def onColClick(self, event):
        """
        Remember which column to sort by, currently only does ascending
        """
        self.sort_col = event.GetColumn()

        # ----------------------------------------------------------------------

    def onKillProc(self):
        """
        Kill the selected process by pid
        """


        '''
        obj = self.procmonOlv.GetSelectedObject()
        try:
            pid = int(obj.pid)
            p = psutil.Process(pid)
            p.terminate()
            self.update("")
        except Exception as e:
            pass
        '''

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
        #self.procmonOlv.SortBy(self.sort_col)
        self.gui_shown = True

    #----------------------------------------------------------------------
    def update(self, event):
        """
        Start a thread to get the pid information
        """
        print ("update thread started!")
        self.timer.Stop()
        #controller.ProcThread()

    #----------------------------------------------------------------------
    def updateDisplay_server(self, procs):#, bad_procs):
        """
        Catches the pubsub message from the thread and updates the display
        """
        print ("thread done, updating display!")
        self.procs = procs
        #self.bad_procs = bad_procs
        self.setProcs()
        #self.q.put(procs)
        if not self.timer.IsRunning():
            self.timer.Start(15000)





















if __name__ == '__main__':
    app = wx.App(False)
    frame = ServerFrame()
    app.MainLoop()