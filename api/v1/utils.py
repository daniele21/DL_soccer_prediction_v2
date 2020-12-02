import io
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg
from flask import Response, render_template

import scripts.data.constants as K
from scripts.utils.loading import load_configs

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

        for league_name in K.LEAGUE_NAMES:
            model, config = load_configs(league_name)

            models[league_name] = model
            configs[league_name] = config

        return models, configs