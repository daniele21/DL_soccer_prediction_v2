import tkinter as tk
from copy import deepcopy

class Grid_Structure():

    def __init__(self, row, column, rowspan=1, columnspan=1, padx=1, pady=1, sticky=tk.N):
        self.row = row
        self.column = column
        self.rowspan = rowspan
        self.columnspan = columnspan
        self.padx = padx
        self.pady = pady
        self.sticky = sticky

    def add_row(self, num=1):
        self.row += num

    def add_column(self, num=1):
        self.column += num

    def copy(self):
        return deepcopy(self)


class Pack_Structure():

    def __init__(self, fill=None, expand=False,
                 side=tk.TOP, padx=0, pady=0,
                 anchor=tk.N, ipdax=0, ipady=0):

        self.fill = fill
        self.expand = expand
        self.side = side,
        self.padx = padx
        self.pady = pady
        self.anchor = anchor
        self.ipadx = ipdax
        self.ipady = ipady

    def set_padx(self, padx):
        self.padx = padx

    def set_pady(self, pady):
        self.pady = pady


def place_widget(widget, place):

    if(isinstance(place, Grid_Structure)):
        widget.grid(row = place.row,
                    rowspan = place.rowspan,
                    column = place.column,
                    columnspan = place.columnspan,
                    padx = place.padx,
                    pady = place.pady)

    elif(isinstance(place, Pack_Structure)):
        widget.pack(fill=place.fill,
                    expand=place.expand,
                    side=place.side,
                    padx=place.padx,
                    pady=place.pady,
                    anchor=place.anchor,
                    ipadx=place.ipadx,
                    ipady=place.ipady)

    else:
        raise ValueError('Wrong placement var')