import wx
import os
import pickle

from typing import List, Any
import xml.etree.ElementTree as ET
from metaDataSet import MetaDataSet, Property, Cardinality, Datatype
from metaDataHelpers import DateCtrl, CalendarDlg


################# TODO List #################
#
# - more properties, classes
# - call method when something changed in a field; then, call specific validation
#
#############################################

################ Idea List ##################
#
# - I'd love to have an over-arching progress bar that indicates to the user, how much of the forms they have filled out
#   (see wx.Gauge)
#
#############################################

def collectMetadata():
    """
    Runner function that launches the app.

    Calling this method initiates a data handler and opens the GUI.
    """
    # create a data handler
    global data_handler
    data_handler = DataHandling()
    # open GUI
    app = wx.App()
    frame = ProjectFrame()
    app.MainLoop()


class DataHandling:
    """ This class handles data.

    It checks for availability in the filesystem, and
    if not, creates the data structure. It also takes care for the storage on disk.
    The data are stored as a pickle file.

    The class should not be called as a static.
    Rather, there should at any given time be an instance of this class (`data_handler`) be available.
    All calls should be done on this instance, as it holds the actual data representation.
    """

    def __init__(self):
        self.projects = []
        self.containers = {}
        self.data_storage = os.path.expanduser("~") + "/DaSCH/config/repos.data"
        # LATER: path could be made customizable
        self.load_data()

    def add_project(self, folder_path: str):
        """
        Add a new project.

        This project adds a new project folder to the collection after the user specified the folder.

        The Project is appended at the end of the list.

        Args:
            folder_path (str): path to the project folder
        """
        index = len(self.projects)
        folder_name = os.path.basename(folder_path)
        dataset = MetaDataSet(index, folder_name, folder_path)
        self.projects.append(dataset)
        self.save_data()

    def associate_container(self, prop, container):
        """
        Stores a pair of `metaDataSet.Property` and `PropertyRow` in the Handler's container dict.

        This allows to update a property value according to it's associated UI component.
        """
        self.containers[prop] = container

    def load_data(self):
        """
        Load data from previous runtimes (if any).

        Currently, this checks `~/DaSCH/config/repos.data`.
        """
        if not os.path.exists(self.data_storage):
            os.makedirs(os.path.dirname(self.data_storage), exist_ok=True)
            return
        with open(self.data_storage, 'rb') as file:
            self.projects = pickle.load(file)
            # LATER: in principal, we could append the data instead of replacing it
            # (for loading multiple data sets and combining them)
            # would have to make sure the indices are correct and no doubles are being added

    def save_data(self):
        """
        Save data to disc.

        Currently, the data are stored under `~/DaSCH/config/repos.data`.
        """
        # LATER: could let the user decide where to store the data.
        print("Saving data...")
        for p in self.projects:
            print(p)
        with open(self.data_storage, 'wb') as file:
            pickle.dump(self.projects, file)

    def process_data(self, index: int):
        """
        ToDo: implement this class.
        """
        # TODO: implement data procession.
        # Probably just calls processing on the selected data set
        print(f'Should be processing Dataset: {index}')

    def validate_all(self, dataset):
        """
        Validates all properties in a specific `MetaDataSet.`
        """
        print("should be validating the data")
        # TODO: validate: call validation. and give indication, if there is a problem

    def update_all(self, dataset):
        """
        TODO: docstring
        """
        for prop in dataset.project.get_properties():
            container = self.containers[prop]
            prop.value = container.get_value()
            print(prop.value)
        for prop in dataset.dataset.get_properties():
            container = self.containers[prop]
            prop.value = container.get_value()
            print(prop.value)


########## Here starts UI stuff ##############


