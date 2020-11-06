import sys
import wx
import wx.adv

from datetime import date as dt


class FormHelper:

    def add_widgets(self):
        pass


class DateCtrl(wx.ComboCtrl):
    INPUT_FORMAT = 0
    DISPLAY_FORMAT = 1

    def __init__(self, parent, size, pos, input_format, display_format,
            title, default_to_today, allow_null):
        wx.ComboCtrl.__init__(self, parent, size=size, pos=pos)

        self.input_format = input_format
        self.display_format = display_format
        self.title = title
        self.default_to_today = default_to_today
        self.allow_null = allow_null

        self.TextCtrl.Bind(wx.EVT_SET_FOCUS, self.on_got_focus)
        self.TextCtrl.Bind(wx.EVT_CHAR, self.on_char)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)

        self.nav = False  # force navigation after selecting date
        self.is_valid = True  # unlike IsValid(), a blank date can be valid
        self.current_format = self.DISPLAY_FORMAT
        self.date = wx.DateTime()
        self.setup_button()  # create a custom button for popup
        (self.blank_string, self.yr_pos, self.mth_pos, self.day_pos,
            self.literal_pos) = self.setup_input_format()

        # set up button coords for mouse hit-test
        self.b_x1 = self.TextRect[2] - 2
        self.b_y1 = self.TextRect[1] - 1
        self.b_x2 = self.b_x1 + self.ButtonSize[0] + 3
        self.b_y2 = self.b_y1 + self.ButtonSize[1] + 1
        self.on_button = False

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.show_tooltip)

    def on_mouse_enter(self, evt):
        if self.b_x1 <= evt.X <= self.b_x2:
            if self.b_y1 <= evt.Y <= self.b_y2:
                self.on_button = True
                self.timer.Start(500, oneShot=True)
        evt.Skip()

    def on_mouse_leave(self, evt):
        if self.on_button:
            self.on_button = False
            self.timer.Stop()
        evt.Skip()

    def show_tooltip(self, evt):
        abs_x, abs_y = self.ScreenPosition
        rect = wx.Rect(abs_x+self.b_x1, abs_y+self.b_y1,
            self.b_x2-self.b_x1+1, self.b_y2-self.b_y1+1)
        tip = wx.TipWindow(self, 'Press to pick a date)')
        # tip will be destroyed when mouse leaves this rect
        tip.SetBoundingRect(rect)

    def setup_button(self):  # copied directly from demo
        # make a custom bitmap showing "..."
        bw, bh = 14, 16
        bmp = wx.Bitmap(bw, bh)
        dc = wx.MemoryDC(bmp)

        # clear to a specific background colour
        bgcolor = wx.Colour(255, 254, 255)
        dc.SetBackground(wx.Brush(bgcolor))
        dc.Clear()

        # draw the label onto the bitmap
        label = u'\u2026'  # unicode ellipsis
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, (bw-tw), (bw-tw))
        del dc

        # now apply a mask using the bgcolor
        bmp.SetMaskColour(bgcolor)

        # and tell the ComboCtrl to use it
        self.SetButtonBitmaps(bmp, True)

    def setup_input_format(self):
        """
        Modify the defined input format to a string where each character
        represents one character of the input string.
        Generate and return a blank string to fill in the control.
        Return positions within the string of yr, mth, day and literals.
        """
        format = self.input_format
        blank_string = format

        yr_pos = format.find('%y')
        if yr_pos > -1:
            blank_string = blank_string[:yr_pos]+'  '+blank_string[yr_pos+2:]
            yr_pos = (yr_pos, yr_pos+2)
        else:
            yr_pos = format.find('%Y')
            if yr_pos > -1:
                blank_string = blank_string[:yr_pos]+'    '+blank_string[yr_pos+2:]
                format = format[:yr_pos+2]+'YY'+format[yr_pos+2:]
                yr_pos = (yr_pos, yr_pos+4)

        mth_pos = format.find('%m')
        if mth_pos > -1:
            blank_string = blank_string[:mth_pos]+'  '+blank_string[mth_pos+2:]
            mth_pos = (mth_pos, mth_pos+2)

        day_pos = format.find('%d')
        if day_pos > -1:
            blank_string = blank_string[:day_pos]+'  '+blank_string[day_pos+2:]
            day_pos = (day_pos, day_pos+2)

        literal_pos = [i for (i, ch) in enumerate(blank_string)
            if blank_string[i] == format[i]]

        return blank_string, yr_pos, mth_pos, day_pos, literal_pos

    # Overridden from ComboCtrl, called when the combo button is clicked
    def OnButtonClick(self):
        self.SetFocus()  # in case we do not have focus
        dlg = CalendarDlg(self)
        dlg.CentreOnScreen()
        if dlg.ShowModal() == wx.ID_OK:
            self.date = dlg.cal.Date
            self.Value = self.date.Format(self.display_format)
            self.current_format = self.DISPLAY_FORMAT
            self.nav = True  # force navigation to next control
        dlg.Destroy()

    # Overridden from ComboCtrl to avoid assert since there is no ComboPopup
    def DoSetPopupControl(self, popup):
        pass

    def on_got_focus(self, evt):
        if self.nav:  # user has made a selection, so move on
            self.nav = False
            wx.CallAfter(self.Navigate)
        else:
            text_ctrl = self.TextCtrl
            if not self.is_valid:  # re-focus after error
                pass  # leave Value alone
            elif self.date.IsValid():
                text_ctrl.Value = self.date.Format(self.input_format)
            elif self.default_to_today:
                self.date = wx.DateTime.Today()
                text_ctrl.Value = self.date.Format(self.input_format)
            else:
                text_ctrl.Value = self.blank_string
            self.current_format = self.INPUT_FORMAT
            text_ctrl.InsertionPoint = 0
            text_ctrl.SetSelection(-1, -1)
            text_ctrl.pos = 0
        evt.Skip()

    def convert_to_wx_date(self):  # conversion and validation method
        self.is_valid = True

        value = self.Value
        if value in (self.blank_string, ''):
            if self.default_to_today:
                self.date = wx.DateTime.Today()
                self.Value = self.date.Format(self.display_format)
            elif self.allow_null:
                self.date = wx.DateTime()
                self.Value = ''
            else:
                wx.CallAfter(self.display_error, 'Date is required')
            return

        if self.current_format == self.DISPLAY_FORMAT:  # no validation reqd
            self.TextCtrl.SetSelection(0, 0)
            return

        today = dt.today()

        if self.yr_pos == -1:  # 'yr' not an element of input_format
            year = today.year
        else:
            year = value[self.yr_pos[0]:self.yr_pos[1]].strip()
            if year == '':
                year = today.year
            elif len(year) == 2:
                # assume year is in range (today-90) to (today+10)
                year = int(year) + int(today.year/100)*100
                if year - today.year > 10:
                    year -= 100
                elif year - today.year < -90:
                    year += 100
            else:
                year = int(year)

        if self.mth_pos == -1:  # 'mth' not an element of input_format
            month = today.month
        else:
            month = value[self.mth_pos[0]:self.mth_pos[1]].strip()
            if month == '':
                month = today.month
            else:
                month = int(month)

        if self.day_pos == -1:  # 'day' not an element of input_format
            day = today.day
        else:
            day = value[self.day_pos[0]:self.day_pos[1]].strip()
            if day == '':
                day = today.day
            else:
                day = int(day)

        try:
            date = dt(year, month, day)  # validate using python datetime
        except ValueError as error:  # gives a meaningful error message
            wx.CallAfter(self.display_error, error.args[0])
        else:  # date is valid
            self.date = wx.DateTimeFromDMY(day, month-1, year)
            self.Value = self.date.Format(self.display_format)
            self.current_format = self.DISPLAY_FORMAT

    def display_error(self, errmsg):
        self.is_valid = False
        self.SetFocus()
        dlg = wx.MessageDialog(self, errmsg,
            self.title, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def on_char(self, evt):
        text_ctrl = self.TextCtrl
        code = evt.KeyCode
        if code in (wx.WXK_SPACE, wx.WXK_F4) and not evt.AltDown():
            self.OnButtonClick()
            return
        max = len(self.blank_string)
        if code in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_HOME, wx.WXK_END):
            if text_ctrl.Selection == (0, max):
                text_ctrl.SetSelection(0, 0)
            if code == wx.WXK_LEFT:
                if text_ctrl.pos > 0:
                    text_ctrl.pos -= 1
                    while text_ctrl.pos in self.literal_pos:
                        text_ctrl.pos -= 1
            elif code == wx.WXK_RIGHT:
                if text_ctrl.pos < max:
                    text_ctrl.pos += 1
                    while text_ctrl.pos in self.literal_pos:
                        text_ctrl.pos += 1
            elif code == wx.WXK_HOME:
                text_ctrl.pos = 0
            elif code == wx.WXK_END:
                text_ctrl.pos = max
            text_ctrl.InsertionPoint = text_ctrl.pos
            return
        if code in (wx.WXK_BACK, wx.WXK_DELETE):
            if text_ctrl.Selection == (0, max):
                text_ctrl.Value = self.blank_string
                text_ctrl.SetSelection(0, 0)
            if code == wx.WXK_BACK:
                if text_ctrl.pos == 0:
                    return
                text_ctrl.pos -= 1
                while text_ctrl.pos in self.literal_pos:
                    text_ctrl.pos -= 1
            elif code == wx.WXK_DELETE:
                if text_ctrl.pos == max:
                    return
            curr_val = text_ctrl.Value
            text_ctrl.Value = curr_val[:text_ctrl.pos]+' '+curr_val[text_ctrl.pos+1:]
            text_ctrl.InsertionPoint = text_ctrl.pos
            return
        if code in (wx.WXK_TAB, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) or code > 255:
            evt.Skip()
            return
        if text_ctrl.pos == max:
            wx.Bell()
            return
        ch = chr(code)
        if ch not in ('0123456789'):
            wx.Bell()
            return
        if text_ctrl.Selection == (0, max):
            curr_val = self.blank_string
        else:
            curr_val = text_ctrl.Value
        text_ctrl.Value = curr_val[:text_ctrl.pos]+ch+curr_val[text_ctrl.pos+1:]
        text_ctrl.pos += 1
        while text_ctrl.pos in self.literal_pos:
            text_ctrl.pos += 1
        text_ctrl.InsertionPoint = text_ctrl.pos

class CalendarDlg(wx.Dialog):
    def __init__(self, parent):

        wx.Dialog.__init__(self, parent, title=parent.title)
        panel = wx.Panel(self, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        cal = wx.adv.GenericCalendarCtrl(panel, date=parent.date)

        if sys.platform != 'win32':
            # gtk truncates the year - this fixes it
            w, h = cal.Size
            cal.Size = (w+15, h+85)
            cal.MinSize = cal.Size

        sizer.Add(cal, 0)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add((0, 0), 1)
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_ok.SetDefault()
        button_sizer.Add(btn_ok, 0, wx.ALL, 2)
        button_sizer.Add((0, 0), 1)
        btn_can = wx.Button(panel, wx.ID_CANCEL)
        button_sizer.Add(btn_can, 0, wx.ALL, 2)
        button_sizer.Add((0, 0), 1)
        sizer.Add(button_sizer, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Fit(panel)
        self.ClientSize = panel.Size

        cal.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        cal.SetFocus()
        self.cal = cal

    def on_key_down(self, evt):
        code = evt.KeyCode
        if code == wx.WXK_TAB:
            self.cal.Navigate()
        elif code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.EndModal(wx.ID_OK)
        elif code == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            evt.Skip()
