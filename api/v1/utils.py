import io

from matplotlib.backends.backend_agg import FigureCanvasAgg
from flask import Response, render_template, make_response

import scripts.constants.league as LEAGUE
from scripts.utils.checker import check_league, check_predict_paths
from scripts.utils.loading import load_configs, load_configs_from_paths


def show_plot(fig):

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype=f"image/png")

def load_models(league_name=None):

    if league_name is not None:
        model, config = load_configs(league_name)

        return model, config

    else:
        models, configs = {}, {}

        for league_name in LEAGUE.LEAGUE_NAMES:
            model, config = load_configs(league_name)

            models[league_name] = model
            configs[league_name] = config

        return models, configs


def load_model_and_config(req_params, models, configs):

    model, config = None, None

    if ('league_name' in req_params.keys() and models is not None and configs is not None):
        league_name = req_params['league_name']
        outcome, msg = check_league(league_name)
        if (outcome == False):
            response = {'check':False,
                        'msg':msg}

        # league_params = configs[league_name]['league']
        # data_params = configs[league_name]['data']
        # model = models[league_name]
        # feat_eng = configs[league_name]['feat_eng']
        else:
            model, config = models[league_name], configs[league_name]
            response = {'check': True}

    elif ('model_dir' in req_params.keys() and 'model_name' in req_params.keys()):
        model_dir = req_params['model_dir']
        model_name = req_params['model_name']
        response = check_predict_paths(model_dir, model_name)

        if (response['check']):

            paths = response['paths']
            config, model = load_configs_from_paths(paths)
            # league_params = config['league']
            # data_params = config['data']
            # feat_eng = config['feat_eng']

    else:
        msg = 'Body does not provide the required params'
        response = {'check':False,
                    'msg':msg}

    return response, model, config