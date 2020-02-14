from datetime import date
from getpass import getuser
from ntpath import basename
import wx
from openpyxl import load_workbook


# Global Variables
pb = False


# Global Constants
ROUGH_PHASE = 1
FINISH_PHASE = 2
CONTINUE = 2
OVERRIDE = -2
CANCEL = -1


def check_for_duplicates(import_directory, imported_list):
    """This function checks if the file has already been imported"""
    for imp in imported_list:   # cycles through the directories of the previously imported files
        if import_directory == imp:  # if the directory we are trying to import matches a directory in the database
            return True     # we found a match
    return False    # no matches were found


def open_spreadsheet(directory):
    """This function tries to open a spreadsheet and prompts the user if it cannot"""
    while True:     # infinite loop
        try:
            dashboard = load_workbook(filename=directory, read_only=False, data_only=True)  # tries to open spreadsheet
            return dashboard    # returns the spreadsheet if it was opened
        except PermissionError:     # the spreadsheet is already open by something else
            dialog = DatasheetOpenDialog(basename(directory), None, wx.ID_ANY, "")  # asks if the user wants to retry
            retry = dialog.ShowModal()  # captures the users response
            if not retry:   # if the user doesn't want to retry
                return None


class FileDropTarget(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """

    def __init__(self, obj, import_files):
        """ Initialize the Drop Target, passing in the Object Reference to
        indicate what should receive the dropped files """
        # Initialize the wxFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files
        self.obj = obj
        self.import_files = import_files

    def OnDropFiles(self, x, y, file_names):
        """ Implement File Drop """
        # Move Insertion Point to the end of the widget's text
        self.obj.SetInsertionPointEnd()
        # append a list of the file names dropped
        dup_check = False
        for file in file_names:
            for iFile in self.import_files:
                if file == iFile:
                    dup_check = True
                continue
            if not dup_check:
                self.obj.WriteText(basename(file) + '\n')
                self.import_files.append(file)
            else:
                print("Removed duplicate import file!")
                wx.MessageBox("File already in import list.", "Error", wx.OK | wx.ICON_INFORMATION)
                dup_check = False
        self.obj.WriteText('\n')
        return True


class SavFrame(wx.Frame):
    """This object is the main window"""
    # def __init__(self, header_message, choices, checkbox_names, checkbox_values, buttons, *args, **kwds):
    def __init__(self, *args, **kwargs):
        # print(kwargs)
        tmp_kwargs = {}
        title, header_message, choices, checkbox_names, checkbox_values, buttons = "", "", [], [], [], []
        self.choices, self.checkbox_names, self.checkbox_values, self.button_objects = [], [], [], []
        self.title = ""
        self.header_message = ""
        for (key, value), kwarg in zip(kwargs.items(), kwargs):
            if key == 'title':
                self.title = str(value)
            elif key == 'header_message':
                header_message = str(value)
            elif key == 'choices':
                for v in value:
                    choices.append(str(v))
            elif key == 'checkbox_names':
                for v in value:
                    checkbox_names.append(str(v))
            elif key == 'checkbox_values':
                for v in value:
                    checkbox_values.append(int(v))
            elif key == 'buttons':
                for v in value:
                    buttons.append(str(v))
            else:
                tmp_kwargs.update(kwarg)
        # print(tmp_kwargs)

        tmp_kwargs["style"] = tmp_kwargs.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        # print(tmp_kwargs)
        wx.Frame.__init__(self, *args, **tmp_kwargs)

        self.import_files = []

        self.SetSize((640, 428))
        self.button_browse = wx.FilePickerCtrl(self)
        # self.button_4.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_choose_file)
        self.text_ctrl_drag_drop = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)

        drop_target = FileDropTarget(self.text_ctrl_drag_drop, self.import_files)

        # Link the Drop Target Object to the Text Control
        self.text_ctrl_drag_drop.SetDropTarget(drop_target)

        # initializes the local variables
        if header_message:
            self.header_message = header_message
        if choices:
            self.choices = choices

        # initializes the buttons
        if choices:
            self.choices = wx.Choice(self, wx.ID_ANY, choices=self.choices)

        if checkbox_names:
            self.checkbox_names = []
            for checkbox_name in checkbox_names:
                self.checkbox_names.append(wx.CheckBox(self, wx.ID_ANY, checkbox_name))
        if checkbox_values:
            self.checkbox_values = checkbox_values

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        if buttons:
            self.button_objects = []
            for button in buttons:
                # print(1111111, button)
                self.button_objects.append(wx.Button(self, wx.ID_ANY, button))
            # self.button_continue = wx.Button(self, wx.ID_ANY, "Continue")
            # self.button_cancel = wx.Button(self, wx.ID_ANY, "Cancel")
            # self.button_clear = wx.Button(self, wx.ID_ANY, "Clear")

        self.__set_properties()
        self.__do_layout()
        self.SetMinSize((345, 345))

        # initializes the events
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_choose_file, self.button_browse)
        if self.choices:
            self.Bind(wx.EVT_CHOICE, self.on_phase_selection, self.choices)
        # self.Bind(wx.EVT_CHECKBOX, self.on_general_master_dashboard_checkbox, self.checkbox_general_dashboard)
        # self.Bind(wx.EVT_CHECKBOX, self.on_kaceys_master_dashboard_checkbox, self.checkbox_kacey_dashboard)
        # self.Bind(wx.EVT_CHECKBOX, self.on_jakes_master_dashboard_checkbox, self.checkbox_jake_dashboard)

        if self.button_objects:
            for button_object in self.button_objects:
                if 'clear' in button_object.GetLabel().lower():
                    # print(f"Clear button ini for {button_object.GetLabel()}")
                    self.Bind(wx.EVT_BUTTON, self.on_clear, button_object)
                elif 'cancel' in button_object.GetLabel().lower():
                    # print(f'cancel button ini for {button_object.GetLabel()}')
                    self.Bind(wx.EVT_BUTTON, self.on_cancel_program, button_object)
                else:
                    self.Bind(wx.EVT_BUTTON, self.button_event_handler, button_object)

        # self.Bind(wx.EVT_BUTTON, self.on_continue_from_main_window, self.button_continue)
        # self.Bind(wx.EVT_BUTTON, self.on_cancel_program, self.button_cancel)
        # self.Bind(wx.EVT_BUTTON, self.on_clear, self.button_clear)
        self.Bind(wx.EVT_ICONIZE, self.on_minimize)

    def __set_properties(self):
        self.SetTitle(self.title)
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("SAV-Social-Profile.jpg", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        if self.choices:
            self.choices.SetMinSize((102, 23))
            self.choices.SetSelection(0)
        if self.checkbox_names and self.checkbox_values:
            for checkbox_object, checkbox_value in zip(self.checkbox_names, self.checkbox_values):
                # print(333, self.checkbox_values, checkbox_value)
                checkbox_object.SetValue(checkbox_value)

    def __do_layout(self):
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.GridBagSizer(0, 0)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.VERTICAL)
        sizer_12 = wx.BoxSizer(wx.VERTICAL)
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.VERTICAL)

        label_1 = wx.StaticText(self, wx.ID_ANY, self.header_message)
        sizer_10.Add(label_1, 0, wx.ALL, 5)
        static_line_1 = wx.StaticLine(self, wx.ID_ANY)
        sizer_10.Add(static_line_1, 0, wx.EXPAND, 0)
        sizer_5.Add(sizer_10, 0, wx.EXPAND, 0)
        sizer_16.Add(self.button_browse, 0, wx.ALL, 12)
        label_6 = wx.StaticText(self, wx.ID_ANY, "Or drag and drop files below")
        sizer_16.Add(label_6, 0, wx.ALIGN_CENTER, 0)
        sizer_7.Add(sizer_16, 0, wx.EXPAND, 0)
        sizer_14.Add(self.text_ctrl_drag_drop, 1, wx.EXPAND, 0)
        sizer_7.Add(sizer_14, 1, wx.EXPAND, 0)
        sizer_6.Add(sizer_7, 2, wx.EXPAND, 0)
        bitmap_2 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("SAV-Company-Logo.png", wx.BITMAP_TYPE_ANY))
        sizer_12.Add(bitmap_2, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 12)
        if self.choices:
            sizer_13.Add(self.choices, 0, wx.BOTTOM | wx.LEFT, 6)
        sizer_12.Add(sizer_13, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_12, 0, wx.EXPAND, 0)
        if self.checkbox_names:
            for checkbox_objects in self.checkbox_names:
                sizer_15.Add(checkbox_objects, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)

        sizer_11.Add(sizer_15, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_6.Add(sizer_8, 0, wx.EXPAND | wx.LEFT, 6)
        sizer_5.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_9.Add(self.panel_1, (0, 0), (1, 1), wx.EXPAND, 0)

        if self.button_objects:
            for i, button_object in enumerate(self.button_objects):
                sizer_9.Add(button_object, (0, i + 1), (1, 1), wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 6)
        # sizer_9.Add(self.button_continue, (0, 1), (1, 1), wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 6)
        # sizer_9.Add(self.button_cancel, (0, 3), (1, 1), wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 6)
        # sizer_9.Add(self.button_clear, (0, 2), (1, 1), wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 6)
        sizer_5.Add(sizer_9, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 12)
        self.SetSizer(sizer_5)
        self.Layout()

    def on_choose_file(self, event):  # button_browse
        dup_check = False
        file = self.button_browse.GetPath()  # catches what file the user chose
        for iFile in self.import_files:   # checks if file is already in the to-be imported list
            if file == iFile:
                dup_check = True
        if not file.endswith('.xlsx'):
            wx.MessageBox("Incorrect file type. Please choose an .xlsx file.", "Error", wx.OK | wx.ICON_INFORMATION)
            event.skip()
        if not dup_check:
            self.import_files.append(file)
            self.text_ctrl_drag_drop.WriteText(basename(file) + '\n')   # shows the user they chose this
        else:
            print("Removed duplicate import file!")
            wx.MessageBox("File already in import list.", "Error", wx.OK | wx.ICON_INFORMATION)
        event.Skip()

    def on_phase_selection(self, event):  # event handler
        print(self.choices.GetSelection())
        event.Skip()

    def button_event_handler(self, event):  # event handler
        print(f"Button Handler! for {event.GetEventObject().GetLabel()}")
        print(f"choice: {self.choices.GetSelection()}")
        for check_name in self.checkbox_names:
            print(f"Checkbox {check_name}: {check_name.GetValue()}")
            print(self.import_files)
        event.Skip()

    def on_cancel_program(self, event):  # event handler
        print('Canceling!')
        print(getuser())
        self.Destroy()
        event.Skip()

    def on_clear(self, event):     # resets the program
        print('Clearing!')
        self.text_ctrl_drag_drop.SetValue("")
        global pb
        self.import_files.clear()
        pb = not pb
        event.Skip()

    @staticmethod
    def on_minimize(event):     # easter egg
        global pb
        if pb:
            wx.MessageBox("Or is it Peanutbutter?", "Peanutbutter!", wx.OK | wx.ICON_INFORMATION)
        pb = False
        event.Skip()


class DatasheetOpenDialog(wx.Dialog):
    def __init__(self, open_data_sheet, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.open_data_sheet = open_data_sheet
        self.text_ctrl_open_datasheet = wx.TextCtrl(self, wx.ID_ANY,
                                                    f"{open_data_sheet} is open by a user. Please close "
                                                    f"{open_data_sheet} and click \"Retry\".",
                                                    style=wx.BORDER_NONE | wx.TE_MULTILINE | wx.TE_READONLY)
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        self.button_1 = wx.Button(self, wx.ID_ANY, "Retry")
        self.button_5 = wx.Button(self, wx.ID_ANY, "Back")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.text_ctrl_open_data_sheet, self.text_ctrl_open_datasheet)
        self.Bind(wx.EVT_BUTTON, self.on_retry, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_back, self.button_5)

    def __set_properties(self):
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("SAV-Social-Profile.jpg", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        self.SetTitle("dialog_3")
        self.text_ctrl_open_datasheet.SetBackgroundColour(wx.Colour(255, 255, 255))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.text_ctrl_open_datasheet, 0, wx.ALL | wx.EXPAND, 12)
        sizer_2.Add(self.panel_2, 1, 0, 0)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_2.Add(self.button_5, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_1.Add(sizer_2, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def text_ctrl_open_data_sheet(self, event):  # event handler
        print(f"{self.open_data_sheet} is currently open by a user!")
        event.Skip()

    def on_retry(self, event):  # event handler
        self.EndModal(True)
        self.Destroy()
        event.Skip()

    def on_back(self, event):  # event handler
        self.EndModal(False)
        self.Destroy()
        event.Skip()


class DatasheetAlreadyImportedDialog(wx.Dialog):
    def __init__(self, open_sheet, imported_by, imported_date, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.open_data_sheet = open_sheet
        self.text_ctrl_already_imported = wx.TextCtrl(self, wx.ID_ANY,
                                                      f"{open_sheet}\nHas already been imported by {imported_by} on "
                                                      f"{imported_date}. If you would  like to import the project as a "
                                                      f"new project, select \"Duplicate\". If you want to refresh the "
                                                      f"existing data, select \"Replace\".",
                                                      style=wx.BORDER_NONE | wx.TE_MULTILINE | wx.TE_READONLY)
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        self.button_6 = wx.Button(self, wx.ID_ANY, "Duplicate")
        self.button_1 = wx.Button(self, wx.ID_ANY, "Replace")
        self.button_5 = wx.Button(self, wx.ID_ANY, "Back")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.text_ctrl_open_data_sheet, self.text_ctrl_already_imported)
        self.Bind(wx.EVT_BUTTON, self.on_duplicate, self.button_6)
        self.Bind(wx.EVT_BUTTON, self.on_replace, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_back, self.button_5)

    def __set_properties(self):
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("SAV-Social-Profile.jpg", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        self.SetTitle("dialog_2")
        self.text_ctrl_already_imported.SetBackgroundColour(wx.Colour(255, 255, 255))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.text_ctrl_already_imported, 0, wx.ALL | wx.EXPAND, 12)
        sizer_2.Add(self.panel_2, 1, 0, 0)
        sizer_2.Add(self.button_6, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_2.Add(self.button_5, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_1.Add(sizer_2, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def text_ctrl_open_data_sheet(self, event):  # event handler
        print(f"{self.open_data_sheet} has already been imported")
        event.Skip()

    def on_duplicate(self, event):  # event handler
        if getuser() == "Julian.Kizanis":
            dialog = AreYouSureDuplicateDialog(None, wx.ID_ANY, "")
            answer = dialog.ShowModal()
            if answer:
                self.EndModal(0)
            else:
                self.EndModal(CANCEL)
            self.Destroy()
        else:
            wx.MessageBox("This functionality has been disabled, please contact "
                          "Julian.Kizanis if you wish to duplicate project entries.",
                          "Duplicate", wx.OK | wx.ICON_INFORMATION)
        event.Skip()

    def on_replace(self, event):  # event handler
        dialog = AreYouSureReplaceDialog(None, wx.ID_ANY, "")
        answer = dialog.ShowModal()
        if answer:
            self.EndModal(OVERRIDE)
        else:
            self.EndModal(CANCEL)
        self.Destroy()
        event.Skip()

    def on_back(self, event):  # event handler
        self.EndModal(CANCEL)
        self.Destroy()
        event.Skip()


class AreYouSureReplaceDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        self.button_1 = wx.Button(self, wx.ID_ANY, "Replace")
        self.button_5 = wx.Button(self, wx.ID_ANY, "Back")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_replace, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_back, self.button_5)

    def __set_properties(self):
        self.SetTitle("dialog")
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("SAV-Social-Profile.jpg", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        label_2 = wx.StaticText(self, wx.ID_ANY,
                                "Are you Sure you want to replace/overwrite the project? "
                                "The old data will not be saved.")
        label_2.Wrap(300)
        sizer_1.Add(label_2, 0, wx.ALL, 12)
        sizer_2.Add(self.panel_2, 1, 0, 0)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_2.Add(self.button_5, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_1.Add(sizer_2, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def on_replace(self, event):  # event handler
        self.EndModal(True)
        self.Destroy()
        event.Skip()

    def on_back(self, event):  # event handler
        self.EndModal(False)
        self.Destroy()
        event.Skip()


class AreYouSureDuplicateDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        self.button_1 = wx.Button(self, wx.ID_ANY, "Duplicate")
        self.button_5 = wx.Button(self, wx.ID_ANY, "Back")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_duplicate, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_back, self.button_5)

    def __set_properties(self):
        _icon = wx.NullIcon
        _icon.CopyFromBitmap(wx.Bitmap("SAV-Social-Profile.jpg", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle("dialog_1")

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        label_2 = wx.StaticText(self, wx.ID_ANY, "Are you Sure you want to add the project as a duplicate?")
        label_2.Wrap(300)
        sizer_1.Add(label_2, 0, wx.ALL, 12)
        sizer_2.Add(self.panel_2, 1, 0, 0)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_2.Add(self.button_5, 0, wx.ALIGN_BOTTOM | wx.ALL | wx.FIXED_MINSIZE, 12)
        sizer_1.Add(sizer_2, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 1)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def on_duplicate(self, event):  # event handler
        self.EndModal(True)
        self.Destroy()
        event.Skip()

    def on_back(self, event):  # event handler
        self.EndModal(False)
        self.Destroy()
        event.Skip()


class MyApp(wx.App):
    def OnInit(self):
        # self.frame = FirstFrame(None, wx.ID_ANY, "Default Header Message", ["Choice 0", "Choice 1", "Choice 2"],
        #                         ["Checkbox 0", "Checkbox 1", "Checkbox 2"], [True, False, True],
        #                         ["Continue", "Do Something", "Clear", "Cancel"])
        self.frame = SavFrame(None, wx.ID_ANY, "",
                              header_message="This is a header!",
                              choices=['choice 0', 'choice 1', 'choice 2'],
                              checkbox_names=['check box 0', 'check box 1', 'check box 2'],
                              checkbox_values=[1, 0, True],
                              buttons=['button 0', 'button 1', 'clear', 'cancel', 'button 4'])

        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    ImportProjectDatasheets = MyApp(0)
    ImportProjectDatasheets.MainLoop()