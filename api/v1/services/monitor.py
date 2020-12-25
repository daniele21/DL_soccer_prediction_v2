from flask import current_app as app
from flask import render_template

from api.v1.utils import show_plot
from core.file_manager.loading import load_json
from scripts.constants.paths import STATIC_DIR
from scripts.visualization.plots import plot_loss


@app.route('/api/v1/monitor/training', methods=['GET'])
def training_monitor():

    losses_filepath = f'{STATIC_DIR}losses.json'
    losses_dict = load_json(losses_filepath)

    train_losses = losses_dict['train']
    eval_losses = losses_dict['eval']

    fig = plot_loss(train_losses, eval_losses,
                    figsize=(7, 5), save=False,
                    plot=False)

    return show_plot(fig)


