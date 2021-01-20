import tkinter
from tkinter import ttk, messagebox
from scripts.gui.gui_utils import place_on_center


class Root_Window(tkinter.Tk):

    def __init__(self, api_config):
        super().__init__()

        place_on_center(self)

        self.api_config = api_config

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

    def init_elements(self):
        pass

    def main_window(self):
        pass



class Frame_Window(tkinter.Frame):

    def __init__(self, master, controller):

        super().__init__(master)
        self.controller = controller
        self.frames = {}

    def init_elements(self):
        pass

    def main_window(self):
        pass

class Child_Window(tkinter.Toplevel):

    def __init__(self, master, controller):

        super().__init__(master)
        self.controller = controller

        place_on_center(self)
        self.master.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.destroy()
        self.master.deiconify()

    def init_elements(self):
        pass

    def main_window(self):
        pass
