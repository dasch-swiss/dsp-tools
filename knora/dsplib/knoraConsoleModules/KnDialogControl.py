from typing import Any, Union, List, Set, Dict, Tuple, Optional, Callable, TypedDict

import wx
import wx.grid

from pprint import pprint
from copy import deepcopy
from enum import Enum, unique


from wx.lib.itemspicker import ItemsPicker, \
                               EVT_IP_SELECTION_CHANGED, \
                               IP_SORT_CHOICES, IP_SORT_SELECTED,\
                               IP_REMOVE_FROM_CHOICES
import wx.lib.scrolledpanel

from ..models.langstring import Languages, LangStringParam, LangString
from ..models.helpers import Cardinality, BaseError
from ..widgets.doublepassword import DoublePasswordCtrl


def show_error(message: str, err: BaseError) -> None:
    dlg = wx.MessageDialog(None,
                           message=message + "\n" + err.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


@unique
class PropertyStatus(Enum):
    UNCHANGED = "(unchanged)"
    CHANGED = "(changed)"
    NEW = "(new)"
    DELETED = "(deleted)"


class HasPropertyInfo(TypedDict):
    """
    Each ResourceClass instance has a member variable that holds a list of the properties
    this must/should have (implemented in triplestore using cardinality restrictions). In Addition
    the gui_order is defined which gives the GUI hints in which order the data fields should
    be displayed. Thus this is kind of a "case-class" and type defintion for typing
    """
    cardinality: Cardinality  # see knora/models/helper.py
    gui_order: int
    status: PropertyStatus


class ItemsPickerDialog(wx.Dialog):
    """
    A Class that implements a picker dialog, that is a dialog with available options
    on the left and selectd options on the right. We can add/remove options by shifting
    from right to left or vice versa.
    """
    def __init__(self,
                 parent: wx.Window,
                 titlestr: str = 'TITEL',
                 leftstr: str = 'LEFT',
                 rightstr: str = 'RIGHT',
                 available: List[str] = [],
                 chosen: List[str] = [],
                 ipStyle = IP_REMOVE_FROM_CHOICES):
        super().__init__(
            parent=parent,
            title=titlestr,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ip = ItemsPicker(self,
                              choices=available,
                              label=leftstr,
                              selectedLabel=rightstr,
                              ipStyle=ipStyle)
        self.ip.SetSelections(chosen)
        #self.ip.Bind(EVT_IP_SELECTION_CHANGED, self.OnSelectionChange)
        self.ip._source.SetMinSize((-1,150))

        sizer.Add(self.ip, 0, wx.ALL, 10)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(sizer)

    def GetSelections(self) -> List[str]:
        return self.ip.GetSelections()

    def GetItems(self) -> List[str]:
        return self.ip.GetItems()


class KnDialogControl:
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 control: wx.Control,
                 newentry: bool = False,
                 changed_cb: Optional[Callable[[wx.Event, Optional[Any]], None]] = None,
                 reset_cb: Optional[Callable[[wx.Event], None]] = None):
        self.label = wx.StaticText(panel, label=label)
        self.control = control
        self.newentry = newentry
        self.changed_cb = changed_cb
        self.reset_cb = reset_cb

        if not newentry:
            self.undo = wx.Button(panel, label="X", size=wx.Size(25, -1))
            self.undo.Bind(wx.EVT_BUTTON, self.reset_ctrl)
            self.undo.Disable()
        else:
            self.undo = None
        gsizer.Add(self.label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(self.control, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        if not newentry:
            gsizer.Add(self.undo, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

    def control_changed(self, event: wx.Event, user_data: Any = None):
        if not self.newentry:
            self.undo.Enable()
        if self.changed_cb is not None:
            self.changed_cb(event, user_data)

    def reset_ctrl(self, event):
        if not self.newentry:
            self.undo.Disable()
        if self.reset_cb is not None:
            self.reset_cb(event)

    def get_changed(self):
        return None

class KnDialogStaticText(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 value: Optional[str] = None,
                 style: int = 0):
        self.static_text = wx.StaticText(panel,
                                         name=name,
                                         label=value if value is not None else "",
                                         style=style)
        super().__init__(panel, gsizer, label, name, self.static_text, True if value is None else False)


class KnDialogTextCtrl(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 value: Optional[str] = None,
                 size: wx.Size = wx.DefaultSize,
                 style: int = 0,
                 password: bool = False,
                 enabled: bool = True,
                 validator: Optional[wx.Validator] = wx.DefaultValidator,
                 changed_cb: Optional[Callable[[wx.Event, Optional[Any]], None]] = None):
        self.orig_value = value
        if password:
            self.text_ctrl = DoublePasswordCtrl(panel,
                                                name=name,
                                                value=value if value is not None else "",
                                                size=wx.Size(200, -1) if size != wx.DefaultSize else size,
                                                style=style,
                                                validator=validator)
        else:
            self.text_ctrl = wx.TextCtrl(panel,
                                         name=name,
                                         value=value if value is not None else "",
                                         size=wx.Size(200, -1) if size != wx.DefaultSize else size,
                                         style=style,
                                         validator=validator)

        self.text_ctrl.Bind(wx.EVT_TEXT, self.text_changed)
        if not enabled:
            self.text_ctrl.Disable()
        super().__init__(panel, gsizer, label, name, self.text_ctrl, True if value is None else False, changed_cb)

    def text_changed(self, event) -> None:
        super().control_changed(event)

    def reset_ctrl(self, event) -> None:
        self.text_ctrl.SetValue(self.orig_value)
        super().reset_ctrl(event)

    def set_value(self, value: Optional[str]) -> None:
        self.text_ctrl.SetValue(value if value else "")
        self.orig_value = value
        if self.undo:
            self.undo.Disable()

    def get_value(self):
        value = self.text_ctrl.GetValue()
        return value if value else None

    def get_changed(self):
        new_value = self.text_ctrl.GetValue()
        if self.orig_value == new_value:
            return None
        else:
            return new_value

    def SetValidator(self, validator: wx.Validator = wx.DefaultValidator):
        self.text_ctrl.SetValidator(validator)


class KnDialogLangStringCtrl(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 value: Optional[LangString] = None,
                 size: Optional[wx.Size] = None,
                 style=None,
                 enabled: bool = True,
                 validator: Optional[wx.Validator] = None):
        self.orig_value = value

        self.container = wx.Panel(panel, style=wx.BORDER_SIMPLE)
        #self.winsizer = wx.BoxSizer(wx.VERTICAL)
        self.winsizer = wx.FlexGridSizer(cols=2)
        self.text_ctrl: Dict[Languages, wx.TextCtrl] = {}

        if value is not None:
            langlabel = 'No lang:'
            self.no_langlabel = wx.StaticText(self.container, label=langlabel)
            self.winsizer.Add(self.no_langlabel)
            value_no = value.get_by_lang() if value is not None else None
            if style is None:
                if validator is None:
                    self.text_ctrl_no = wx.TextCtrl(self.container,
                                                    name=name,
                                                    value=value_no if value_no is not None else "",
                                                    size=wx.Size(200, -1) if size is None else size)
                else:
                    self.text_ctrl_no = wx.TextCtrl(self.container,
                                                    name=name,
                                                    value=value_no if value_no is not None else "",
                                                    size=wx.Size(200, -1) if size is None else size,
                                                    validator=validator)
            else:
                if validator is None:
                    self.text_ctrl_no = wx.TextCtrl(self.container,
                                                    name=name,
                                                    value=value_no if value_no is not None else "",
                                                    size=wx.Size(200, -1) if size is None else size,
                                                    style=style)
                else:
                    self.text_ctrl_no = wx.TextCtrl(self.container,
                                                    name=name,
                                                    value=value_no if value_no is not None else "",
                                                    size=wx.Size(200, -1) if size is None else size,
                                                    style=style,
                                                    validator=validator)
            self.winsizer.Add(self.text_ctrl_no, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
            self.text_ctrl_no.Bind(wx.EVT_TEXT, self.text_changed)
        else:
            self.text_ctrl_no = None

        self.langlabel: Dict[Languages, str] = {}
        for lang in Languages:
            if lang == Languages.EN:
                langlabel = "English:"
            elif lang == Languages.DE:
                langlabel = "Deutsch:"
            elif lang == Languages.FR:
                langlabel = "Français:"
            else:
                langlabel = "Italiano:"
            self.langlabel[lang] = wx.StaticText(self.container, label=langlabel)
            self.winsizer.Add(self.langlabel[lang])
            value_lang = value.get_by_lang(lang) if value is not None else None
            if style is None:
                if validator is None:
                    self.text_ctrl[lang] = wx.TextCtrl(self.container,
                                                       name=name,
                                                       value=value_lang if value_lang is not None else "",
                                                       size=wx.Size(200, -1) if size is None else size)
                else:
                    self.text_ctrl[lang] = wx.TextCtrl(self.container,
                                                       name=name,
                                                       value=value_lang if value_lang is not None else "",
                                                       size=wx.Size(200, -1) if size is None else size,
                                                       validator=validator)
            else:
                if validator is None:
                    self.text_ctrl[lang] = wx.TextCtrl(self.container,
                                                       name=name,
                                                       value=value_lang if value_lang is not None else "",
                                                       size=wx.Size(200, -1) if size is None else size,
                                                       style=style)
                else:
                    self.text_ctrl[lang] = wx.TextCtrl(self.container,
                                                       name=name,
                                                       value=value_lang if value_lang is not None else "",
                                                       size=wx.Size(200, -1) if size is None else size,
                                                       style=style,
                                                       validator=validator)
            self.winsizer.Add(self.text_ctrl[lang], proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
            self.text_ctrl[lang].Bind(wx.EVT_TEXT, self.text_changed)
            self.container.SetSizerAndFit(self.winsizer)

        if not enabled:
            for lang in Languages:
                self.text_ctrl[lang].Disable()
        super().__init__(panel, gsizer, label, name, self.container, True if value is None else False)

    def text_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        val = self.orig_value.get_by_lang() if self.orig_value is not None else None
        if self.text_ctrl_no is not None:
            self.text_ctrl_no.SetValue(val if val is not None else "")
        for lang in Languages:
            val = self.orig_value.get_by_lang(lang)  if self.orig_value is not None else None
            self.text_ctrl[lang].SetValue(val if val is not None else "")
        super().reset_ctrl(event)

    def set_value(self, value: LangString):
        val = value.get_by_lang()
        self.text_ctrl_no.SetValue(val if val else "")
        for lang in Languages:
            val = value.get_by_lang(lang)
            self.text_ctrl[lang].SetValue(val if val else "")
        self.orig_value = value
        if self.undo:
            self.undo.Disable()


    def get_value(self) -> LangString:
        value: Dict[Languages, str] = {}
        for lang in Languages:
            tmp_value = self.text_ctrl[lang].GetValue()
            if tmp_value:
                value[lang] = tmp_value
        if not value:
            value = self.text_ctrl_no.GetValue() if self.text_ctrl_no is not None else None
        return LangString(value)

    def get_changed(self):
        new_value = self.get_value()
        if self.orig_value == new_value:
            return None
        else:
            return new_value

class KnDialogChoice(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 choices: List[str],
                 value: Optional[str] = None,
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        choices.sort()
        self.choices = choices
        self.orig_value = self.choices[0] if value is None else value
        self.switcherStrToInt: Dict[str, int] = {}
        i = 0
        for c in self.choices:
            self.switcherStrToInt[c] = i
            i += 1
        self.choice_ctrl = wx.Choice(panel, choices=self.choices)
        if value is not None:
            if value in choices:
                self.choice_ctrl.SetSelection(self.switcherStrToInt[value])
        self.choice_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        if not enabled:
            self.choice_ctrl.Disable()
        super().__init__(panel, gsizer, label, name, self.choice_ctrl, True if value is None else False, changed_cb)

    def set_choices(self, choices: List[str]) -> None:
        self.choice_ctrl.Clear()
        self.choice_ctrl.Append(choices)
        self.choices = choices
        super().control_changed(None, self.get_value())

    def choice_changed(self, event: wx.Event) -> None:
        super().control_changed(event, self.get_value())

    def reset_ctrl(self, event: wx.Event) -> None:
        self.choice_ctrl.SetSelection(self.switcherStrToInt[self.orig_value])
        super().reset_ctrl(event)

    def set_value(self, value: Optional[int]) -> None:
        self.choice_ctrl.SetSelection(value if value else 0)
        self.orig_value = value
        if self.undo:
            self.undo.Disable()

    def get_value(self) -> Union[str, None]:
        value = self.choice_ctrl.GetCurrentSelection()
        if value == -1:
            return None
        return self.choices[value]

    def get_changed(self):
        new_value = self.choice_ctrl.GetCurrentSelection()
        if self.orig_value == self.choices[new_value]:
            return None
        else:
            return self.choices[new_value]


class KnDialogChoiceArr(KnDialogControl):
    """
    A control with dynamic number of choices
    """
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 choices: List[str],
                 value: Optional[List[str]] = None,
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        self.choices = choices
        self.gsizer = gsizer
        self.panel = panel
        self.orig_value = choices[0] if value is None else value
        self.switcherStrToInt: Dict[str, int] = {}
        i = 0
        for c in self.choices:
            self.switcherStrToInt[c] = i
            i += 1
        self.container = wx.Panel(panel, style=wx.BORDER_SIMPLE)
        self.winsizer = wx.BoxSizer(wx.VERTICAL)

        self.choice_ctrl: List[wx.Choice] = []
        if value is not None:
            for val in value:
                tmp_choice_ctrl = wx.Choice(self.container, choices=self.choices)
                self.winsizer.Add(tmp_choice_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
                self.choice_ctrl.append(tmp_choice_ctrl)
                tmp_choice_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        else:
            tmp_choice_ctrl = wx.Choice(self.container, choices=self.choices)
            self.winsizer.Add(tmp_choice_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
            self.choice_ctrl.append(tmp_choice_ctrl)
            tmp_choice_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)

        self.bsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add = wx.Button(self.container, label="+", size=wx.Size(25, -1))
        self.add.Bind(wx.EVT_BUTTON, self.add_field)
        self.bsizer.Add(self.add)
        self.remove = wx.Button(self.container, label="-", size=wx.Size(25, -1))
        self.remove.Bind(wx.EVT_BUTTON, self.remove_field)
        self.bsizer.Add(self.remove)

        self.winsizer.Add(self.bsizer)
        self.container.SetSizerAndFit(self.winsizer)


        if value is not None:
            for i, x in enumerate(self.choice_ctrl):
                x.SetSelection(self.switcherStrToInt[value[i]])
        for x in self.choice_ctrl:
            x.Bind(wx.EVT_CHOICE, self.choice_changed)
        if not enabled:
            for x in self.choice_ctrl:
                x.Disable()
        super().__init__(panel, gsizer, label, name, self.container, True if value is None else False, changed_cb)

    def add_field(self, event):
        tmp_choice_ctrl = wx.Choice(self.container, choices=self.choices)
        tmp_choice_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        self.choice_ctrl.append(tmp_choice_ctrl)
        n = self.winsizer.GetItemCount()
        self.winsizer.Insert(n - 1, tmp_choice_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()

    def remove_field(self, event):
        n = self.winsizer.GetItemCount()
        print("n=", n)
        item = self.winsizer.GetItem(n - 2)
        item.GetWindow().Destroy()
        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()

    def set_choices(self, choices: List[str]):
        self.choice_ctrl.Clear()
        self.choice_ctrl.Insert(choices)
        self.choices = choices

    def choice_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        self.choice_ctrl.SetSelection(self.switcherStrToInt[self.orig_value])
        super().reset_ctrl(event)

    def get_value(self):
        value = self.choice_ctrl.GetCurrentSelection()
        return self.choices[value]

    def get_changed(self):
        new_value = self.choice_ctrl.GetCurrentSelection()
        if self.orig_value == self.choices[new_value]:
            return None
        else:
            return self.choices[new_value]

class KnDialogSuperProperties(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 all_properties1: Dict[str, Dict[str, Set[str]]],
                 all_properties: Dict[str, Dict[str, Set[str]]],
                 value: Optional[List[str]] = None,
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        self.gsizer = gsizer
        self.panel = panel
        self.all_properties1 = all_properties1
        self.all_properties = all_properties
        self.pcnt = 0

        self.prefixes1 = [key for key, x in self.all_properties1.items()]
        self.prefixes = [key for key, x in self.all_properties.items()]

        self.container = wx.Panel(panel, style=wx.BORDER_SIMPLE)
        self.winsizer = wx.BoxSizer(wx.VERTICAL)

        tmp_prefix1 = 'knora-api'
        if value is not None and type(value) is list:
            tmp = value[0].split(':')
            if len(tmp) == 1:
                tmp_prefix1 = 'knora-api'
                tmp_value = tmp[0]
            else:
                if tmp == "":
                    tmp_prefix1 = self.onto.name
                else:
                    tmp_prefix1 = tmp[0]
                tmp_value = tmp[1]

        self.ele1 = wx.BoxSizer(wx.HORIZONTAL)
        self.prefix1_ctrl = wx.Choice(self.container, choices=self.prefixes1)
        self.prefix1_ctrl.Bind(wx.EVT_CHOICE, self.prefix1_changed)
        self.ele1.Add(self.prefix1_ctrl)
        self.sep1_ctrl = wx.StaticText(self.container, label=' : ')
        self.ele1.Add(self.sep1_ctrl)
        self.props1 = [key for key, x in self.all_properties1[tmp_prefix1].items()]
        self.prop1_ctrl = wx.Choice(self.container, choices=self.props1)
        self.prop1_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        self.ele1.Add(self.prop1_ctrl)
        self.winsizer.Add(self.ele1)
        if value is not None and type(value) is list:
            self.prefix1_ctrl.SetSelection(self.prefixes1.index(tmp_prefix1))
            self.prop1_ctrl.SetSelection(self.props1.index(tmp_value))

        self.bsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add = wx.Button(self.container, label="+", size=wx.Size(25, -1))
        self.add.Bind(wx.EVT_BUTTON, self.add_field)
        self.bsizer.Add(self.add)
        self.remove = wx.Button(self.container, label="-", size=wx.Size(25, -1))
        self.remove.Bind(wx.EVT_BUTTON, self.remove_field)
        self.bsizer.Add(self.remove)

        self.prop2_ctrl: List[wx.Choice] = []
        self.prefix2_ctrl: List[wx.Choice] = []

        self.winsizer.Add(self.bsizer)
        self.container.SetSizerAndFit(self.winsizer)

        if not enabled:
            self.prefix1_ctrl.Disable()
            self.prop1_ctrl.Disable()
            for i in range(0, self.pcnt):
                self.prefix2_ctrl[i].Disable()
                self.prop2_ctrl.Disable()
            self.add.Disable()
            self.remove.Disable()

        super().__init__(panel, gsizer, label, name, self.container, True if value is None else False, changed_cb)

    def add_field(self, event) -> None:
        container2 = wx.Panel(self.container, style=wx.BORDER_NONE)
        ele2 = wx.BoxSizer(wx.HORIZONTAL)
        self.prefix2_ctrl.append(wx.Choice(container2, id=self.pcnt, choices=self.prefixes))
        self.prefix2_ctrl[self.pcnt].Bind(wx.EVT_CHOICE, self.prefix2_changed)
        ele2.Add(self.prefix2_ctrl[self.pcnt], flag=wx.EXPAND)
        sep2_ctrl = wx.StaticText(container2, label=' : ')
        ele2.Add(sep2_ctrl, flag=wx.EXPAND)
        props2 = [key for key, x in self.all_properties['knora-api'].items()]
        self.prop2_ctrl.append(wx.Choice(container2, choices=props2))
        self.prop2_ctrl[self.pcnt].Bind(wx.EVT_CHOICE, self.choice_changed)
        ele2.Add(self.prop2_ctrl[self.pcnt], flag=wx.EXPAND)
        container2.SetSizerAndFit(ele2)
        self.pcnt = self.pcnt + 1

        n = self.winsizer.GetItemCount()
        self.winsizer.Insert(n - 1, container2, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()
        super().control_changed(event, self.get_value())

    def remove_field(self, event: wx.Event) -> None:
        if self.pcnt == 0:
            return
        n = self.winsizer.GetItemCount()
        item = self.winsizer.GetItem(n - 2)
        item.GetWindow().Destroy()
        self.prop2_ctrl.pop()
        self.prefix2_ctrl.pop()
        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()
        self.pcnt = self.pcnt - 1
        super().control_changed(event, self.get_value())

    def prefix1_changed(self, event: wx.Event) -> None:
        choice = event.GetEventObject()
        value = choice.GetCurrentSelection()
        self.prop1_ctrl.Clear()
        items = [key for key, val in self.all_properties1[self.prefixes1[value]].items()]
        self.prop1_ctrl.Append(items)
        self.choice_changed(event)

    def prefix2_changed(self, event: wx.Event) -> None:
        id = event.GetId()
        choice = event.GetEventObject()
        print('id=', id)
        value = choice.GetCurrentSelection()
        print('value=', self.prefixes[value])
        self.prop2_ctrl[id].Clear()
        items = [key for key, val in self.all_properties[self.prefixes[value]].items()]
        self.prop2_ctrl[id].Append(items)
        self.choice_changed(event)

    def get_value(self) -> List[Tuple[str, str]]:
        prefix1 = self.prefixes1[self.prefix1_ctrl.GetCurrentSelection()]
        items = [key for key, val in self.all_properties1[prefix1].items()]
        prop1 = items[self.prop1_ctrl.GetCurrentSelection()]
        result: List[Tuple[str, str]] = [(prefix1, prop1)]
        for i in range(0, self.pcnt):
            prefix = self.prefixes[self.prefix2_ctrl[i].GetCurrentSelection()]
            items = [key for key, val in self.all_properties[prefix].items()]
            prop2 = items[self.prop2_ctrl[i].GetCurrentSelection()]
            result.append((prefix, prop2))
        return result

    def choice_changed(self, event) -> None:
        super().control_changed(event, self.get_value())


class KnDialogSuperResourceClasses(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 all_resourceclasses1: Dict[str, Dict[str, Set[str]]],
                 all_resourceclasses: Dict[str, Dict[str, Set[str]]],
                 value: Optional[List[str]] = None,
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        self.gsizer = gsizer
        self.panel = panel
        self.all_resourceclasses1 = all_resourceclasses1
        self.all_resourceclasses = all_resourceclasses
        self.pcnt = 0

        self.prefixes1 = [key for key, x in self.all_resourceclasses1.items()]
        self.prefixes = [key for key, x in self.all_resourceclasses.items()]

        self.container = wx.Panel(panel, style=wx.BORDER_SIMPLE)
        self.winsizer = wx.BoxSizer(wx.VERTICAL)

        tmp_prefix1 = 'knora-api'
        if value is not None and type(value) is list:
            tmp = value[0].split(':')
            if len(tmp) == 1:
                tmp_prefix1 = 'knora-api'
                tmp_value = tmp[0]
            else:
                if tmp == "":
                    tmp_prefix1 = self.onto.name
                else:
                    tmp_prefix1 = tmp[0]
                tmp_value = tmp[1]

        self.ele1 = wx.BoxSizer(wx.HORIZONTAL)
        self.prefix1_ctrl = wx.Choice(self.container, choices=self.prefixes1)
        self.prefix1_ctrl.Bind(wx.EVT_CHOICE, self.prefix1_changed)
        self.ele1.Add(self.prefix1_ctrl)
        self.sep1_ctrl = wx.StaticText(self.container, label=' : ')
        self.ele1.Add(self.sep1_ctrl)
        self.resclasses1 = list(self.all_resourceclasses1[tmp_prefix1])
        self.resclass1_ctrl = wx.Choice(self.container, choices=self.resclasses1)
        self.resclass1_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        self.ele1.Add(self.resclass1_ctrl)
        self.winsizer.Add(self.ele1)
        if value is not None and type(value) is list:
            self.prefix1_ctrl.SetSelection(self.prefixes1.index(tmp_prefix1))
            self.resclass1_ctrl.SetSelection(self.resclasses1.index(tmp_value))

        self.bsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add = wx.Button(self.container, label="+", size=wx.Size(25, -1))
        self.add.Bind(wx.EVT_BUTTON, self.add_field)
        self.bsizer.Add(self.add)
        self.remove = wx.Button(self.container, label="-", size=wx.Size(25, -1))
        self.remove.Bind(wx.EVT_BUTTON, self.remove_field)
        self.bsizer.Add(self.remove)

        self.resclass2_ctrl: List[wx.Choice] = []
        self.prefix2_ctrl: List[wx.Choice] = []

        self.winsizer.Add(self.bsizer)
        self.container.SetSizerAndFit(self.winsizer)

        if not enabled:
            self.prefix1_ctrl.Disable()
            self.resclass1_ctrl.Disable()
            for i in range(0, self.pcnt):
                self.prefix2_ctrl[i].Disable()
                self.resclass2_ctrl.Disable()
            self.add.Disable()
            self.remove.Disable()

        super().__init__(panel, gsizer, label, name, self.container, True if value is None else False, changed_cb)

    def add_field(self, event) -> None:
        container2 = wx.Panel(self.container, style=wx.BORDER_NONE)
        ele2 = wx.BoxSizer(wx.HORIZONTAL)
        self.prefix2_ctrl.append(wx.Choice(container2, id=self.pcnt, choices=self.prefixes))
        self.prefix2_ctrl[self.pcnt].Bind(wx.EVT_CHOICE, self.prefix2_changed)
        ele2.Add(self.prefix2_ctrl[self.pcnt], flag=wx.EXPAND)
        sep2_ctrl = wx.StaticText(container2, label=' : ')
        ele2.Add(sep2_ctrl, flag=wx.EXPAND)
        resclasses2 = list(self.all_resourceclasses['knora-api'])
        self.resclass2_ctrl.append(wx.Choice(container2, choices=resclasses2))
        self.resclass2_ctrl[self.pcnt].Bind(wx.EVT_CHOICE, self.choice_changed)
        ele2.Add(self.resclass2_ctrl[self.pcnt], flag=wx.EXPAND)
        container2.SetSizerAndFit(ele2)
        self.pcnt = self.pcnt + 1

        n = self.winsizer.GetItemCount()
        self.winsizer.Insert(n - 1, container2, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()
        super().control_changed(event, self.get_value())

    def remove_field(self, event: wx.Event) -> None:
        if self.pcnt == 0:
            return
        n = self.winsizer.GetItemCount()
        item = self.winsizer.GetItem(n - 2)
        item.GetWindow().Destroy()
        self.resclass2_ctrl.pop()
        self.prefix2_ctrl.pop()
        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()
        self.pcnt = self.pcnt - 1
        super().control_changed(event, self.get_value())

    def prefix1_changed(self, event: wx.Event) -> None:
        choice = event.GetEventObject()
        value = choice.GetCurrentSelection()
        self.resclass1_ctrl.Clear()
        items = list(self.all_resourceclasses1[self.prefixes1[value]])
        self.resclass1_ctrl.Append(items)
        self.choice_changed(event)

    def prefix2_changed(self, event: wx.Event) -> None:
        id = event.GetId()
        choice = event.GetEventObject()
        print('id=', id)
        value = choice.GetCurrentSelection()
        print('value=', self.prefixes[value])
        self.resclass2_ctrl[id].Clear()
        items = list(self.all_resourceclasses[self.prefixes[value]])
        self.resclass2_ctrl[id].Append(items)
        self.choice_changed(event)

    def get_value(self) -> List[Tuple[str, str]]:
        prefix1 = self.prefixes1[self.prefix1_ctrl.GetCurrentSelection()]
        items = list(self.all_resourceclasses1[prefix1])
        resclass1 = items[self.resclass1_ctrl.GetCurrentSelection()]
        result: List[Tuple[str, str]] = [(prefix1, resclass1)]
        for i in range(0, self.pcnt):
            prefix = self.prefixes[self.prefix2_ctrl[i].GetCurrentSelection()]
            items = [key for key, val in self.all_resourceclasses[prefix].items()]
            resclass2 = items[self.resclass2_ctrl[i].GetCurrentSelection()]
            result.append((prefix, resclass2))
        return result

    def choice_changed(self, event) -> None:
        super().control_changed(event, self.get_value())


class KnDialogCheckBox(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 status: Optional[bool] = None):
        self.orig_status = status
        self.checkbox_ctrl = wx.CheckBox(panel, label=label)
        if status is not None:
            self.checkbox_ctrl.SetValue(status)
        self.checkbox_ctrl.Bind(wx.EVT_CHECKBOX, self.checkbox_changed)
        super().__init__(panel, gsizer, label, name, self.checkbox_ctrl, True if status is None else False)

    def checkbox_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        self.checkbox_ctrl.SetValue(self.orig_status)
        super().reset_ctrl(event)

    def set_value(self, status: Optional[bool]):
        self.checkbox_ctrl.SetValue(status if status is not None else False)
        self.orig_status = status
        if self.undo:
            self.undo.Disable()

    def get_value(self):
        return self.checkbox_ctrl.GetValue()

    def get_changed(self):
        new_status = self.checkbox_ctrl.GetValue()
        if self.orig_status == new_status:
            return None
        else:
            return new_status


class KnCollapsiblePicker:
    def __init__(self,
                 parent: wx.Window,
                 sizer: wx.Sizer,
                 label: str,
                 available: Union[List[str],None],
                 chosen: List[str],
                 selected: List[str],
                 on_change_cb: Callable[[wx.Event], None],
                 on_add_cb: Optional[Callable[[str], None]] = None,
                 on_rm_cb:  Optional[Callable[[str], None]] = None):
        self.available = available
        self.chosen = chosen
        self.selected = selected
        self.on_change_cb = on_change_cb
        self.on_add_cb = on_add_cb
        self.on_rm_cb = on_rm_cb
        self.cp = wx.CollapsiblePane(parent,
                                     label=label,
                                     style=wx.CP_DEFAULT_STYLE)
        self.cpp = self.cp.GetPane()
        self.localsizer = wx.BoxSizer(wx.VERTICAL)
        self.itemlist = wx.CheckListBox(self.cpp, choices=self.chosen)
        self.itemlist.Bind(wx.EVT_CHECKLISTBOX, self.checkbox_changed_cb)
        for sel in selected:
            self.itemlist.Check(self.chosen.index(sel))
        self.cpp.SetSizer(self.localsizer)
        self.localsizer.SetSizeHints(self.cpp)
        self.localsizer.Add(self.itemlist, flag=wx.EXPAND | wx.GROW | wx.ALL)

        if self.available is not None:
            self.modify = wx.Button(self.cpp, label="Add/Remove...")
            self.modify.Bind(wx.EVT_BUTTON, self.picker)
            self.localsizer.Add(self.modify, flag=wx.EXPAND | wx.ALL)

        self.cpp.SetSizer(self.localsizer)

        sizer.Add(self.cp, 0, flag=wx.EXPAND | wx.ALL | wx.GROW, border=5)

    def picker(self, event):
        d = ItemsPickerDialog(self.cp,
                              titlestr="Project membership",
                              leftstr='Available projects:',
                              rightstr='Member of project:',
                              available=self.available,
                              chosen=self.chosen,
                              ipStyle=IP_REMOVE_FROM_CHOICES)
        res = d.ShowModal()
        if res == wx.ID_OK:
            removed = []
            for i in d.GetItems():
                if i not in self.available:
                    removed.append(i)
            for i in removed:
                if self.on_rm_cb is not None:
                    self.on_rm_cb(i)
                pos = self.itemlist.FindString(i)
                self.itemlist.Delete(pos)
            added = []
            for  i in d.GetSelections():
                if i not in self.chosen:
                    added.append(i)
            if len(added) > 0:
                if self.on_add_cb is not None:
                    for i in added:
                        self.on_add_cb(i)
                self.itemlist.InsertItems(added, 0)

        d.Destroy()

    def checkbox_changed_cb(self, event):
        s = event.GetString()
        all_s = self.itemlist.GetCheckedStrings()
        on = s in all_s
        res = self.on_change_cb(s, on)
        if not res:
            i = self.itemlist.FindString(s)
            if on:
                self.itemlist.Check(i, True)
            else:
                self.itemlist.Check(i, False)


    def GetCheckedItems(self):
        return self.itemlist.GetCheckedItems()

    def GetCheckedStrings(self):
        return self.itemlist.GetCheckedStrings()

    def GetItemsAndCheck(self) -> Dict[str, bool]:
        count = self.itemlist.GetCount()
        all = [self.itemlist.GetString(x) for x in range(count)]
        checked = self.itemlist.GetCheckedStrings()
        return dict(map(lambda x: (x, x in checked), all))

class KnDialogGuiAttributes(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 gui_element: str,
                 all_attributes: Dict[str, List[str]],
                 all_lists: List[str],
                 value: Optional[Dict[str, str]] = None,
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        self.all_attributes = all_attributes
        self.all_lists = all_lists
        self.gui_element = gui_element
        self.value = value
        self.gsizer = gsizer
        self.panel = panel
        self.container = wx.Panel(self.panel, style=wx.BORDER_SIMPLE)

        self.create_panel(gui_element)

        super().__init__(panel, gsizer, label, name, self.container, True if value is None else False, changed_cb)

    def create_panel(self, gui_element):
        self.gui_element = gui_element
        self.winsizer = wx.FlexGridSizer(cols=3)

        self.attr_name_ctrl: List[wx.StaticText] = []
        self.attr_colon_ctrl: List[wx.StaticText] = []
        self.attr_val_ctrl: List[Union[wx.TextCtrl, wx.Choice]] = []
        self.pcnt = 0

        attributes = self.all_attributes[gui_element]
        for attribute in attributes:
            attr_name, attr_type = attribute.split('=')
            self.attr_name_ctrl.append(wx.StaticText(parent=self.container, label=attr_name))
            self.winsizer.Add(self.attr_name_ctrl[self.pcnt])
            self.attr_colon_ctrl.append(wx.StaticText(parent=self.container, label=' : '))
            self.winsizer.Add(self.attr_colon_ctrl[self.pcnt])
            val = self.value.get(attr_name) if self.value else None
            if attr_type == 'integer':
                self.attr_val_ctrl.append(wx.TextCtrl(parent=self.container,
                                                      name=attr_name,
                                                      value=val if val is not None else ""))
            elif attr_type == 'decimal':
                self.attr_val_ctrl.append(wx.TextCtrl(parent=self.container,
                                                      name=attr_name,
                                                      value=val if val is not None else ""))
            elif attr_type == 'percent':
                self.attr_val_ctrl.append(wx.TextCtrl(parent=self.container,
                                                      name=attr_name,
                                                      value=val if val is not None else ""))
            elif attr_type == '<list-name>':
                self.attr_val_ctrl.append(wx.Choice(parent=self.container, choices=self.all_lists))
                if val in self.all_lists:
                    self.attr_val_ctrl[self.pcnt].SetSelection(self.all_lists.index(val))
            elif attr_type == 'soft|hard':
                self.attr_val_ctrl.append(wx.Choice(parent=self.container, choices=['soft', 'hard']))
                self.attr_val_ctrl[self.pcnt].SetSelection(0 if val == 'soft' else 1)
            else:
                pass
            self.winsizer.Add(self.attr_val_ctrl[self.pcnt])
            self.pcnt = self.pcnt + 1

        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()
        self.panel.Layout()

    def set_gui_element(self, gui_element: str):
        for child in self.container.GetChildren():
            child.Destroy()
        self.create_panel(gui_element)

    def get_value(self):
        attributes = self.all_attributes[self.gui_element]
        values = {}
        for i, attribute in list(enumerate(attributes)):
            attr_name, attr_type = attribute.split('=')
            if attr_type == 'integer':
                values[attr_name] = self.attr_val_ctrl[i].GetValue()
            elif attr_type == 'decimal':
                values[attr_name] = self.attr_val_ctrl[i].GetValue()
            elif attr_type == 'percent':
                values[attr_name] = self.attr_val_ctrl[i].GetValue()
            elif attr_type == '<list-name>':
                values[attr_name] = self.all_lists[self.attr_val_ctrl[i].GetSelection()]
            elif attr_type == 'soft|hard':
                l = ['soft', 'hard']
                values[attr_name] = l[self.attr_val_ctrl[i].GetSelection()]
            else:
                pass
        return values


class KnDialogHasProperty(KnDialogControl):
    """
    Implements a knora-specific "has_property" widget to be used within a KnDialogControl
    """
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 all_props: List[str] = None,
                 value: Dict[str, HasPropertyInfo] = None,  # {<name>: HasPropertyInfo}
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        """
        Constructor of "has_property" widget for use within a KnDialogControl
        :param panel: Parent panel
        :param gsizer: Parent sizer to be assumed a wc.FlexGridSizer
        :param label: Label for control (visible string in the GUI)
        :param name: Name of the window (wx internal use)
        :param all_props: List of all properties posible/allowed
        :param value: Dict of selected properties in the form Dict[str, HasPropertyInfo]: {<name>: HasPropertyInfo}
        :param enabled: True if widget can modify data
        :param changed_cb: Callback if something is changed
        """
        self.value: Dict[str, HasPropertyInfo] = value
        self.orig_value: Dict[str, HasPropertyInfo] = deepcopy(value)
        self.all_props: List[str] = all_props
        self.gsizer = gsizer
        self.panel = panel
        self.container = wx.Panel(self.panel, style=wx.BORDER_SIMPLE)
        self.winsizer = wx.BoxSizer(wx.VERTICAL)

        self.has_property_grid = wx.lib.scrolledpanel.ScrolledPanel(self.container, -1,
                                                                    size=(400, 150),
                                                                    style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER,
                                                                    name="has_property_grid")
        self.has_property_gsizer = wx.FlexGridSizer(cols=4, vgap=2, hgap=6)

        font = wx.Font(wx.FontInfo().Bold())
        name_label_ctrl = wx.StaticText(parent=self.has_property_grid, label="Name")  #.SetFont(font)
        name_label_ctrl.SetFont(font)
        self.has_property_gsizer.Add(name_label_ctrl, flag=wx.EXPAND)

        cardinality_label_ctrl = wx.StaticText(parent=self.has_property_grid, label="Card.")  #.SetFont(font)
        cardinality_label_ctrl.SetFont(font)
        self.has_property_gsizer.Add(cardinality_label_ctrl, flag=wx.EXPAND)

        order_label_ctrl = wx.StaticText(parent=self.has_property_grid, label="Order")  #.SetFont(font)
        order_label_ctrl.SetFont(font)
        self.has_property_gsizer.Add(order_label_ctrl, flag=wx.EXPAND)

        status_label_ctrl = wx.StaticText(parent=self.has_property_grid, label="Status")  #.SetFont(font)
        status_label_ctrl.SetFont(font)
        self.has_property_gsizer.Add(status_label_ctrl, flag=wx.EXPAND)

        self.name_ctrl: List[wx.StaticText] = []
        self.cardinality_ctrl: List[wx.Choice] = []
        self.order_ctrl: List[wx.SpinCtrl] = []
        self.status_ctrl: List[wx.StaticText] = []
        self.idx: Dict[str, int] = {x.value: i for i, x in enumerate(Cardinality)}  # lookuptable propnames to index
        self.rcnt = 0
        if value:
            for propname, propinfo in value.items():
                self.add_one_property(propname=propname,
                                      propinfo=propinfo,
                                      propstatus=PropertyStatus.UNCHANGED)
                self.rcnt = self.rcnt + 1

        self.winsizer.Add(self.has_property_grid)

        self.modify = wx.Button(self.container, label="Add/Remove...")
        self.modify.Bind(wx.EVT_BUTTON, self.picker)
        self.winsizer.Add(self.modify, flag=wx.EXPAND | wx.ALL)

        self.has_property_grid.SetSizer(self.has_property_gsizer)
        self.has_property_grid.SetAutoLayout(1)
        self.has_property_grid.SetupScrolling()

        self.container.SetSizerAndFit(self.winsizer)
        self.panel.SetSizerAndFit(self.gsizer)
        self.panel.GetParent().resize()
        self.panel.Layout()
        super().__init__(panel, gsizer, label, name, self.container, True if value is None else False, changed_cb)

    def add_one_property(self,
                         propname: str,
                         propinfo: HasPropertyInfo,
                         propstatus: PropertyStatus):
        self.name_ctrl.append(wx.StaticText(parent=self.has_property_grid, label=propname))
        self.has_property_gsizer.Add(self.name_ctrl[self.rcnt], flag=wx.EXPAND)

        self.cardinality_ctrl.append(wx.Choice(parent=self.has_property_grid, choices=[x.value for x in Cardinality]))
        self.cardinality_ctrl[self.rcnt].Bind(wx.EVT_CHOICE, lambda event: self.cardinality_changed(event, propname))
        self.cardinality_ctrl[self.rcnt].SetSelection(self.idx[propinfo['cardinality'].value])
        self.has_property_gsizer.Add(self.cardinality_ctrl[self.rcnt], flag=wx.EXPAND)

        self.order_ctrl.append(wx.SpinCtrl(parent=self.has_property_grid,
                                           value=str(propinfo['gui_order'])
                                           if propinfo.get('gui_order') is not None else "0",
                                           size=(50, -1), min=0, max=99))
        self.order_ctrl[self.rcnt].Bind(wx.EVT_SPINCTRL, lambda event: self.gui_order_changed(event, propname))
        self.has_property_gsizer.Add(self.order_ctrl[self.rcnt], flag=wx.EXPAND)

        self.status_ctrl.append(wx.StaticText(parent=self.has_property_grid, label=propstatus.value))
        self.has_property_gsizer.Add(self.status_ctrl[self.rcnt], flag=wx.EXPAND)

    def rm_one_property(self, propname: str) -> None:
        """
        This method removes a property from the list and value object.
        Note: Should only by used for properties that have been added berfore interactively!

        :param propname: Name of the property
        :return: None
        """
        vkeys = [*self.value]
        if propname in vkeys:
            i = vkeys.index(propname)
            self.name_ctrl[i].Destroy()
            self.cardinality_ctrl[i].Destroy()
            self.order_ctrl[i].Destroy()
            self.status_ctrl[i].Destroy()
            del self.value[propname]
        self.has_property_grid.SetAutoLayout(1)
        self.has_property_grid.SetupScrolling()
        self.panel.GetParent().resize()
        self.panel.Layout()

    def change_status(self, propname: str, status: PropertyStatus) -> None:
        """
        Changes the status of property

        :param propname: Name of the property
        :param status: The new status
        :return: None
        """
        self.value[propname]['status'] = status
        vkeys = [*self.value]
        if propname in vkeys:
            i = vkeys.index(propname)
            self.status_ctrl[i].SetLabel(self.value[propname]['status'].value)
            if status == PropertyStatus.DELETED:
                self.cardinality_ctrl[i].Disable()
                self.order_ctrl[i].Disable()
            else:
                self.cardinality_ctrl[i].Enable()
                self.order_ctrl[i].Enable()


        else:
            print('ERRROR!!!!!!!!!!!!!!')

    def cardinality_changed(self, event: wx.Event, propname: str) -> None:
        choice = event.GetEventObject()
        value = choice.GetCurrentSelection()
        cardlist = [x for i, x in enumerate(Cardinality)]
        self.value[propname]['cardinality'] = cardlist[value]
        if self.value[propname]['status'] == PropertyStatus.UNCHANGED:
            self.change_status(propname, PropertyStatus.CHANGED)

    def gui_order_changed(self, event: wx.Event, propname: str) -> None:
        spin = event.GetEventObject()
        value = spin.GetValue()
        self.value[propname]['cardinality'] = int(value)
        if self.value[propname]['status'] == PropertyStatus.UNCHANGED:
            self.change_status(propname, PropertyStatus.CHANGED)

    def picker(self, event):
        chosen = [propname for propname, propinfo in self.value.items() if propinfo['status'] != PropertyStatus.DELETED]
        available = [x for x in self.all_props if x not in chosen]
        d = ItemsPickerDialog(self.panel,
                              titlestr="Has property",
                              leftstr="Available properties",
                              rightstr="Chosen properties",
                              available=available,
                              chosen=chosen,  # all keys of dict as list
                              ipStyle=IP_REMOVE_FROM_CHOICES)
        res = d.ShowModal()
        if res == wx.ID_OK:
            for elestr in d.GetItems():
                if elestr not in available:
                    #
                    # we mark the HasPropertyClass instance for deletion
                    #
                    if self.value.get(elestr) is not None:
                        if self.value[elestr]['status'] == PropertyStatus.NEW:
                            # this property has been added before interactively by the user
                            self.rm_one_property(elestr)
                        else:
                            # this is a property that has been here initially
                            self.change_status(elestr, PropertyStatus.DELETED)
            for elestr in d.GetSelections():
                if elestr not in chosen:
                    #
                    # add a new HasPropertyClass instance
                    #
                    if self.value.get(elestr) is not None:
                        # the property has already been on the list if has_properties before
                        if self.orig_value.get(elestr) is not None:
                            # the property has been on the "original" has_properties list
                            # we add again what previously has been deleted interactively by the user
                            self.value[elestr]['cardinality'] = self.orig_value[elestr]['cardinality']
                            self.value[elestr]['gui_order'] = self.orig_value[elestr]['gui_order']
                            self.change_status(elestr, PropertyStatus.UNCHANGED)
                            vkeys = [*self.value]
                            if elestr in vkeys:
                                i = vkeys.index(elestr)
                                self.cardinality_ctrl[i].SetSelection(self.idx[self.value[elestr]['cardinality'].value])
                                self.order_ctrl[i].SetValue(str(self.value[elestr]['gui_order']))
                        else:
                            # has been added, then deleted and now we add it again
                            # should never occur, since we remove such properties when deleted!
                            self.change_status(elestr, PropertyStatus.NEW)
                    else:
                        # we add a new one
                        info: HasPropertyInfo = {'cardinality': Cardinality.C_0_1,
                                                 'gui_order': self.rcnt,
                                                 'status': PropertyStatus.NEW}
                        self.add_one_property(propname=elestr,
                                              propinfo=info,
                                              propstatus=PropertyStatus.NEW)
                        self.value[elestr] = info
                        self.rcnt = self.rcnt + 1
        self.has_property_grid.SetAutoLayout(1)
        self.has_property_grid.SetupScrolling()
        self.panel.GetParent().resize()
        self.panel.Layout()
        d.Destroy()

    def get_value(self) -> Optional[Dict[str, HasPropertyInfo]]:
        return self.value if self.value else None

    def get_changed(self) -> Optional[Dict[str, HasPropertyInfo]]:
        new_value = {propname: propinfo for propname, propinfo in self.value.items() if propinfo['status'] != PropertyStatus.UNCHANGED}
        if new_value:
            return None
        else:
            return new_value
