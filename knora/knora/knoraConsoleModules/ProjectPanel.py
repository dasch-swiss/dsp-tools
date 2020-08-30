from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint
import re

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

from knora.knoraConsoleModules.KnDialogControl import show_error, KnDialogControl, KnDialogTextCtrl, \
    KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker, KnDialogLangStringCtrl


class ProjectPanel(wx.Panel):
    """
    This class implements the project overview panel.
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
        Sets the connection to th server

        :param con: Connection instance
        :return: None
        """
        self.con = con

    def update(self) -> None:
        """
        Updates the project list.

        :return: None
        """
        try:
            projects = Project.getAllProjects(self.con)
        except BaseError as err:
            show_error("Couldn't read projects!", err)
        else:
            self.listctl.DeleteAllItems()
            for project in projects:
                self.listctl.Append((project.shortcode,
                                     project.shortname,
                                     project.longname,
                                     'active' if project.status else 'inactive'))
                self.ids.append(project.id)
            self.listctl.SetColumnWidth(0, -1)
            self.listctl.SetColumnWidth(1, -1)
            self.listctl.SetColumnWidth(2, -1)
            self.listctl.SetColumnWidth(3, -1)
            self.listctl.Select(0)
            self.Layout()

    def new_entry(self, event: wx.Event) -> None:
        """
        Adds a new project.

        :param event: wx.Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        project_iri = self.ids[idx]
        pe = ProjectEntryDialog(self.con, project_iri, True, self)
        res = pe.ShowModal()
        if res == wx.ID_OK:
            project = pe.get_value()
            try:
                project = project.create()
            except BaseError as err:
                show_error("Couldn't create project!", err)
            else:
                self.listctl.Append((project.shortcode,
                                     project.shortname,
                                     project.longname,
                                     'active' if project.status else 'inactive'))
                self.ids.append(project.id)

    def edit_entry(self, event: wx.Event) -> None:
        """
        Modifies project data

        :param event: a wx:Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        project_iri = self.ids[idx]
        pe = ProjectEntryDialog(self.con, project_iri, False, self)
        res = pe.ShowModal()
        if res == wx.ID_OK:
            project: Project = pe.get_changed()
            try:
                project.update()
            except BaseError as err:
                show_error("Couldn't modify the project!", err)
            else:
                self.listctl.SetItem(idx, 0, project.shortcode)
                self.listctl.SetItem(idx, 1, project.shortname)
                self.listctl.SetItem(idx, 2, project.longname)
                self.listctl.SetItem(idx, 3, 'active' if project.status else 'inactive')
        pe.Destroy()

    def delete_entry(self, event: wx.Event) -> None:
        """
        Delete a project in making it "inactive". A project can not be removed completely

        :param event: wx.Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        project_iri = self.ids[idx]
        dlg = wx.MessageDialog(parent=self,
                               message="Do You really want to delete this project (make it inactive)?",
                               caption="Delete ?",
                               style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            try:
                project = Project(con=self.con, id=project_iri).delete()
            except BaseError as err:
                show_error("Couldn't delete project!", err)
            else:
                self.listctl.SetItem(idx, 3, 'active' if project.status else 'inactive')


SHORTCODE = 1
SHORTNAME = 2
LONGNAME = 3
KEYWORDS = 4

class ProjectValidator(wx.Validator):
    """
    Validator for the input fields...
    """
    def __init__(self, flag=None):
        """
        Constructor for the validator
        :param flag: Must be SHORTCODE, SHORTNAME, LONGNAME, KEYWORDS
        """
        wx.Validator.__init__(self)
        self.flag = flag

    def Clone(self):
        return ProjectValidator(self.flag)

    def Validate(self, win):
        """
        That's the validator method
        :param win:
        :return:
        """
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if self.flag == SHORTCODE:
            if len(text) != 4:
                wx.MessageBox("Shortcode must be exactely 4 hex digits!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            for x in text:
                if x not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                             'A', 'B', 'C', 'D', 'E', 'F', 'a', 'b', 'c', 'd', 'e', 'f']:
                    wx.MessageBox("Sortcode must be exactely 4 hex digits!", "Error")
                    textCtrl.SetBackgroundColour("pink")
                    textCtrl.SetFocus()
                    textCtrl.Refresh()
                    return False
            return True
        elif self.flag == SHORTNAME:
            if len(text) == 0:
                wx.MessageBox("A shortname must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.fullmatch("^[\\w\-]+$", text):
                wx.MessageBox("A valid shortname must be given! (letters A-Z, a-z, 0-9, _, -)", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        elif self.flag == LONGNAME:
            if len(text) == 0:
                wx.MessageBox("A longname must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        elif self.flag == KEYWORDS:
            if len(text) == 0:
                wx.MessageBox("A comma separated list of keywords must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.fullmatch("^([\\w\- ]+)( *, *[\\w\-]+)*", text):
                wx.MessageBox("A comma separated list of keywords must be given!", "Error")
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

class ProjectEntryDialog(wx.Dialog):
    """
    wx.Dialog for entry or modification of the project data
    """

    def __init__(self,
                 con: Connection = None,
                 project_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        """
        Constructor of the project data entry dialog

        :param con: Instance of Connection object
        :param project_iri: IRI of the project if modifying the data of an exiting project, None else.
        :param newentry: True if creating a new entry, False if modifying an existing entry
        :param args: Other arguments
        :param kw: Other keywords
        """
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
        except BaseError as err:
            show_error("Couldn't get information from knora", err)
            return
        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
            enable_shortcode = True
        else:
            cols = 3
            enable_shortcode = False
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_shortcode = None if newentry else self.project.shortcode if self.project.shortcode is not None else ""
        self.shortcode = KnDialogTextCtrl(panel=panel1,
                                          gsizer=gsizer,
                                          label="Shortcode: ",
                                          name="shortcode",
                                          value=tmp_shortcode,
                                          enabled=enable_shortcode,
                                          validator=ProjectValidator(SHORTCODE))

        tmp_shortname = None if newentry else self.project.shortname if self.project.shortname is not None else ""
        self.shortname = KnDialogTextCtrl(panel=panel1,
                                          gsizer=gsizer,
                                          label="Shortname: ",
                                          name="shortname",
                                          value=tmp_shortname,
                                          enabled=enable_shortcode,
                                          validator=ProjectValidator(SHORTNAME))

        tmp_longname = None if newentry else self.project.longname if self.project.longname is not None else ""
        self.longname = KnDialogTextCtrl(panel=panel1,
                                         gsizer=gsizer,
                                         label="Longname: ",
                                         name="longname",
                                         value=tmp_longname,
                                         size=wx.Size(400, 70),
                                         style=wx.TE_MULTILINE,
                                         validator=ProjectValidator(LONGNAME))

        if not newentry:
            tmp = self.project.description if self.project.description is not None else LangString("")
        else:
            tmp = None
        self.description = KnDialogLangStringCtrl(panel=panel1,
                                                  gsizer=gsizer,
                                                  label="Description: ",
                                                  name="descr",
                                                  value=tmp,
                                                  size=wx.Size(400, -1),
                                                  style=wx.TE_MULTILINE)

        tmp_keywords = None if newentry else ', '.join(self.project.keywords) if self.project.shortname is not None else ""
        self.keywords = KnDialogTextCtrl(panel=panel1,
                                         gsizer=gsizer,
                                         label="Keywords: ",
                                         name="keywords",
                                         value=tmp_keywords,
                                         size=wx.Size(400, 70),
                                         style=wx.TE_MULTILINE,
                                         validator=ProjectValidator(KEYWORDS))

        self.selfjoin = KnDialogCheckBox(panel=panel1,
                                         gsizer=gsizer,
                                         label="Selfjoin: ",
                                         name="selfjoin",
                                         status=self.project.selfjoin)
        self.status = KnDialogCheckBox(panel=panel1,
                                       gsizer=gsizer,
                                       label="Status: ",
                                       name="active",
                                       status=self.project.status)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def get_value(self) -> Union[Project, None]:
        """
        Get all values from the project entry dialog. Used to create a new project.

        :return: Either a Project instance or None, if there's an error
        """
        if self.keywords.get_value():
            keywords = [x.strip() for x in self.keywords.get_value().split(',')]
        try:
            self.project = Project(con=self.con,
                                   shortcode=self.shortcode.get_value(),
                                   shortname=self.shortname.get_value(),
                                   longname=self.longname.get_value(),
                                   description=self.description.get_value(),
                                   keywords=keywords,
                                   status=self.status.get_value(),
                                   selfjoin=self.selfjoin.get_value())
        except BaseError as err:
            show_error("Error creating Project instance!", err)
            return None
        else:
            return self.project

    def get_changed(self) -> Union[Project, None]:
        """
        Get all changed values of an existing projects. Modifies the Project instance

        :return: Project instance with modified values
        """
        try:
            tmp = self.shortcode.get_changed()
            if tmp is not None:
                self.project.shortcode = tmp

            tmp = self.shortname.get_changed()
            if tmp is not None:
                self.project.shortname = tmp

            tmp = self.longname.get_changed()
            if tmp is not None:
                self.project.longname = tmp

            tmp = self.description.get_changed()
            if tmp is not None:
                self.project.description = tmp

            newset = set([x.strip() for x in self.keywords.get_value().split(',')])
            oldset = set(self.project.keywords)
            if oldset != newset:
                added = newset - oldset
                removed = oldset - newset
                for kw in added:
                    self.project.addKeyword(kw)
                for kw in removed:
                    self.project.rmKeyword(kw)

            tmp = self.selfjoin.get_changed()
            if tmp is not None:
                self.project.selfjoin = tmp

            tmp = self.status.get_changed()
            if tmp is not None:
                self.project.status = tmp
        except BaseError as err:
            show_error("Modifying project data failed!", err)
            return None
        else:
            return self.project
