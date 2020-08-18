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

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogChoiceArr, \
    KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText, KnDialogSuperProperties

def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


resp = {
    'Representation',
    'AudioRepresentation',
    'DDDRepresentation',
    'DocumentRepresentation',
    'MovingImageRepresentation',
    'StillImageRepresentation',
    'TextRepresentation',
}

knora_api_properties = {
    'hasValue': {'TextValue', 'UriValue', 'BooleanValue', 'IntValue', 'DecimalValue', 'DateValue',
                 'TimeValue', 'ListValue', 'IntervalValue', 'GeonameValue', 'GeomValue'},
    'hasLinkTo': {'#res'},
    'hasRepresentation': {'#rep'},
    'isPartOf': {'#res'},
    'seqnum': {'IntValue'},
    'hasColor': {'ColorValue'},
    'hasComment': {'TextValue'},
    'hasGeometry': {'GeomValue'},
    'isRegionOf': {'#rep'},
    'isAnnotationOf': {'#res'}
}

dcterms_properties = {
    'abstract': {'TextValue'},
    'accessRights': {'TextValue'},
    'accrualMethod': {'TextValue', 'UriValue', 'ListValue'},
    'accrualPeriodicity': {'TextValue', 'UriValue', 'ListValue'},
    'accrualPolicy': {'TextValue', 'UriValue', 'ListValue'},
    'alternative': {'TextValue'},
    'audience': {'TextValue', 'UriValue', 'ListValue', '#res'},
    'available': {'TextValue', 'DateValue'},
    'bibliographicCitation': {'TextValue', '#res'},
    'conformsTo': {'TextValue', 'UriValue', 'ListValue'},
    'contributor': {'TextValue', 'UriValue', 'ListValue', '#res'},
    'coverage': {'TextValue', 'UriValue', 'ListValue', '#res'},
    'created': {'TextValue', 'DateValue'},
    'creator': {'TextValue', 'UriValue', '#res'},
    'date': {'TextValue', 'DateValue'},
    'dateAccepted': {'TextValue', 'DateValue'},
    'dateCopyrighted': {'TextValue', 'DateValue'},
    'dateSubmitted': {'TextValue', 'DateValue'},
    'description': {'TextValue'},
    'educationLevel': {'TextValue', 'UriValue', 'ListValue', '#res'},
    'extent': {'TextValue'},
    'format': {'TextValue','ListValue'},
    'hasFormat': {'#res'},
    'hasPart': {'#res'},
    'hasVersion': {'#res'},
    'identifier': {'TextValue', 'UriValue'},
    'instructionalMethod': {'TextValue', 'UriValue', '#res'},
    'isFormatOf': {'#res'},
    'isPartOf': {'#res'},
    'isReferencedBy': {'#res'},
    'isReplacedBy': {'#res'},
    'isRequiredBy': {'#res'},
    'issued': {'TextValue', 'DateValue'},
    'isVersionOf': {'#res'},
    'language': {'TextValue','ListValue'},
    'license': {'TextValue', 'UriValue', '#res'},
    'mediator': {'UriValue', '#res'},
    'medium': {'TextValue', 'UriValue', '#res'},
    'modified': {'TextValue', 'DateValue'},
    'provenance': {'TextValue', 'UriValue', '#res'},
    'publisher': {'TextValue', 'UriValue', '#res'},
    'references': {'#res'},
    'relation': {'TextValue', 'UriValue', '#res'},
    'replaces': {'#res'},
    'requires': {'#res'},
    'rights': {'TextValue', 'UriValue', '#res'},
    'rightsHolder': {'TextValue', 'UriValue', '#res'},
    'source': {'TextValue', 'UriValue', '#res'},
    'spatial': {'TextValue', 'GeonameValue'},
    'subject': {'TextValue', 'UriValue', '#res'},
    'tableOfContents': {'TextValue', 'UriValue', '#res'},
    'temporal': {'TextValue', 'IntervalValue', 'DateValue'},
    'title': {'TextValue'},
    'type': {'TextValue', 'ListValue'},
    'valid': {'TextValue', 'DateValue'},
}

