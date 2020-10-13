import wx
import os
import pickle
from typing import List, Any
import xml.etree.ElementTree as ET


class DataHandling:
    """ This class handles data. It checks for availability in the filesystem, and
         if not, creates the data structure. It also takes care for the storage on disk.
        The data are stored as a pickle file. """

    def __init__(self):
        self.repos = List[Any]
        self.home = os.path.expanduser("~")
        self.path = self.home + "/DaSCH/config/repos.data"
        self.ontop = "/DaSCH/config/"
        self.fullpath = self.home + self.ontop

        if os.path.exists(self.path):
            f = open(self.path, 'rb')
            self.repos = pickle.load(f)
            f.close()
        else:
            """ Create directories first """
            os.makedirs(self.fullpath, exist_ok=True)
            """ create the empty file and write a structure """
            f = open(self.path, 'wb')
            self.repos: List[Any] = []
            pickle.dump(self.repos, f)
            f.close()

    def get_repo(self):
        """ will this function always work? """
        return self.repos

    def store_repo(self, repos):
        self.repos = repos
        f = open(self.path, 'wb')
        """ Dump the object to the file """
        pickle.dump(repos, f)
        f.close()


class ProjectFrame(wx.Frame):
    """ This class sets the Project frame, and creates the file menu. Here we open folders and
        ingest new project files """

    def __init__(self):
        super().__init__(parent=None,
                         title='Project Data Editor', size=(1100, 350))
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
            """ Here the update function is called. This function is strictly restricted to new folders.
                New data will be appended to the available structure. Add an index """
            index = self.panel.index
            self.panel.add_new_project(dlg.GetPath(), index)
        dlg.Destroy()


