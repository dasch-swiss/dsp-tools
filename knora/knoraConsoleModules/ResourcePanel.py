from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint
import copy

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

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogChoiceArr, \
    KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText, KnDialogSuperResourceClasses, KnDialogGuiAttributes, \
    KnDialogLangStringCtrl


def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

permissions = {
    'RV': 'restricted view',
    'V': 'view',
    'M': 'modify',
    'D': 'delete',
    'CR': 'change rights'
}

knora_api_resclasses = {
    'Resource',
    'Representation',
    'AudioRepresentation',
    'DDDRepresentation',
    'DocumentRepresentation',
    'MovingImageRepresentation',
    'StillImageRepresentation',
    'TextRepresentation',
    'Annotation',
    'ExternalResource',
    'Region',
    'LinkObj'
}

dcterm_classes = {
    'Agent',
    'AgentClass',
    'BibliographicResource',
    'FileFormat',
    'Frequency',
    'Jurisdiction',
    'LicenseDocument',
    'LinguisticSystem',
    'Location',
    'LocationPeriodOrJurisdiction',
    'MediaType',
    'MediaTypeOrExtent',
    'MethodOfAccrual',
    'MethodOfInstruction',
    'PeriodOfTime',
    'PhysicalMedium',
    'PhysicalResource',
    'Policy',
    'ProvenanceStatement',
    'RightsStatement',
    'SizeOrDuration',
    'Standard'
}

dcmi_classes = {
    'Collection',
    'Dataset',
    'Event',
    'Image',
    'InteractiveResource',
    'MovingImage',
    'PhysicalObject',
    'Service',
    'Software',
    'Sound',
    'StillImage',
    'Text'
}

foaf_classes = {
    'Agent',
    'Document',
    'Group',
    'Image',
    'Organization',
    'Person',
    'OnlineAccount',
    'PersonalProfileDocument',
    'Project',
    'LabelProperty',
    'OnlineChatAccount',
    'OnlineEcommerceAccount',
    'OnlineGamingAccount'
}

all_classes = {
    'knora-api': knora_api_resclasses,
    'dcterms': dcterm_classes,
    'dcmi': dcmi_classes,
    'foaf': foaf_classes
}


