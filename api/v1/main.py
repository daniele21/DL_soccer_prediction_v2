from flask import render_template
from . import app

@app.route('/')
def homepage():
    return render_template('index.html')