class ProjectFrame(wx.Frame):
    """
    This class sets the Project frame, and creates the file menu.

    Here we open folders and ingest new project files.
    """

    def __init__(self):
        super().__init__(parent=None,
                         title='Project Data Editor', size=(1100, 450))
        self.panel = ProjectPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_folder_menu_item = file_menu.Append(
            wx.ID_ANY, 'Open Folder',
            'Open a folder with project files'
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.on_open_folder,
            source=open_folder_menu_item,
        )
        self.SetMenuBar(menu_bar)

    def on_open_folder(self, event):
        title = "Choose a directory:"
        dlg = wx.DirDialog(self, title,
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            # Here the update function is called. This function is strictly restricted to new folders.
            # New data will be appended to the available structure. Add an index
            # index = self.panel.index
            self.panel.add_new_project(dlg.GetPath())
        dlg.Destroy()


class ProjectPanel(wx.Panel):
    """ This class manages the window content.

    It displays a list of projects, which are selectable and provides an edit button.
    """

    def __init__(self, parent, selection=None):
        super().__init__(parent)
        # Here we create the window ...
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="DaSCH Service Platform - Metadata Collection", size=(400, -1))
        main_sizer.Add(title, 0, wx.ALL | wx.LEFT, 10)

        # TODO: Here we might do some cosmetics (Title, info button and the like ...
        self.folder_path = ""
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 200),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )

        self.create_header()

        # Here we create the Edit button
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 20)

        new_folder_button = wx.Button(self, label='New Folder')
        new_folder_button.Bind(wx.EVT_BUTTON, parent.on_open_folder)
        main_sizer.Add(new_folder_button, 0, wx.ALL | wx.CENTER, 5)

        # Something is not yet working...
        # edit_button = wx.Button(self, label='Add Folder')
        # edit_button.Bind(wx.EVT_BUTTON, self.on_open_folder)
        # main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)

        edit_tabs_button = wx.Button(self, label='Edit in Tabs')
        edit_tabs_button.Bind(wx.EVT_BUTTON, self.on_edit_tabbed)
        main_sizer.Add(edit_tabs_button, 0, wx.ALL | wx.CENTER, 5)

        process_xml_button = wx.Button(self, label='Process selected to XML')
        process_xml_button.Bind(wx.EVT_BUTTON, self.on_process_data)
        main_sizer.Add(process_xml_button, 0, wx.ALL | wx.Center, 5)
        self.SetSizer(main_sizer)
        self.Fit()

        self.display_repos()

    def on_open_folder(self, event):
        """
        Open a new folder and add it to projects.
        """
        title = "Choose a directory:"
        dlg = wx.DirDialog(self, title,
                           style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            # Here the update function is called. This function is strictly restricted to new folders.
            # New data will be appended to the available structure.
            self.panel.add_new_project(dlg.GetPath())
        dlg.Destroy()

    def display_repos(self):
        """
        Display all loaded repos in the list.
        """

        for project in data_handler.projects:
            self.list_ctrl.InsertItem(project.index, project.path)
            self.list_ctrl.SetItem(project.index, 1, project.name)
            self.list_ctrl.SetItem(project.index, 2, str(project.files))
            # TODO: make this look pretty? depends on what we do with files

    def create_header(self):
        """ Here we create the header for once and always...
        """
        # Construct a header
        self.list_ctrl.InsertColumn(0, 'Folder', width=340)
        self.list_ctrl.InsertColumn(1, 'Project', width=240)
        self.list_ctrl.InsertColumn(2, 'List of files', width=500)

    def load_view(self):
        # The previous list contents is cleared before reloading it
        self.list_ctrl.ClearAll()
        # Construct a header
        self.create_header()
        self.display_repos()

    def on_edit_tabbed(self, event):
        """ This function calls the EditBaseDialog and hands over pFiles, a list.
                """
        selection = self.list_ctrl.GetFocusedItem()
        if selection >= 0:
            repo = data_handler.projects[selection]
            dlg = TabbedWindow(self, repo)
            dlg.Show()
            self.Disable()

    def on_process_data(self, event):
        """ Set selection and call create_xml """
        selection = self.list_ctrl.GetFocusedItem()
        if selection >= 0:
            data_handler.process_data(selection)
            # LATER: let this return indication of success. display something to the user.

    def add_new_project(self, folder_path):
        """ Add a new project.

            Where is this function called? It is called by on_open_folder in in the Class ProjectFrame
            What should this function do? It should get a new project, store it and then reload the project list
        """
        dir_list = os.listdir(folder_path)
        if '.DS_Store' in dir_list:
            dir_list.remove('.DS_Store')

        data_handler.add_project(folder_path)
        # self.display_repos()
        self.load_view()


class TabOne(wx.Panel):
    """
    Tab holding the project base information
    """

    def __init__(self, parent, dataset):
        wx.Panel.__init__(self, parent)
        self.dataset = dataset

        ##### Project name as caption
        sizer = wx.GridBagSizer(10, 10)
        project_label = wx.StaticText(self, label="Current Project:")
        project_name = wx.StaticText(self, label=self.dataset.name)
        # QUESTION: should this be changeable?
        sizer.Add(project_label, pos=(0, 0))
        sizer.Add(project_name, pos=(0, 1))

        ##### Path to folder
        path_label = wx.StaticText(self, label="Path (Readonly): ")
        sizer.Add(path_label, pos=(1, 0))
        path_field = wx.TextCtrl(self, style=wx.TE_READONLY, size=(550, -1))
        path_field.SetValue(self.dataset.path)
        sizer.Add(path_field, pos=(1, 1))
        # TODO: add button to change folder
        path_help = wx.Button(self, label="?")
        path_help.Bind(wx.EVT_BUTTON, lambda event: self.show_help(event,
                                                                   "Path to the folder with the data",
                                                                   "/some/path/to/folder"))
        sizer.Add(path_help, pos=(1, 2))

        ##### Files
        files_label = wx.StaticText(self, label="Files: ")
        sizer.Add(files_label, pos=(2, 0))
        file_list = wx.ListBox(self, size=(550, -1))
        # TODO: Add Buttons to add and delete files
        # TODO: add all files in data to listbox
        sizer.Add(file_list, pos=(2, 1))
        path_help = wx.Button(self, label="?")
        path_help.Bind(wx.EVT_BUTTON, lambda event: self.show_help(event,
                                                                   "Files associated with the project",
                                                                   "sample_project.zip"))
        # TODO: give some indication on the state of this dataset. (valid, invalid, percentage of properties or similar)
        sizer.Add(path_help, pos=(2, 2))
        sizer.AddGrowableCol(1)
        self.SetSizer(sizer)

    def show_help(self, evt, message, sample):
        win = HelpPopup(self, message, sample)
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))
        win.Popup()


