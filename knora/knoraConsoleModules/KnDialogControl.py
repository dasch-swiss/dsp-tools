from typing import List, Set, Dict, Tuple, Optional, Any, Union, Callable

import os
import sys
import wx
from typing import List, Set, Dict, Tuple, Optional, Callable
from knora import KnoraError, Knora
from pprint import pprint

from wx.lib.itemspicker import ItemsPicker, \
                               EVT_IP_SELECTION_CHANGED, \
                               IP_SORT_CHOICES, IP_SORT_SELECTED,\
                               IP_REMOVE_FROM_CHOICES

class ItemsPickerDialog(wx.Dialog):
    def __init__(self,
                 parent: wx.Window,
                 available: List[str],
                 chosen: List[str],
                 ipStyle):
        super().__init__(
            parent=parent,
            title="Project membership",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ip = ItemsPicker(self,
                              choices=available,
                              label='Available projects',
                              selectedLabel='Member of project:',
                              ipStyle=ipStyle)
        self.ip.SetSelections(chosen)
        #self.ip.Bind(EVT_IP_SELECTION_CHANGED, self.OnSelectionChange)
        self.ip._source.SetMinSize((-1,150))

        sizer.Add(self.ip, 0, wx.ALL, 10)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(sizer)

    def GetSelections(self):
        return self.ip.GetSelections()

    def GetItems(self):
        return self.ip.GetItems()


class KnDialogControl:
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 control: wx.Control,
                 newentry: bool = False,
                 changed_cb: Optional[Callable[[wx.Event, Optional[Any]], None]] = None):
        self.label = wx.StaticText(panel, label=label)
        self.control = control
        self.newentry = newentry
        self.changed_cb = changed_cb

        if not newentry:
            self.undo = wx.Button(panel, label="X", size=wx.Size(25, -1))
            self.undo.Bind(wx.EVT_BUTTON, self.reset_ctrl)
            self.undo.Disable()
        gsizer.Add(self.label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(self.control, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        if not newentry:
            gsizer.Add(self.undo, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

    def control_changed(self, event: wx.Event, user_data: Any = None):
        if not self.newentry:
            self.undo.Enable()
        if self.changed_cb is not None:
            self.changed_cb(wx.Event, user_data)

    def reset_ctrl(self, event):
        if not self.newentry:
            self.undo.Disable()

    def get_changed(self):
        return None

class KnDialogStaticText(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 value: Optional[str] = None,
                 style = None):
        if style is None:
            self.static_text = wx.StaticText(panel,
                                             name=name,
                                             label=value if value is not None else "")
        else:
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
                 size: Optional[wx.Size] = None,
                 style=None,
                 enabled: bool = True):
        self.orig_value = value
        if style is None:
            self.text_ctrl = wx.TextCtrl(panel,
                                         name=name,
                                         value=value if value is not None else "",
                                         size=wx.Size(200, -1) if size is None else size)
        else:
            self.text_ctrl = wx.TextCtrl(panel,
                                         name=name,
                                         value=value if value is not None else "",
                                         size=wx.Size(200, -1) if size is None else size,
                                         style=style)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.text_changed)
        if not enabled:
            self.text_ctrl.Disable()
        super().__init__(panel, gsizer, label, name, self.text_ctrl, True if value is None else False)

    def text_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        self.text_ctrl.SetValue(self.orig_value)
        super().reset_ctrl(event)

    def get_value(self):
        value = self.text_ctrl.GetValue()
        return value if value else None

    def get_changed(self):
        new_value = self.text_ctrl.GetValue()
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
        self.choices = choices
        self.orig_value = choices[0] if value is None else value
        self.switcherStrToInt: Dict[str, int] = {}
        i = 0
        for c in self.choices:
            self.switcherStrToInt[c] = i
            i += 1
        self.choice_ctrl = wx.Choice(panel, choices=choices)
        if value is not None:
            self.choice_ctrl.SetSelection(self.switcherStrToInt[value])
        self.choice_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        if not enabled:
            self.choice_ctrl.Disable()
        super().__init__(panel, gsizer, label, name, self.choice_ctrl, True if value is None else False, changed_cb)

    def set_choices(self, choices: List[str]):
        self.choice_ctrl.Clear()
        self.choice_ctrl.Append(choices)
        self.choices = choices
        super().control_changed(None, self.get_value())

    def choice_changed(self, event):
        super().control_changed(event, self.get_value())

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

        self.choice_ctrl = []
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
        print("======> choice_changed")
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
                 all_properties: Dict[str, Dict[str, Set[str]]],
                 value: Optional[List[str]] = None,
                 enabled: bool = True,
                 changed_cb: Optional[Callable[[wx.Event], None]] = None):
        self.gsizer = gsizer
        self.panel = panel
        self.all_properties = all_properties
        self.pcnt = 0

        self.prefixes = [key for key, x in self.all_properties.items()]

        self.container = wx.Panel(panel, style=wx.BORDER_SIMPLE)
        self.winsizer = wx.BoxSizer(wx.VERTICAL)

        self.ele1 = wx.BoxSizer(wx.HORIZONTAL)
        self.prefix1_ctrl = wx.Choice(self.container, choices=['knora-api'])
        self.prefix1_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        self.ele1.Add(self.prefix1_ctrl)
        self.sep1_ctrl = wx.StaticText(self.container, label=' : ')
        self.ele1.Add(self.sep1_ctrl)
        self.props1 = [key for key, x in self.all_properties['knora-api'].items()]
        self.prop1_ctrl = wx.Choice(self.container, choices=self.props1)
        self.prop1_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        self.ele1.Add(self.prop1_ctrl)
        self.winsizer.Add(self.ele1)
        if value is not None and type(value) is list:
            self.prop1_ctrl.SetSelection(self.props1.index(value[0]))

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
        self.prefix2_ctrl[self.pcnt].Bind(wx.EVT_CHOICE, self.prefix_changed)
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

    def prefix_changed(self, event: wx.Event) -> None:
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
        prop1 = self.props1[self.prop1_ctrl.GetCurrentSelection()]
        result: List[Tuple[str, str]] = [('knora-api', prop1)]
        for i in range(0, self.pcnt):
            prefix = self.prefixes[self.prefix2_ctrl[i].GetCurrentSelection()]
            items = [key for key, val in self.all_properties[prefix].items()]
            prop2 = items[self.prop2_ctrl[i].GetCurrentSelection()]
            result.append((prefix, prop2))
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



