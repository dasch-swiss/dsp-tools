import os
import sys
import wx
import wx.adv
from wx.adv import TaskBarIcon as TaskBarIcon
import pkg_resources  # part of setuptools

# version = pkg_resources.require("knora")[0].version

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from dsplib.models.connection import Connection
from dsplib.knoraConsoleModules.ProjectPanel import ProjectPanel
from dsplib.knoraConsoleModules.ListPanel import ListPanel
from dsplib.knoraConsoleModules.UserPanel import UserPanel
from dsplib.knoraConsoleModules.GroupPanel import GroupPanel
from dsplib.knoraConsoleModules.OntoPanel import OntoPanel


class DemoTaskBarIcon(TaskBarIcon):
    TBMENU_RESTORE = wx.NewIdRef()
    TBMENU_CLOSE = wx.NewIdRef()

    def __init__(self, frame):
        TaskBarIcon.__init__(self, wx.adv.TBI_DOCK) # wx.adv.TBI_CUSTOM_STATUSITEM
        self.frame = frame

        # Set the image
        current_dir = os.path.dirname(os.path.realpath(__file__))
        print('----->', current_dir)
        icon = self.MakeIcon(wx.Image(os.path.join(current_dir,'icons/knora-py-logo.png'), wx.BITMAP_TYPE_PNG))
        self.SetIcon(icon, "Knora-py Console")
        self.imgidx = 1

        # bind some events
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarActivate)
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)


    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default EVT_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Restore Knora-py Console")
        menu.Append(self.TBMENU_CLOSE,   "Close Knora-py Console")
        return menu


    def MakeIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.Icon(img.ConvertToBitmap())
        return icon


    def OnTaskBarActivate(self, evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()


    def OnTaskBarClose(self, evt):
        wx.CallAfter(self.frame.Close)


class KnoraConsole(wx.Frame):
    """
    Main Window for Knora console
    """

    def __init__(self, *args, **kw):
        super(KnoraConsole, self).__init__(*args, **kw)

        try:
            self.tbicon = DemoTaskBarIcon(self)
        except:
            self.tbicon = None

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Knora Console")

        self.nb = wx.Notebook(self)

        self.project_panel = ProjectPanel(parent=self.nb, on_project_added_cb=self.project_added_cb)
        self.nb.InsertPage(index=0, page=self.project_panel, text="Projects")

        self.list_panel = ListPanel(self.nb)
        self.nb.InsertPage(index=1, page=self.list_panel, text="Lists")

        self.group_panel = GroupPanel(self.nb)
        self.nb.InsertPage(index=2, page=self.group_panel, text="Groups")

        self.user_panel = UserPanel(self.nb)
        self.nb.InsertPage(index=3, page=self.user_panel, text="Users")

        self.onto_panel = OntoPanel(self.nb)
        self.nb.InsertPage(index=4, page=self.onto_panel, text="Ontologies")

        self.con = None

    def project_added_cb(self):
        self.list_panel.update()
        self.group_panel.update()
        self.user_panel.update()
        self.onto_panel.update()

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        connectItem = fileMenu.Append(wx.ID_OPEN, "&Open connection...\tCtrl-O",
                                    "Connect to server")
        disconnectItem = fileMenu.Append(wx.ID_CLOSE, "&Close connection...\tCtrl-C",
                                    "Disconnect from server")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&Connection")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.onConnect, connectItem)
        self.Bind(wx.EVT_MENU, self.onDisconnect, disconnectItem)
        self.Bind(wx.EVT_MENU, self.onExit, exitItem)
        self.Bind(wx.EVT_MENU, self.onAbout, aboutItem)

    def onExit(self, event):
        """Close the frame, terminating the application."""
        self.con = None
        self.Close(True)

    def onConnect(self, event):
        """Say hello to the user."""
        dialog = OpenConnectionDialog(self)
        if dialog.GetReturnCode() == wx.ID_OK:
            self.con = dialog.get_res()

            self.project_panel.set_connection(self.con)
            self.project_panel.update()

            self.list_panel.set_connection(self.con)
            self.list_panel.update()

            self.user_panel.set_connection(self.con)
            self.user_panel.update()

            self.group_panel.set_connection(self.con)
            self.group_panel.update()

            self.onto_panel.set_connection(self.con)
            self.onto_panel.update()

    def onDisconnect(self, event):
        wx.MessageBox("Disconnect from server")

    def onAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("Knora Console V" + version,
                      "Knora Console, a tool for setting up Knora",
                      wx.OK | wx.ICON_INFORMATION)


class OpenConnectionDialog(wx.Dialog):
    """
    This open a dialog which allows the user to select a server and to
    give the username and password
    """

    def __init__(self, *args, **kw):
        super(OpenConnectionDialog, self).__init__(*args, **kw,
                                                   title="Open connection...",
                                                   style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        topsizer = wx.BoxSizer(wx.VERTICAL)

        panel1 = wx.Panel(self)
        l0 = wx.StaticText(panel1, label="Server: ")
        server = wx.TextCtrl(panel1, name="server", value="http://0.0.0.0:3333", size=wx.Size(200, -1))

        l1 = wx.StaticText(panel1, label="Username: ")
        username = wx.TextCtrl(panel1, name="username", value="root@example.com", size=wx.Size(200, -1))
        l2 = wx.StaticText(panel1, label="Password: ")
        password = wx.TextCtrl(panel1, name="password", value="test", size=wx.Size(200, -1), style=wx.TE_PASSWORD)
        gsizer = wx.GridSizer(cols=2)
        gsizer.Add(l0, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, border=3)
        gsizer.Add(server, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, border=3)
        gsizer.Add(l1, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, border=3)
        gsizer.Add(username, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, border=3)
        gsizer.Add(l2, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, border=3)
        gsizer.Add(password, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, border=3)
        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

        self.ShowModal()
        if self.GetReturnCode() == wx.ID_OK:
            server_str = server.GetLineText(0)
            username_str = username.GetLineText(0)
            password_str = password.GetLineText(0)
            self.con = Connection(server_str)
            self.con.login(username_str, password_str)

        else:
            print("CANCEL PRESSED")

    def get_res(self):
        return self.con

def mainknora():
    app = wx.App()
    frm = KnoraConsole(None, title='Knora Console V0.1.1 Beta', size=wx.Size(800, 600))
    frm.Show()
    app.MainLoop()
    print("Bye Bye")

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.

    app = wx.App()
    frm = KnoraConsole(None, title='Knora Console V0.1.1 Beta', size=wx.Size(800, 600))

    frm.Show()
    app.MainLoop()
    print("Bye Bye")
