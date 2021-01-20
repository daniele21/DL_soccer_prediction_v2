# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from scripts.constants.configs import ICON_PATH, AWAY, HOME
from scripts.constants.league import LEAGUE_NAMES, TEAMS_LEAGUE
from scripts.frontend.actions import league_on_change
from scripts.frontend.api_requests import league_request, league_teams_request
from scripts.frontend.graphic_objects import insertOptionMenu
from scripts.frontend.gui_interface import Frame_Window, Child_Window
from scripts.frontend.window_manager import Grid_Structure, Pack_Structure, place_widget
from scripts.frontend.actions import calculate_action

INIT_FIELD_DICT = {HOME:[],
                   AWAY: []}


class Predict_window(Child_Window):
    
    def __init__(self, master, controller, api_config):
        super().__init__(master, controller)

        self.api_config = api_config

        self.league_list = self.init_leagues()
        self.teams_dict = self.init_teams()

        self.init_elements()
        self.main_window()

        self.mainloop()

    def init_leagues(self):
        if self.api_config is not None:
            response = league_request(self.api_config)
            json_response = response.json()
            leagues = json_response['league_name']

        else:
            leagues = LEAGUE_NAMES

        return leagues

    def init_teams(self):
        teams_dict = {}

        for league_name in self.league_list:

            if self.api_config is not None:
                response = league_teams_request(self.api_config, league_name)
                json_response = response.json()
                teams_list = json_response['teams']

            else:
                teams_list = TEAMS_LEAGUE[league_name]

            teams_dict[league_name] = teams_list

        return teams_dict


    def init_elements(self):
        self.matches_vars = {'home_team': [],
                             'away_team':  [],
                             '1X_bet': [],
                             'X2_bet': []}

        self.matches = {'1X_bet': [],
                        'home_team': [],
                        'away_team': [],
                        'X2_bet': []}

        self.league_var = tk.StringVar()
        self.round_var = tk.StringVar()

        self.frames = {'league':  Frame_Window(self, None),
                       'matches': Frame_Window(self, None),
                       'buttons': Frame_Window(self, None)}

        # ttk.Button(self, text='prova').pack()

        # TEAMA MENU ITEMS
        # league_grid = Grid_Structure(1, 1, 1, 3, 20, 20)
        league_pack = Pack_Structure(fill=tk.X,
                                     padx=5, pady=5)

        first_item = 'Select one League'
        # league_menu = insertOptionMenu(self.frames['league'], self.league_var,
        #                                first_item, self.league_list
        #                                )
        league_menu = insertOptionMenu(self.frames['league'], self.league_var,
                                       elem_list=self.league_list
                                       )
        place_widget(league_menu, league_pack)

        # calculate_grid = Grid_Structure(league_grid.row + 15, 3, 1, 1)
        calculate_pack = Pack_Structure(side=tk.RIGHT, padx=30, pady=50)

        # CALCULATE BUTTON
        args_fn = {'root': self,
                   'round_var': self.round_var,
                   'matches': self.matches_vars,
                   'league': self.league_var,
                   'api_config': self.api_config}

        self.confirm_button = tk.Button(self.frames['buttons'], text='Confirm',
                                        command=lambda *args, x=args_fn: calculate_action(x, *args)
                                        )
        place_widget(self.confirm_button, calculate_pack)
        # self.confirm_button.grid(row=calculate_grid.row,
        #                          column=2,
        #                          padx=10,
        #                          pady=5)

        # CLEAR BUTTON
        args_fn = {'root': self,
                   # 'teams': self.teams,
                   'teams_list': self.teams_dict,
                   'league_var': self.league_var,}

        self.clear_button = tk.Button(self.frames['buttons'], text='Clear All',
                                      # command=lambda *args, x=args_fn:
                                      # clear_all_action(x, *args)
                                      )
        clear_pack = Pack_Structure(side=tk.LEFT, padx=30, pady=50)

        place_widget(self.clear_button, clear_pack)

        # self.clear_button.grid(row=calculate_grid.row,
        #                        column=3,
        #                        padx=10,
        #                        pady=5)

        # ROUND
        # tk.Label(self.root, text='Round N.').grid(row=calculate_grid.row - 1,
        #                                           column=1,
        #                                           pady=(20, 10))

        round_label = tk.Label(self.frames['buttons'], text='Round N.')
        round_pack = Pack_Structure(side=tk.LEFT, padx=30, pady=20)
        place_widget(round_label, round_pack)

        # tk.Entry(self.root, textvariable=self.round_var,
        #          justify='center',
        #          width=7).grid(row=calculate_grid.row, column=1)

        round_entry = tk.Entry(self.frames['buttons'], textvariable=self.round_var,
                 justify='center',
                 width=7)
        round_pack.set_padx(10)
        place_widget(round_entry, round_pack)


    def main_window(self):

        self.league_var.set('Select League')

        args_fn = {'root': self,
                   'frames': self.frames,
                   'teams_dict': self.teams_dict,
                   'matches': self.matches_vars,
                   'league_var': self.league_var,
                   'ok_button': self.confirm_button,
                   'clear_button': self.clear_button
                   }

        self.league_var.trace('w',
                              lambda *args, x=args_fn: league_on_change(x, *args))

        for frame in self.frames.values():
            frame.pack()