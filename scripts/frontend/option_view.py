# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from scripts.constants.configs import ICON_PATH
from scripts.frontend.api_requests import league_request, league_teams_request
from scripts.frontend.gui_interface import Root_Window, Frame_Window
from scripts.frontend.predict_view import Predict_window

from scripts.gui.gui_utils import (GridStructure)



class Option_view(Root_Window):

    def __init__(self, api_config):
        super().__init__(api_config)

        # self.iconphoto('icon.png')
        # self.iconphoto(ICON_PATH)
        # self.iconbitmap(default=ICON_PATH)
        self.title('Soccer Forecast Manager')

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand = True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self._init_elements()
        self.main_window()

        self.mainloop()

    def _init_elements(self):
        self.buttons = {}
        self.windows = {}

        self.windows['main'] = Main_window(self.container, self)
        self.windows['main'].pack()
        # self.button['predict'] = ttk.Button(self.master, text='Predict',
        #                                     command=self.open_predict_view)
        self.show_frame('main')

    def main_window(self):
        pass
        # self.league_var.set('League Name')
        #
        # args_fn = {'root': self.root,
        #            'teams_dict': self.teams_dict,
        #            'league_var': self.league_var,
        #            'bet_var': self.bet_var,
        #            'teams_menu': self.teams_menu,
        #            'teams': self.teams,
        #            'ok_button': self.confirm_button,
        #            'clear_button': self.clear_button
        #            }
        #
        # self.league_var.trace('w', lambda *args, x=args_fn: leagueOnChange(x, *args))
        #
        # self.confirm_button.configure(state=tk.DISABLED)
        # self.clear_button.configure(state=tk.DISABLED)


    def show_frame(self, frame_name):

        frame = self.windows[frame_name]
        frame.tkraise()

    def open_predict_view(self):
        self.windows['predict'] = Predict_window(self,
                                                 self,
                                                 self.api_config)
        # self.windows['predict'].raise_window()


class Main_window(Frame_Window):

    def __init__(self, master, controller):
        super(Main_window, self).__init__(master, controller)

        self.init_elements()

    def init_elements(self):
        ttk.Button(self.master, text='predict',
                   command=self.controller.open_predict_view).pack()

        # label = ttk.Label(self, text="Start Page")
        # label.pack(pady=10, padx=10)
        #
        # button = ttk.Button(self, text="Visit Page 1")
        # button.pack()
        #
        # button2 = ttk.Button(self, text="Visit Page 2")
        # button2.pack()

    def main_window(self):
        pass
