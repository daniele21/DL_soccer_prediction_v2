# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from scripts.frontend.analysis_view import Analysis_window
from scripts.frontend.config import TITLE_FONT
from scripts.frontend.gui_interface import Root_Window, Frame_Window
from scripts.frontend.predict_view import Predict_window
from scripts.frontend.probability_view import Probability_window
from scripts.frontend.score_view import Score_window
from scripts.frontend.window_manager import Grid_Structure, place_widget


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
        self.windows['main'].grid()
        # self.button['predict'] = ttk.Button(self.master, text='Predict',
        #                                     command=self.open_predict_view)
        self.show_frame('main')

    def main_window(self):
        pass


    def show_frame(self, frame_name):

        frame = self.windows[frame_name]
        frame.tkraise()

    def open_predict_view(self):
        self.windows['predict'] = Predict_window(self,
                                                 self,
                                                 self.api_config)

    def open_analysis_view(self):
        self.windows['thr_analysis'] = Analysis_window(self,
                                                       self,
                                                       self.api_config)

    def open_score_view(self):
        self.windows['strength'] = Score_window(self,
                                                    self,
                                                    self.api_config)

    def open_probability_view(self):
        self.windows['probability'] = Probability_window(self,
                                                         self,
                                                         self.api_config)


class Main_window(Frame_Window):

    def __init__(self, master, controller):
        super(Main_window, self).__init__(master, controller)

        self.init_elements()

    def init_elements(self):
        # TITLE
        title_label = ttk.Label(self.master, text='Soccer Prediction App', font=TITLE_FONT)
        title_grid = Grid_Structure(row=0, column=0, columnspan=3, pady=1, padx=1)
        place_widget(title_label, title_grid)

        buttons_frame = Frame_Window(self.master, None)
        frame_grid = Grid_Structure(row=title_grid.row+1, column=0, columnspan=3)
        place_widget(buttons_frame, frame_grid)

        # PREDICT BUTTON
        predict_button = ttk.Button(buttons_frame, text='Predict',
                                    command=self.controller.open_predict_view)

        predict_grid = Grid_Structure(row=title_grid.row+1, column=0, padx=20, pady=20)
        place_widget(predict_button, predict_grid)

        # PROBABILITIES BUTTON
        thr_button = ttk.Button(buttons_frame, text='Probabilities',
                                command=self.controller.open_probability_view)
        prob_grid = predict_grid.copy()
        prob_grid.add_column(1)
        place_widget(thr_button, prob_grid)

        # THR ANALYSIS BUTTON
        thr_button = ttk.Button(buttons_frame, text='Thr. Analysis',
                                command=self.controller.open_analysis_view)
        thr_grid = prob_grid.copy()
        thr_grid.add_column(1)
        place_widget(thr_button, thr_grid)

        # TEAMS SCORES
        scores_button = ttk.Button(buttons_frame, text='Teams Strength',
                                   command=self.controller.open_score_view)
        scores_grid = thr_grid.copy()
        scores_grid.add_column(1)
        place_widget(scores_button, scores_grid)

    def main_window(self):
        pass
