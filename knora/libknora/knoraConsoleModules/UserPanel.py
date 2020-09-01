from typing import List, Set, Dict, Tuple, Optional, Any, Union

import os
import sys
import wx
from pprint import pprint
import re

from enum import Enum, unique

from ..models.helpers import Actions, BaseError, Context, Cardinality
from ..models.langstring import Languages, LangStringParam, LangString
from ..models.connection import Connection, Error
from ..models.project import Project
from ..models.listnode import ListNode
from ..models.group import Group
from ..models.user import User
from ..models.ontology import Ontology
from ..models.propertyclass import PropertyClass
from ..models.resourceclass import ResourceClass

from ..knoraConsoleModules.KnDialogControl import show_error, KnDialogControl, KnDialogTextCtrl, KnDialogChoice,\
    KnDialogCheckBox, KnCollapsiblePicker


class UserPanel(wx.Panel):
    """
    User tab where new users can be added or the data of existing users modified. This panel allows also
    to define the project and group memberships.
    """
    def __init__(self, *args, **kw):
        """
        Constructor for the user panel.

        :param args: Other arguments
        :param kw: Other keywords
        """
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
        self.listctl.AppendColumn("Status", width=wx.LIST_AUTOSIZE)

        topsizer.Add(self.listctl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.edit_button = wx.Button(parent=self, label="edit")
        self.edit_button.Bind(wx.EVT_BUTTON, self.edit_entry)
        self.new_button = wx.Button(parent=self, label="new")
        self.new_button.Bind(wx.EVT_BUTTON, self.new_entry)
        self.delete_button = wx.Button(parent=self, label="delete")
        self.delete_button.Bind(wx.EVT_BUTTON, self.delete_entry)
        bottomsizer.Add(self.edit_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.new_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
        bottomsizer.Add(self.delete_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)

        topsizer.Add(bottomsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(topsizer)

    def set_connection(self, con: Connection) -> None:
        """
        Set the connection

        :param con: Connection instance
        :return: None
        """
        self.con = con

    def update(self) -> None:
        """
        Update the list of users

        :return: None
        """
        try:
            users = User.getAllUsers(self.con)
        except BaseError as err:
            show_error("Couldn't get user information!", err)
            return
        self.listctl.DeleteAllItems()
        for user in users:
            self.listctl.Append((user.username,
                                 user.familyName,
                                 user.givenName,
                                 user.email,
                                 'active' if user.status else 'inactive'))
            self.ids.append(user.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.SetColumnWidth(3, -1)
        self.listctl.SetColumnWidth(4, -1)
        self.listctl.Select(0)

    def new_entry(self, event: wx.Event) -> None:
        """
        Create the dialog window for entering a new user.

        :param event: wx.Event
        :return: None
        """
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
                                 user.email,
                                 'active' if user.status else 'inactive'))
            self.ids.append(user.id)

    def edit_entry(self, event: wx.Event) -> None:
        """
        Modify an existing user.

        :param event: wx.Event
        :return: None
        """
        idx = self.listctl.GetFirstSelected()
        user_iri = self.ids[idx]
        ue = UserEntryDialog(self.con, user_iri, False, self)
        res = ue.ShowModal()
        if res == wx.ID_OK:
            user: User = ue.get_changed()
            if user.has_changed('password'):
                dlg = wx.TextEntryDialog(
                    self, 'Please enter Your admin password', 'Password',
                    style=wx.TE_PASSWORD | wx.OK | wx.CANCEL)
                if dlg.ShowModal() == wx.ID_OK:
                    admin_password = dlg.GetValue()
                    try:
                        user = user.update(admin_password)
                    except BaseError as err:
                        show_error("Could not update user information!", err)
                    dlg.Destroy()
            else:
                try:
                    user = user.update()
                except BaseError as err:
                    show_error("Could not update user information!", err)
            self.listctl.SetItem(idx, 0, user.username)
            self.listctl.SetItem(idx, 1, user.familyName)
            self.listctl.SetItem(idx, 2, user.givenName)
            self.listctl.SetItem(idx, 3, user.email)
            self.listctl.SetItem(idx, 4, 'active' if user.status else 'inactive')
        ue.Destroy()

    def delete_entry(self, event: wx.Event) -> None:
        idx = self.listctl.GetFirstSelected()
        user_iri = self.ids[idx]
        dlg = wx.MessageDialog(parent=self,
                               message="Do You really want to delete this user (make it inactive)?",
                               caption="Delete ?",
                               style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            try:
                user = User(con=self.con, id=user_iri).delete()
            except BaseError as err:
                show_error("Couldn't delete user!", err)
            else:
                self.listctl.SetItem(idx, 4, 'active' if user.status else 'inactive')

@unique
class UserFields(Enum):
    EMAIL = 1
    USERNAME = 2
    PASSWORD = 3
    LASTNAME = 4
    FIRSTNAME = 5

class UserValidator(wx.Validator):
    """
    Validator for the input fields...
    """
    def __init__(self, flag: UserFields):
        """
        Constructor for the validator
        :param flag: Must be SHORTCODE, SHORTNAME, LONGNAME, KEYWORDS
        """
        wx.Validator.__init__(self)
        self.flag = flag

    def Clone(self):
        return UserValidator(self.flag)

    def Validate(self, win):
        """
        That's the validator method

        :param win:
        :return:
        """
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()

        if self.flag == UserFields.EMAIL:
            if len(text) == 0:
                wx.MessageBox("An email address must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.fullmatch("^[\w\.\+\-]+\@([\w]+\.)+([a-z]{2,3})$", text):
                wx.MessageBox("Email address not valid", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        elif self.flag == UserFields.USERNAME:
            if len(text) < 4 or len(text) > 50:
                wx.MessageBox("A username with 4 - 50 characters must be given!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.match("^[a-zA-Z0-1-]+([a-zA-Z0-1_\.-]?[a-zA-Z0-1-])+$", text):
                wx.MessageBox("A valid username must be given! (letters A-Z, a-z, 0-9, _, -)", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        elif self.flag == UserFields.LASTNAME or self.flag == UserFields.FIRSTNAME:
            if self.flag == UserFields.LASTNAME:
                field = "lastname"
            else:
                field = 'firstname'
            if len(text) == 0:
                wx.MessageBox("A {} must be given!".format(field), "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.fullmatch("^\\S+$", text):
                wx.MessageBox("A valid {} must not contain whitespace characters!".format(field), "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        elif self.flag == UserFields.PASSWORD:
            if text is None:
                wx.MessageBox("The passwords in both fields must be identical!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if text == "":
                return True
            if len(text) < 8:
                wx.MessageBox("The password must have at least 8 characters!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            if not re.fullmatch("^\\S+$", text):
                wx.MessageBox("A valid password must not contain whitespace characters!", "Error")
                textCtrl.SetBackgroundColour("pink")
                textCtrl.SetFocus()
                textCtrl.Refresh()
                return False
            return True
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

class UserEntryDialog(wx.Dialog):
    """
    Dialog window to create or modify user information
    """
    def __init__(self,
                 con: Connection = None,
                 user_iri: Union[str, None] = None,
                 newentry: bool = True,
                 *args, **kw):
        """
        Constructor of user entry/modify dialog window

        :param con: Connection instance
        :param user_iri: IRI of the user, or None, if a new user should be created
        :param newentry: True, if a new user should created, False, if an existing user should be modified
        :param args: Other args
        :param kw: Other keywords
        """
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
        except BaseError as err:
            show_error("Couldn't get user information from knora", err)
            return
        topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
        else:
            cols = 3
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_email = None if newentry else self.user.email if self.user.email is not None else ""
        self.email = KnDialogTextCtrl(panel=panel1,
                                      gsizer=gsizer,
                                      label="Email: ",
                                      name="email",
                                      value=tmp_email,
                                      validator=UserValidator(flag=UserFields.EMAIL))

        tmp_username = None if newentry else self.user.username if self.user.username is not None else ""
        self.username = KnDialogTextCtrl(panel=panel1,
                                         gsizer=gsizer,
                                         label="Username: ",
                                         name="username",
                                         value=tmp_username,
                                         validator=UserValidator(flag=UserFields.USERNAME))

        tmp_password = None if newentry else ""
        self.password = KnDialogTextCtrl(panel=panel1,
                                         gsizer=gsizer,
                                         label="Password: ",
                                         name="password",
                                         value=tmp_password,
                                         password=True,
                                         validator=wx.DefaultValidator,
                                         changed_cb=self.password_changed)
        self.passwd_validator = False

        tmp_familyName = None if newentry else self.user.familyName if self.user.familyName is not None else ""
        self.familyName = KnDialogTextCtrl(panel=panel1,
                                           gsizer=gsizer,
                                           label="Lastname: ",
                                           name="familyName",
                                           value=tmp_familyName,
                                           validator=UserValidator(flag=UserFields.LASTNAME))

        tmp_givenName = None if newentry else self.user.givenName if self.user.givenName is not None else ""
        self.givenName = KnDialogTextCtrl(panel=panel1,
                                          gsizer=gsizer,
                                          label="Firstname: ",
                                          name="givenName",
                                          value=tmp_givenName,
                                          validator=UserValidator(flag=UserFields.FIRSTNAME))

        self.lang = KnDialogChoice(panel=panel1,
                                   gsizer=gsizer,
                                   label="Language: ",
                                   name="lang",
                                   choices=[x.value for x in Languages],
                                   value=None if self.user.lang is None else self.user.lang.value)
        self.sysadmin = KnDialogCheckBox(panel=panel1,
                                         gsizer=gsizer,
                                         label="Sysadmin: ",
                                         name="sysadmin",
                                         status=self.user.sysadmin)
        self.status = KnDialogCheckBox(panel=panel1,
                                       gsizer=gsizer,
                                       label="Status: ",
                                       name="active",
                                       status=self.user.status)

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
            member_proj_iris = list(map(lambda a: a[0], self.user.in_projects.items()))

            tmp = list(filter(lambda a: a[1], self.user.in_projects.items()))
            admin_proj_iris = list(map(lambda a: a[0], tmp))

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

        all_group_names = [a.name for a in self.all_groups]  # list(map(lambda a: a.name, self.all_groups))
        self.grpmap_name_iri = {a.name: a.id for a in self.all_groups}  # dict(map(lambda a: (a.name, a.id), self.all_groups))
        self.grpmap_iri_name = {a.id: a.name for a in self.all_groups}  # dict(map(lambda a: (a.id, a.name), self.all_groups))
        self.in_groups = [self.grpmap_iri_name[a] for a in self.user.in_groups]  # list(map(lambda a: self.grpmap_iri_name[a], self.user.in_groups))

        self.grpsel = KnCollapsiblePicker(parent=self,
                                          sizer=topsizer,
                                          label="Member of groups:",
                                          available=None,
                                          chosen=all_group_names,
                                          selected=list(self.in_groups),
                                          on_change_cb=self.group_cb)

        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(topsizer)

    def password_changed(self, event: wx.Event, user_data: Any):
        if not self.passwd_validator:
            self.password.SetValidator(UserValidator(flag=UserFields.PASSWORD))
            self.passwd_validator = True

    def password_reset(self, event: wx.Event):
        if self.passwd_validator:
            self.password.SetValidator(wx.DefaultValidator)
            self.passwd_validator = False

    def get_value(self) -> Union[User, None]:
        """
        Get all the values from the entry dialog and prepare a User instance

        :return: User instance ready to write
        """
        in_groups = set(map(lambda x: self.grpmap_name_iri[x], self.grpsel.GetCheckedStrings()))
        in_projects = dict(map(lambda x: (self.projmap_name_iri[x[0]], x[1]), self.projsel.GetItemsAndCheck().items()))
        pp = self.projsel.GetItemsAndCheck()
        try:
            self.user = User(
                con=self.con,
                username=self.username.get_value(),
                email=self.email.get_value(),
                givenName=self.givenName.get_value(),
                familyName=self.familyName.get_value(),
                lang=self.lang.get_value(),
                password=self.password.get_value(),
                status=self.status.get_value(),
                sysadmin=self.sysadmin.get_value(),
                in_groups=in_groups,
                in_projects=in_projects
            )
        except BaseError as err:
            show_error("Couldn't create User instance!", err)
            return None
        return self.user

    def get_changed(self) -> Union[User, None]:
        """
        Get all changed fields from the user modification dialog and modify the User instance appropriately.

        :return: User instance ready to update
        """
        try:
            tmp = self.email.get_changed()
            if tmp is not None:
                self.user.email = tmp

            tmp = self.username.get_changed()
            if tmp is not None:
                self.user.username = tmp

            tmp = self.familyName.get_changed()
            if tmp is not None:
                self.user.familyName = tmp

            tmp = self.givenName.get_changed()
            if tmp is not None:
                self.user.givenName = tmp

            tmp = self.lang.get_changed()
            if tmp is not None:
                self.user.lang = tmp

            tmp = self.status.get_changed()
            if tmp is not None:
                self.user.status = tmp

            tmp = self.password.get_changed()
            if tmp is not None:
                self.user.password = tmp

            tmp = self.sysadmin.get_changed()
            if tmp is not None:
                self.user.sysadmin = tmp
        except BaseError as err:
            show_error("Error modifying user data!", err)
            return None
        return self.user

    def add_to_proj(self, index: int) -> None:
        """
        Callback for KnCollapsiblePicker when a user is added to a project

        :param index: Index of project
        :return: None
        """
        proj_iri = self.projmap_name_iri[index]
        try:
            self.user.addToProject(proj_iri)
        except BaseError as err:
            show_error("Coudn't add user to project!", err)
        self.member_proj_names.append(index)
        self.notmember_proj_names.remove(index)

    def rm_from_proj(self, index: int) -> None:
        """
        Callback for KnCollapsiblePicker when a user is removed from a project.

        :param index: Index of project
        :return:None
        """
        proj_iri = self.projmap_name_iri[index]
        # if user is also admin of project, we first remove him from being an admin
        try:
            self.user.rmFromProject(proj_iri)
        except BaseError as err:
            show_error("Couldn't remove user from project!", err)
        self.member_proj_names.remove(index)
        self.notmember_proj_names.append(index)

    def projadmin_cb(self, index: int, on: bool) -> bool:
        """
        Callback for KnCollapsiblePicker when the project admin checbox changes status.

        :param index: Index of project
        :param on: True, if user should be project admin, otherwise false
        :return: True, if everything worked, False on error
        """
        proj_iri = self.projmap_name_iri[index]
        try:
            if on:
                self.user.makeProjectAdmin(proj_iri)
            else:
                self.user.unmakeProjectAdmin(proj_iri)
        except BaseError as err:
            show_error("Couldn't modify admin flag of project", err)
            return False
        return True

    def group_cb(self, index: int, on: bool) -> bool:
        """
        Callback for KnCollapsiblePicker when group membership changes.

        :param index: Group index
        :param on: True, if user should be member of group, False otherwise.
        :return: True, if everything worked, False on error
        """
        grp_iri = self.grpmap_name_iri[index]
        try:
            if on:
                self.user.addToGroup(grp_iri)
            else:
                self.user.rmFromGroup(grp_iri)
        except BaseError as err:
            show_error("Couldn't modify group membershio flag of group", err)
            return False
        return True