class PropertyRow():
    """
    A row in a tab of the UI

    This Class organizes a single row in the data tabs.
    Upon initiation, the UI elements ara generated and placed.
    Later on, the data handler can let this class return the value that the property should be assigned.

    Args:
        parent (wx.ScrolledWindow): The scrolled panel in which the row is to be placed.
        dataset (Any): The Dataset that is to be displayed
        prop (Property): The property to be displayed
        sizer (wx.Sizer): The sizer that organizes the layout of the parent component
        index (int): the row in the sizer grid
    """

    def __init__(self, parent, dataset, prop, sizer, index):
        self.prop = prop
        name_label = wx.StaticText(parent, label=prop.name + ": ")
        sizer.Add(name_label, pos=(index, 0))

        # TODO: indicate optional vs. mandatory values

        # String or String/URL etc.
        if prop.datatype == Datatype.STRING \
            or prop.datatype == Datatype.STRING_OR_URL \
            or prop.datatype == Datatype.URL \
            or prop.datatype == Datatype.PLACE:
            if prop.cardinality == Cardinality.ONE:  # String or similar, exactly 1
                textcontrol = wx.TextCtrl(parent, size=(550, -1))
                if prop.value:
                    textcontrol.SetValue(prop.value)
                sizer.Add(textcontrol, pos=(index, 1))
                self.data_widget = textcontrol
            elif prop.cardinality == Cardinality.ONE_TO_TWO:  # String or similar, 1-2
                inner_sizer = wx.BoxSizer(wx.VERTICAL)
                textcontrol1 = wx.TextCtrl(parent, size=(550, -1))
                inner_sizer.Add(textcontrol1)
                inner_sizer.AddSpacer(5)
                textcontrol2 = wx.TextCtrl(parent, size=(550, -1))
                textcontrol2.SetHint('Second value is optional')
                inner_sizer.Add(textcontrol2)
                if prop.value:
                    if len(prop.value) > 0 and prop.value[0]:
                        textcontrol1.SetValue(prop.value[0])
                    if len(prop.value) > 1 and prop.value[1]:
                        textcontrol2.SetValue(prop.value[1])
                sizer.Add(inner_sizer, pos=(index, 1))
                self.data_widget = [textcontrol1, textcontrol2]
            elif prop.cardinality == Cardinality.ONE_TO_UNBOUND \
                or prop.cardinality == Cardinality.UNBOUND:  # String or similar, 1-n or 0-n
                inner_sizer = wx.BoxSizer()
                textcontrol = wx.TextCtrl(parent, size=(200, -1))
                inner_sizer.Add(textcontrol)
                inner_sizer.AddSpacer(5)
                plus_button = wx.Button(parent, label="+")
                plus_button.Bind(wx.EVT_BUTTON,
                                 lambda e: parent.add_to_list(e,
                                                              content_list,
                                                              textcontrol.GetValue()))
                inner_sizer.Add(plus_button)
                inner_sizer.AddSpacer(5)
                content_list = wx.ListBox(parent, size=(250, -1))
                if prop.value:
                    for val in prop.value:
                        content_list.Append(val)
                inner_sizer.Add(content_list)
                sizer.Add(inner_sizer, pos=(index, 1))
                print(content_list)
                self.data_widget = content_list
        # date
        elif prop.datatype == Datatype.DATE:
            if prop.cardinality == Cardinality.ONE:
                input_format = '%d-%m-%Y'
                display_format = '%d-%m-%Y'
                date = DateCtrl(parent, size=(130, -1), pos=(150, 80),
                                input_format=input_format, display_format=display_format,
                                title=prop.name, default_to_today=False, allow_null=False)
                sizer.Add(date, pos=(index, 1))
                parent.first_time = True  # don't validate date first time
                parent.SetFocus()
                self.data_widget = date
                print("Datum: ")
                print(date.GetValue())

        btn = wx.Button(parent, label="?")
        btn.Bind(wx.EVT_BUTTON, lambda event: parent.show_help(event, prop.description, prop.example))
        sizer.Add(btn, pos=(index, 2))

    def get_value(self):
        """
        Returns the new property value that has been entered to the UI
        """
        datatype = self.prop.datatype
        cardinality = self.prop.cardinality
        # String or String/URL etc.
        if datatype == Datatype.STRING \
            or datatype == Datatype.STRING_OR_URL \
            or datatype == Datatype.URL \
            or datatype == Datatype.PLACE:
            if cardinality == Cardinality.ONE:
                return self.data_widget.GetValue()
            if cardinality == Cardinality.ONE_TO_TWO:
                return [self.data_widget[0].GetValue(), self.data_widget[1].GetValue()]
            if cardinality == Cardinality.ONE_TO_UNBOUND \
                or cardinality == Cardinality.UNBOUND:
                return self.data_widget.GetStrings()
        return "Couldn't find my value... sorry"


