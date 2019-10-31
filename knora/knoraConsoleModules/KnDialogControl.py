from typing import List, Set, Dict, Tuple, Optional, Any, Union, Callable

import os
import sys
import wx
from typing import List, Set, Dict, Tuple, Optional
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
                 control: wx.Control):
        self.label = wx.StaticText(panel, label=label)
        self.control = control

        self.undo = wx.Button(panel, label="X", size=wx.Size(25, -1))
        self.undo.Bind(wx.EVT_BUTTON, self.reset_ctrl)
        self.undo.Disable()
        gsizer.Add(self.label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(self.control, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(self.undo, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

    def control_changed(self, event):
        self.undo.Enable()

    def reset_ctrl(self, event):
        self.undo.Disable()

    def get_changed(self):
        return None

class KnDialogTextCtrl(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 value: str,
                 style = None):
        self.orig_value = value
        if style is None:
            self.text_ctrl = wx.TextCtrl(panel, name=name, value=value, size=wx.Size(200, -1))
        else:
            self.text_ctrl = wx.TextCtrl(panel, name=name, value=value, size=wx.Size(200, -1),
                                     style=style)
        self.text_ctrl.Bind(wx.EVT_TEXT, self.text_changed)
        super().__init__(panel, gsizer, label, name, self.text_ctrl)

    def text_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        self.text_ctrl.SetValue(self.orig_value)
        super().reset_ctrl(event)

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
                 value: str):
        self.orig_value = value
        self.switcher: Dict[str, int] = {}
        i = 0
        for c in choices:
            self.switcher[c] = i
            i += 1
        self.choice_ctrl = wx.Choice(panel, choices=choices)
        self.choice_ctrl.SetSelection(self.switcher[value])
        self.choice_ctrl.Bind(wx.EVT_CHOICE, self.choice_changed)
        super().__init__(panel, gsizer, label, name, self.choice_ctrl)

    def choice_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        self.choice_ctrl.SetSelection(self.switcher[self.orig_value])
        super().reset_ctrl(event)

    def get_changed(self):
        new_value = self.choice_ctrl.GetCurrentSelection()
        if self.switcher[self.orig_value] == new_value:
            return None
        else:
            return new_value


class KnDialogCheckBox(KnDialogControl):
    def __init__(self,
                 panel: wx.Panel,
                 gsizer: wx.FlexGridSizer,
                 label: str,
                 name: str,
                 status: bool):
        self.orig_status = status
        self.checkbox_ctrl = wx.CheckBox(panel, label=label)
        self.checkbox_ctrl.SetValue(status)
        self.checkbox_ctrl.Bind(wx.EVT_CHECKBOX, self.checkbox_changed)
        super().__init__(panel, gsizer, label, name, self.checkbox_ctrl)

    def checkbox_changed(self, event):
        super().control_changed(event)

    def reset_ctrl(self, event):
        self.checkbox_ctrl.SetValue(self.orig_status)
        super().reset_ctrl(event)

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
                 available: List[str],
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
        self.itemlist.Bind(wx.EVT_CHECKLISTBOX, self.on_change_cb)
        for sel in selected:
            self.itemlist.Check(self.chosen.index(sel))
        self.cpp.SetSizer(self.localsizer)
        self.localsizer.SetSizeHints(self.cpp)
        self.localsizer.Add(self.itemlist, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL)
        self.modify = wx.Button(self.cpp, label="Add/Remove...")
        self.modify.Bind(wx.EVT_BUTTON, self.picker)

        self.localsizer.Add(self.modify, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL)
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

    def GetCheckedItems(self):
        return self.itemlist.GetCheckedItems()

    def GetCheckedStrings(self):
        return self.itemlist.GetCheckedStrings()

    def rebuild(self, choices: List[str], selected: List[str]):
        self.choices = choices
        self.itemlist.Destroy()
        self.itemlist = wx.CheckListBox(self.cpp, choices=self.choices)
        self.itemlist.Bind(wx.EVT_CHECKLISTBOX, self.on_change_cb)
        for sel in selected:
            self.itemlist.Check(choices.index(sel))
        self.localsizer.Add(self.itemlist, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL)
        self.itemlist.Fit()
        self.itemlist.GetParent().SendSizeEvent()


