from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from typing import List, Set, Dict, Tuple, Optional
from knora import KnoraError, Knora
from pprint import pprint


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


class KnCollapsileChecklist:
    def __init__(self,
                 parent: wx.Window,
                 sizer: wx.Sizer,
                 label: str,
                 choices: List[str] = [],
                 selected: List[str] = []):
        self.cp = wx.CollapsiblePane(parent,
                                     label=label,
                                     style=wx.CP_DEFAULT_STYLE)
        cpp = self.cp.GetPane()
        localsizer = wx.BoxSizer(wx.VERTICAL)
        itemlist = wx.CheckListBox(cpp, choices=choices)
        for sel in selected:
            itemlist.Check(choices.index(sel))
        cpp.SetSizer(localsizer)
        localsizer.SetSizeHints(cpp)
        localsizer.Add(itemlist, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL)
        cpp.SetSizer(localsizer)

        sizer.Add(self.cp, 0, flag=wx.EXPAND | wx.ALL | wx.GROW, border=5)
