from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
import re

from pprint import pprint
from enum import Enum, unique

from knora.models.helpers import Actions, BaseError, Context, Cardinality, LastModificationDate
from knora.models.langstring import Languages, LangStringParam, LangString
from knora.models.connection import Connection, Error
from knora.models.project import Project
from knora.models.listnode import ListNode
from knora.models.group import Group
from knora.models.user import User
from knora.models.ontology import Ontology
from knora.models.propertyclass import PropertyClass
from knora.models.resourceclass import ResourceClass

from knora.knoraConsoleModules.KnDialogControl import show_error, KnDialogControl, KnDialogTextCtrl, KnDialogChoice, \
    KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText
from knora.knoraConsoleModules.ResourcePanel import ResourcePanel
from knora.knoraConsoleModules.PropertyPanel import PropertyPanel


class OntoPanel(wx.Panel):
    """
    This opens the ontology panel, which includes a ResourcePanel and PropertyPanel
    """
    def __init__(self, *args, **kw):
        """
        Initialize the ontology panel

        :param args: Other args
        :param kw: Other keywords
        """
        super(OntoPanel, self).__init__(*args, **kw)

        self.con = None
        self.projects = None
        self.ids = []
        self.proj_iri_name = {}
        self.proj_name_iri = {}

        topsizer = wx.BoxSizer(wx.VERTICAL)

        thsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pfilter_label = wx.StaticText(self, label="Filter by Project: ")
        thsizer.Add(self.pfilter_label, flag=wx.EXPAND | wx.ALL, border=3)
        self.pfilter = wx.Choice(self)
        self.pfilter.Bind(wx.EVT_CHOICE, self.pfilter_changed)
        thsizer.Add(self.pfilter, flag=wx.EXPAND | wx.ALL, border=3)
        topsizer.Add(thsizer, flag=wx.EXPAND)

        self.listctl = wx.ListCtrl(self, name="Ontologies:",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.listctl.AppendColumn("Project", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Label", width=wx.LIST_AUTOSIZE)
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
        Set the connection to the Kbora server

        :param con: Connection object
        :return: None
        """
        self.con = con

    def update(self) -> None:
        """
        Draw or redraw the list of ontologies

        :return: None
        """
        try:
            ontologies = Ontology.getAllOntologies(con=self.con)
        except BaseError as show_error:
            show_error("Couldn't get the existing ontologies!", err)
            return
        try:
            self.projects = Project.getAllProjects(con=self.con)
        except BaseError as show_error:
            show_error("Couldn't get the existing projects!", err)
            return
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.projects))
        self.proj_name_iri = dict(map(lambda x: (x.shortname, x.id), self.projects))
        self.pnames = [x.shortname for x in self.projects if x.shortname != "SystemProject"]
        self.pnames.insert(0, "-")
        self.pfilter.Clear()
        self.pfilter.Append(self.pnames)
        self.listctl.DeleteAllItems()
        for ontology in ontologies:
            if self.proj_iri_name.get(ontology.project) == "SystemProject":
                continue
            self.listctl.Append((self.proj_iri_name.get(ontology.project),
                                 ontology.name,
                                 ontology.label))
            self.ids.append(ontology.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.Select(0)

    def pfilter_changed(self, event: wx.Event) -> None:
        """
        The filter for project changed.It redisplays the onfology according to the project filter.
        :param event: The wx.Event
        :return: None
        """
        pname = self.pnames[self.pfilter.GetCurrentSelection()]
        if pname == "-":
            try:
                ontologies = Ontology.getAllOntologies(con=self.con)
            except BaseError as err:
                show_error("Couldn't get the existing ontologies!", err)
                return
        else:
            piri = self.proj_name_iri.get(pname)
            try:
                ontologies = Ontology.getProjectOntologies(self.con, piri)
            except BaseError as err:
                show_error("Couldn't get the ontologies of the selected project!", err)
                return
        self.listctl.DeleteAllItems()
        self.ids = []
        for ontology in ontologies:
            if self.proj_iri_name.get(ontology.project) == "SystemProject":
                continue
            self.listctl.Append((self.proj_iri_name.get(ontology.project),
                                 ontology.name,
                                 ontology.label))
            self.ids.append(ontology.id)

    def new_entry(self, event: wx.Event) -> None:
        """
        The use selected to create a new ontology. This opens a OntologyEntryDialog for entering the ontology
        data.

        :param event: Button event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        onto_iri = self.ids[idx]
        ontology_entry = OntologyEntryDialog(self.con, onto_iri, True, self)
        res = ontology_entry.ShowModal()
        if res == wx.ID_OK:
            onto = ontology_entry.get_value()
            try:
                lmd, onto = onto.create()
            except BaseError as err:
                show_error("Couldn't create the new ontology!", err)
                return
            self.listctl.Append((onto.name,
                                 self.proj_iri_name[onto.project],
                                 onto.label))
            self.ids.append(onto.id)

    def edit_entry(self, event: wx.Event) -> None:
        """
        The user selected to edit/modify an existing ontology. This opens a OntologyEntryDialog for editing the ontology
        data of the selected ontology.

        :param event: Button event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        onto_iri = self.ids[idx]
        ontology_entry = OntologyEntryDialog(self.con, onto_iri, False, self)
        res = ontology_entry.ShowModal()
        if res == wx.ID_OK:
            lmd, onto = ontology_entry.get_changed()
            try:
                lmd, onto = onto.update(lmd)
            except BaseError as err:
                show_error("Couln't modify the ontology!", err)
                return
            self.listctl.SetItem(idx, 0, onto.name)
            self.listctl.SetItem(idx, 2, onto.label)

        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        ontology_entry.Destroy()

    def delete_entry(self, event: wx.Event) -> None:
        """
        Delete the selected ontology. If the ontology has any associated data, the deletion will fail and
        an appropriate error message is being displayed.

        :param event: Button event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        onto_iri = self.ids[idx]
        dlg = wx.MessageDialog(parent=self,
                               message="Do You really want to delete this ontology completely?",
                               caption="Delete ?",
                               style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            try:
                lmd, onto = Ontology(con=self.con, id=onto_iri).read()
                result = onto.delete(lmd)
            except BaseError as err:
                show_error("Couldn't delete ontology!", err)
            else:
                self.update()

@unique
class OntoFields(Enum):
    NAME = 1
    LABEL = 2


class OntoValidator(wx.Validator):
    """
    Validator for the input fields...
    """

    def __init__(self, flag: OntoFields):
        """
        Constructor for the validator
        :param flag: Must be NAME, LABEL
        """
        wx.Validator.__init__(self)
        self.flag = flag

    def Clone(self):
        return OntoValidator(self.flag)

    def Validate(self, win):
        """
        That's the validator method

        :param win:
        :return:
        """
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if self.flag == OntoFields.NAME:
            if len(text) == 0:
                wx.MessageBox("An ontology name must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.fullmatch("^[\w\-]+$", text):
                wx.MessageBox("Ontology name is not valid", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        elif self.flag == OntoFields.LABEL:
            if len(text) < 1:
                wx.MessageBox("A label has to be given!", "Error")
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


class OntologyEntryDialog(wx.Dialog):
    """
    This is a dialog for creating/modifying ontologies including sub-dialogs for resources and
    propertes and assigning cardinalities to the properties.
    """
    def __init__(self,
                 con: Connection = None,
                 onto_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        """
        Constructor for the OntologyEntryDialog.

        :param con: Connection instance
        :param onto_iri: Iri of the ontology to modify, None when creating a new ontology
        :param newentry: True, if creating a nw ontology, False otherwise
        :param args: Other args
        :param kw: Other keywords
        """
        super().__init__(*args, **kw,
                         title="Ontology Entry",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.onto_iri = onto_iri
        self.con = con
        try:
            if newentry:
                self.onto = Ontology(con=con)
                self.last_modification_date = None
            else:
                self.last_modification_date, self.onto = Ontology(con=con, id=onto_iri).read()
            self.all_projects = Project.getAllProjects(con)
        except BaseError as err:
            show_error("Couldn't get information from knora", err)
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

        if not newentry:
            self.mod_date = KnDialogStaticText(panel=panel1,
                                               gsizer=gsizer,
                                               label="Last Mod.-date:",
                                               name="mod_date",
                                               value=str(self.last_modification_date))

        tmp_name = None if newentry else self.onto.name if self.onto.name is not None else ""
        self.name = KnDialogTextCtrl(panel=panel1,
                                     gsizer=gsizer,
                                     label="Name: ",
                                     name="name",
                                     value=tmp_name,
                                     enabled=enable_project,
                                     validator=OntoValidator(OntoFields.NAME))

        tmp_label = None if newentry else self.onto.label if self.onto.label is not None else ""
        self.label = KnDialogTextCtrl(panel=panel1,
                                      gsizer=gsizer,
                                      label="Label: ",
                                      name="label",
                                      value=tmp_label,
                                      validator=OntoValidator(OntoFields.LABEL))

        tmp_comment = None if newentry else self.onto.comment if self.onto.comment is not None else ""
        self.comment = KnDialogTextCtrl(panel=panel1,
                                        gsizer=gsizer,
                                        label="Comment: ",
                                        name="comment",
                                        value=tmp_comment,
                                        size=wx.Size(400, 70),
                                        style=wx.TE_MULTILINE)

        tmp_project = None if newentry else self.proj_iri_name.get(self.onto.project)
        self.project = KnDialogChoice(panel=panel1,
                                      gsizer=gsizer,
                                      label="Project",
                                      name="project",
                                      choices=proj_names,
                                      value=tmp_project,
                                      enabled=enable_project)


        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        if not newentry:
            self.splitter = wx.SplitterWindow(parent=self)
            self.leftp = ResourcePanel(parent=self.splitter, con=self.con, onto=self.onto)
            self.rightp = PropertyPanel(parent=self.splitter, con=self.con, onto=self.onto)

            self.splitter.SplitVertically(self.leftp, self.rightp)

            topsizer.Add(self.splitter, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def get_value(self) -> Union[Ontology, None]:
        """
        Get all values and return an instance of Ontology filled with these values. The resulting
        Ontology instance may be used to create a new ontology.

        :return: Ontology instance
        """
        try:
            self.onto = Ontology(con=self.con,
                                 name=self.name.get_value(),
                                 label=self.label.get_value(),
                                 comment=self.comment.get_value(),
                                 project=self.proj_name_iri.get(self.project.get_value()))
        except BaseError as err:
            show_error("Couln't create Ontology instance!", err)
            return None
        return self.onto

    def get_changed(self) -> Union[Ontology, None]:
        """
        Get all values the user has changed by nodifying the fields of the Ontology instance.

        :return: Ontology instance
        """
        try:
            tmp = self.label.get_changed()
            if tmp is not None:
                self.onto.label = tmp
            tmp = self.comment.get_changed()
            if tmp is not None:
                self.onto.comment = tmp
        except BaseError as err:
            show_error("Can not modify ontology data", err)
            return None

        return self.last_modification_date, self.onto
