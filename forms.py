from flask_wtf import FlaskForm
from wtforms import SelectField
from flask import Markup


class LanguageForm(FlaskForm):
    language = SelectField('Language', choices=[ ('es', 'Español') , ('en', 'English')])