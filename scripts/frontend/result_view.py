from scripts.frontend.config import TITLE_FONT, HEADER_FONT, ITEMS_FONT, DEFAULT_ENTRY_PARAMS, DEFAULT_FONT_STYLE, \
    DEFAULT_ENTRY_HEIGHT, DEFAULT_FONT
from scripts.frontend.graphic_objects import insert_label, insert_entry
from scripts.frontend.gui_interface import Child_Window, Frame_Window
from scripts.frontend.window_manager import Grid_Structure, place_widget

import tkinter as tk


class Result_view(Child_Window):

    def __init__(self, master, controller, results):
        super().__init__(master, controller)

        self.results = results

        self.init_elements()
        self.main_window()

        self.mainloop()

    def init_elements(self):
        for k in self.results.keys():
            if(k == 'predict'):
                self.init_predict_result()

    def init_predict_result(self):
        predict_result = self.results['predict']
        matches = list(predict_result.keys())

        home_bets = [predict_result[match]['1X'] for match in matches]
        away_bets = [predict_result[match]['X2'] for match in matches]
        home_pred = [str(predict_result[match]["pred_1X"])[:5] for match in matches]
        away_pred = [str(predict_result[match]["pred_X2"])[:5] for match in matches]
        home_pred_bet = [str(predict_result[match]["pred_1X_bet"])[:5] for match in matches]
        away_pred_bet = [str(predict_result[match]["pred_X2_bet"])[:5] for match in matches]
        event = [predict_result[match]['event'] for match in matches if 'event' in predict_result[match].keys()]
        prob = [str(predict_result[match]["prob"])[:5] for match in matches if 'prob' in predict_result[match].keys()]

        self.labels_dict = self.init_labels()

        self.fill_column_table('match', matches)
        self.fill_column_table('home_bet', home_bets)
        self.fill_column_table('away_bet', away_bets)
        self.fill_column_table('home_pred', home_pred)
        self.fill_column_table('away_pred', away_pred)
        self.fill_column_table('home_pred_bet', home_pred_bet)
        self.fill_column_table('away_pred_bet', away_pred_bet)

        if(len(event)>0 and len(prob)>0):
            self.fill_column_table('event', event)
            self.fill_column_table('prob', prob)


    def init_labels(self):
        """

        Returns:
            labels_dict:  dict { 'title': {'label': widget,
                                           'place': Pack_Structure | Grid_Structure},
                                 'match': {'label': widget,
                                           'place': Pack_Structure | Grid_Structure},
                                 'home_bet': {'label': widget,
                                              'place': Pack_Structure | Grid_Structure},
                                 'away_bet': {'label': widget,
                                              'place': Pack_Structure | Grid_Structure},
                                 'home_pred': {'label': widget,
                                               'place': Pack_Structure | Grid_Structure},
                                 'away_pred': {'label': widget,
                                               'place': Pack_Structure | Grid_Structure},
                                 'home_pred_bet': {'label': widget,
                                                   'place': Pack_Structure | Grid_Structure},
                                 'away_pred_bet': {'label': widget,
                                                   'place': Pack_Structure | Grid_Structure},
                                 'event': {'label': widget,
                                           'place': Pack_Structure | Grid_Structure},
                                 'pred': {'label': widget,
                                          'place': Pack_Structure | Grid_Structure}}

        """
        labels_dict = {}

        title_label = insert_label(self, text='Prediction Results', font=TITLE_FONT)
        title_grid = Grid_Structure(row=0, column=0, columnspan=9, pady=10)
        place_widget(title_label, title_grid)
        labels_dict['title'] = {'label': title_label,
                                'place': title_grid}

        header_grid = Grid_Structure(row=title_grid.row + 1, column=0, padx=15, pady=10)
        match_label = insert_label(self, text='Match', font=HEADER_FONT)
        place_widget(match_label, header_grid)
        labels_dict['match'] = {'label': match_label,
                                'place': header_grid}

        home_bet_grid = header_grid.copy()
        home_bet_grid.add_column(1)
        home_bet_label = insert_label(self, text='1X odd', font=HEADER_FONT)
        place_widget(home_bet_label, home_bet_grid)
        labels_dict['home_bet'] = {'label': home_bet_label,
                                   'place': home_bet_grid}

        away_bet_grid = home_bet_grid.copy()
        away_bet_grid.add_column(1)
        away_bet_label = insert_label(self, text='X2 odd', font=HEADER_FONT)
        place_widget(away_bet_label, away_bet_grid)
        labels_dict['away_bet'] = {'label': away_bet_label,
                                'place': away_bet_grid}

        home_pred_grid = away_bet_grid.copy()
        home_pred_grid.add_column(1)
        home_pred_label = insert_label(self, text='1X prob', font=HEADER_FONT)
        place_widget(home_pred_label, home_pred_grid)
        labels_dict['home_pred'] = {'label': home_pred_label,
                                    'place': home_pred_grid}

        away_pred_grid = home_pred_grid.copy()
        away_pred_grid.add_column(1)
        away_pred_label = insert_label(self, text='X2 prob', font=HEADER_FONT)
        place_widget(away_pred_label, away_pred_grid)
        labels_dict['away_pred'] = {'label': away_pred_label,
                                    'place': away_pred_grid}

        home_pred_bet_grid = away_pred_grid.copy()
        home_pred_bet_grid.add_column(1)
        home_pred_bet_label = insert_label(self, text='Real 1X', font=HEADER_FONT)
        place_widget(home_pred_bet_label, home_pred_bet_grid)
        labels_dict['home_pred_bet'] = {'label': home_pred_bet_label,
                                        'place': home_pred_bet_grid}

        away_pred_bet_grid = home_pred_bet_grid.copy()
        away_pred_bet_grid.add_column(1)
        away_pred_bet_label = insert_label(self, text='Real X2', font=HEADER_FONT)
        place_widget(away_pred_bet_label, away_pred_bet_grid)
        labels_dict['away_pred_bet'] = {'label': away_pred_bet_label,
                                    'place': away_pred_bet_grid}

        event_grid = away_pred_bet_grid.copy()
        event_grid.add_column(1)
        event_label = insert_label(self, text='Event', font=HEADER_FONT)
        place_widget(event_label, event_grid)
        labels_dict['event'] = {'label': event_label,
                                'place': event_grid}

        prob_grid = event_grid.copy()
        prob_grid.add_column(1)
        prob_label = insert_label(self, text='Match Prob.', font=HEADER_FONT)
        place_widget(prob_label, prob_grid)
        labels_dict['prob'] = {'label': prob_label,
                                'place': prob_grid}

        return labels_dict

    def fill_column_table(self, id, column_items):
        label_place = self.labels_dict[id]['place']
        grid = label_place.copy()
        grid.add_row(1)
        grid.pady=5

        for item in column_items:
            label = insert_label(self, text=item, font=ITEMS_FONT, justify=tk.LEFT)
            place_widget(label, grid)
            grid.add_row(1)


    def main_window(self):
        pass