class ProjectPanel(wx.Panel):
    """ This class manages the window content. It displays a list of projects, which are selectable and
        provides an edit button.
    """

    def __init__(self, parent, selection=None):
        super().__init__(parent)
        """ Here we create the window ... """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.folder_path = ""
        self.row_obj_dict = {}

        self.list_ctrl = wx.ListCtrl(
            self, size=(-1, 200),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )

        self.create_header()

        """ Here we create the Edit button"""
        main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 20)
        edit_button = wx.Button(self, label='Edit')
        edit_button.Bind(wx.EVT_BUTTON, self.on_edit)
        main_sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)
        process_xml_button = wx.Button(self, label='Process selected to XML')
        process_xml_button.Bind(wx.EVT_BUTTON, self.on_process_xml)
        main_sizer.Add(process_xml_button, 0, wx.ALL | wx.Center, 5)
        self.SetSizer(main_sizer)

        """ Can we write a separate function for this whole block? (Fetching and displaying data comes several times.
        Redundant and Error prone ). Just see below... """

        repos = DataHandling().get_repo()

        self.index = 0
        for project in repos:
            if project:
                # print(project)
                self.list_ctrl.InsertItem(self.index, project[0]['folder'])
                self.list_ctrl.SetItem(self.index, 1, project[1]['repo'])
                self.list_ctrl.SetItem(self.index, 2, project[2]['files'])
                self.row_obj_dict[self.index] = project
                self.index += 1
            else:
                break

    def create_header(self):

        """ Here we create the header for once and always... """
        """ Construct a header """
        self.list_ctrl.InsertColumn(0, 'Folder', width=340)
        self.list_ctrl.InsertColumn(1, 'Project', width=240)
        self.list_ctrl.InsertColumn(2, 'List of files', width=500)

    def load_view(self):

        """ The previous list contents is cleared before reloading it... """
        self.list_ctrl.ClearAll()
        """ Construct a header """
        self.create_header()

        """ Read the data from filesystem and display in a loop """
        repos = DataHandling().get_repo()
        # print(repos)
        self.index = 0
        for project in repos:
            # print(project)
            self.list_ctrl.InsertItem(self.index, project[0]['folder'])
            self.list_ctrl.SetItem(self.index, 1, project[1]['repo'])
            self.list_ctrl.SetItem(self.index, 2, project[2]['files'])
            self.row_obj_dict[self.index] = project
            self.index += 1

    def on_edit(self, event):
        """ This function calls the EditBaseDialog and hands over pFiles, a list. """
        selection = self.list_ctrl.GetFocusedItem()
        if selection >= 0:
            pFiles = self.row_obj_dict[selection]
            print(pFiles)
            # print(selection)
            """ Here we call the edit dialog
                ToDo: pFiles, project, project_data: this is confusing. By the way, it is not a dictionary: Done?
            """
            dlg = EditBaseDialog(pFiles, selection)
            dlg.ShowModal()
            """ This starts the reload of the view. Saving data is done by the save function inside the Dialog box. """
            self.load_view()
            dlg.Destroy()

    def on_process_xml(self, event):
        """ Set selection and call create_xml """
        selection = self.list_ctrl.GetFocusedItem()
        if selection >= 0:

            # print(selection)
            """ Here we call the create_xml function of HandleXML class
                I start without dialog. Maybe we create a dialog box, which indicates success or failure...
            """
            # dlg = EditBaseDialog(pFiles, selection)
            # dlg.ShowModal()
            """ Quick and dirty..."""
            HandleXML().create_xml(selection)
            # self.load_view()
            # dlg.Destroy()

    def add_new_project(self, folder_path, index):
        """ Adds a new project.
            Where is this function called? It is called by on_open_folder in in the Class ProjectFrame
            What should this function do? It should get a new project, store it and then reload the project list
        """
        self.index_test = index
        print("Index_test: ")
        print(self.index_test)
        self.folder_path = folder_path
        repos = DataHandling().get_repo()
        project_data = []
        """ Here we get the index for the new project"""
        self.index = 0
        for project in repos:
            self.index += 1

        dir_list = os.listdir(folder_path)
        if '.DS_Store' in dir_list:
            dir_list.remove('.DS_Store')

        ttls = ""
        first = True
        for b in range(len(dir_list)):
            if first:
                ttls += dir_list[b]
                first = False
            else:
                ttls += ", " + dir_list[b]
        """ Slicing the last folder to denominate a project name """
        array = folder_path.split("/")
        last_one = len(array)
        project_name = array[last_one - 1]
        """ Now we produce dictionaries"""
        f_path = {'folder': folder_path}
        p_repo = {'repo': project_name}
        f_files = {'files': ttls}
        project_data.append(f_path)
        project_data.append(p_repo)
        project_data.append(f_files)
        repos.append(project_data)
        """ Now we write the repos to disk... """
        DataHandling().store_repo(repos)
        self.load_view()


