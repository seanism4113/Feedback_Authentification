from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired()])
    password = PasswordField('Password', validators = [InputRequired(), Length(min=8, message='Password must be a minimum of a characters')])
    email = EmailField('Email', validators = [InputRequired()],render_kw={'placeholder': 'johnDoe@gmail.com'})
    first_name = StringField('First Name', validators = [InputRequired()])
    last_name = StringField('Last Name', validators = [InputRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired()])
    password = PasswordField('Password', validators = [InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField('Title', validators = [InputRequired()])
    content = TextAreaField('Content', validators = [InputRequired()])


