from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from models.helpers import Actions, BaseError, Context, Cardinality
from models.langstring import Languages, LangStringParam, LangString
from models.connection import Connection, Error
from models.project import Project
from models.listnode import ListNode
from models.group import Group
from models.user import User
from models.ontology import Ontology
from models.propertyclass import PropertyClass
from models.resourceclass import ResourceClass

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker

def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

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
        self.new_button.Bind(wx.EVT_BUTTON, self.new_entry)
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self):
        projects = Project.getAllProjects(self.con)
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

    def new_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        project_iri = self.ids[idx]
        pe = ProjectEntryDialog(self.con, project_iri, True, self)
        res = pe.ShowModal()
        if res == wx.ID_OK:
            project = pe.get_value()
            project = project.create()
            self.listctl.Append((project.shortcode,
                                 project.shortname,
                                 project.longname,
                                 project.description[Languages.EN]))
            self.ids.append(project.id)

    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        project_iri = self.ids[idx]
        pe = ProjectEntryDialog(self.con, project_iri, False, self)
        res = pe.ShowModal()
        if res == wx.ID_OK:
            project: Project = pe.get_changed()
            project.update()
            self.listctl.SetItem(idx, 0, project.shortcode)
            self.listctl.SetItem(idx, 1, project.shortname)
            self.listctl.SetItem(idx, 2, project.longname)
            self.listctl.SetItem(idx, 3, project.description[Languages.EN])

        pe.Destroy()


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
        except BaseError as knerr:
            show_error("Couldn't get information from knora", knerr)
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
        self.shortcode = KnDialogTextCtrl(panel1, gsizer, "Shortcode: ", "shortcode", tmp_shortcode, enabled=enable_shortcode)

        tmp_shortname = None if newentry else self.project.shortname if self.project.shortname is not None else ""
        self.shortname = KnDialogTextCtrl(panel1, gsizer, "Shortname: ", "shortname", tmp_shortname, enabled=enable_shortcode)

        tmp_longname = None if newentry else self.project.longname if self.project.longname is not None else ""
        self.longname = KnDialogTextCtrl(panel1, gsizer, "Longname: ", "longname", tmp_longname, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp = self.project.description.get_by_lang(Languages.EN)
        tmp_descr_en = None if newentry else tmp if tmp is not None else ""
        self.descr_en = KnDialogTextCtrl(panel1, gsizer, "Description (en): ", "descr_den", tmp_descr_en, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp = self.project.description.get_by_lang(Languages.DE)
        tmp_descr_de = None if newentry else tmp if tmp is not None else ""
        self.descr_de = KnDialogTextCtrl(panel1, gsizer, "Description (de): ", "descr_de", tmp_descr_de, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp = self.project.description.get_by_lang(Languages.FR)
        tmp_descr_fr = None if newentry else tmp if tmp is not None else ""
        self.descr_fr = KnDialogTextCtrl(panel1, gsizer, "Description (fr): ", "descr_fr", tmp_descr_fr, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp = self.project.description.get_by_lang(Languages.IT)
        tmp_descr_it = None if newentry else tmp if tmp is not None else ""
        self.descr_it = KnDialogTextCtrl(panel1, gsizer, "Description (it): ", "descr_it", tmp_descr_it, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

        tmp = self.project.description.get_by_lang()
        if tmp is not None:
            tmp_descr_ = None if newentry else tmp if tmp is not None else ""
            self.descr_ = KnDialogTextCtrl(panel1, gsizer, "Description (it): ", "descr_", tmp_descr_, size=wx.Size(200,50), style=wx.TE_MULTILINE)

        tmp_keywords = None if newentry else ', '.join(self.project.keywords) if self.project.shortname is not None else ""
        self.keywords = KnDialogTextCtrl(panel1, gsizer, "Keywords: ", "keywords", tmp_keywords, size=wx.Size(400, 70), style=wx.TE_MULTILINE)

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

    def get_value(self) -> Project:
        description = {}
        if self.descr_en.get_value():
            description[Languages.EN] = self.descr_en.get_value()
        if self.descr_de.get_value():
            description[Languages.DE] = self.descr_de.get_value()
        if self.descr_fr.get_value():
            description[Languages.FR] = self.descr_fr.get_value()
        if self.descr_it.get_value():
            description[Languages.IT] = self.descr_it.get_value()
        if description:
            self.project.description = description
        if self.keywords.get_value():
            keywords = [x.strip() for x in self.keywords.get_value().split(',')]
        self.project = Project(con=self.con,
                               shortcode=self.shortcode.get_value(),
                               shortname=self.shortname.get_value(),
                               longname=self.longname.get_value(),
                               description=description,
                               keywords=keywords,
                               status=self.status.get_value(),
                               selfjoin=self.selfjoin.get_value())
        return self.project

    def get_changed(self) -> Project:
        tmp = self.shortcode.get_changed()
        if tmp is not None:
            self.project.shortcode = tmp

        tmp = self.shortname.get_changed()
        if tmp is not None:
            self.project.shortname = tmp

        tmp = self.longname.get_changed()
        if tmp is not None:
            self.project.longname = tmp

        tmp = self.descr_en.get_changed()
        if tmp is not None:
            self.project.addDescription(Languages.EN, tmp)

        tmp = self.descr_de.get_changed()
        if tmp is not None:
            self.project.addDescription(Languages.DE, tmp)

        tmp = self.descr_fr.get_changed()
        if tmp is not None:
            self.project.addDescription(Languages.FR, tmp)

        tmp = self.descr_it.get_changed()
        if tmp is not None:
            self.project.addDescription(Languages.IT, tmp)

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


        return self.project
