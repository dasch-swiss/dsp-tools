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

from KnDialogControl import KnDialogControl, KnDialogTextCtrl, KnDialogChoice, KnDialogCheckBox, KnCollapsiblePicker

def show_error(msg: str, knerr: KnoraError):
    dlg = wx.MessageDialog(self,
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
                 con: Knora = None,
                 user_iri: str = None,
                 *args, **kw):
        super(UserEntryDialog, self).__init__(*args, **kw,
                                              title="User Entry",
                                              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.user_iri = user_iri
        self.con = con
        try:
            self.user_info = self.con.get_user_by_iri(user_iri)
            self.all_projects = self.con.get_existing_projects(full=True)
            self.all_groups = self.con.get_groups()
        except KnoraError as knerr:
            show_error("Couldn't get information from knora", knerr)
        #pprint(self.all_groups)
        pprint(self.user_info)

        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        gsizer = wx.FlexGridSizer(cols=3)

        self.email = KnDialogTextCtrl(panel1, gsizer, "Email: ", "email", self.user_info['email'])
        self.username = KnDialogTextCtrl(panel1, gsizer, "Username: ", "username", self.user_info['username'])
        self.password = KnDialogTextCtrl(panel1, gsizer, "Password: ", "password", "", style=wx.TE_PASSWORD)
        self.lastname = KnDialogTextCtrl(panel1, gsizer, "Lastname: ", "familyName", self.user_info['familyName'])
        self.firstname = KnDialogTextCtrl(panel1, gsizer, "Firstname: ", "givenName", self.user_info['givenName'])
        self.language = KnDialogChoice(panel1, gsizer, "Language: ", "lang", ["en", "de", "fr", "it"], self.user_info['lang'])

        self.is_sysadmin = False;
        tmp = self.user_info['permissions']['groupsPerProject']
        if tmp.get('http://www.knora.org/ontology/knora-admin#SystemProject') is not None:
            if "http://www.knora.org/ontology/knora-admin#SystemAdmin" in tmp['http://www.knora.org/ontology/knora-admin#SystemProject']:
                self.is_sysadmin = True
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
        project_list_formatter = lambda a: a['shortname'] + ' (' + a['shortcode'] + ')'

        self.all_projs = list(map(project_list_formatter, self.all_projects)) # all projects
        self.all_proj_iris = list(map(lambda a: a['id'], self.all_projects))

        chosen_projs = list(map(project_list_formatter, self.user_info['projects']))  # projects user is in
        #self.sel_proj_iris = list(map(lambda a: a['id'], user_info['projects']))

        available_projs = list(filter(lambda a: a not in chosen_projs, self.all_projs))

        self.projsel = KnCollapsiblePicker(self,
                                           topsizer,
                                           "Member of projects:",
                                           available_projs,
                                           chosen_projs,
                                           [],
                                           self.proj_cb,
                                           self.add_to_proj,
                                           self.rm_from_proj)

        # get list of selected project IRI's
        sp = self.projsel.GetCheckedItems()
        sel_proj_iris = []
        for i in sp:
            sel_proj_iris.append(self.all_proj_iris[i])

        # select the right groups
        self.group_list_formatter = lambda a: a['name'] + ' (' + a['project']['shortname'] + ')'
        valid_grps = list(filter(lambda a: a['project']['id'] in sel_proj_iris, self.all_groups))
        all_grps = list(map(self.group_list_formatter, valid_grps))
        sel_grps = list(map(self.group_list_formatter, self.user_info['groups']))
        #self.group_iris = list(map(lambda a: a['id'], valid_groups))

        #self.grpsel = KnCollapsileChecklist(self, topsizer, "Member of groups:", all_grps, sel_grps, self.group_cb)

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
        i = self.all_projs.index(s)
        proj_iri = self.all_proj_iris[i]
        self.con.add_user_to_project(self.user_iri, proj_iri)

    def rm_from_proj(self, s):
        i = self.all_projs.index(s)
        proj_iri = self.all_proj_iris[i]
        self.con.rm_user_from_project(self.user_iri, proj_iri)

    def proj_cb(self, event):
        print("Projects CheckListBox changed!")
        sp = self.projsel.GetCheckedItems()
        sel_proj_iris = []
        for i in sp:
            sel_proj_iris.append(self.all_proj_iris[i])
        valid_grps = list(filter(lambda a: a['project']['id'] in sel_proj_iris, self.all_groups))
        all_grps = list(map(self.group_list_formatter, valid_grps))
        sel_grps = list(map(self.group_list_formatter, self.user_info['groups']))
        self.grpsel.rebuild(all_grps, sel_grps)

    def group_cb(self, event):
        print("Groups CheckListBox changed!")






