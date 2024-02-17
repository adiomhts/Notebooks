from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    old_password = PasswordField('Old password')
    new_password = PasswordField('New password', validators=[Length(min=6, message='The password must contain more than 6 characters.')])
    confirm_password = PasswordField('Confirm new password', validators=[EqualTo('new_password', message='Passwords have to match.')])
    submit = SubmitField('Save changes')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6, message='The password must contain more than 6 characters.')])
    confirm_password = PasswordField('Confirm password', validators=[EqualTo('password', message='Passwords have to match.')])
    submit = SubmitField('Sign up')