class ResourcePanel(wx.Window):
    def __init__(self,
                 con: Connection = None,
                 onto: Ontology = None,
                 *args, **kw):
        super().__init__(*args, **kw)

        self.con = con
        self.onto = onto
        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.ids: List[int] = []
        self.reslist = wx.ListCtrl(self,
                                   name="resources",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)

        self.reslist.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.reslist.AppendColumn("Label", width=wx.LIST_AUTOSIZE)
        self.reslist.AppendColumn("Derived from", width=wx.LIST_AUTOSIZE)

        for cnt, res in enumerate(onto.resource_classes):
            supers = [onto.context.reduce_iri(x) for x in res.superclasses]
            self.reslist.Append((res.name, res.label[Languages.EN], ", ".join(supers)))
            self.ids.append(cnt)

        topsizer.Add(self.reslist, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

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

    def new_entry(self, event):
        dialog = ResourceClassEntryDialog(self.con, self.onto, None, True, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            resourceclass = dialog.get_value()
            lmd, resourceclass = resourceclass.create(self.onto.lastModificationDate)
            resourceclass.print()
            lmd2, self.onto = self.onto.read()
            self.onto.lastModificationDate = lmd
            self.reslist.Append((resourceclass.name,
                                 resourceclass.label[Languages.EN]))
            self.ids.append(resourceclass.id)
        dialog.Destroy()

    def edit_entry(self, event):
        idx = self.reslist.GetFirstSelected()
        dialog = ResourceClassEntryDialog(self.con, self.onto, self.ids[idx], False, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            resourceclass: ResourceClass = dialog.get_changed()
            lmd, resourceclass = resourceclass.update(self.onto.lastModificationDate)
            lmd2, self.onto = self.onto.read()
            pprint(lmd)
            pprint(lmd2)
            self.onto.lastModificationDate = lmd
            self.reslist.SetItem(idx, 0, resourceclass.name)
            self.reslist.SetItem(idx, 1, resourceclass.label[Languages.EN])
        dialog.Destroy()

class ResourceClassEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 onto: Ontology = None,
                 rindex: int = None,
                 newentry: bool = True,
                 *args, **kw):
        """
        Create a dialog window to enter or modify a property

        :param con: Connection instance
        :param onto: The current ontology
        :param rindex: Index of the resource in the list of resource classes
        :param newentry: True, if we want to enter a new property
        :param args:
        :param kw:
        """
        super().__init__(*args, **kw,
                         title="Property Entry",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.con = con
        lmd, self.onto = onto.read()

        #
        # Get all ontologies belonging to the current project
        #
        self.pontos = Ontology.getProjectOntologies(con=self.con, project_id=self.onto.project)

        try:
            if newentry:
                self.resourceclass = ResourceClass(con=con, context=onto.context)
                self.last_modification_date = onto.lastModificationDate
            else:
                self.resourceclass = onto.resource_classes[rindex]
        except BaseError as knerr:
            show_error("Couldn't get information from knora", knerr)
            return

        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
            enable_all = True
        else:
            cols = 3
            enable_all = False
        gsizer = wx.FlexGridSizer(cols=cols)

        #
        # resource class name
        #
        tmp_name = None if newentry else self.resourceclass.name if self.resourceclass.name is not None else ""
        self.name = KnDialogTextCtrl(panel1, gsizer, "Name: ", "name", tmp_name, enabled=enable_all)

        #
        # resource class labels (language dependent)
        #
        if not newentry:
            tmp = self.resourceclass.label if self.resourceclass.label is not None else LangString("")
        else:
            tmp = None
        self.label = KnDialogLangStringCtrl(panel1, gsizer, "Label: ", "label", tmp, size=wx.Size(400, -1))

        #
        # property comment (language dependent)
        #
        if self.resourceclass.comment:
            print(self.resourceclass.comment._simplestring)
            pprint(self.resourceclass.comment._langstrs)
        if not newentry:
            tmp = self.resourceclass.comment if self.resourceclass.comment is not None else LangString("")
        else:
            tmp = None
        self.comment = KnDialogLangStringCtrl(panel1, gsizer, "Comment: ", "comment", tmp,
                                              size=wx.Size(400, 50), style=wx.TE_MULTILINE)

        #
        # now we process the list of super resource classes
        #
        if not newentry:
            tmp = [self.onto.context.reduce_iri(x) for x in self.resourceclass.superclasses]
        tmp_super = None if newentry else tmp if tmp is not None else []

        self.aclasses2 = copy.deepcopy(all_classes)
        for ponto in self.pontos:
            lmd, tmp_ponto = ponto.read()
            if tmp_ponto.resource_classes is None:
                continue
            for pres in tmp_ponto.resource_classes:
                if self.aclasses2.get(tmp_ponto.name) is None:
                    self.aclasses2[tmp_ponto.name] = set()
                self.aclasses2[tmp_ponto.name].add(pres.name)
        self.aclasses1 = copy.deepcopy(self.aclasses2)
        del self.aclasses1['dcterms']
        del self.aclasses1['dcmi']
        del self.aclasses1['foaf']
        self.superclasses = KnDialogSuperResourceClasses(panel=panel1,
                                                         gsizer=gsizer,
                                                         label="Superclasses: ",
                                                         name="superclasses",
                                                         all_resourceclasses1=self.aclasses1,
                                                         all_resourceclasses=self.aclasses2,
                                                         value=tmp_super,
                                                         changed_cb=self.super_changed,
                                                         enabled=enable_all)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        self.topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(self.topsizer)

    def super_changed(self, event: wx.Event, user_data: Any):
        pass

    def resize(self):
        self.SetSizerAndFit(self.topsizer)

    def get_value(self) -> ResourceClass:
        superclasses = [x[0] + ':' + x[1] for x in self.superclasses.get_value()]

        self.resourceclass = ResourceClass(
            con=self.con,
            context=self.onto.context,
            name=self.name.get_value(),
            label=self.label.get_value(),
            comment=self.comment.get_value(),
            ontology_id=self.onto.id,
            superclasses=superclasses
        )
        return self.resourceclass

    def get_changed(self) -> ResourceClass:
        tmp = self.label.get_changed()
        if tmp is not None:
            self.resourceclass.label = tmp
        tmp = self.comment.get_changed()
        if tmp is not None:
            self.resourceclass.comment = tmp
        return self.resourceclass
