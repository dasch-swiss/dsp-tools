from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from knora import KnoraError, Knora
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
if not path in sys.path:
    sys.path.append(path)

from models.Helpers import Languages, Actions, LangString
from models.KnoraUser import KnoraUser
from models.Connection import Connection

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
        self.edit_button.Bind(wx.EVT_BUTTON, self.start_entry)
        self.new_button = wx.Button(parent=self, label="new")
        self.new_button.Bind(wx.EVT_BUTTON, self.new_entry)
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection):
        self.con = con

    def update(self, con: Connection):
        users = KnoraUser.getAllUsers(con)
        self.listctl.DeleteAllItems()
        for user in users:
            self.listctl.Append((user.username, user.familyName, user.givenName, user.email))
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

    def start_entry(self, event):
        idx = self.listctl.GetFirstSelected()
        user_iri = self.ids[idx]
        ue = UserEntryDialog(self.con, user_iri, False, self)
        res = ue.ShowModal()
        if res == wx.ID_OK:
            changeset = ue.get_changed()
            try:

                self.con.update_user(user_iri=user_iri,
                                     username=changeset['username'],
                                     email=changeset['email'],
                                     given_name=changeset['firstname'],
                                     family_name=changeset['lastname'],
                                     lang=changeset['language'])
            except KnoraError as knerr:
                show_error("Setting user data failed!", knerr)
                return

            if changeset['password'] is not None:
                dlg = wx.TextEntryDialog(
                    self, 'Please enter Your admin password', 'Password',
                    style=wx.TE_PASSWORD | wx.OK | wx.CANCEL)
                if dlg.ShowModal() == wx.ID_OK:
                    admin_password = dlg.GetValue()
                    try:
                        self.con.change_user_password(user_iri=user_iri,
                                                      admin_password=admin_password,
                                                      new_password=changeset['password'])
                    except KnoraError as knerr:
                        show_error("Setting the password failed!", knerr)

                dlg.Destroy()

            if changeset['sysadmin'] is not None:
                try:
                    if changeset['sysadmin']:
                        self.con.add_user_to_sysadmin(user_iri=user_iri)
                    else:
                        self.con.rm_user_from_sysadmin(user_iri=user_iri)
                except KnoraError as knerr:
                    show_error("Modifying the sysadmin flag failed!", knerr)


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

    def __init__(self,
                 con: Connection = None,
                 user_iri: str = None,
                 newentry: bool = True,
                 *args, **kw):
        super(UserEntryDialog, self).__init__(*args, **kw,
                                              title="User Entry",
                                              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.user_iri = user_iri
        self.con = con
        try:
            if not newentry:
                tmpuser = KnoraUser(con=con, id=user_iri)
                self.user = tmpuser.read()
            else:
                self.user = KnoraUser(con=con)
            self.all_projects = KnoraProject.getAllProjects(con)
            self.all_groups = self.con.get_groups()
        except KnoraError as knerr:
            show_error("Couldn't get information from knora", knerr)
            return
        #pprint(self.all_groups)
        pprint(self.user_info)

        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
        else:
            cols = 3
        gsizer = wx.FlexGridSizer(cols=cols)

        self.email = KnDialogTextCtrl(panel1, gsizer, "Email: ", "email", self.user_info['email'])
        self.username = KnDialogTextCtrl(panel1, gsizer, "Username: ", "username", self.user_info['username'])
        self.password = KnDialogTextCtrl(panel1, gsizer, "Password: ", "password", self.user_info['password'], style=wx.TE_PASSWORD)
        self.lastname = KnDialogTextCtrl(panel1, gsizer, "Lastname: ", "familyName", self.user_info['familyName'])
        self.firstname = KnDialogTextCtrl(panel1, gsizer, "Firstname: ", "givenName", self.user_info['givenName'])
        self.language = KnDialogChoice(panel1, gsizer, "Language: ", "lang", ["en", "de", "fr", "it"], self.user_info['lang'])

        self.is_sysadmin = False;
        if not newentry:
            tmp = self.user_info['permissions']['groupsPerProject']
            if tmp.get('http://www.knora.org/ontology/knora-admin#SystemProject') is not None:
                if "http://www.knora.org/ontology/knora-admin#SystemAdmin" in tmp['http://www.knora.org/ontology/knora-admin#SystemProject']:
                    self.is_sysadmin = True
        else:
            self.is_sysadmin = None
        self.sysadmin = KnDialogCheckBox(panel1, gsizer, "Sysadmin: ", " ", self.is_sysadmin)
        self.status = KnDialogCheckBox(panel1, gsizer, "Status: ", "active", self.user_info['status'])

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)

        #
        # preparing project information
        #
        if not newentry:
            tmp = list(filter(lambda a: 'http://www.knora.org/ontology/knora-admin#ProjectMember' in a[1], self.user_info['permissions']['groupsPerProject'].items()))
            member_proj_iris = list(map(lambda a: a[0], tmp))

            tmp = list(filter(lambda a: 'http://www.knora.org/ontology/knora-admin#ProjectAdmin' in a[1], self.user_info['permissions']['groupsPerProject'].items()))
            admin_proj_iris = list(map(lambda a: a[0], tmp))

        project_list_formatter = lambda a: (a['shortname'] + ' (' + a['shortcode'] + ')', a['id'])

        self.projmap_name_iri = dict(map(lambda a: (a['shortname'] + ' (' + a['shortcode'] + ')', a['id']), self.all_projects)) # all projects
        self.projmap_iri_name = dict(map(lambda a: (a['id'], a['shortname'] + ' (' + a['shortcode'] + ')'), self.all_projects))

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


        self.group_list_formatter = lambda a: a['name'] + ' (' + a['project']['shortname'] + ')'
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

    def get_changed(self):
        return {
            "email": self.email.get_changed(),
            "username": self.username.get_changed(),
            "lastname": self.lastname.get_changed(),
            "firstname": self.firstname.get_changed(),
            "language": self.language.get_changed(),
            "status": self.status.get_changed(),
            "password": self.password.get_changed(),
            "sysadmin": self.sysadmin.get_changed()
        }

    def add_to_proj(self, s):
        proj_iri = self.projmap_name_iri[s]
        try:
            self.con.add_user_to_project(self.user_iri, proj_iri)
        except KnoraError as knerr:
            show_error("Coudn't add user to project!", knerr)
        self.member_proj_names.append(s)
        self.notmember_proj_names.remove(s)

    def rm_from_proj(self, s):
        proj_iri = self.projmap_name_iri[s]
        # if user is also admin of project, we first remove him from being an admin
        if s in self.admin_proj_names:
            try:
                self.con.rm_user_from_project_admin(self.user_iri, proj_iri)
            except:
                show_error("Couldn't remove user from project admin!")
            self.admin_proj_names.remove(s)
        try:
            self.con.rm_user_from_project(self.user_iri, proj_iri)
        except KnoraError as knerr:
            show_error("Couldn't remove user from project!", knerr)
        self.member_proj_names.remove(s)
        self.notmember_proj_names.append(s)

    def projadmin_cb(self, s, on) -> bool:
        proj_iri = self.projmap_name_iri[s]
        try:
            if on:
                self.con.add_user_to_project_admin(self.user_iri, proj_iri)
            else:
                self.con.rm_user_from_project_admin(self.user_iri, proj_iri)
        except KnoraError as knerr:
            show_error("Couldn't modify admin flag of project", knerr)
            return False
        return True

    def group_cb(self, s, on) -> bool:
        print("Groups CheckListBox changed!")






