import os
import sys
import wx
from typing import List, Set, Dict, Tuple, Optional
from knora import KnoraError, Knora
from pprint import pprint

class UserPanel(wx.Panel):
    """
    User tab
    """
    def __init__(self, *args, **kw):
        super(UserPanel, self).__init__(*args, **kw)

        self.con = None
        self.ids = []

        topsizer = wx.BoxSizer(wx.VERTICAL)

        self.listctl = wx.ListCtrl(self, name="Users:",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.listctl.AppendColumn("Username", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Lastname", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Firstname", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Email", width=wx.LIST_AUTOSIZE)

        topsizer.Add(self.listctl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_button = wx.Button(parent=self, label="edit")
        self.edit_button.Bind(wx.EVT_BUTTON, self.start_entry)
        self.new_button = wx.Button(parent=self, label="new")
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Knora):
        self.con = con

    def update(self, con: Knora):
        users = con.get_users()
        self.listctl.DeleteAllItems()
        for user in users:
            self.listctl.Append((user['username'], user['familyName'], user['givenName'], user['email']))
            self.ids.append(user['id'])
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.SetColumnWidth(3, -1)
        self.listctl.Select(0)

    def start_entry(self, event):
        ue = UserEntryDialog(self.con, self.ids[self.listctl.GetFirstSelected()], self)
        #ue = UserEntryDialog(self)

class UserEntryDialog(wx.Dialog):
    def __init__(self, con: Knora = None, iri: str = None, *args, **kw):
        super(UserEntryDialog, self).__init__(*args, **kw,
                                              title="User Entry",
                                              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        user_info = con.get_user_by_iri(iri)
        existing_projects = con.get_existing_projects(full=True)
        pprint(user_info)
        pprint(existing_projects)

        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)

        gsizer = wx.FlexGridSizer(cols=2)

        username_l = wx.StaticText(panel1, label="Username: ")
        username = wx.TextCtrl(panel1, name="Username", value=user_info['username'], size=wx.Size(200, -1))
        gsizer.Add(username_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(username, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

        password_l = wx.StaticText(panel1, label="Password: ")
        password = wx.TextCtrl(panel1, name="password", value="test", size=wx.Size(200, -1), style=wx.TE_PASSWORD)
        gsizer.Add(password_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(password, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

        lastname_1 = wx.StaticText(panel1, label="Lastname: ")
        lastname = wx.TextCtrl(panel1, name="lastname", value=user_info['familyName'], size=wx.Size(200, -1))
        gsizer.Add(lastname_1, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(lastname, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

        firstname_l = wx.StaticText(panel1, label="Firstname: ")
        firstname = wx.TextCtrl(panel1, name="firstname", value=user_info['givenName'], size=wx.Size(200, -1))
        gsizer.Add(firstname_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(firstname, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

        langswitcher = {
            "en": 0,
            "de": 1,
            "fr": 2,
            "it": 3
        }
        language_l = wx.StaticText(panel1, label="Language: ")
        language = wx.Choice(panel1, choices=["en", "de", "fr", "it"])
        language.SetSelection(langswitcher[user_info['lang']])
        gsizer.Add(language_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(language, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

        status_l = wx.StaticText(panel1, label="Status: ")
        status = wx.CheckBox(panel1, label="active")
        status.SetValue(user_info['status'])
        gsizer.Add(status_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)
        gsizer.Add(status, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=3)

        projects_l = wx.StaticText(panel1, label="Projects: ")
        plist = list(map(lambda a: a['shortname'] + ' (' + a['shortcode'] + ')', user_info['projects']))

        projects = wx.CheckListBox(panel1, choices=plist)
        for i in range(len(plist)):
            projects.Check(i)
        projsizer = wx.BoxSizer(wx.VERTICAL)
        projsizer.Add(projects, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL)
        projs = list(map(lambda a: a['shortname'] + ' (' + a['shortcode'] + ')', existing_projects))
        projlist = wx.Choice(panel1, choices=projs)
        projsizer.Add(projlist, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL)

        gsizer.Add(projects_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL, border=3)
        gsizer.Add(projsizer, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL, border=3)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)
        self.ShowModal()
