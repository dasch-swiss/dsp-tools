import wx
import os
import pickle
from pprint import pprint
from typing import List, Any
import xml.etree.ElementTree as ET
from metaDataSet import MetaDataSet, Property

################# TODO List #################
#
# - generalize forms with custom widget
# - allow custom widget to handle any kind of UI element, not just text box
# - maybe have two separate widgets: form and field, where a form takes multiple fields?
# - "files", what does it actually do? how should we work with it?
# - more properties
# - how to handle dates?
# - how to handle cardinality?
#
# - add more properties
#
#############################################

################ Idea List ##################
#
# - instead of too many up-popping dialogs, we could work with tabs
#   (see e.g.: https://pythonspot.com/wxpython-tabs/ )
# - if so, underneath the tabbed `wx.Notebook`, we could always have the same save and cancel buttons
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
        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)
        process_xml_button = wx.Button(self, label='Process selected to XML')
        process_xml_button.Bind(wx.EVT_BUTTON, self.on_process_data)
        main_sizer.Add(process_xml_button, 0, wx.ALL | wx.Center, 5)
        self.SetSizer(main_sizer)

        self.display_repos()


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


    def on_edit(self, event):
        """ This function calls the EditBaseDialog and hands over pFiles, a list.
        """
        selection = self.list_ctrl.GetFocusedItem()
        if selection >= 0:
            repo = data_handler.projects[selection]
            dlg = EditBaseDialog(repo)
            dlg.ShowModal()
            # This starts the reload of the view. Saving data is done by the save function inside the Dialog box.
            self.load_view()
            dlg.Destroy()


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
        # QUESTION: why do we need this?
        dir_list = os.listdir(folder_path)
        if '.DS_Store' in dir_list:
            dir_list.remove('.DS_Store')
        
        data_handler.add_project(folder_path)
        self.display_repos()



