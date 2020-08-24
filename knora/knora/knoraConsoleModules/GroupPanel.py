from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint

from knora.models.helpers import Actions, BaseError, Context, Cardinality
from knora.models.langstring import Languages, LangStringParam, LangString
from knora.models.connection import Connection, Error
from knora.models.project import Project
from knora.models.listnode import ListNode
from knora.models.group import Group
from knora.models.user import User
from knora.models.ontology import Ontology
from knora.models.propertyclass import PropertyClass
from knora.models.resourceclass import ResourceClass

from knora.knoraConsoleModules.KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker

def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

class GroupPanel(wx.Panel):
    """
    User tab
    """
    def __init__(self, *args, **kw):
        super(GroupPanel, self).__init__(*args, **kw)

        self.con = None
        self.projects = None
        self.ids = []
        self.proj_iri_name = {}
        self.proj_name_iri = {}

        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.listctl = wx.ListCtrl(self, name="Groups:",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.listctl.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Project", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Description", width=wx.LIST_AUTOSIZE)
        topsizer.Add(self.listctl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_button = wx.Button(parent=self, label="edit")
        self.edit_button.Bind(wx.EVT_BUTTON, self.edit_entry)
        self.new_button = wx.Button(parent=self, label="new")
        self.new_button.Bind(wx.EVT_BUTTON, self.new_entry)
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self):
        groups = Group.getAllGroups(con=self.con)
        self.projects = Project.getAllProjects(con=self.con)
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.projects))
        self.listctl.DeleteAllItems()
        for group in groups:
            print(group.name)
            self.listctl.Append((group.name,
                                 self.proj_iri_name[group.project],
                                 group.description))
            self.ids.append(group.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.Select(0)

    def new_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        group_iri = self.ids[idx]
        ge = GroupEntryDialog(self.con, group_iri, True, self)
        res = ge.ShowModal()
        if res == wx.ID_OK:
            group = ge.get_value()
            group = group.create()
            self.listctl.Append((group.name,
                                 self.proj_iri_name[group.project],
                                 group.description))
            self.ids.append(group.id)

    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        group_iri = self.ids[idx]
        ge = GroupEntryDialog(self.con, group_iri, False, self)
        res = ge.ShowModal()
        if res == wx.ID_OK:
            group: Group = ge.get_changed()
            group = group.update()

            self.listctl.SetItem(idx, 0, group.name)
            self.listctl.SetItem(idx, 2, group.description)

        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        ge.Destroy()

class GroupEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 group_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        super().__init__(*args, **kw,
                         title="Group Entry",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.group_iri = group_iri
        self.con = con
        try:
            if newentry:
                self.group = Group(con=con)
            else:
                tmpgroup = Group(con=con, id=group_iri)
                self.group = tmpgroup.read()
            self.all_projects = Project.getAllProjects(con)
            #self.all_groups = Group.getAllGroups(con)
        except BaseError as knerr:
            show_error("Couldn't get information from knora", knerr)
            return
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.all_projects))
        self.proj_name_iri = dict(map(lambda x: (x.shortname, x.id), self.all_projects))
        proj_names = list(map(lambda x: x.shortname, self.all_projects))
        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
            enable_project = True
        else:
            cols = 3
            enable_project = False
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_name = None if newentry else self.group.name if self.group.name is not None else ""
        self.name = KnDialogTextCtrl(panel1, gsizer, "Name: ", "name", tmp_name)

        tmp_description = None if newentry else self.group.description if self.group.description is not None else ""
        self.description = KnDialogTextCtrl(panel1, gsizer, "Description: ", "description", tmp_description, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp_project = None if newentry else self.proj_iri_name.get(self.group.project)
        self.project = KnDialogChoice(panel1, gsizer, "Project", "project", proj_names, tmp_project, enabled=enable_project)

        self.selfjoin = KnDialogCheckBox(panel1, gsizer, "Selfjoin: ", "selfjoin", self.group.selfjoin)
        self.status = KnDialogCheckBox(panel1, gsizer, "Status: ", "active", self.group.status)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def get_value(self) -> Group:
        self.group = Group(con=self.con,
                           name=self.name.get_value(),
                           description=self.description.get_value(),
                           project=self.proj_name_iri.get(self.project.get_value()),
                           status=self.status.get_value(),
                           selfjoin=self.selfjoin.get_value())
        return self.group

    def get_changed(self) -> Group:
        tmp = self.name.get_changed()
        if tmp is not None:
            self.group.name = tmp

        tmp = self.description.get_changed()
        if tmp is not None:
            self.group.description = tmp

        tmp = self.selfjoin.get_changed()
        if tmp is not None:
            self.group.selfjoin = tmp

        tmp = self.status.get_changed()
        if tmp is not None:
            self.group.status = tmp

        return self.group
