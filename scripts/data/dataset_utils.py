# from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from scripts.constants.configs import DEFAULT_EVAL_SIZE

import matplotlib.pyplot as plt


def windowed_dataset_split(data_size, params):
    """

    Args:
        data_size: int
        params:    dict{ 'window_size':     int,
                         'eval_size' :      int,
                         'max_train_size':  int

    Returns:
        train_indexes  list
        test_indexes:  list
    """

    window = params['window_size']
    eval_size = params['eval_size']
    max_train_size = params['max_train_size']
    n_splits = params['n_splits']
    gap = params['gap']
    production = params['production']
    # plot = params['plot'] if 'plot' in (params.keys()) else False


    # splitter = TimeSeriesSplit(n_splits=n_splits,
    #                            max_train_size=max_train_size,
    #                            test_size=eval_size)

    splitter = TimeSeriesSplitter(window, max_train_size,
                                  eval_size, n_splits,
                                  gap, production)

    return splitter

class TimeSeriesSplitter():

    def __init__(self, window, max_train_size=None,
                               test_size=None,
                               n_splits=None,
                               gap=None,
                               production=False):

        """

        Args:
            window:         seasonal range                      -> int
            max_train_size:                                     -> int
            test_size:                                          -> int
            n_splits:                                           -> int
            gap:            n different samples bewteen splits  -> int
        """
        self.window = window
        self.max_train_size = max_train_size if max_train_size is not None else window
        self.test_size = test_size if test_size is not None else window
        self.n_splits = n_splits
        self.gap = gap if gap is not None else test_size
        self.production = production

    def split(self, data_size, plot=False):

        data_range = np.arange(0, data_size, 1)
        train_indexes, test_indexes = [], []

        first_timestamp = self._get_first_timestamp(data_range)

        for i in range(self.n_splits):

            if self.production and i == self.n_splits-1:
                end_timestamp = first_timestamp + self.max_train_size
                end_test_timestamp = end_timestamp
            else:
                end_timestamp = first_timestamp + self.max_train_size
                end_test_timestamp = end_timestamp + self.test_size

            if(end_test_timestamp > data_size):
                break

            train_index = np.arange(first_timestamp, end_timestamp, 1)
            test_index = np.arange(end_timestamp, end_test_timestamp, 1)

            first_timestamp = first_timestamp + self.gap

            train_indexes.append(train_index)
            test_indexes.append(test_index)

            if(plot):
                plt.plot([min(train_index), max(train_index)], [i, i], c='r')

                if len(test_index) > 0:
                    plt.plot([min(test_index), max(test_index)], [i, i], c='b')

                plt.axvline(min(train_index), c='green', alpha=0.3)
                plt.axvline(max(train_index), c='y', alpha=0.3)

        if(plot):
            plt.show()

        return train_indexes, test_indexes

    def _get_first_timestamp(self, data_range):

        if not self.n_splits:

            if self.production:
                n_splits = ((len(data_range) - self.max_train_size) // self.gap) + 1
                first_timestamp = len(data_range) - self.max_train_size - (n_splits - 1) * self.gap

            else:
                n_splits = ((len(data_range) - self.test_size - self.max_train_size) // self.gap) + 1
                first_timestamp = len(data_range) - self.test_size - self.max_train_size - (n_splits - 1) * self.gap

            self.n_splits = n_splits

        else:
            first_timestamp = None

            for split in range(self.n_splits, 0, -1):
                if self.production:
                    first_timestamp = (len(data_range) - self.max_train_size) - split * self.gap
                else:
                    first_timestamp = (len(data_range) - self.test_size - self.max_train_size) - split * self.gap

                if (first_timestamp > 0):
                    break


        return first_timestamp

    def get_splits(self):

        return self.n_splits






