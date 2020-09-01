from typing import Any, Union, List, Set, Dict, Tuple, Optional, Callable, TypedDict

import wx

class DoublePasswordCtrl(wx.Control):

    def __init__(self,
                 parent: wx.Window,
                 id: int = wx.ID_ANY,
                 pos: wx.Point = wx.DefaultPosition,
                 size: wx.Size = wx.DefaultSize,
                 style: int = wx.NO_BORDER,
                 validator: wx.Validator = wx.DefaultValidator,
                 name: str = "DoublePassword",
                 value: str = ""):
        super().__init__(parent=parent,
                         id=id,
                         pos=pos,
                         size=size,
                         style=style,
                         validator=validator,
                         name=name)

        sizer = wx.BoxSizer(wx.VERTICAL)
        halfheight = size.GetHeight()
        if halfheight > 0:
            halfheight = halfheight / 2
        self.password1 = wx.TextCtrl(parent=self,
                                     name=name + '1',
                                     value=value if value is not None else "",
                                     size=wx.Size(size.GetWidth(), halfheight),
                                     style=style | wx.TE_PASSWORD)
        self.password1.Bind(wx.EVT_TEXT, self.text1_changed)
        sizer.Add(self.password1)

        self.password2 = wx.TextCtrl(parent=self,
                                     name=name + '2',
                                     value=value if value is not None else "",
                                     size=wx.Size(size.GetWidth(), halfheight),
                                     style=style | wx.TE_PASSWORD)
        self.password2.Bind(wx.EVT_TEXT, self.text2_changed)
        sizer.Add(self.password2)
        self.SetSizerAndFit(sizer)

    def text1_changed(self, event: wx.CommandEvent) -> None:
        self.text_changed()
        event.Skip()

    def text2_changed(self, event: wx.CommandEvent) -> None:
        self.text_changed()
        event.Skip()

    def text_changed(self) -> None:
        event = wx.PyCommandEvent(wx.EVT_TEXT.typeId, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def GetValue(self) -> Union[str, None]:
        if self.password1.GetValue() == self.password2.GetValue():
            return self.password1.GetValue()
        else:
            return None

    def SetValue(self, value: str) -> None:
        self.password1.SetValue(value)
        self.password2.SetValue(value)

    def SetBackgroundColour(self, color):
        self.password1.SetBackgroundColour(color)
        self.password2.SetBackgroundColour(color)

    def SetFocus(self):
        self.password1.SetFocus()

    def Refresh(self):
        self.password1.Refresh()
        self.password2.Refresh()

    def SetValidator(self, validator: wx.Validator = wx.DefaultValidator):
        self.password1.SetValidator(validator)
        self.password2.SetValidator(validator)
