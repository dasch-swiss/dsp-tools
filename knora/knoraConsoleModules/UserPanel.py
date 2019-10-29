from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from typing import List, Set, Dict, Tuple, Optional
from knora import KnoraError, Knora
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsileChecklist

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
        idx = self.listctl.GetFirstSelected()
        user_iri = self.ids[idx]
        ue = UserEntryDialog(self.con, user_iri, self)
        res = ue.ShowModal()
        if res == wx.ID_OK:
            changeset = ue.get_changed()
            pprint(changeset)
            self.con.update_user(user_iri=user_iri,
                                 username=changeset['username'],
                                 email=changeset['email'],
                                 given_name=changeset['firstname'],
                                 family_name=changeset['lastname'],
                                 lang=changeset['language'])
            if changeset['username'] is not None:
                self.listctl.SetItem(idx, 0, changeset['username'])
            if changeset['lastname'] is not None:
                self.listctl.SetItem(idx, 1, changeset['lastname'])
            if changeset['firstname'] is not None:
                self.listctl.SetItem(idx, 2, changeset['firstname'])
            if changeset['email'] is not None:
                self.listctl.SetItem(idx, 3, changeset['email'])
        ue.Destroy()

class UserEntryDialog(wx.Dialog):

    def __init__(self, con: Knora = None, iri: str = None, *args, **kw):
        super(UserEntryDialog, self).__init__(*args, **kw,
                                              title="User Entry",
                                              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        user_info = con.get_user_by_iri(iri)
        existing_projects = con.get_existing_projects(full=True)
        existing_groups = con.get_groups()
        pprint(existing_groups)

        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        gsizer = wx.FlexGridSizer(cols=3)

        self.email = KnDialogTextCtrl(panel1, gsizer, "Email: ", "email", user_info['email'])
        self.username = KnDialogTextCtrl(panel1, gsizer, "Username: ", "username", user_info['username'])
        self.password = KnDialogTextCtrl(panel1, gsizer, "Password: ", "password", "", style=wx.TE_PASSWORD)
        self.lastname = KnDialogTextCtrl(panel1, gsizer, "Lastname: ", "familyName", user_info['familyName'])
        self.firstname = KnDialogTextCtrl(panel1, gsizer, "Firstname: ", "givenName", user_info['givenName'])
        self.language = KnDialogChoice(panel1, gsizer, "Language: ", "lang", ["en", "de", "fr", "it"], user_info['lang'])
        self.status = KnDialogCheckBox(panel1, gsizer, "Status: ", "status", user_info['status'])



        #gsizer.Add(projects_l, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL, border=3)
        #gsizer.Add(projsizer, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.GROW | wx.ALL, border=3)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)


        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        project_list_formatter = lambda a: a['shortname'] + ' (' + a['shortcode'] + ')'
        plist = list(map(project_list_formatter, user_info['projects'])) # projects user is in
        projs = list(map(project_list_formatter, existing_projects)) # all projects
        projs.sort()

        projsel = KnCollapsileChecklist(self, topsizer, "Member of projects:", projs, plist)

        group_list_formatter = lambda a: a['name'] + ' (' + a['project']['shortname'] + ')'
        groups = list(map(group_list_formatter, existing_groups))

        grpsel = KnCollapsileChecklist(self, topsizer, "Member of groups:", groups, [])

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def get_changed(self):
        return {
            "email": self.email.get_changed(),
            "username": self.username.get_changed(),
            "lastname": self.lastname.get_changed(),
            "firstname": self.firstname.get_changed(),
            "language": self.language.get_changed(),
        }






