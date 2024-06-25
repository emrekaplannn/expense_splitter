from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import FloatField
from wtforms import SelectField

from wtforms.fields.simple import HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from models import User


class RegistrationForm(FlaskForm):
    name = StringField('Name',
                       validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=8,
                                                            message='Password should be at least %(min)d characters '
                                                                    'long')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')


class KittyForm(FlaskForm):
    kitty_name = StringField('Event Name', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    money = HiddenField('Home Currency', default='TRY')
    participants = StringField('Participant', validators=[DataRequired()])
    submit = SubmitField('Create Kitty')




class ExpenseAdditionForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    split_equally = BooleanField('Split Equally',default=True)
    group_member_checkboxes = SelectMultipleField('Group Members')
    payer = SelectField('Payer', coerce=int)
    submit = SubmitField('Add Expense')
