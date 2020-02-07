import os
from app import app
from flask import render_template, url_for
from flask import request, redirect
from flask import jsonify, make_response
from datetime import datetime
from werkzeug.utils import secure_filename

# forms.py
from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename

class DataInputForm(FlaskForm):
    starttime = StringField('Starttime', validators=[DataRequired()])
    capture = FileField('Capture', validators=[
        FileRequired(), 
        FileAllowed(app.config["ALLOWED_CAPTURE_EXTENSIONS"], 'This file should be formated as a csv with a .txt or .csv extension!')
        ])
    telespor = FileField('Telespor', validators=[
        FileRequired(), 
        FileAllowed(app.config["ALLOWED_TELESPOR_EXTENSIONS"], 'Upload a CSV file please!')
        ])
    submit = SubmitField('Submit')
#

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
    form = DataInputForm()
    if form.validate_on_submit():
        print('OK!')
        print('Starttime:', form.starttime.data)
        capture = form.capture.data
        cap_filename = secure_filename(capture.filename)
        capture.save(os.path.join(app.root_path, app.config['FILE_UPLOADS'], cap_filename))
        print('Capture:', cap_filename)
        telespor = form.telespor.data
        ts_filename = secure_filename(telespor.filename)
        telespor.save(os.path.join(app.root_path, app.config['FILE_UPLOADS'], ts_filename))
        print('Telespor:', ts_filename)
        redirect(url_for('input-data', form=form))
    print('TS ERRORS', form.telespor.errors)
    print('CAP ERRORS', form.capture.errors)
    return render_template("public/input_data.html", form=form)


@app.route("/map")
def show_map():
    return render_template("public/map.html")
