import os
from app import app
from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, TextField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from datetime import datetime


class DataInputForm(FlaskForm):
    epoch = '1970-01-01 00:00:00'
    starttime = DateTimeField('Starttime*', validators=[DataRequired()])
    capture = FileField('Capture*', validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_CAPTURE_EXTENSIONS"],
                    'This file should be formated as a csv with a .txt or .csv extension!')
    ])
    telespor = FileField('Telespor*', validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_TELESPOR_EXTENSIONS"],
                    'Upload a CSV file please!')
    ])
    # , default=datetime.strptime(epoch, '%Y-%m-%d %H:%M:%S'))
    signalstart = DateTimeField('Signal start')
    # , default=datetime.strptime(epoch, '%Y-%m-%d %H:%M:%S'))
    signalend = DateTimeField('Signal end')
    samplerate = SelectField('Sample rate', choices=[(
        '10S', '10S'), ('60S', '60S')], default='10S')
    submit = SubmitField('Submit')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        result = True
        if self.signalstart.data < self.starttime.data:
            result = False
        if self.signalend.data < self.signalstart.data:
            result = False
        return result
