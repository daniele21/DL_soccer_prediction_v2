from sklearn.model_selection import TimeSeriesSplit
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
        splitter: TimeSeriesSplit (from sklearn.model_selection)
    """

    window = params['window_size']
    eval_size = params['eval_size'] if 'eval_size' in list(params.keys()) else DEFAULT_EVAL_SIZE
    max_train_size = params['max_train_size'] if 'max_train_size' in list(params.keys()) else window # ~380 (una stagione)
    n_splits = 5 if 'n_splits' not in list(params.keys()) else params['n_splits']


    splitter = TimeSeriesSplit(n_splits=n_splits,
                               max_train_size=max_train_size,
                               test_size=eval_size)

    return splitter

class TimeSeriesSplitter():

    def __init__(self, window, max_train_size=None,
                               test_size=None,
                               n_splits=None,
                               gap=None):

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

    def split(self, data_size, plot=False):

        data_range = np.arange(0, data_size, 1)
        train_indexes, test_indexes = [], []

        if not self.n_splits:
            first_timestamp, n_splits = self._get_first_timestamp(data_range)
        else:
            n_splits = self.n_splits

            for split in range(n_splits, 0, -1):
                first_timestamp = (len(data_range) - self.test_size - self.max_train_size) - split*self.gap
                if(first_timestamp > 0):
                    break

        for i in range(n_splits):
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
                plt.plot([min(test_index), max(test_index)], [i, i], c='b')

                plt.axvline(min(train_index), c='green', alpha=0.3)

        if(plot):
            plt.show()

        return train_indexes, test_indexes

    def _get_first_timestamp(self, data_range):

        n_splits = ((len(data_range) - self.test_size - self.max_train_size) // self.gap) + 1
        first_timestamp = len(data_range) - self.test_size - self.max_train_size - (n_splits-1)*self.gap

        return first_timestamp, n_splits






