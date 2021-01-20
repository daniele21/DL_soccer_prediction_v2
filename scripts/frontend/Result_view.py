from scripts.frontend.config import TITLE_FONT, HEADER_FONT, ITEMS_FONT
from scripts.frontend.graphic_objects import insert_label
from scripts.frontend.gui_interface import Child_Window
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
