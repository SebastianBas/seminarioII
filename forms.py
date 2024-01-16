from flask_wtf import FlaskForm
from wtforms import SelectField

class LanguageForm(FlaskForm):
    language = SelectField('Language', choices=[ ('es', 'Español') , ('en', 'English')])