class EditBaseDialog(wx.Dialog):
    """ This class manages the editing on the first level: folder, project and files """

    def __init__(self, pFiles, selection):
        """ pFiles is expected to be a dictionary within a list.
            This we get from the on_edit Dialog but we do not get it, directly if we try to select a newly
            added project add_new project """
        self.selection = selection
        self.pFiles = pFiles
        title = "Editing " + self.pFiles[1]['repo']

        """ Here we have a problem. We expect a dictionary within a list but we get a list
            if a new project has been added.
        """
        super().__init__(parent=None, title=title, size=(500, 250))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.folder = wx.TextCtrl(self, value=self.pFiles[0]['folder'])
        self.add_widgets('Folder', self.folder)
        self.project = wx.TextCtrl(self, value=self.pFiles[1]['repo'])
        self.add_widgets('Project', self.project)
        self.files = wx.TextCtrl(self, value=self.pFiles[2]['files'])
        self.add_widgets('Files', self.files)

        btn_sizer = wx.BoxSizer()
        save_btn = wx.Button(self, label='Save')
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        btn_sizer.Add(save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(wx.Button(
            self, id=wx.ID_CANCEL), 0, wx.ALL, 5)
        self.main_sizer.Add(btn_sizer, 0, wx.CENTER)

        p_btn_sizer = wx.BoxSizer()
        naming_btn = wx.Button(self, label='Project Base Names')
        naming_btn.Bind(wx.EVT_BUTTON, self.on_edit_definitions)
        p_btn_sizer.Add(naming_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(p_btn_sizer, 0, wx.CENTER)

        self.SetSizer(self.main_sizer)

    def on_edit_definitions(self, event):
        """ This dialog calls the second level dialog class (short name, short code etc.) """
        dlg = EditNamingDialog(self.pFiles, self.selection)
        dlg.ShowModal()
        """ Saving data and reload??? is done by the save function inside the Dialog box. """
        # reload view ??? Or is this a different situation?
        dlg.Destroy()

    def add_widgets(self, label_text, text_ctrl):
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, label=label_text, size=(50, -1))
        row_sizer.Add(label, 0, wx.ALL, 5)
        row_sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.main_sizer.Add(row_sizer, 0, wx.EXPAND)

    def on_save(self, event):
        self.pFiles[0]['folder'] = self.folder.GetValue()
        self.pFiles[1]['repo'] = self.project.GetValue()
        self.pFiles[2]['files'] = self.files.GetValue()
        """ First we get the repos, then we replace the repo, we have changed by selection,
            and then we write write the repos to disk again. """
        repos = DataHandling().get_repo()
        repos[self.selection] = self.pFiles
        """ Now we write the repos to disk... Reload is done by the calling dialog """
        DataHandling().store_repo(repos)
        self.Close()


class EditNamingDialog(wx.Dialog):
    """ This class produces a dialog window to acquire the fundamental information bits of the project
        These are:  Shortcode of the project, short title of the project, Ark identifier, Official long title of the
        project, language, file names, file descriptions, dataset is part of the project (???) """

    def __init__(self, pFiles, selection):
        title = "New dialog box"
        super().__init__(parent=None, title=title, size=(600, 400))
        self.pFiles = pFiles
        self.selection = selection
        print(self.selection)
        print(pFiles[1]['repo'])
        label1 = pFiles[1]['repo']

        repos = DataHandling().get_repo()
        # Remove after testing...
        print("repos: ")
        print(repos)
        print("repos selection: ")
        print(repos[selection])
        number = len(repos[self.selection])
        print("number: ")
        print(number)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        project_label = wx.StaticText(self, label="Current Project: " + label1)
        subject_label = wx.StaticText(self, label="Fundamental Names and Definitions")
        header_sizer.Add(project_label, 0, wx.EXPAND)
        header_sizer.Add(subject_label, 0, wx.EXPAND)
        self.main_sizer.Add(header_sizer, 0, wx.LEFT)

        sizer = wx.GridBagSizer(5, 5)

        if len(repos[self.selection]) == 4:
            print("Some functional metadata available")
            text_ctl_shortname = repos[selection][3][0]['short name']
            text_ctl_shortcode = repos[selection][3][1]['short code']
            text_ctl_long_title = repos[selection][3][2]['long title']
            text_ctl_ark_identifier = repos[selection][3][3]['ark identifier']
            text_ctl_language = repos[selection][3][4]['language']
            # Remove after testing
            print(text_ctl_shortname)
            print(text_ctl_shortcode)
            print(text_ctl_long_title)
            print(text_ctl_ark_identifier)
            print(text_ctl_language)

            shortname = wx.StaticText(self, label="Short Name: (required)")
            sizer.Add(shortname, pos=(0, 0), flag=wx.ALL, border=5)
            # asterisk = wx.StaticText(self, label="*")
            # asterisk.SetForegroundColour((255, 0, 0))
            # sizer.Add(asterisk, pos=(0, 0), flag=wx.ALL)
            self.tc_shortname = wx.TextCtrl(self, value=text_ctl_shortname)
            sizer.Add(self.tc_shortname, pos=(0, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
            shortcode = wx.StaticText(self, label="Shortcode:")
            sizer.Add(shortcode, pos=(1, 0), flag=wx.ALL, border=5)
            self.tc_shortcode = wx.TextCtrl(self, value=text_ctl_shortcode)
            sizer.Add(self.tc_shortcode, pos=(1, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
            long_title = wx.StaticText(self, label="Official long title of the project: ")
            sizer.Add(long_title, pos=(2, 0), flag=wx.ALL, border=5)
            self.tc_long_title = wx.TextCtrl(self, size=(350, 50), style=wx.TE_MULTILINE, value=text_ctl_long_title)
            sizer.Add(self.tc_long_title, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)
            ark_identifier = wx.StaticText(self, label="ARK Identifier:")
            sizer.Add(ark_identifier, pos=(3, 0), flag=wx.ALL, border=5)
            self.tc_ark_identifier = wx.TextCtrl(self, value=text_ctl_ark_identifier)
            sizer.Add(self.tc_ark_identifier, pos=(3, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
            language = wx.StaticText(self, label="Language:")
            sizer.Add(language, pos=(4, 0), flag=wx.ALL, border=5)
            languages = ['German', 'French', 'Italian', 'English']
            self.combo = wx.ComboBox(self, choices=languages, value=text_ctl_language)
            sizer.Add(self.combo, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)
            self.main_sizer.Add(sizer, 0, wx.EXPAND)

            btn_sizer = wx.BoxSizer()
            save_btn = wx.Button(self, label='Save')
            save_btn.Bind(wx.EVT_BUTTON, self.on_save_reload)
            btn_sizer.Add(save_btn, 0, wx.ALL, 5)
            btn_sizer.Add(wx.Button(
                self, id=wx.ID_CANCEL), 0, wx.ALL, 5
            )
            self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
            self.SetSizer(self.main_sizer)
        else:
            print("Functional metadata not yet available")
            shortname = wx.StaticText(self, label="Short Name: (required)")
            sizer.Add(shortname, pos=(0, 0), flag=wx.ALL, border=5)
            # asterisk = wx.StaticText(self, label="*")
            # asterisk.SetForegroundColour((255, 0, 0))
            # sizer.Add(asterisk, pos=(0, 0), flag=wx.ALL)
            self.tc_shortname = wx.TextCtrl(self)
            sizer.Add(self.tc_shortname, pos=(0, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
            shortcode = wx.StaticText(self, label="Shortcode:")
            sizer.Add(shortcode, pos=(1, 0), flag=wx.ALL, border=5)
            self.tc_shortcode = wx.TextCtrl(self)
            sizer.Add(self.tc_shortcode, pos=(1, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
            long_title = wx.StaticText(self, label="Official long title of the project: ")
            sizer.Add(long_title, pos=(2, 0), flag=wx.ALL, border=5)
            self.tc_long_title = wx.TextCtrl(self, size=(350, 50), style=wx.TE_MULTILINE)
            sizer.Add(self.tc_long_title, pos=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)
            ark_identifier = wx.StaticText(self, label="ARK Identifier:")
            sizer.Add(ark_identifier, pos=(3, 0), flag=wx.ALL, border=5)
            self.tc_ark_identifier = wx.TextCtrl(self)
            sizer.Add(self.tc_ark_identifier, pos=(3, 1), span=(1, 2), flag=wx.EXPAND | wx.ALL, border=5)
            language = wx.StaticText(self, label="Language:")
            sizer.Add(language, pos=(4, 0), flag=wx.ALL, border=5)
            languages = ['German', 'French', 'Italian', 'English']
            self.combo = wx.ComboBox(self, choices=languages)
            sizer.Add(self.combo, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)
            self.main_sizer.Add(sizer, 0, wx.EXPAND)

            btn_sizer = wx.BoxSizer()
            save_btn = wx.Button(self, label='Save')
            save_btn.Bind(wx.EVT_BUTTON, self.on_save_new)
            btn_sizer.Add(save_btn, 0, wx.ALL, 5)
            btn_sizer.Add(wx.Button(
                self, id=wx.ID_CANCEL), 0, wx.ALL, 5
            )
            self.main_sizer.Add(btn_sizer, 0, wx.CENTER)
            self.SetSizer(self.main_sizer)

    def on_save_new(self, event):
        print("Save pressed")
        txt_short_name = self.tc_shortname.GetValue()
        txt_short_code = self.tc_shortcode.GetValue()
        txt_long_title = self.tc_long_title.GetValue()
        txt_ark_identifier = self.tc_ark_identifier.GetValue()
        txt_language = self.combo.GetValue()
        print("Selection: ")
        print(self.selection)
        repos = DataHandling().get_repo()
        print("Repo: ")
        print(repos[self.selection])
        metadata = []
        """ Now we create the dictionaries: """
        dict_s_n = {'short name': txt_short_name}
        dict_s_c = {'short code': txt_short_code}
        dict_l_t = {'long title': txt_long_title}
        dict_a_i = {'ark identifier': txt_ark_identifier}
        dict_lg = {'language': txt_language}
        metadata.append(dict_s_n)
        metadata.append(dict_s_c)
        metadata.append(dict_l_t)
        metadata.append(dict_a_i)
        metadata.append(dict_lg)
        # This will be different
        repos[self.selection].append(metadata)
        print("Repos after appending metadata: ")
        print(repos[self.selection])
        DataHandling().store_repo(repos)
        self.Close()

    def on_save_reload(self, event):
        print("Save pressed")
        txt_short_name = self.tc_shortname.GetValue()
        txt_short_code = self.tc_shortcode.GetValue()
        txt_long_title = self.tc_long_title.GetValue()
        txt_ark_identifier = self.tc_ark_identifier.GetValue()
        txt_language = self.combo.GetValue()
        print("Selection: ")
        print(self.selection)
        repos = DataHandling().get_repo()
        print("Repo: ")
        print(repos[self.selection])
        metadata = []
        """ Now we create the dictionaries: """
        dict_s_n = {'short name': txt_short_name}
        dict_s_c = {'short code': txt_short_code}
        dict_l_t = {'long title': txt_long_title}
        dict_a_i = {'ark identifier': txt_ark_identifier}
        dict_lg = {'language': txt_language}
        metadata.append(dict_s_n)
        metadata.append(dict_s_c)
        metadata.append(dict_l_t)
        metadata.append(dict_a_i)
        metadata.append(dict_lg)
        # This will be different
        # repos[self.selection].append(metadata)
        repos[self.selection][3] = metadata
        print("Repos after appending metadata: ")
        print(repos[self.selection])
        DataHandling().store_repo(repos)
        self.Close()


class HandleXML(DataHandling):
    """ This Class generates the element tree and applies the respective Data to the element tree. """

    def __init__(self):

        self.repos = DataHandling().get_repo()


    def create_xml(self, selection):
        """ Here we create the RDF Model and derived from it a XML, JSON or Turtle file or whatever """

        self.selection = selection

        print("Trying to create XML-File via RDF_LIB")
        print("For Testing:")
        print("Selection:")
        print(self.selection)
        print("All repositories available...")
        print(self.repos)
        print("Selected repository: ")
        print(self.repos[self.selection])

        repo = self.repos[self.selection]
        print(repo)

        root = ET.Element("root")
        project = ET.SubElement(root, "Project Resources")
        # very static...
        folder_contents = repo[0]['folder']
        ET.SubElement(project, "Folder", name="Folder").text = folder_contents
        repo_name = repo[1]['repo']
        ET.SubElement(project, "Project", name="Project").text = repo_name
        file_list = repo[2]['files']
        ET.SubElement(project, "Files", name="Files").text = file_list
        print("xml-dump:")
        ET.dump(root)


if __name__ == '__main__':
    app = wx.App()
    frame = ProjectFrame()
    app.MainLoop()
