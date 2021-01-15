from scripts.constants.configs import *
from scripts.constants.league import *
from scripts.constants.paths import *

SERIE_A_PARAMS = {
                    "league": {
                        "league_name": SERIE_A,
                        "n_prev_match": 10,
                        "league_dir": DATA_DIR,
                        "train": "True"
                    },
                    "data": {
                        "normalize": "True",
                        "window_size": 50,
                        "dataset": BASE_DATASET,
                        "split_size": 0.986,    # TO BE UPDATED (~50)
                        "test_size": 100,
                        "batch_size": 10,
                        "version": 2,
                        "league_dir": "resources/leagues_data/",
                        "train": "True"
                    },
                    "model": {
                        "dataset": BASE_DATASET,
                        "version": 2,
                        "out_lstm": 100,
                        "n_lstm_layer": 2,
                        "bidirectional": "True",
                        "kernel": 10,
                        "padding": 1,
                        "conv_layers": 1,
                        "optimizer": ADAM_OPTIMIZER,
                        "lr": 0.00001,
                        "loss": BCE_LOSS,
                        "seed": 2020,
                        "device": CUDA_DEVICE,
                        "verbose": "True",
                        "plot": "False",
                        "static_dir": STATIC_DIR
                    }

                }

PREMIER_PARAMS = {
                    "league": {
                        "league_name": PREMIER,
                        "n_prev_match": 10,
                        "league_dir": DATA_DIR,
                        "train": "True"
                    },
                    "data": {
                        "normalize": "True",
                        "window_size": 50,
                        "dataset": BASE_DATASET,
                        "split_size": 0.986,    # TO BE UPDATED (~50)
                        "test_size": 100,
                        "batch_size": 10,
                        "version": 2,
                        "league_dir": DATA_DIR,
                        "train": "True"
                    },
                    "model": {
                        "dataset": BASE_DATASET,
                        "version": 2,
                        "out_lstm": 100,
                        "n_lstm_layer": 2,
                        "bidirectional": "True",
                        "kernel": 10,
                        "padding": 1,
                        "conv_layers": 1,
                        "optimizer": ADAM_OPTIMIZER,
                        "lr": 0.00001,
                        "loss": BCE_LOSS,
                        "seed": 2020,
                        "device": CUDA_DEVICE,
                        "verbose": "True",
                        "plot": "False",
                        "static_dir": STATIC_DIR
                    }

                }

MODEL_PARAMS = {SERIE_A: SERIE_A_PARAMS}