class DataTab(wx.ScrolledWindow):

    def __init__(self, parent, dataset, title):
        wx.Panel.__init__(self, parent, style=wx.EXPAND)

        self.dataset = dataset

        sizer = wx.GridBagSizer(10, 10)

        if dataset:
            for i, prop in enumerate(dataset.get_properties()):
                # self.add_widgets(dataset, prop, sizer, i)
                row = PropertyRow(self, dataset, prop, sizer, i)
                data_handler.associate_container(prop, row)
        self.SetSizer(sizer)
        print("index i: ")
        print(i)

        self.SetScrollbars(0, 16, 60, 15)

        # save_button = wx.Button(self, label='Save')
        # # save_button.Bind(wx.EVT_BUTTON, self.on_save)
        # saveclose_button = wx.Button(self, label='Save and Close')
        # # saveclose_button.Bind(wx.EVT_BUTTON, self.on_saveclose)
        # cancel_button = wx.Button(self, label='Cancel')
        # # cancel_button.Bind(wx.EVT_BUTTON, self.on_close)
        # button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # button_sizer.Add(save_button, 0, wx.ALL, 5)
        # button_sizer.Add(saveclose_button, 0, wx.ALL, 5)
        # button_sizer.Add(cancel_button, 0, wx.ALL, 5)
        # sizer.Add(button_sizer, pos=(0, i+1), span=(1, 3), flag=wx.ALL | wx.BOTTOM, border=5)
        # self.SetSizer(sizer)

    def on_t_got_focus(self, evt):
        if self.first_time:
            self.first_time = False
        else:
            self.start_date.convert_to_wx_date()
        evt.Skip()

    def add_to_list(self, event, content_list, addable):
        """
        add an object to a listbox.
        """
        if not addable:
            return
        content_list.Append(str(addable))

    def remove_from_list(self, event, content_list, removable):
        """
        remove an object from a listbox.

        """
        # ToDo: make it work...

        if not removable:
            return
        content_list.Remove(str(removable))

    def show_help(self, evt, message, sample):
        """
        Show a help dialog
        """
        win = HelpPopup(self, message, sample)
        btn = evt.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        win.Position(pos, (0, sz[1]))
        win.Popup()


