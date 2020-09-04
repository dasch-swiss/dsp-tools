from typing import List, Set, Dict, Tuple, Optional, Any, Union, Callable

import wx

from ..models.helpers import Actions, BaseError, Context, Cardinality
from ..models.langstring import Languages, LangStringParam, LangString
from ..models.connection import Connection
from ..models.project import Project
from ..models.listnode import ListNode

from ..knoraConsoleModules.KnDialogControl import show_error, KnDialogControl, KnDialogTextCtrl, KnDialogChoice, \
    KnDialogCheckBox, KnCollapsiblePicker, KnDialogStaticText, KnDialogLangStringCtrl

class ListPanel(wx.Panel):

    def __init__(self,
                 *args, **kw):
        super().__init__(*args, **kw)

        self.projects = None
        self.con = None
        self.ids = []
        self.proj_iri_name = {}
        self.proj_name_iri = {}

        topsizer = wx.BoxSizer(wx.VERTICAL)

        thsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pfilter_label = wx.StaticText(self, label="Filter by Project: ")
        thsizer.Add(self.pfilter_label, flag=wx.EXPAND | wx.ALL, border=3)
        self.pfilter = wx.Choice(self)
        self.pfilter.Bind(wx.EVT_CHOICE, self.pfilter_changed)
        thsizer.Add(self.pfilter, flag=wx.EXPAND | wx.ALL, border=3)
        topsizer.Add(thsizer, flag=wx.EXPAND)

        self.listctl = wx.ListCtrl(self, name="Lists:",
                                   style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES)
        self.listctl.AppendColumn("Project", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Name", width=wx.LIST_AUTOSIZE)
        self.listctl.AppendColumn("Label", width=wx.LIST_AUTOSIZE)
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
        self.con = con

    def update(self) -> None:
        try:
            lists = ListNode.getAllLists(con=self.con)
        except BaseError as err:
            show_error("Couldn't get the existing lists!", err)
            return
        try:
            self.projects = Project.getAllProjects(con=self.con)
        except BaseError as err:
            show_error("Couldn't get the existing projects!", err)
            return
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.projects))
        self.proj_name_iri = dict(map(lambda x: (x.shortname, x.id), self.projects))
        self.pnames = [x.shortname for x in self.projects if x.shortname != "SystemProject"]
        self.pnames.insert(0, "-")
        self.pfilter.Clear()
        self.pfilter.Append(self.pnames)
        self.listctl.DeleteAllItems()
        for list in lists:
            self.listctl.Append((self.proj_iri_name.get(list.project),
                                 list.name if list.name else "-",
                                 list.label[Languages.EN]))
            self.ids.append(list.id)
        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        self.listctl.Select(0)

    def pfilter_changed(self, event: wx.Event) -> None:
        """
        The filter for project changed.It redisplays the lists according to the project filter.
        :param event: The wx.Event
        :return: None
        """
        pname = self.pnames[self.pfilter.GetCurrentSelection()]
        if pname == "-":
            try:
                lists = ListNode.getAllLists(con=self.con)
            except BaseError as err:
                show_error("Couldn't get the existing lists!", err)
                return
        else:
            piri = self.proj_name_iri.get(pname)
            try:
                lists = ListNode.getAllLists(self.con, piri)
            except BaseError as err:
                show_error("Couldn't get the lists of the selected project!", err)
                return
        self.listctl.DeleteAllItems()
        self.ids = []
        for list in lists:
            if self.proj_iri_name.get(list.project) == "SystemProject":
                continue
            self.listctl.Append((self.proj_iri_name.get(list.project),
                                 list.name if list.name else "-",
                                 list.label[Languages.EN]))
            self.ids.append(list.id)

    def new_entry(self, event: wx.Event) -> None:
        idx = self.listctl.GetFirstSelected()
        list_iri = self.ids[idx]
        list_entry = NewListNodeDialog(parent=self, con=self.con)
        res = list_entry.ShowModal()
        if res == wx.ID_OK:
            list = list_entry.get_value()
            try:
                list = list.create()
            except BaseError as err:
                show_error("Couldn't create the new list!", err)
                return
            self.listctl.Append((self.proj_iri_name[list.project],
                                 list.name if list.name else "-",
                                 list.label[Languages.EN]))
            self.ids.append(list.id)

    def edit_entry(self, event: wx.Event) -> None:
        idx = self.listctl.GetFirstSelected()
        rootnode_iri = self.ids[idx]
        list_entry = ModifyListNodeDialog(parent=self,
                                          con=self.con,
                                          rootnode_iri=rootnode_iri,
                                          listnode_iri=rootnode_iri)
        res = list_entry.ShowModal()
        if res == wx.ID_OK:
            list = list_entry.get_changed()
            try:
                list = list.update()
            except BaseError as err:
                show_error("Couldn't modify the list!", err)
                return
            self.listctl.SetItem(idx, 0, list.name if list.name else "-")
            self.listctl.SetItem(idx, 2, list.label[Languages.EN])

        self.listctl.SetColumnWidth(0, -1)
        self.listctl.SetColumnWidth(1, -1)
        self.listctl.SetColumnWidth(2, -1)
        list_entry.Destroy()

    def delete_entry(self, event: wx.Event) -> None:
        pass