class EditBaseDialog(wx.Dialog):
    """ This class manages the editing on the first level: folder, project and files """

    # def __init__(self, pFiles, selection):
    def __init__(self, dataset: MetaDataSet):
        """
        pFiles is expected to be a dictionary within a list.

        This we get from the on_edit Dialog but we do not get it, directly if we try to select a newly
        added project add_new project
        """
        self.dataset = dataset
        title = "Editing " + dataset.name

        super().__init__(parent=None, title=title, size=(500, 250))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.folder = wx.TextCtrl(self, value=dataset.path)
        self.add_widgets('Folder', self.folder)
        self.project = wx.TextCtrl(self, value=dataset.name)
        self.add_widgets('Project', self.project)
        self.files = wx.TextCtrl(self, value=str(dataset.files))
        self.add_widgets('Files', self.files)

        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(wx.Button(self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)

        p_btn_sizer = wx.BoxSizer()
        naming_btn = wx.Button(self, label='Project Base Names')
        naming_btn.Bind(wx.EVT_BUTTON, self.on_edit_definitions)
        p_btn_sizer.Add(naming_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(p_btn_sizer, 0, wx.CENTER)

        self.SetSizer(self.main_sizer)

    def on_edit_definitions(self, event):
        """ This dialog calls the second level dialog class (short name, short code etc.) """
        dlg = EditNamingDialog(self.dataset)
        dlg.ShowModal()
        """ Saving data and reload??? is done by the save function inside the Dialog box. """
        # reload view ??? Or is this a different situation?
        dlg.Destroy()

        # TODO: We should apply this widget to all forms. See below.


    def add_widgets(self, label_text, text_ctrl):
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label=label_text, size=(50, -1))
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.main_sizer.Add(row_sizer, 0, wx.EXPAND)

    def on_save(self, event):
        self.dataset.path = self.folder.GetValue()
        self.dataset.name = self.project.GetValue()
        self.dataset.files = self.files.GetValue()
        # FIXME: how can files be editable like this?
        # do files even need to be editable?
        # what do we do with file information?
        data_handler.save_data()
        self.Close()


class EditNamingDialog(wx.Dialog):
    """
    This class produces a dialog window to acquire the fundamental information bits of the project.

    These are:  Shortcode of the project, short title of the project, Ark identifier, Official long title of the
    project, language, file names, file descriptions, dataset is part of the project (???)
    """

    def __init__(self, dataset: MetaDataSet):
        title = "New dialog box"
        super().__init__(parent=None, title=title, size=(600, 400))
        self.dataset = dataset

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        project_label = wx.StaticText(self, label="Current Project: " + dataset.name)
        subject_label = wx.StaticText(self, label="Fundamental Names and Definitions")
        header_sizer.Add(project_label, 0, wx.EXPAND)
        header_sizer.Add(subject_label, 0, wx.EXPAND)
        self.main_sizer.Add(header_sizer, 0, wx.LEFT)

        sizer = wx.GridBagSizer(5, 5)
        self.tc_name = wx.TextCtrl(self)
        self.add_widgets(sizer, dataset.project.name, 0, 0, self.tc_name)
        self.tc_description = wx.TextCtrl(self, size=(350, 60), style=wx.TE_MULTILINE)
        self.add_widgets(sizer, dataset.project.description, 1, 0, self.tc_description)
        self.tc_url = wx.TextCtrl(self)
        self.add_widgets(sizer, dataset.project.url, 2, 0, self.tc_url)

        # TODO: Start date
        # TODO: End date
        # TODO: Temporal Coverage
        # TODO: Spacial Coverage
        # TODO: Funder
        # TODO: Grant
        # TODO: Keywords
        # TODO: Discipline
        # etc.

        # Note: that's how language was done previousely
        # text_ctl_language = ['language']
        # languages = ['German', 'French', 'Italian', 'English']
        # self.combo = wx.ComboBox(self, choices=languages, value=text_ctl_language)
        # self.add_widgets(sizer, 'Language', 'Insert the main language, your project is in.', 4, 0, self.combo)

        self.main_sizer.Add(sizer, 0, wx.EXPAND)
        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(wx.Button(
            self, id=wx.ID_CANCEL), 0, wx.ALL, 5
        )
        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
        self.SetSizer(self.main_sizer)


    def add_widgets(self, sizer, prop: Property, pos_x, pos_y, text_control):
        # LATER: adjust to new params
        """
        This function compresses the writing of Grid form entries. The next step will be to move it into a
        helper class to make it accessible for other classes.

        Parameters
        ----------
        sizer : wx.GridBagSizer
        prop : `metaDataSet.Property`
        pos_x : integer
        pos_y : integer
        text_control : wx.TextControl
        """
        # TODO: do something with datatype
        # TODO: do something with cardinality
        # TODO: this currently assumes every value to be a string. How can we solve this?
        # -> generalize, so that widget can take any kind of UI element
        value = ""
        if prop.value:
            value = str(prop.value)
        text_control.SetValue(value)
        self.text_control = text_control
        label = wx.StaticText(self, label=prop.name)
        sizer.Add(label, pos=(pos_x, pos_y), flag=wx.ALL, border=5)
        text_control.SetToolTip(prop.description)
        sizer.Add(text_control, pos=(pos_x, pos_y + 1), flag=wx.EXPAND | wx.ALL, border=5)

    def on_save(self, event):
        print("Save pressed")
        self.dataset.project.name.value = self.tc_name.GetValue()
        self.dataset.project.description.value = self.tc_description.GetValue()
        self.dataset.project.url.value = self.tc_url.GetValue()
        data_handler.save_data()
        self.Close()

# LATER: probably obsolete? in any case, move functionality to metaDataSet
# class HandleXML(DataHandling):
#     """ This Class generates the element tree and applies the respective Data to the element tree. """

#     def __init__(self):
#         self.repos = DataHandling().get_repo()

#     def create_xml(self, selection):
#         """ Here we create the RDF Model and derived from it a XML, JSON or Turtle file or whatever """

#         self.selection = selection

#         print("Trying to create XML-File via RDF_LIB")
#         print("For Testing:")
#         print("Selection:")
#         print(self.selection)
#         print("All repositories available...")
#         print(self.repos)
#         print("Selected repository: ")
#         print(self.repos[self.selection])

#         repo = self.repos[self.selection]
#         print(repo)

#         root = ET.Element("root")
#         project = ET.SubElement(root, "Project Resources")
#         # very static...
#         folder_contents = repo[0]['folder']
#         ET.SubElement(project, "Folder", name="Folder").text = folder_contents
#         repo_name = repo[1]['repo']
#         ET.SubElement(project, "Project", name="Project").text = repo_name
#         file_list = repo[2]['files']
#         ET.SubElement(project, "Files", name="Files").text = file_list
#         print("xml-dump:")
#         ET.dump(root)


if __name__ == '__main__':
    collectMetadata()
