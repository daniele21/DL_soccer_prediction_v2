import tkinter as tk
from tkinter import ttk

# style = ttk.Style()
# style.configure("TMenubutton", font=('courier new', 10, 'bold'),
#                 foreground="black", background="white")
#
# l1 = ttk.Label(text="Test", style="BW.TLabel")
# l2 = ttk.Label(text="Test", style="BW.TLabel")
from scripts.constants.configs import HOME, AWAY
from scripts.frontend.config import DEFAULT_FONT_STYLE, DEFAULT_STYLE_MENU
from scripts.frontend.gui_interface import Frame_Window
from scripts.frontend.window_manager import place_widget, Pack_Structure
from scripts.gui.gui_utils import destroyMenus

DEFAULT_TEAM = 'Team'
DEFAULT_BET = '1.00'

def insertOptionMenu(root, var, elem_list, first_item=None,
                     command=None, style=DEFAULT_STYLE_MENU):
    # menu = tk.OptionMenu(root, var, *list_elem)
    # menu = ttk.OptionMenu(root, var, first_item, *list_elem,
    #                       command=command
    #                       )
    menu = tk.OptionMenu(root, var, *elem_list,
                          command=command
                          )
    menu.configure(font=DEFAULT_STYLE_MENU['font'])
    menu.configure(font=DEFAULT_STYLE_MENU['width'])
    # menu.config(font=('courier new', 10, 'bold'))

    return menu


def insert_entry(root, var, params=None):
    # return ttk.Entry(root,
    #                  textvariable=var,
    #                  # justify=params['justify'],
    #                  # font=(FONT, 10, 'bold'),
    #                  width=7
    #                  )
    return tk.Entry(root,
                         textvariable=var,
                         # justify=params['justify'],
                         # font=(FONT, 10, 'bold'),
                         width=7
                         )

def insert_label(root, text,
                 font=DEFAULT_FONT_STYLE,
                 justify=tk.CENTER):

    label = tk.Label(root, text=text, justify=justify)
    label.configure(font=font)

    return label

def insertMatch(root, teams_list, index, callback=None):
    teamA_var = tk.StringVar(name='Home_' + index)
    teamB_var = tk.StringVar(name='Away_' + index)
    betA_var = tk.StringVar(name='H_bet_' + index)
    betB_var = tk.StringVar(name='A_bet_' + index)

    teamA_var.set(DEFAULT_TEAM)
    teamB_var.set(DEFAULT_TEAM)
    betA_var.set(DEFAULT_BET)
    betB_var.set(DEFAULT_BET)

    place = Pack_Structure(expand=False,
                           fill=None,
                           padx=50,
                           pady=5,
                           ipady=5)

    vsLabel = tk.Label(root, text='vs')

    betA_entry = insert_entry(root, betA_var)
    menuA = insertOptionMenu(root, teamA_var, teams_list,
                             # first_item=DEFAULT_TEAM
                             )
    menuB = insertOptionMenu(root, teamB_var, teams_list,
                             # first_item=DEFAULT_TEAM
                             )
    betB_entry = insert_entry(root, betB_var)

    place.side = tk.LEFT
    place_widget(betA_entry, place)
    place_widget(menuA, place)
    place_widget(vsLabel, place)
    place_widget(menuB, place)
    place_widget(betB_entry, place)

    return {'menu':{HOME: menuA,
                    AWAY: menuB},
            'bet':{HOME: betA_entry,
                   AWAY: betB_entry},
            'bet_var':{HOME: betA_var,
                       AWAY: betB_var},
            'team_var':{HOME: teamA_var,
                        AWAY: teamB_var},}


def _insert_match_menus(root, frames, teams_list, matches):

    matches_frame = frames['matches']

    if (len(matches_frame.frames) > 0):
        for frame in matches_frame.frames.values():
            frame.destroy()

    n_teams = len(teams_list)

    matches_list = []


    for i in range(n_teams // 2):
        frame = Frame_Window(matches_frame, None)
        matches_frame.frames[f'match_{i}'] = frame

        match_widget_dict = insertMatch(frame, teams_list, str(i))

        matches_list.append(match_widget_dict)
        i += 1

        frame.pack()

        home_team, away_team = match_widget_dict['team_var'][HOME].get(), match_widget_dict['team_var'][AWAY].get()
        # home_bet, away_bet = match_widget_dict['bet_var'][HOME].get(), match_widget_dict['bet_var'][AWAY].get()

        # if(home_team != DEFAULT_TEAM and away_team != DEFAULT_TEAM):
        matches['1X_bet'].append(match_widget_dict['bet_var'][HOME])
        matches['X2_bet'].append(match_widget_dict['bet_var'][AWAY])
        matches['home_team'].append(match_widget_dict['team_var'][HOME])
        matches['away_team'].append(match_widget_dict['team_var'][AWAY])


    return matches_list