class Probability_view(Child_Window):

    def __init__(self, master, controller, results):
        super().__init__(master, controller)

        self.results = results

        self.init_elements()
        self.main_window()

        self.mainloop()

    def init_elements(self):
        self.frames = {'data': None,
                       'buttons': None}

        self.frames['buttons'] = Frame_Window(self, None)

        self.prob_button = tk.Button(self.frames['buttons'], text='Probabilities', command=self.init_prob_result)
        self.prob_button.config(state=tk.DISABLED)
        prob_button_grid = Grid_Structure(1, 0, padx=50, pady=30)
        place_widget(self.prob_button, prob_button_grid)

        self.odds_button = tk.Button(self.frames['buttons'], text='Odds', command=self.init_odds_result)
        self.odds_button.config(state=tk.NORMAL)
        odds_button_grid = Grid_Structure(1, 1, padx=50, pady=30)
        place_widget(self.odds_button, odds_button_grid)

        self.init_table()
        self.init_prob_result()
        # self.init_odds_result()

    def init_table(self):
        self.labels_dict = self.init_labels()
        self.entries = None

    def init_prob_result(self):
        self.prob_button.config(state=tk.DISABLED)
        self.odds_button.config(state=tk.NORMAL)
        prob_df = self.results['prob']

        matches = prob_df['match'].to_list()
        home_win = prob_df['1'].to_list()
        draw = prob_df['X'].to_list()
        away_win = prob_df['2'].to_list()
        under = prob_df['under_2.5'].to_list()
        over = prob_df['over_2.5'].to_list()
        goal = prob_df['goal'].to_list()
        nogoal = prob_df['nogoal'].to_list()

        self.fill_column_table('match', matches, item_type='str', params={'justify': 'center',
                                                                             'font': (DEFAULT_FONT, 15),
                                                                             'width': 30,
                                                                             'height': DEFAULT_ENTRY_HEIGHT})
        self.fill_column_table('home', home_win, item_type='double')
        self.fill_column_table('draw', draw, item_type='double')
        self.fill_column_table('away', away_win, item_type='double')
        self.fill_column_table('under', under, item_type='double')
        self.fill_column_table('over', over, item_type='double')
        self.fill_column_table('goal', goal, item_type='double')
        self.fill_column_table('nogoal', nogoal, item_type='double')

    def init_odds_result(self):
        self.prob_button.config(state=tk.NORMAL)
        self.odds_button.config(state=tk.DISABLED)
        odds_df = self.results['odds']

        matches = odds_df['match'].to_list()
        home_win = odds_df['1'].to_list()
        draw = odds_df['X'].to_list()
        away_win = odds_df['2'].to_list()
        under = odds_df['under_2.5'].to_list()
        over = odds_df['over_2.5'].to_list()
        goal = odds_df['goal'].to_list()
        nogoal = odds_df['nogoal'].to_list()

        self.fill_column_table('match', matches, item_type='str', params={'justify': 'center',
                                                                          'font': (DEFAULT_FONT, 15),
                                                                          'width': 30,
                                                                          'height': DEFAULT_ENTRY_HEIGHT})
        self.fill_column_table('home', home_win, item_type='double', odds=True)
        self.fill_column_table('draw', draw, item_type='double', odds=True)
        self.fill_column_table('away', away_win, item_type='double', odds=True)
        self.fill_column_table('under', under, item_type='double', odds=True)
        self.fill_column_table('over', over, item_type='double', odds=True)
        self.fill_column_table('goal', goal, item_type='double', odds=True)
        self.fill_column_table('nogoal', nogoal, item_type='double', odds=True)

    def init_labels(self):
        """

        Returns:
            labels_dict:  dict { 'title': {'label': widget,
                                           'place': Pack_Structure | Grid_Structure},
                                 'match': {'label': widget,
                                           'place': Pack_Structure | Grid_Structure},
                                 'home': {'label': widget,
                                              'place': Pack_Structure | Grid_Structure},
                                 'draw': {'label': widget,
                                              'place': Pack_Structure | Grid_Structure},
                                 'away': {'label': widget,
                                               'place': Pack_Structure | Grid_Structure},
                                 'under': {'label': widget,
                                               'place': Pack_Structure | Grid_Structure},
                                 'over': {'label': widget,
                                                   'place': Pack_Structure | Grid_Structure},
                                 'goal': {'label': widget,
                                                   'place': Pack_Structure | Grid_Structure},
                                 'noprob': {'label': widget,
                                           'place': Pack_Structure | Grid_Structure}

        """
        if(self.frames['data'] is not None):
            self.frames['data'].destroy()

        self.frames['data'] = Frame_Window(self, None)

        labels_dict = {}

        title_label = insert_label(self.frames['data'], text='Prediction Results', font=TITLE_FONT)
        title_grid = Grid_Structure(row=0, column=0, columnspan=9, pady=10)
        place_widget(title_label, title_grid)
        labels_dict['title'] = {'label': title_label,
                                'place': title_grid}

        header_grid = Grid_Structure(row=title_grid.row + 1, column=0, padx=15, pady=10)
        match_label = insert_label(self.frames['data'], text='Match', font=HEADER_FONT)
        place_widget(match_label, header_grid)
        labels_dict['match'] = {'label': match_label,
                                'place': header_grid}

        home_prob_grid = header_grid.copy()
        home_prob_grid.add_column(1)
        home_prob_label = insert_label(self.frames['data'], text='1', font=HEADER_FONT)
        place_widget(home_prob_label, home_prob_grid)
        labels_dict['home'] = {'label': home_prob_label,
                                   'place': home_prob_grid}

        draw_prob_grid = home_prob_grid.copy()
        draw_prob_grid.add_column(1)
        draw_prob_label = insert_label(self.frames['data'], text='X', font=HEADER_FONT)
        place_widget(draw_prob_label, draw_prob_grid)
        labels_dict['draw'] = {'label': draw_prob_label,
                                    'place': draw_prob_grid}

        away_prob_grid = draw_prob_grid.copy()
        away_prob_grid.add_column(1)
        away_prob_label = insert_label(self.frames['data'], text='2', font=HEADER_FONT)
        place_widget(away_prob_label, away_prob_grid)
        labels_dict['away'] = {'label': away_prob_label,
                                    'place': away_prob_grid}

        under_prob_grid = away_prob_grid.copy()
        under_prob_grid.add_column(1)
        under_prob_label = insert_label(self.frames['data'], text='Under', font=HEADER_FONT)
        place_widget(under_prob_label, under_prob_grid)
        labels_dict['under'] = {'label': under_prob_label,
                                    'place': under_prob_grid}

        over_prob_grid = under_prob_grid.copy()
        over_prob_grid.add_column(1)
        over_prob_label = insert_label(self.frames['data'], text='Over', font=HEADER_FONT)
        place_widget(over_prob_label, over_prob_grid)
        labels_dict['over'] = {'label': over_prob_label,
                                        'place': over_prob_grid}

        goal_prob_grid = over_prob_grid.copy()
        goal_prob_grid.add_column(1)
        goal_prob_label = insert_label(self.frames['data'], text='Goal', font=HEADER_FONT)
        place_widget(goal_prob_label, goal_prob_grid)
        labels_dict['goal'] = {'label': goal_prob_label,
                                    'place': goal_prob_grid}

        nogoal_prob_grid = goal_prob_grid.copy()
        nogoal_prob_grid.add_column(1)
        nogoal_prob_label = insert_label(self.frames['data'], text='No Goal', font=HEADER_FONT)
        place_widget(nogoal_prob_label, nogoal_prob_grid)
        labels_dict['nogoal'] = {'label': nogoal_prob_label,
                                'place': nogoal_prob_grid}

        return labels_dict


    def fill_column_table(self, id, column_items, item_type, params=DEFAULT_ENTRY_PARAMS, odds=False):
        label_place = self.labels_dict[id]['place']
        grid = label_place.copy()
        grid.add_row(1)
        grid.pady=5

        if(self.entries is not None):
            for entry in self.entries:
                entry.destroy()

        for item in column_items:
            if(item_type == 'double' and not odds):
                item_value = f'{float(item)*100:.0f} %'
            elif(item_type == 'double' and odds):
                item_value = f'{float(item):.2f}'
            else:
                item_value = item

            var = tk.StringVar()
            var.set(item_value)

            state = tk.NORMAL
            entry_widget = insert_entry(self.frames['data'], var, params=params)
            entry_widget.config(state=state)
            # label = insert_label(self, text=item, font=ITEMS_FONT, justify=tk.LEFT)
            place_widget(entry_widget, grid)
            grid.add_row(1)



    def main_window(self):
        for i, frame in enumerate(self.frames.values()):
            place_widget(frame, Grid_Structure(i+20, 0, columnspan=10))

