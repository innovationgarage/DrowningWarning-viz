import os
from app import app
from flask import render_template, url_for
from flask import request, redirect, send_from_directory
from flask import jsonify, make_response
from datetime import datetime
from werkzeug.utils import secure_filename
from . import preprocess
from . import forms

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
    return render_template("public/index.html")


@app.route("/about")
def about():
    return render_template("public/about.html")


@app.route("/dashboard")
def admin_dashboard():
    return render_template("public/dashboard.html")

@app.route("/input-data", methods=["GET", "POST"])
def input_data():
    form = forms.DataInputForm(csrf_enabled=False)
    if form.validate_on_submit():
        capture = form.capture.data
        cap_filename = secure_filename(capture.filename)
        capture.save(os.path.join(app.root_path, app.config['FILE_UPLOADS'], cap_filename))

        telespor = form.telespor.data
        ts_filename = secure_filename(telespor.filename)
        telespor.save(os.path.join(app.root_path, app.config['FILE_UPLOADS'], ts_filename))
        return redirect(url_for('data_submit', cap_filename=cap_filename, ts_filename=ts_filename, starttime=form.data['starttime']))
    else:
        cap_filename = None
        ts_filename = None

    return render_template("public/input_data.html", form=form)

@app.route("/data-submit")
def data_submit():
    starttime = request.values['starttime']
    cap_filename = os.path.join(app.root_path, app.config['FILE_UPLOADS'], request.values['cap_filename'])
    ts_filename = os.path.join(app.root_path, app.config['FILE_UPLOADS'], request.values['ts_filename'])
    args = {
        'ti': ts_filename,
        'ci': cap_filename,
        'allout': os.path.join(app.root_path, app.config['FILE_PROCESSED'], 'all_data.csv'),
        'starttime': starttime,
        'signalstart': "2019-10-11 11:00:00+00:00",
        'signalend': "2019-10-11 17:00:00+00:00",
        'samplerate': "10S"
    }
    preprocess.main(args)
    return render_template("public/map.html")    

@app.route("/map")
def show_map():
    return render_template("public/map.html")
