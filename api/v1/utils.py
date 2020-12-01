import io
import base64

from matplotlib.backends.backend_agg import FigureCanvasAgg
from flask import Response, render_template


def show_plot(fig):

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)

    return Response(output.getvalue(), mimetype=f"image/png")