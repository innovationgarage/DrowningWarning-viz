import os
from app import app
from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename

class DataInputForm(FlaskForm):
    starttime = DateTimeField('Starttime', validators=[DataRequired()])
    capture = FileField('Capture', validators=[
        FileRequired(), 
        FileAllowed(app.config["ALLOWED_CAPTURE_EXTENSIONS"], 'This file should be formated as a csv with a .txt or .csv extension!')
        ])
    telespor = FileField('Telespor', validators=[
        FileRequired(), 
        FileAllowed(app.config["ALLOWED_TELESPOR_EXTENSIONS"], 'Upload a CSV file please!')
        ])
    submit = SubmitField('Submit')