class HelpPopup(wx.PopupTransientWindow):
    def __init__(self, parent, message, sample):
        wx.PopupTransientWindow.__init__(self, parent)
        panel = wx.Panel(self)

        st = wx.StaticText(panel, -1,
                           "Description:\n" +
                           message + "\n\n" +
                           "Example:\n" +
                           sample)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(st, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
        sizer.Fit(panel)
        sizer.Fit(self)
        self.Layout()


class TabbedWindow(wx.Frame):
    def __init__(self, parent, dataset: MetaDataSet):
        wx.Frame.__init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
                          size=(900, 600), style=wx.DEFAULT_FRAME_STYLE,
                          name="Metadata tabs")
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.panel = wx.Panel(self)
        self.parent = parent
        self.dataset = dataset

        # Create a panel and notebook (tabs holder)
        panel = self.panel
        # panel = wx.Panel(self)
        nb = wx.Notebook(panel)
        nb.SetMinSize((900, 500))
        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

        # Create the tab windows
        tab1 = TabOne(nb, self.dataset)
        tab2 = DataTab(nb, self.dataset.project, "Project")
        tab3 = DataTab(nb, self.dataset.dataset, "Dataset")
        # tab4 = DataTab(nb, None, "Person")
        # tab5 = DataTab(nb, None, "Organization")
        # tab6 = DataTab(nb, None, "Data Management Plan")

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Base Data")
        nb.AddPage(tab2, "Project")
        nb.AddPage(tab3, "Dataset")
        # nb.AddPage(tab4, "Person")
        # nb.AddPage(tab5, "Organization")
        # nb.AddPage(tab6, "Data Management Plan")

        nb_sizer = wx.BoxSizer()
        nb_sizer.Add(nb, 1, wx.ALL | wx.EXPAND)

        # Buttons
        save_button = wx.Button(panel, label='Save')
        save_button.Bind(wx.EVT_BUTTON, self.on_save)
        saveclose_button = wx.Button(panel, label='Save and Close')
        saveclose_button.Bind(wx.EVT_BUTTON, self.on_saveclose)
        cancel_button = wx.Button(panel, label='Cancel')
        cancel_button.Bind(wx.EVT_BUTTON, self.on_close)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(save_button, 0, wx.ALL, 5)
        button_sizer.Add(saveclose_button, 0, wx.ALL, 5)
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)

        # Set notebook in a sizer to create the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb_sizer, 0, wx.ALL | wx.EXPAND, 5)
        sizer.AddSpacer(5)
        sizer.Add(button_sizer, 0, wx.ALL | wx.BOTTOM, 5)
        panel.SetSizer(sizer)
        # sizer.Fit(self)

        print(sizer.Fit(self))

        # self.Show()

    def on_tab_change(self, event):
        self.save()

    def on_save(self, event):
        self.save()

    def on_saveclose(self, event):
        self.save()
        self.close()

    def on_close(self, event):
        self.close()

    def save(self):
        print("should save tabs content")
        data_handler.update_all(self.dataset)
        data_handler.validate_all(self.dataset)
        data_handler.save_data()

    def close(self):
        self.parent.Enable()
        self.Destroy()


if __name__ == '__main__':
    collectMetadata()
