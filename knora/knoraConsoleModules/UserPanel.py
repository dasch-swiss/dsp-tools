from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from knora import KnoraError, Knora
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from models.helpers import Languages, Actions, LangString
from models.user import User
from models.project import Project
from models.group import Group
from models.connection import Connection

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker

def show_error(msg: str, knerr: KnoraError):
    dlg = wx.MessageDialog(None,
                           message=msg + "\n" + knerr.message,
                           caption='Error',
                           style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


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
        self.edit_button.Bind(wx.EVT_BUTTON, self.edit_entry)
        self.new_button = wx.Button(parent=self, label="new")
        self.new_button.Bind(wx.EVT_BUTTON, self.new_entry)
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self):
        users = User.getAllUsers(self.con)
        self.listctl.DeleteAllItems()
        for user in users:
            self.listctl.Append((user.username,
                                 user.familyName,
                                 user.givenName,
                                 user.email))
            self.ids.append(user.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.SetColumnWidth(3, -1)
        self.listctl.Select(0)

    def new_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        user_iri = self.ids[idx]
        ue = UserEntryDialog(self.con, user_iri, True, self)
        res = ue.ShowModal()
        if res == wx.ID_OK:
            user = ue.get_value()
            user = user.create()
            self.listctl.Append((user.username,
                                 user.familyName,
                                 user.givenName,
                                 user.email))
            self.ids.append(user.id)


    def edit_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        user_iri = self.ids[idx]
        ue = UserEntryDialog(self.con, user_iri, False, self)
        res = ue.ShowModal()
        if res == wx.ID_OK:
            user: User = ue.get_changed()
            if 'password' in user.changed:
                dlg = wx.TextEntryDialog(
                    self, 'Please enter Your admin password', 'Password',
                    style=wx.TE_PASSWORD | wx.OK | wx.CANCEL)
                if dlg.ShowModal() == wx.ID_OK:
                    admin_password = dlg.GetValue()
                    user = user.update(admin_password)
                dlg.Destroy()
            else:
                user.print()
                user = user.update()

            self.listctl.SetItem(idx, 0, user.username)
            self.listctl.SetItem(idx, 1, user.familyName)
            self.listctl.SetItem(idx, 2, user.givenName)
            self.listctl.SetItem(idx, 3, user.email)

        ue.Destroy()

class UserEntryDialog(wx.Dialog):

    def __init__(self,
                 con: Connection = None,
                 user_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        super().__init__(*args, **kw,
                         title="User Entry",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.user_iri = user_iri
        self.con = con
        try:
            if newentry:
                self.user = User(con=con)
            else:
                tmpuser = User(con=con, id=user_iri)
                self.user = tmpuser.read()
            self.all_projects = Project.getAllProjects(con)
            self.all_groups = Group.getAllGroups(con)
        except KnoraError as knerr:
            show_error("Couldn't get information from knora", knerr)
            return
        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
        else:
            cols = 3
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_email = None if newentry else self.user.email if self.user.email is not None else ""
        self.email = KnDialogTextCtrl(panel1, gsizer, "Email: ", "email", tmp_email)

        tmp_username = None if newentry else self.user.username if self.user.username is not None else ""
        self.username = KnDialogTextCtrl(panel1, gsizer, "Username: ", "username", tmp_username)

        tmp_password = None if newentry else ""
        self.password = KnDialogTextCtrl(panel1, gsizer, "Password: ", "password", tmp_password, style=wx.TE_PASSWORD)
        self.password2 = KnDialogTextCtrl(panel1, gsizer, "Password: ", "password", tmp_password, style=wx.TE_PASSWORD)

        tmp_familyName = None if newentry else self.user.familyName if self.user.familyName is not None else ""
        self.familyName = KnDialogTextCtrl(panel1, gsizer, "Lastname: ", "familyName", self.user.familyName)

        tmp_givenName = None if newentry else self.user.givenName if self.user.givenName is not None else ""
        self.givenName = KnDialogTextCtrl(panel1, gsizer, "Firstname: ", "givenName", self.user.givenName)

        self.lang = KnDialogChoice(panel1, gsizer, "Language: ", "lang", ["en", "de", "fr", "it"], None if self.user.lang is None else self.user.lang.value)
        self.sysadmin = KnDialogCheckBox(panel1, gsizer, "Sysadmin: ", " ", self.user.sysadmin)
        self.status = KnDialogCheckBox(panel1, gsizer, "Status: ", "active", self.user.status)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        #
        # preparing project information
        #
        if not newentry:
            tmp = list(filter(lambda a: not a[1], self.user.in_projects.items()))
            #member_proj_iris = list(map(lambda a: a[0], tmp))
            member_proj_iris = list(map(lambda a: a[0], self.user.in_projects.items()))

            tmp = list(filter(lambda a: a[1], self.user.in_projects.items()))
            admin_proj_iris = list(map(lambda a: a[0], tmp))

        project_list_formatter = lambda a: (a.shortname + ' (' + a.shortcode + ')', a.id)

        self.projmap_name_iri = dict(map(lambda a: (a.shortname + ' (' + a.shortcode + ')', a.id), self.all_projects)) # all projects
        self.projmap_iri_name = dict(map(lambda a: (a.id, a.shortname + ' (' + a.shortcode + ')'), self.all_projects))

        if not newentry:
            self.member_proj_names = list(map(lambda a: self.projmap_iri_name[a], member_proj_iris))
            notmember_proj_iris = list(filter(lambda a: a not in member_proj_iris, list(self.projmap_iri_name.keys())))
        else:
            self.member_proj_names = []
            notmember_proj_iris = list(self.projmap_iri_name.keys())

        self.notmember_proj_names = list(map(lambda a: self.projmap_iri_name[a], notmember_proj_iris))

        if not newentry:
            self.admin_proj_names = list(map(lambda a: self.projmap_iri_name[a], admin_proj_iris))
        else:
            self.admin_proj_names = []

        self.projsel = KnCollapsiblePicker(parent=self,
                                           sizer=topsizer,
                                           label="Is in project: (Checked: admin)",
                                           available=self.notmember_proj_names,
                                           chosen=self.member_proj_names,
                                           selected=self.admin_proj_names,
                                           on_change_cb=self.projadmin_cb,
                                           on_add_cb=self.add_to_proj,
                                           on_rm_cb=self.rm_from_proj)

        self.group_list_formatter = lambda a: a.name
        all_group_names = list(map(self.group_list_formatter, self.all_groups))

        self.grpsel = KnCollapsiblePicker(parent=self,
                                          sizer=topsizer,
                                          label="Member of groups:",
                                          available=None,
                                          chosen=all_group_names,
                                          selected=[],
                                          on_change_cb=self.group_cb)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def get_value(self) -> User:
        self.user.email = self.email.get_value()
        self.user.username = self.username.get_value()
        self.user.familyName = self.familyName.get_value()
        self.user.givenName = self.givenName.get_value()
        print('==>LANG: ', self.lang.get_value())
        self.user.lang = self.lang.get_value()
        self.user.status = self.status.get_value()
        self.user.password = self.password.get_value()
        self.user.sysadmin = self.sysadmin.get_value()
        return self.user

    def get_changed(self) -> User:
        self.user.email = self.email.get_changed()
        self.user.username = self.username.get_changed()
        self.user.familyName = self.familyName.get_changed()
        self.user.givenName = self.givenName.get_changed()
        self.user.lang = self.lang.get_changed()
        self.user.status = self.status.get_changed()
        self.user.password = self.password.get_changed()
        self.user.sysadmin = self.sysadmin.get_changed()
        return self.user

    def add_to_proj(self, s)-> None:
        proj_iri = self.projmap_name_iri[s]
        try:
            self.user.addToProject(proj_iri)
        except BaseError as knerr:
            show_error("Coudn't add user to project!", knerr)
        self.member_proj_names.append(s)
        self.notmember_proj_names.remove(s)

    def rm_from_proj(self, s) -> None:
        proj_iri = self.projmap_name_iri[s]
        # if user is also admin of project, we first remove him from being an admin
        try:
            self.user.rmFromProject(proj_iri)
        except BaseError as knerr:
            show_error("Couldn't remove user from project!", knerr)
        self.member_proj_names.remove(s)
        self.notmember_proj_names.append(s)

    def projadmin_cb(self, s, on) -> bool:
        proj_iri = self.projmap_name_iri[s]
        try:
            if on:
                self.user.makeProjectAdmin(proj_iri)
            else:
                self.user.unmakeProjectAdmin(proj_iri)
        except BaseError as knerr:
            show_error("Couldn't modify admin flag of project", knerr)
            return False
        return True

    def group_cb(self, s, on) -> bool:
        print("Groups CheckListBox changed!")






