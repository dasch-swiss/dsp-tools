from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from models.helpers import Actions, BaseError, Context, Cardinality, LastModificationDate
from models.langstring import Languages, LangStringParam, LangString
from models.connection import Connection, Error
from models.project import Project
from models.listnode import ListNode
from models.group import Group
from models.user import User
from models.ontology import Ontology
from models.propertyclass import PropertyClass
from models.resourceclass import ResourceClass

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText
from ResourcePanel import ResourcePanel
from PropertyPanel import PropertyPanel

def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


class OntoPanel(wx.Panel):
    """
    User tab
    """
    def __init__(self, *args, **kw):
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
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self):
        ontologies = Ontology.getAllOntologies(con=self.con)
        self.projects = Project.getAllProjects(con=self.con)
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

    def pfilter_changed(self, event):
        pname = self.pnames[self.pfilter.GetCurrentSelection()]
        if pname == "-":
            ontologies = Ontology.getAllOntologies(con=self.con)
        else:
            piri = self.proj_name_iri.get(pname)
            ontologies = Ontology.getProjectOntologies(self.con, piri)
        self.listctl.DeleteAllItems()
        for ontology in ontologies:
            if self.proj_iri_name.get(ontology.project) == "SystemProject":
                continue
            self.listctl.Append((self.proj_iri_name.get(ontology.project),
                                 ontology.name,
                                 ontology.label))
            self.ids.append(ontology.id)

    def new_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        onto_iri = self.ids[idx]
        ontology_entry = OntologyEntryDialog(self.con, onto_iri, True, self)
        res = ontology_entry.ShowModal()
        if res == wx.ID_OK:
            onto = ontology_entry.get_value()
            lmd, onto = onto.create()
            self.listctl.Append((onto.name,
                                 self.proj_iri_name[onto.project],
                                 onto.label))
            self.ids.append(onto.id)

    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        onto_iri = self.ids[idx]
        ontology_entry = OntologyEntryDialog(self.con, onto_iri, False, self)
        res = ontology_entry.ShowModal()
        if res == wx.ID_OK:
            lmd, onto = ontology_entry.get_changed()
            lmd, onto = onto.update(lmd)
            self.listctl.SetItem(idx, 0, onto.name)
            self.listctl.SetItem(idx, 2, onto.label)

        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        ontology_entry.Destroy()

class OntologyEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 onto_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
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

        if not newentry:
            self.mod_date = KnDialogStaticText(panel1, gsizer, "Last Mod.-date:", "mod_date", str(self.last_modification_date))

        tmp_name = None if newentry else self.onto.name if self.onto.name is not None else ""
        self.name = KnDialogTextCtrl(panel1, gsizer, "Name: ", "name", tmp_name, enabled=enable_project)

        tmp_label = None if newentry else self.onto.label if self.onto.label is not None else ""
        self.label = KnDialogTextCtrl(panel1, gsizer, "Label: ", "label", tmp_label)

        tmp_comment = None if newentry else self.onto.comment if self.onto.comment is not None else ""
        self.comment = KnDialogTextCtrl(panel1, gsizer, "Comment: ", "comment", tmp_comment, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp_project = None if newentry else self.proj_iri_name.get(self.onto.project)
        self.project = KnDialogChoice(panel1, gsizer, "Project", "project", proj_names, tmp_project, enabled=enable_project)


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

    def get_value(self) -> Ontology:
        self.onto = Ontology(con=self.con,
                             name=self.name.get_value(),
                             label=self.label.get_value(),
                             comment=self.comment.get_value(),
                             project=self.proj_name_iri.get(self.project.get_value()))
        return self.onto

    def get_changed(self) -> Ontology:
        tmp = self.label.get_changed()
        if tmp is not None:
            self.onto.label = tmp

        tmp = self.comment.get_changed()
        if tmp is not None:
            self.onto.comment = tmp

        return self.last_modification_date, self.onto