foaf_properties = {
    'homepage': {'UriValue'},
    'isPrimaryTopicOf': {'TextValue', 'UriValue', '#res'},
    'knows': {'TextValue', 'UriValue', '#res'},
    'made': {'TextValue', 'UriValue', '#res'},
    'maker': {'TextValue', 'UriValue', '#res'},
    'mbox': {'UriValue'},
    'member': {'TextValue', 'UriValue', '#res'},
    'page': {'TextValue', 'UriValue', '#rep'},
    'primaryTopic': {'TextValue', 'UriValue', '#rep'},
    'weblog': {'TextValue', 'UriValue', '#rep'},
    'account': {'TextValue', 'UriValue', '#res'},
    'accountName': {'TextValue'},
    'accountServiceHomepage': {'TextValue', 'UriValue', '#rep'},
    'aimChatID': {'TextValue'},
    'based_near': {'TextValue', 'GeonameValue'},
    'currentProject': {'TextValue', 'UriValue', '#res'},
    'depiction': {'TextValue', 'UriValue', '#rep'},
    'depicts': {'TextValue', 'UriValue', '#res'},
    'familyName': {'TextValue'},
    'firstName': {'TextValue'},
    'focus': {'TextValue', 'UriValue', '#res'},
    'gender': {'TextValue', 'ListValue'},
    'givenName': {'TextValue'},
    'icqChatID': {'TextValue'},
    'img': {'#rep'},
    'interest': {'TextValue', 'UriValue', '#rep'},
    'jabberID': {'TextValue'},
    'lastName': {'TextValue'},
    'logo': {'TextValue', 'UriValue', '#res'},
    'mbox_sha1sum': {'TextValue'},
    'msnChatID': {'TextValue'},
    'myersBriggs': {'TextValue'},
    'name': {'TextValue'},
    'nick': {'TextValue'},
    'openid': {'TextValue'},
    'pastProject': {'TextValue', 'UriValue', '#res'},
    'phone': {'TextValue', 'UriValue'},
    'plan': {'TextValue'},
    'publications': {'TextValue', 'UriValue', '#rep'},
    'schoolHomepage': {'TextValue', 'UriValue', '#rep'},
    'skypeID': {'TextValue'},
    'thumbnail': {'#rep'},
    'tipjar': {'TextValue', 'UriValue', '#rep'},
    'title': {'TextValue'},
    'topic': {'TextValue', 'UriValue', '#res'},
    'topic_interest': {'TextValue', 'UriValue', '#rep'},
    'workInfoHomepage': {'TextValue', 'UriValue', '#rep'},
    'workplaceHomepage': {'TextValue', 'UriValue', '#rep'},
    'yahooChatID': {'TextValue'},
    'age': {'TextValue', 'IntValue'},
    'birthday': {'TextValue', 'DateValue'},
    'membershipClass': {'TextValue', 'UriValue', '#res'},
    'sha1':  {'TextValue', 'UriValue', '#rep'},
    'status': {'TextValue', 'ListValue'},
    'dnaChecksum': {'TextValue'},
    'family_name': {'TextValue'},
    'fundedBy': {'TextValue', 'UriValue', '#res'},
    'geekcode': {'TextValue'},
    'givenname': {'TextValue'},
    'holdsAccount': {'TextValue', 'UriValue', '#res'},
    'surname': {'TextValue'},
    'theme': {'TextValue', 'UriValue', '#res'}
}

all_properties = {
    'knora-api': knora_api_properties,
    'dcterms': dcterms_properties,
    'foaf': foaf_properties
}

