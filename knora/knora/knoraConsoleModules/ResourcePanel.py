from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint
import copy

from knora.models.helpers import Actions, BaseError, Context, Cardinality, LastModificationDate
from knora.models.langstring import Languages, LangStringParam, LangString
from knora.models.connection import Connection, Error
from knora.models.project import Project
from knora.models.listnode import ListNode
from knora.models.group import Group
from knora.models.user import User
from knora.models.ontology import Ontology
from knora.models.propertyclass import PropertyClass
from knora.models.resourceclass import ResourceClass, HasProperty

from knora.knoraConsoleModules.KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogChoiceArr, \
    KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText, KnDialogSuperResourceClasses, KnDialogGuiAttributes, \
    KnDialogLangStringCtrl, KnDialogHasProperty, PropertyStatus


def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + str(knerr),
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

        self.reslist = wx.ListCtrl(self,
                                   name="resources",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)

        self.reslist.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.reslist.AppendColumn("Label", width=wx.LIST_AUTOSIZE)
        self.reslist.AppendColumn("Derived from", width=wx.LIST_AUTOSIZE)

        for cnt, res in enumerate(onto.resource_classes):
            supers = [onto.context.reduce_iri(x) for x in res.superclasses]
            self.reslist.Append((res.name, res.label[Languages.EN], ", ".join(supers)))

        topsizer.Add(self.reslist, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

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

    def new_entry(self, event):
        dialog = ResourceClassEntryDialog(self.con, self.onto, None, True, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            resourceclass = dialog.get_value()
            index, resourceclass = self.onto.addResourceClass(resourceclass=resourceclass, create=True)
            self.reslist.Append((resourceclass.name,
                                 resourceclass.label[Languages.EN]))
        dialog.Destroy()

    def edit_entry(self, event):
        idx = self.reslist.GetFirstSelected()
        dialog = ResourceClassEntryDialog(self.con, self.onto, idx, False, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            resourceclass: ResourceClass = dialog.get_changed()
            resource_class = self.onto.updateResourceClass(idx, resourceclass)
            #lmd, resourceclass = resourceclass.update(self.onto.lastModificationDate)
            #lmd2, self.onto = self.onto.read()
            #self.onto.lastModificationDate = lmd
            self.reslist.SetItem(idx, 0, resourceclass.name)
            self.reslist.SetItem(idx, 1, resourceclass.label[Languages.EN])
        dialog.Destroy()

    def delete_entry(self, event):
        idx = self.reslist.GetFirstSelected()
        dlg = wx.MessageDialog(parent=self,
                               message="Do You really want to delete this resource?",
                               caption="Delete ?",
                               style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            try:
                self.onto.removeResourceClass(index=idx, erase=True)
                self.reslist.DeleteItem(idx)
            except BaseError as err:
                show_error("Couldn't delete resource class", err)



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

        if self.resourceclass.has_properties is not None and len(self.resourceclass.has_properties) > 0:
            link_value_props = {propclass.id for propclass in onto.property_classes
                                if propclass.object == 'knora-api:LinkValue' or
                                'knora-api:hasLinkToValue' in propclass.superproperties or
                                'knora-api:isPartOfValue' in propclass.superproperties or
                                'knora-api:isRegionOfValue' in propclass.superproperties}

            value = { name: {'cardinality': hasprop.cardinality, 'gui_order': hasprop.gui_order, 'status': PropertyStatus.UNCHANGED}
                      for (name, hasprop) in self.resourceclass.has_properties.items()
                      if hasprop.ptype == HasProperty.Ptype.other and
                      onto.context.get_qualified_iri(hasprop.property_id) not in link_value_props }
        else:
            value = {}

        #
        # Get all ontologies belonging to the current project
        #
        self.pontos = Ontology.getProjectOntologies(con=self.con, project_id=self.onto.project)

        #
        # collect all properties from all omtologies in this project  ToDo: properties from shared ontologies
        #
        self.all_props: List[str] = []
        for ponto in self.pontos:
            lmd, tmp_ponto = ponto.read()
            if tmp_ponto.property_classes is None:
                continue
            for pprop in tmp_ponto.property_classes:
                if pprop.object == 'knora-api:LinkValue':
                    continue
                if 'knora-api:hasLinkToValue' in pprop.superproperties:
                    continue
                if 'knora-api:isPartOfValue' in pprop.superproperties:
                    continue
                if 'knora-api:isRegionOfValue' in pprop.superproperties:
                    continue
                self.all_props.append(tmp_ponto.name + ':' + pprop.name)
        self.has_properties_ctrl = KnDialogHasProperty(panel=panel1,
                                                       gsizer=gsizer,
                                                       label="Has properties: ",
                                                       name="has_properties",
                                                       all_props=self.all_props,
                                                       value=value)
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
        tmp = self.has_properties_ctrl.get_changed()
        if tmp:
            for propname, propinfo in tmp:
                if propinfo['status'] == PropertyStatus.CHANGED:
                    self.resourceclass.updateProperty()
        print('++++++++++++++++++++++++++++++++')
        pprint(tmp)
        print('++++++++++++++++++++++++++++++++')
        return self.resourceclass
