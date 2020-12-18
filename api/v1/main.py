from flask import Flask
from flask import render_template
# from api.v1.services.read import get_teams
from . import app

@app.route('/')
def homepage():
    return render_template('index.html')
