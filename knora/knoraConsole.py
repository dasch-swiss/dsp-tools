import os
import sys
import wx
from typing import List, Set, Dict, Tuple, Optional
from knora import KnoraError, Knora
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from knoraConsoleModules.ProjectPanel import ProjectPanel
from knoraConsoleModules.UserPanel import UserPanel


class KnoraConsole(wx.Frame):
    """
    Main Window for Knora console
    """

    def __init__(self, *args, **kw):
        super(KnoraConsole, self).__init__(*args, **kw)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Knora Console")

        self.nb = wx.Notebook(self)

        self.project_panel = ProjectPanel(self.nb)
        self.nb.InsertPage(index=0, page=self.project_panel, text="Projects")

        self.up = UserPanel(self.nb)
        self.nb.InsertPage(index=1, page=self.up, text="Users")

        self.con = None


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
            self.project_panel.update(self.con)

            self.up.set_connection(self.con)
            self.up.update(self.con)

    def onDisconnect(self, event):
        wx.MessageBox("Disconnect from server")

    def onAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("Knora Console",
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
            self.con = Knora(server_str)
            self.con.login(username_str, password_str)

        else:
            print("CANCEL PRESSED")

    def get_res(self):
        return self.con

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.

    app = wx.App()
    frm = KnoraConsole(None, title='Knora Console V0.1.1 Beta', size=wx.Size(800, 600))
    frm.Show()
    app.MainLoop()
    print("Bye Bye")
