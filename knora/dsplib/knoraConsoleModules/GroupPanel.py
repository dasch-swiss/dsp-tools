from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint
import re

from ..models.helpers import Actions, BaseError, Context, Cardinality
from ..models.langstring import Languages, LangStringParam, LangString
from ..models.connection import Connection
from ..models.project import Project
from ..models.listnode import ListNode
from ..models.group import Group
from ..models.user import User
from ..models.ontology import Ontology
from ..models.propertyclass import PropertyClass
from ..models.resourceclass import ResourceClass

from ..knoraConsoleModules.KnDialogControl import show_error, KnDialogControl, KnDialogTextCtrl, KnDialogChoice,\
    KnDialogCheckBox, KnCollapsiblePicker

from pprint import pprint

class GroupPanel(wx.Panel):
    """
    Group panel for modifying/adding user groups
    """

    def __init__(self, *args, **kw):
        """
        Constructor for the group panel

        :param args: other arguments
        :param kw: other keywords
        """
        super(GroupPanel, self).__init__(*args, **kw)

        self.con = None
        self.projects = None
        self.ids = []
        self.proj_iri_name = {}
        self.proj_name_iri = {}

        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.listctl = wx.ListCtrl(parent=self,
                                   name="Groups:",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.listctl.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Project", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Description", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Status", width=wx.LIST_AUTOSIZE)
        topsizer.Add(self.listctl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_button = wx.Button(parent=self, label="edit")
        self.edit_button.Bind(wx.EVT_BUTTON, self.edit_entry)
        self.new_button = wx.Button(parent=self, label="new")
        self.new_button.Bind(wx.EVT_BUTTON, self.new_entry)
        self.delete_button = wx.Button(parent=self, label="delete")
        self.delete_button.Bind(wx.EVT_BUTTON, self.delete_entry)
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.delete_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection) -> None:
        """
        Set the connection to the server
        :param con: Connection instance
        :return: None
        """
        self.con = con
        return None

    def update(self) -> None:
        """
        Update the list of groups to be displayed

        :return: None
        """
        try:
            groups = Group.getAllGroups(con=self.con)
            self.projects = Project.getAllProjects(con=self.con)
        except BaseError as err:
            show_error("Couldn't get group/project information!")
            return None
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.projects))
        self.listctl.DeleteAllItems()
        for group in groups:
            self.listctl.Append((group.name,
                                 self.proj_iri_name[group.project],
                                 group.description if len(group.description) < 32 else group.description[:31] + '…',
                                 'active' if group.status else 'inactive'))
            self.ids.append(group.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.Select(0)
        self.Layout()

    def new_entry(self, event: wx.Event) -> None:
        """
        Start the Dialog for making a new group entry

        :param event: wx.Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        group_iri = self.ids[idx]
        ge = GroupEntryDialog(self.con, group_iri, True, self)
        res = ge.ShowModal()
        if res == wx.ID_OK:
            group = ge.get_value()
            group = group.create()
            pprint(self.proj_iri_name)
            print(group.project)
            self.listctl.Append((group.name,
                                 self.proj_iri_name[group.project],
                                 group.description))
            self.ids.append(group.id)

    def edit_entry(self, event: wx.Event) -> None:
        """
        Start the Dialog for modifying a group entry

        :param event: wx.Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        group_iri = self.ids[idx]
        ge = GroupEntryDialog(self.con, group_iri, False, self)
        res = ge.ShowModal()
        if res == wx.ID_OK:
            group: Group = ge.get_changed()
            try:
                group = group.update()
            except BaseError as err:
                show_error("Could'nt update group information!", err)
                return
            else:
                self.listctl.SetItem(idx, 0, group.name)
                self.listctl.SetItem(idx, 2, group.description if len(group.description) < 32 else group.description[:31] + '…',)
                self.listctl.SetItem(idx, 3, 'active' if group.status else 'inactive')

        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.SetColumnWidth(2, -1)
        ge.Destroy()

    def delete_entry(self, event: wx.Event) -> None:
        """
        Delete a group in making it "inactive". A group can not be removed completely

        :param event: wx.Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        group_iri = self.ids[idx]
        dlg = wx.MessageDialog(parent=self,
                               message="Do You really want to delete this group (make it inactive)?",
                               caption="Delete ?",
                               style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            try:
                group = Group(con=self.con, id=group_iri).delete()
            except BaseError as err:
                show_error("Couldn't delete project!", err)
            else:
                self.listctl.SetItem(idx, 3, 'active' if group.status else 'inactive')

NAME = 1

class GroupValidator(wx.Validator):
    """
    Validator for the input fields...
    """
    def __init__(self, flag=None):
        """
        Constructor for the validator
        :param flag: Must be NAME
        """
        wx.Validator.__init__(self)
        self.flag = flag

    def Clone(self):
        return GroupValidator(self.flag)

    def Validate(self, win):
        """
        That's the validator method
        :param win:
        :return:
        """
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if self.flag == NAME:
            if len(text) == 0:
                wx.MessageBox("A group name must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.match("^[\\w\-]+$", text):
                wx.MessageBox("A valid group name must be given! (letters A-Z, a-z, 0-9, _, -)", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

class GroupEntryDialog(wx.Dialog):
    """
    Open a group entry/modify dialog
    """

    def __init__(self,
                 con: Connection = None,
                 group_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        """
        Constructor of group entry dialog

        :param con: Connection instance
        :param group_iri: IRI of the group to modify, or None, if a new group
        :param newentry: True, if a new group should be created, False otherwise
        :param args: Other args
        :param kw: Other keywords
        """
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
        except BaseError as knerr:
            show_error("Couldn't get group information from knora", knerr)
            return
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.all_projects))
        self.proj_name_iri = dict(map(lambda x: (x.shortname, x.id), self.all_projects))
        proj_names = list(map(lambda x: x.shortname, self.all_projects))
        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
            enable_group = True
        else:
            cols = 3
            enable_group = False
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_name = None if newentry else self.group.name if self.group.name is not None else ""
        self.name = KnDialogTextCtrl(panel=panel1,
                                     gsizer=gsizer,
                                     label="Name: ",
                                     name="name",
                                     value=tmp_name,
                                     validator=GroupValidator(NAME))

        tmp_description = None if newentry else self.group.description if self.group.description is not None else ""
        self.description = KnDialogTextCtrl(panel=panel1,
                                            gsizer=gsizer,
                                            label="Description: ",
                                            name="description",
                                            value=tmp_description,
                                            size=wx.Size(400, 70),
                                            style=wx.TE_MULTILINE)

        tmp_project = None if newentry else self.proj_iri_name.get(self.group.project)
        self.project = KnDialogChoice(panel=panel1,
                                      gsizer=gsizer,
                                      label="Project",
                                      name="project",
                                      choices=proj_names,
                                      value=tmp_project,
                                      enabled=enable_group)

        self.selfjoin = KnDialogCheckBox(panel=panel1,
                                         gsizer=gsizer,
                                         label="Selfjoin: ",
                                         name="selfjoin",
                                         status=self.group.selfjoin)
        self.status = KnDialogCheckBox(panel=panel1,
                                       gsizer=gsizer,
                                       label="Status: ",
                                       name="active",
                                       status=self.group.status)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def get_value(self) -> Union[Group, None]:
        """
        Get all the group values

        :return: Return Group instance
        """
        try:
            self.group = Group(con=self.con,
                               name=self.name.get_value(),
                               description=self.description.get_value(),
                               project=self.proj_name_iri.get(self.project.get_value()),
                               status=self.status.get_value(),
                               selfjoin=self.selfjoin.get_value())
        except BaseError as err:
            show_error("Couldn't get group information!", err)
            return None
        return self.group

    def get_changed(self) -> Group:
        """
        Get all changed group values

        :return: Group instance
        """

        try:
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
        except BaseError as err:
            show_error("Could'nt set change information!", err)
            return None
        return self.group
