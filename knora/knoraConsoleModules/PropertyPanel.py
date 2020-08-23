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
    KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText, KnDialogSuperProperties, KnDialogGuiAttributes, \
    KnDialogLangStringCtrl

def show_error(msg: str, knerr: BaseError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


reps = {
    'knora-api:Representation',
    'knora-api:AudioRepresentation',
    'knora-api:DDDRepresentation',
    'knora-api:DocumentRepresentation',
    'knora-api:MovingImageRepresentation',
    'knora-api:StillImageRepresentation',
    'knora-api:TextRepresentation',
}

ress = {
    'knora-api:Annotation',
    'knora-api:ExternalResource',
    'knora-api:Region',
    'knora-api:LinkObj'
}

knora_api_properties = {
    'hasValue': {'TextValue', 'UriValue', 'BooleanValue', 'IntValue', 'DecimalValue', 'DateValue',
                 'TimeValue', 'ListValue', 'IntervalValue', 'GeonameValue', 'GeomValue'},
    'hasLinkTo': {'#res', '#rep'},
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

gui_elements = {
    'TextValue': ['SimpleText', 'Textarea', 'Richtext'],
    'UriValue': ['SimpleText'],
    'BooleanValue': ['Checkbox'],
    'IntValue': ['SimpleText', 'Spinbox'],
    'DecimalValue': ['SimpleText', 'Slider'],
    'DateValue': ['Date'],
    'ListValue': ['Pulldown', 'List', 'Radio'],
    'IntervalValue': ['SimpleText', 'Interval'],
    'GeonameValue': ['Geonames'],
    'GeomValue': ['Geometry', 'SimpleText'],
    'ColorValue': ['Colorpicker']
}

gui_attributes = {
    'SimpleText': ['maxlength=integer', 'size=integer'],
    'Textarea': ['cols=integer', 'rows=integer', 'width=percent', 'wrap=soft|hard'],
    'Richtext': [],
    'Date': [],
    'Pulldown': ['hlist=<list-name>'],
    'Checkbox': [],
    'List': ['hlist=<list-name>'],
    'Radio': ['hlist=<list-name>'],
    'Slider': ['max=decimal', 'min=decimal'],
    'Spinbox': ['max=integer', 'max=integer'],
    'Interval': [],
    'Geonames': [],
    'Geometry': [],
    'Colorpicker': ['ncolors=integer'],
    'Searchbox': ['numprops=integer']
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
            if prop.object == 'knora-api:LinkValue':
                continue
            if 'knora-api:hasLinkToValue' in prop.superproperties:
                continue
            if 'knora-api:isPartOfValue' in prop.superproperties:
                continue
            if 'knora-api:isRegionOfValue' in prop.superproperties:
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
        dialog = PropertyEntryDialog(self.con, self.onto, None, True, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            property = dialog.get_value()
            lmd, property = property.create(self.onto.lastModificationDate)
            property.print()
            lmd2, self.onto = self.onto.read()
            self.onto.lastModificationDate = lmd
            self.listctl.Append((property.name,
                                 property.label[Languages.EN]))
            self.ids.append(property.id)
        dialog.Destroy()

    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        dialog = PropertyEntryDialog(self.con, self.onto, self.ids[idx], False, self)
        res = dialog.ShowModal()
        if res == wx.ID_OK:
            property: PropertyClass = dialog.get_changed()
            lmd, property = property.update(self.onto.lastModificationDate)
            lmd2, self.onto = self.onto.read()
            pprint(lmd)
            pprint(lmd2)
            self.onto.lastModificationDate = lmd
            self.listctl.SetItem(idx, 0, property.name)
            self.listctl.SetItem(idx, 1, property.label[Languages.EN])
        dialog.Destroy()


class PropertyEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 onto: Ontology = None,
                 pindex: int = None,
                 newentry: bool = True,
                 *args, **kw):
        """
        Create a dialog window to enter or modify a property

        :param con: Connection instance
        :param onto: The current ontology
        :param pindex: Index of the property in the list of property classes, None for a new entry
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
        # Get all ontologies beloning to the current project
        #
        self.pontos = Ontology.getProjectOntologies(con=self.con, project_id=self.onto.project)

        try:
            if newentry:
                self.property = PropertyClass(con=con, context=onto.context)
                self.last_modification_date = onto.lastModificationDate
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

        #
        # property name
        #
        tmp_name = None if newentry else self.property.name if self.property.name is not None else ""
        self.name = KnDialogTextCtrl(panel1, gsizer, "Name: ", "name", tmp_name, enabled=enable_all)

        #
        # property labels (language dependent)
        #
        if not newentry:
            tmp = self.property.label if self.property.label is not None else LangString("")
        else:
            tmp = None
        self.label = KnDialogLangStringCtrl(panel1, gsizer, "Label: ", "label", tmp, size=wx.Size(400, -1))

        #
        # property comment (language dependent)
        #
        if self.property.comment:
            print(self.property.comment._simplestring)
            pprint(self.property.comment._langstrs)
        if not newentry:
            tmp = self.property.comment if self.property.comment is not None else LangString("")
        else:
            tmp = None
        self.comment = KnDialogLangStringCtrl(panel1, gsizer, "Comment: ", "comment", tmp,
                                              size=wx.Size(400, 50), style=wx.TE_MULTILINE)

        #
        # now we process the list of super properties
        #
        if not newentry:
            tmp = [self.onto.context.reduce_iri(x) for x in self.property.superproperties]
        tmp_super = None if newentry else tmp if tmp is not None else []

        self.aproperties2 = copy.deepcopy(all_properties)
        for ponto in self.pontos:
            lmd, tmp_ponto = ponto.read()
            if tmp_ponto.property_classes is None:
                continue
            for pprop in tmp_ponto.property_classes:
                if self.aproperties2.get(tmp_ponto.name) is None:
                    self.aproperties2[tmp_ponto.name] = {}
                self.aproperties2[tmp_ponto.name][pprop.name] = {self.onto.context.reduce_iri(pprop.object)}
        self.aproperties1 = copy.deepcopy(self.aproperties2)
        del self.aproperties1['dcterms']
        del self.aproperties1['foaf']
        self.superprops = KnDialogSuperProperties(panel=panel1,
                                                  gsizer=gsizer,
                                                  label="Superproperties: ",
                                                  name="superproperties",
                                                  all_properties1=self.aproperties1,
                                                  all_properties=self.aproperties2,
                                                  value=tmp_super,
                                                  changed_cb=self.super_changed,
                                                  enabled=enable_all)

        #
        # now we process the options
        #
        objects = ['TextValue', 'ListValue', 'DateValue', 'BooleanValue', 'IntValue', 'DecimalValue',
                   'UriValue', 'GeonameValue', 'IntervalValue', 'ColorValue', 'GeomValue']

        if not newentry:
            objects = {self.property.object}
            tmp_object = self.property.object
        else:
            tmp_object = None if newentry else onto.context.reduce_iri(self.property.object, onto.name)
        self.object = KnDialogChoice(panel=panel1,
                                     gsizer=gsizer,
                                     label="Datatype (object): ",
                                     name="object",
                                     choices=list(objects),
                                     value=tmp_object,
                                     changed_cb=self.object_changed,
                                     enabled=enable_all)

        object = onto.context.reduce_iri(self.object.get_value())
        objects = [k for k, v in gui_elements.items()]
        if object is not None:
            if object in objects:
                choices = gui_elements[object]
            else:
                choices = ['Searchbox']
        else:
            choices = []
        if not newentry:
            if self.property.gui_element is not None:
                tmp = self.onto.context.reduce_iri(self.property.gui_element)
            else:
                tmp = ""
        else:
            tmp = None
        self.gui_element = KnDialogChoice(panel=panel1,
                                          gsizer=gsizer,
                                          label="GUI Element: ",
                                          name="gui_element",
                                          choices=choices,
                                          value=tmp,
                                          changed_cb=self.gui_element_changed,
                                          enabled=enable_all)

        gele = self.gui_element.get_value()
        rootnodes = ListNode.getAllLists(con=self.con, project_iri=onto.project)
        lists = [x.label[Languages.EN] for x in rootnodes]
        if not newentry:
            tmp = self.property.gui_attributes
        else:
            tmp = None
        self.gui_attributes = KnDialogGuiAttributes(panel=panel1,
                                                    gsizer=gsizer,
                                                    label="GUI Attributes: ",
                                                    name="gui_attribute",
                                                    gui_element=gele,
                                                    all_attributes=gui_attributes,
                                                    all_lists=lists,
                                                    value=tmp,
                                                    enabled=enable_all)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        self.topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(self.topsizer)

    def expand_res_rep(self, object_set: Set[str]):
        if '#res' in object_set:
            object_set.remove('#res')
            object_set.update({x.split(':')[1] for x in ress})
            for ponto in self.pontos:
                lmd, fullonto = ponto.read()
                prefix = ':' if fullonto.name == self.onto.name else fullonto.name + ':'
                reslist = [prefix + x.name for x in fullonto.resource_classes]
                object_set.update(reslist)
        if '#rep' in object_set:
            object_set.remove('#rep')
            for ponto in self.pontos:
                lmd, fullonto = ponto.read()
                prefix = ':' if fullonto.name == self.onto.name else fullonto.name + ':'
                reslist = [prefix + x.name for x in fullonto.resource_classes if len(set(x.superclasses) & reps) > 0]
                object_set.update(reslist)

    def super_changed(self, event: wx.Event, user_data: Any):
        object_set = None
        for prefix, super in user_data:
            if object_set is None:
                object_set = self.aproperties2[prefix][super]
                self.expand_res_rep(object_set)
                print(object_set)
            else:
                tmp = self.aproperties2[prefix][super]
                self.expand_res_rep(tmp)
                object_set = object_set & tmp
                print(self.aproperties2[prefix][super])
                print(object_set)
        self.object.set_choices(list(object_set))

    def object_changed(self, event, object):
        print('object changed!')
        objects = [k for k, v in gui_elements.items()]
        if object in objects:
            choices = gui_elements[object]
        else:
            choices = ['Searchbox']
        self.gui_element.set_choices(choices)

    def gui_element_changed(self, event, gele):
        print('gui_element changed!:', gele)
        self.gui_attributes.set_gui_element(gele)
        pass

    def resize(self):
        self.SetSizerAndFit(self.topsizer)

    def get_value(self) -> PropertyClass:
        superproperties = [x[0] + ':' + x[1] for x in self.superprops.get_value()]
        gui_element = 'salsah-gui:' + self.gui_element.get_value()

        self.propertyclass = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name=self.name.get_value(),
            label=self.label.get_value(),
            comment=self.comment.get_value(),
            ontology_id=self.onto.id,
            superproperties=superproperties,
            object=self.object.get_value(),
            gui_element=gui_element,
            gui_attributes=self.gui_attributes.get_value()
        )
        self.propertyclass.print()
        return self.propertyclass

    def get_changed(self) -> PropertyClass:
        tmp = self.label.get_changed()
        if tmp is not None:
            self.property.label = tmp
        tmp = self.comment.get_changed()
        if tmp is not None:
            self.property.comment = tmp
        return self.property
