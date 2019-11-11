from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

#from knora import KnoraError, Knora
from models.Helpers import Languages, Actions, LangString
from models.KnoraProject import KnoraProject
from models.Connection import Connection

class ProjectPanel(wx.Panel):
    """
    Project panel
    """
    def __init__(self, *args, **kw):
        super(ProjectPanel, self).__init__(*args, **kw)

        self.con = None
        self.ids = []

        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.listctl = wx.ListCtrl(self, name="Projects:",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.listctl.AppendColumn("Shortcode", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Shortname", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Longname", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Descriptioon", width=wx.LIST_AUTOSIZE)

        topsizer.Add(self.listctl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_button = wx.Button(parent=self, label="edit")
        self.edit_button.Bind(wx.EVT_BUTTON, self.start_entry)
        self.new_button = wx.Button(parent=self, label="new")
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self, con: Connection):
        projects = KnoraProject.getAllProjects(con)

        #projects = con.get_existing_projects(True)
        self.listctl.DeleteAllItems()
        for project in projects:
            self.listctl.Append((project.shortcode, project.shortname, project.longname, project.description[Languages.EN]))
            self.ids.append(project.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.SetColumnWidth(3, -1)
        self.listctl.Select(0)

    def start_entry(self, event):
        pass
        #ue = UserEntryDialog(self.con, self.ids[self.listctl.GetFirstSelected()], self)
        #ue = UserEntryDialog(self)