class PropertyPanel(wx.Window):
    def __init__(self,
                 con: Connection = None,
                 onto: Ontology = None,
                 *args, **kw):
        super().__init__(*args, **kw)

        self.con = con
        self.onto = onto
        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.ids: List[int] = []
        self.listctl = wx.ListCtrl(self,
                                   name="properties",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)

        self.listctl.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Label", width=wx.LIST_AUTOSIZE)
        for cnt, prop in enumerate(onto.property_classes):
            if 'knora-api:hasLinkToValue' in prop.superproperties:
                continue
            self.listctl.Append((prop.name, prop.label[Languages.EN]))
            self.ids.append(cnt)

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

    def new_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        dialog = PropertyEntryDialog(self.con, self.onto, self.ids[idx], True, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            property = dialog.get_value()
            property = property.create()
            self.listctl.Append((property.name,
                                 property.label))
            self.ids.append(property.id)

    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        dialog = PropertyEntryDialog(self.con, self.onto, self.ids[idx], False, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            property: PropertyClass = dialog.get_changed()
            property.update()
            self.listctl.SetItem(idx, 0, property.name)
            self.listctl.SetItem(idx, 1, property.label)

        dialog.Destroy()


class PropertyEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 onto: Ontology = None,
                 pindex: int = None,
                 newentry: bool = True,
                 *args, **kw):
        super().__init__(*args, **kw,
                         title="Property Entry",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.con = con
        try:
            if newentry:
                self.property = PropertyClass(con=con, context=onto.context)
                self.last_modification_date = None
            else:
                self.property = onto.property_classes[pindex]
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

        tmp_name = None if newentry else self.property.name if self.property.name is not None else ""
        self.name = KnDialogTextCtrl(panel1, gsizer, "Name: ", "name", tmp_name)

        if not newentry:
            tmp = self.property.label.get_by_lang(Languages.EN)
        tmp_label_en = None if newentry else tmp if tmp is not None else ""
        self.label_en = KnDialogTextCtrl(panel1, gsizer, "Label (en): ", "label_en", tmp_label_en)

        if not newentry:
            tmp = self.property.label.get_by_lang(Languages.DE)
        tmp_label_de = None if newentry else tmp if tmp is not None else ""
        self.label_de = KnDialogTextCtrl(panel1, gsizer, "Label (de): ", "label_de", tmp_label_de)

        if not newentry:
            tmp = self.property.label.get_by_lang(Languages.FR)
        tmp_label_fr = None if newentry else tmp if tmp is not None else ""
        self.label_fr = KnDialogTextCtrl(panel1, gsizer, "Label (fr): ", "label_fr", tmp_label_fr)

        if not newentry:
            tmp = self.property.label.get_by_lang(Languages.IT)
        tmp_label_it = None if newentry else tmp if tmp is not None else ""
        self.label_it = KnDialogTextCtrl(panel1, gsizer, "Label (it): ", "label_it", tmp_label_it)

        super_properties = ['hasValue', 'hasLinkTo', 'isPartOf', 'seqnum', 'hasColor', 'hasComment',
                            'hasGeometry', 'isRegionOf', 'isAnnotationOf', 'other']
        # ToDo: if "hasLinkTo", "isPartOf", "isRegionOf" is selected/deselected, adjust choices of "object"!

        #if not newentry:
        #    tmp_super_prop = None if newentry else [onto.context.reduce_iri(x) for x in self.property.superproperties]
        #else:
        #    tmp_super_prop = None
        #self.superpops_choice = KnDialogChoiceArr(panel1, gsizer, "Superproperties", "superproperties",
        #                                      super_properties, tmp_super_prop, enabled=enable_all, changed_cb=self.super_changed)
        prefixes = ['knora-api']
        #tmp = Ontology.getProjectOntologies(con=self.con, project_id=onto.project)
        #if tmp:
        #    project_ontoprefixes = [x.name for x in tmp]
        #    prefixes.extend(project_ontoprefixes)
        #tmp = Ontology.getProjectOntologies(con=self.con, project_id="http://www.knora.org/ontology/knora-admin#SystemProject")
        #if tmp:
        #    shared_ontoprefixes = [x.name for x in tmp]
        #    prefixes.extend(shared_ontoprefixes)

        pprint(prefixes)
        self.superprops = KnDialogSuperProperties(panel=panel1,
                                                  gsizer=gsizer,
                                                  label="Superproperties",
                                                  name="superproperties",
                                                  all_properties=all_properties)

        objects = ['TextValue', 'ListValue', 'DateValue', 'BooleanValue', 'IntValue', 'DecimalValue',
                   'UriValue', 'GeonameValue', 'IntervalValue', 'ColorValue', 'GeomValue']

        if not newentry:
            superproperties = [onto.context.reduce_iri(x) for x in self.property.superproperties]
            if "hasLinkTo" in superproperties or "isPartOf" in superproperties or \
                "isRegionOf" in superproperties or "isAnnotationOf" in superproperties:
                res = [':' + x.name for x in onto.resource_classes]
                objects.extend(res)
                objects.append('other')
        tmp_object = None if newentry else onto.context.reduce_iri(self.property.object, onto.name)
        self.object = KnDialogChoice(panel1, gsizer, "Datatype (object)", "object",
                                              objects, tmp_object, enabled=enable_all)
        # ToDo: Add other option with selection of prefix and resname

        gui_elements = {
            'TextValue': ['SimpleText', 'Textarea', 'Richtext'],
            'UriValue': ['SimpleText'],
            'BooleanValue': ['Checkbox'],
            'IntValue': ['SimpleText', 'Spinbox'],
            'DecimalValue': ['SimpleText', 'Slider'],
            'DateValue': ['Date'],
            'ListValue': ['Pulldown', 'List', 'Radio'],
            'hasLinkTo': ['Searchbox'],
            'IntervalValue': ['SimpleText', 'Interval'],
            'GeonameValue': ['Geonames'],
            'GeomValue': ['Geometry', 'SimpleText']
        }



        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        self.topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(self.topsizer)

    def super_changed(self, event: wx.Event):
        print('gagagagagagagagagg')
        pprint(self)
        pprint(event)


    def resize(self):
        self.SetSizerAndFit(self.topsizer)

    def get_value(self) -> PropertyClass:
        pass

    def get_changed(self) -> PropertyClass:
        pass
