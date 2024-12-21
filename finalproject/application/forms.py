from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired

class TodoForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    completed = SelectField('Completed', choices=[("False", "No"), ("True", "Yes")], validators=[DataRequired()])
    due_date = DateField('Due Date')
    priority = SelectField('Priority', choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")])
    submit = SubmitField("Submit")