class ListNodeEntryForm(wx.Panel):

    def __init__(self,
                 con: Connection,
                 project_iri: Optional[str] = None,
                 listnode_iri: Optional[str] = None,
                 parent_iri: Optional[str] = None,
                 on_save_entry_cb: Optional[Callable[[ListNode], None]] = None,
                 on_add_entry_below_cb: Optional[Callable[[ListNode], None]] = None,
                 *args, **kw):
        super().__init__(*args, **kw)
        self.con = con
        self.project_iri = project_iri
        self.listnode_iri = listnode_iri
        self.parent_iri = parent_iri
        self.on_save_entry_cb = on_save_entry_cb
        self.on_add_entry_below_cb = on_add_entry_below_cb
        try:
            if listnode_iri is None:
                newentry = True
                self.listnode = ListNode(con=con)
            else:
                self.listnode = ListNode(con=con, id=self.listnode_iri).read()
                newentry = False
            self.all_projects = Project.getAllProjects(con)
        except BaseError as err:
            show_error("Couldn't get information from knora", err)
            return
        self.proj_iri_name = dict(map(lambda x: (x.id, x.shortname), self.all_projects))
        self.proj_name_iri = dict(map(lambda x: (x.shortname, x.id), self.all_projects))
        self.proj_names = list(map(lambda x: x.shortname, self.all_projects))
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        panel1 = wx.Panel(self)
        if newentry:
            cols = 2
            enable_widgets = True
        else:
            cols = 3
            enable_widgets = False
        gsizer = wx.FlexGridSizer(cols=cols)

        tmp_project = None if newentry else self.proj_iri_name.get(self.listnode.project)
        enable_projects = enable_widgets
        if self.project_iri:
            enable_projects = False
        self.project_ctrl = KnDialogChoice(panel=panel1,
                                           gsizer=gsizer,
                                           label="Project",
                                           name="project",
                                           choices=self.proj_names,
                                           value=tmp_project,
                                           enabled=enable_projects)
        if self.project_iri:
            index = self.proj_names.index(self.proj_iri_name.get(project_iri))
            self.project_ctrl.set_value(index)

        tmp_label = None if newentry else self.listnode.label if self.listnode.label is not None else ""
        self.label_ctrl = KnDialogLangStringCtrl(panel=panel1,
                                                 gsizer=gsizer,
                                                 label="Label: ",
                                                 name="label",
                                                 value=tmp_label,
                                                 size=wx.Size(400, -1))

        tmp_name = None if newentry else self.listnode.name if self.listnode.name is not None else ""
        self.name_ctrl = KnDialogTextCtrl(panel=panel1,
                                          gsizer=gsizer,
                                          label="Name: ",
                                          name="name",
                                          value=tmp_name,
                                          enabled=enable_widgets,
                                          size=wx.Size(400, -1))

        if not newentry:
            tmp = self.listnode.comment if self.listnode.comment is not None else LangString("")
        else:
            tmp = None
        self.comment_ctrl = KnDialogLangStringCtrl(panel=panel1,
                                                   gsizer=gsizer,
                                                   label="Comment: ",
                                                   name="comment",
                                                   value=tmp,
                                                   size=wx.Size(400, 50),
                                                   style=wx.TE_MULTILINE)

        if not newentry:
            buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
            self.save_button = wx.Button(parent=self, label="Save")
            self.save_button.Bind(wx.EVT_BUTTON, self.save_entry)
            self.add_button = wx.Button(parent=self, label="Add new node below...")
            self.add_button.Bind(wx.EVT_BUTTON, self.add_entry_below)
            self.delete_button = wx.Button(parent=self, label="Delete node")
            self.delete_button.Bind(wx.EVT_BUTTON, self.delete_entry)
            buttonsizer.Add(self.save_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
            buttonsizer.Add(self.add_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)
            buttonsizer.Add(self.delete_button, proportion=1, flag=wx.EXPAND | wx.ALL, border=3)

        gsizer.SetSizeHints(panel1)
        panel1.SetSizer(gsizer)
        panel1.SetAutoLayout(1)
        gsizer.Fit(panel1)

        self.topsizer.Add(panel1, flag=wx.EXPAND | wx.ALL, border=5)
        if not newentry:
            self.topsizer.Add(buttonsizer, proportion=0, flag=wx.EXPAND)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(self.topsizer)

    def set_value(self, listnode: ListNode):
        self.listnode = listnode
        self.parent_iri = listnode.parent
        proj_name = self.proj_iri_name.get(self.listnode.project)
        self.listnode_iri = listnode.id
        self.project_ctrl.set_value(self.proj_names.index(proj_name))
        self.label_ctrl.set_value(listnode.label)
        self.name_ctrl.set_value(listnode.name)
        self.comment_ctrl.set_value(listnode.comment)

    def get_value(self) -> Union[ListNode, None]:
        try:
            self.listnode = ListNode(con=self.con,
                                     project=self.proj_name_iri.get(self.project_ctrl.get_value()),
                                     parent=self.parent_iri,
                                     name=self.name_ctrl.get_value(),
                                     label=self.label_ctrl.get_value(),
                                     comment=self.comment_ctrl.get_value())
        except BaseError as err:
            show_error("Couldn't create ListNode instance!", err)
            return None
        return self.listnode

    def get_changed(self) -> Union[ListNode, None]:
        try:
            tmp = self.name_ctrl.get_changed()
            if tmp is not None:
                self.listnode.name = tmp
            tmp = self.label_ctrl.get_changed()
            if tmp is not None:
                self.listnode.label = tmp
            tmp = self.comment_ctrl.get_changed()
            if tmp is not None:
                self.listnode.comment = tmp
        except BaseError as err:
            show_error("Can not modify ontology data", err)
            return None
        return self.listnode

    def save_entry(self, event: wx.Event) -> None:
        listnode = self.get_changed()
        listnode.print()
        try:
            listnode = listnode.update()
            if self.on_save_entry_cb is not None:
                self.on_save_entry_cb(listnode)

        except BaseError as err:
            show_error("Couldn't update listnode!", err)

    def add_entry_below(self, event: wx.Event) -> None:
        list_entry = NewListNodeDialog(parent=self,
                                       con=self.con,
                                       project_iri=self.listnode.project,
                                       parent_iri=self.listnode_iri,
                                       title="Add new node below")
        res = list_entry.ShowModal()
        if res == wx.ID_OK:
            listnode = list_entry.get_value()
            try:
                listnode = listnode.create()
                listnode.parent = self.listnode_iri
                listnode.project = self.listnode.project
                print('add_entry_below:')
                listnode.print()
                self.on_add_entry_below_cb(listnode)
            except BaseError as err:
                show_error("Couldn't create the new list node!", err)
                return
            listnode.print()


    def delete_entry(self, event: wx.Event) -> None:
        dlg = wx.MessageDialog(parent=self,
                               message="Do You really want to delete this list node completely?",
                               caption="Delete ?",
                               style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.ICON_QUESTION)
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            try:
                self.listnode.delete()
            except BaseError as err:
                show_error("Couldn't delete list node: ", err)



class ListNodesTree(wx.Panel):
    def __init__(self,
                 con: Connection,
                 rootnode_iri: str,
                 item_clicked_cb: Optional[Callable[[wx.Event, ListNode], None]] = None,
                 *args,
                 **kw):

        def add_children(node: ListNode, node_ctrl: wx.TreeItemId):
            if node.children:
                for child in node.children:
                    new_node_item = self.tree_ctrl.AppendItem(node_ctrl, child.label[Languages.EN])
                    self.iri2item[child.id] = new_node_item
                    self.tree_ctrl.SetItemData(new_node_item, child)
                    if child.children:
                        add_children(child, new_node_item)

        super().__init__(*args, **kw)
        self.con = con
        self.iri2item: Dict[str, wx.TreeItemId] = {}
        self.item_clicked_cb = item_clicked_cb

        self.topsizer = wx.BoxSizer(wx.VERTICAL)

        rootnode = ListNode(con=self.con, id=rootnode_iri).getAllNodes()

        self.tree_ctrl = wx.TreeCtrl(parent=self,
                                     size=wx.Size(400, 400),
                                     style=wx.TR_HAS_BUTTONS | wx.TR_SINGLE)
        self.tree_ctrl.Bind(wx.EVT_TREE_SEL_CHANGED, self.item_clicked)
        root_item = self.tree_ctrl.AddRoot(rootnode.label[Languages.EN])
        self.iri2item[rootnode.id] = root_item
        self.tree_ctrl.SetItemData(root_item, rootnode)
        add_children(rootnode, root_item)

        self.tree_ctrl.Expand(root_item)
        self.topsizer.Add(self.tree_ctrl, flag=wx.EXPAND | wx.ALL, border=5)
        self.SetAutoLayout(1)
        self.SetSizerAndFit(self.topsizer)

    def item_clicked(self, event: wx.Event) -> None:
        item = event.GetItem()
        listnode = self.tree_ctrl.GetItemData(item)
        if self.item_clicked_cb is not None:
            self.item_clicked_cb(event, listnode)

    def select_item(self, listnode_iri: str) -> None:
        item = self.iri2item[listnode_iri]
        self.tree_ctrl.SelectItem(item, True)

    def set_item_label(self, listnode_iri: str, label: str) -> None:
        item = self.iri2item[listnode_iri]
        self.tree_ctrl.SetItemText(item, label)

    def add_item_below(self, listnode: ListNode) -> None:
        parent_item = self.iri2item[listnode.parent]
        new_item = self.tree_ctrl.AppendItem(parent_item, listnode.label[Languages.EN])
        self.tree_ctrl.SetItemData(new_item, listnode)
        self.iri2item[listnode.id] = new_item


class NewListNodeDialog(wx.Dialog):

    def __init__(self,
                 con: Connection,
                 project_iri: Optional[str] = None,
                 parent_iri: Optional[str] = None,
                 title: str = "New List Entry",
                 *args, **kw):
        super().__init__(*args, **kw,
                         title=title,
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.con = con
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.form = ListNodeEntryForm(parent=self,
                                      con=self.con,
                                      project_iri=project_iri,
                                      parent_iri=parent_iri)
        self.topsizer.Add(self.form, flag=wx.EXPAND | wx.ALL, border=5)
        bsizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)
        self.SetSizerAndFit(self.topsizer)

    def get_value(self) -> ListNode:
        return self.form.get_value()


class ModifyListNodeDialog(wx.Dialog):

    def __init__(self,
                 con: Connection,
                 rootnode_iri: str,
                 listnode_iri: str,
                 title: str="Modify List Entry",
                 *args, **kw):
        super().__init__(*args, **kw,
                         title=title,
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.con = con
        self.splitsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.leftp = ListNodesTree(parent=self,
                                   con=self.con,
                                   rootnode_iri=rootnode_iri,
                                   item_clicked_cb=self.node_selected,
                                   size=wx.Size(450, -1))
        self.splitsizer.Add(self.leftp, flag=wx.EXPAND | wx.ALL, border=5)
        self.rightp = ListNodeEntryForm(parent=self,
                                        con=self.con,
                                        listnode_iri=rootnode_iri,
                                        on_save_entry_cb=self.on_save,
                                        on_add_entry_below_cb=self.on_add_below)
        self.splitsizer.Add(self.rightp, flag=wx.EXPAND | wx.ALL, border=5)

        self.topsizer.Add(self.splitsizer, flag=wx.EXPAND | wx.ALL, border=5)

        bsizer = self.CreateStdDialogButtonSizer(wx.CLOSE)
        self.topsizer.Add(bsizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizerAndFit(self.topsizer)

    def node_selected(self, event: wx.Event, listnode: ListNode):
        self.rightp.set_value(listnode)

    def on_save(self, listnode: ListNode) -> None:
        self.leftp.set_item_label(listnode.id, listnode.label[Languages.EN])

    def on_add_below(self, listnode: ListNode):
        self.leftp.add_item_below(listnode)

