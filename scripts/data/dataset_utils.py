from sklearn.model_selection import TimeSeriesSplit

from scripts.constants.configs import DEFAULT_EVAL_SIZE


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
    n_splits = data_size // window if 'n_splits' not in list(params.keys()) else params['n_splits']
    max_train_size = params['max_train_size'] if 'max_train_size' in list(params.keys()) else None  # ~380 (una stagione)

    splitter = TimeSeriesSplit(n_splits=n_splits,
                               max_train_size=max_train_size,
                               test_size=eval_size)

    return splitter

class TimeSeriesSplitter():

    def __init__(self, window,  max_train_size=None,
                                test_size=None,
                                n_splits=None):

        self.window = window
        self.max_train_size = max_train_size if max_train_size is not None else window
        self.test_size = test_size if test_size is not None else window
        self.n_splits = n_splits

    def split(self, data_size):
        pass




