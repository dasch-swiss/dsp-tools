from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from models.helpers import Languages, Actions, LangString
#from models.User import User
from models.project import Project
#from models.Group import Group
from models.connection import connection

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker

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
        self.edit_button.Bind(wx.EVT_BUTTON, self.edit_entry)
        self.new_button = wx.Button(parent=self, label="new")
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self):

        projects = Project.getAllProjects(self.con)

        #projects = con.get_existing_projects(True)
        self.listctl.DeleteAllItems()
        for project in projects:
            self.listctl.Append((project.shortcode,
                                 project.shortname,
                                 project.longname,
                                 project.description[Languages.EN]))
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

    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        project_iri = self.ids[idx]
        pe = ProjectEntryDialog(self.con, project_iri, False, self)
        res = pe.ShowModal()


class ProjectEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 project_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        super().__init__(*args, **kw,
                         title="Project Entry",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.project_iri = project_iri
        self.con = con
        try:
            if newentry:
                self.project = Project(con=con)
            else:
                tmpproject = Project(con=con, id=project_iri)
                self.project = tmpproject.read()
            #self.all_projects = Project.getAllProjects(con)
            #self.all_groups = Group.getAllGroups(con)
        except KnoraError as knerr:
            show_error("Couldn't get information from knora", knerr)
            return
        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
        else:
            cols = 3
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_shortcode = None if newentry else self.project.shortcode if self.project.shortcode is not None else ""
        self.shortcode = KnDialogTextCtrl(panel1, gsizer, "Shortcode: ", "shortcode", tmp_shortcode)

        tmp_shortname = None if newentry else self.project.shortname if self.project.shortname is not None else ""
        self.shortname = KnDialogTextCtrl(panel1, gsizer, "Shortname: ", "shortname", tmp_shortname)

        tmp_longname = None if newentry else self.project.longname if self.project.longname is not None else ""
        self.longname = KnDialogTextCtrl(panel1, gsizer, "Longname: ", "longname", tmp_longname, size=wx.Size(200,50), style=wx.TE_MULTILINE)

        self.selfjoin= KnDialogCheckBox(panel1, gsizer, "Selfjoin: ", "selfjoin", self.project.selfjoin)
        self.status = KnDialogCheckBox(panel1, gsizer, "Status: ", "active", self.project.status)


        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)
