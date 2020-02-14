import sav
import wx


class SavFrame(sav.SavFrame):
    def button_event_handler(self, event):  # event handler
        print(f"Button Handler! for {event.GetEventObject().GetLabel()}")
        print(f"choice: {self.choices.GetSelection()}")
        for check_name in self.checkbox_names:
            print(f"Checkbox {check_name}: {check_name.GetValue()}")
        print(self.import_files)
        event.Skip()


class MyApp(wx.App):
    def OnInit(self):
        self.frame = SavFrame(None, wx.ID_ANY, "",
                              title="This is the title!",
                              header_message="This is a header!",
                              choices=['choice 0', 'choice 1', 'choice 2'],
                              checkbox_names=['check box 0', 'check box 1', 'check box 2'],
                              checkbox_values=[1, 0, True],
                              buttons=['button 0', 'button 1', 'clear', 'cancel'])
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    ImportProjectDatasheets = MyApp(0)
    ImportProjectDatasheets.MainLoop()
