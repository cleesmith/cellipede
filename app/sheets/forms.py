from flask_wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class SheetForm(Form):
  name = StringField('Name', validators=[DataRequired()])
  run_at = SelectField(u'Autorun',
    choices=[
      ('never', 'Autorun: never'), ('hourly', 'Autorun: hourly'), ('daily', 'Autorun: daily'), ('weekly', 'Autorun: weekly')
    ]
  )
  gspread_link = StringField('Google Spreadsheet Link', validators=[DataRequired()])
  asheet = TextAreaField('Sheet')
