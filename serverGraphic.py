import wx
from pubsub import pub
from serverDB import DB



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
        """

        :return: extracts the username and password from the fields upon pressing "login" and sends to server
        """

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

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        pc_box = wx.BoxSizer(wx.HORIZONTAL)
        pcImg = wx.Image("pc.png", wx.BITMAP_TYPE_ANY)
        pcImg.Rescale(100, 100)
        pcBmp = wx.Bitmap(pcImg)
        pcBtn = wx.BitmapButton(self, wx.ID_ANY, bitmap=pcBmp, size=wx.DefaultSize)
        pcBtn.SetWindowStyleFlag(wx.NO_BORDER)
        pcBtn.Bind(wx.EVT_BUTTON, self.handle_pc)

        pc_box.Add(pcBtn, 0, wx.ALIGN_LEFT, 5)

        mainSizer.Add(pc_box, 0, wx.LEFT, 5)


        self.SetSizer(mainSizer)
        self.Layout()
        self.Hide()



    def handle_pc(self, event):
        self.Hide()
        self.frame.task.Show()



class TaskPanel(wx.Panel):
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, size=(1024, 768))
        self.frame = parent





















if __name__ == '__main__':
    app = wx.App(False)
    frame = ServerFrame()
    app.MainLoop()