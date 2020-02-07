from flask_wtf import FlaskForm
from wtforms import DateTimeField, StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

class DataInputForm(FlaskForm):
    starttime = DateTimeField('Starttime', validators=[DataRequired()])
#    capture = FileField('Capture', validators=[FileRequired()])
#    telespor = FileField('Telespor', validators=[FileRequired()])
    submit = SubmitField('Submit')

