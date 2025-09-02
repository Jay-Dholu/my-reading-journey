from wtforms import StringField, EmailField, PasswordField, TextAreaField, FileField, DecimalField, DateField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileAllowed, FileRequired
from flask_wtf import FlaskForm
from decimal import Decimal
from models import User


class SignUp(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired(message="Name is required!")])
    userid = StringField(label='User ID', validators=[DataRequired(message="User ID is required!"), Length(2, 20)])
    email = EmailField(label='Email', validators=[DataRequired(message="Email is required!"), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(message="Password is required!"), Length(8, 30)])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(message="Confirm Password is required!"), Length(8, 30), EqualTo('password', message="Passwords didn't matched!")])
    submit = SubmitField(label='Sign Up')


class Login(FlaskForm):
    email = EmailField(label='Email')
    userid = StringField(label='User ID')
    password = PasswordField(label='Password', validators=[DataRequired(), Length(8, 30)])
    submit = SubmitField(label='Login')

    def validate(self, extra_validators=None):
        # Call the default validator
        if not super().validate():
            return False

        # My custom logic to ensure at least one of email or userid is filled, else this will not let user proceed
        if not self.email.data and not self.userid.data:
            raise ValidationError("Either Email or User ID must be filled.")

        return True


class Book(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    author = StringField(label='Author')
    isbn = StringField(label='ISBN', validators=[Optional(), Length(min=10, max=20, message="An ISBN must be 10 to 20 characters long.")])
    genre = StringField(label='Genre')
    rating = DecimalField(label='Rating', places=1, validators=[Optional(), NumberRange(min=0, max=5)], default=Decimal('0.0'))
    description = TextAreaField(label='Description')
    cover_image = FileField(label='Upload Book Cover', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    reading_started = DateField(label='Date Started', validators=[Optional()])
    reading_finished = DateField(label='Date Finished', validators=[Optional()])
    submit = SubmitField('Add Book')


class Data(FlaskForm):
    json_file = FileField('Choose JSON File', validators=[
        FileRequired(),
        FileAllowed(['json'], 'JSON files only!')
    ])
    submit = SubmitField('Upload')


class RequestReset(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    submit = SubmitField(label='Request Password Reset')


class ResetPassword(FlaskForm):
    password = PasswordField(label='New Password', validators=[DataRequired(), Length(8, 30)])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), Length(8, 30), EqualTo('password', message="Passwords didn't matched!")])
    submit = SubmitField(label='Reset Password')


class ResendVerification(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Email')


class EditProfile(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    userid = StringField(label='User ID', validators=[DataRequired(), Length(2, 20)])
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='New Password', validators=[Optional(), Length(8, 30)])
    confirm_password = PasswordField(label='Confirm Password', validators=[Optional(), EqualTo('password', message="Passwords didn't match!")])
    submit = SubmitField(label='Update Profile')

    def validate_email(self, email):
        current_user_id = self.meta.current_user_id
        user = User.query.filter_by(email=email.data).first()

        if user and user.id != current_user_id:
            raise ValidationError('This Email Address is already taken. Please choose another one.')
        
    def validate_userid(self, userid):
        current_user_id = self.meta.current_user_id
        user = User.query.filter_by(userid=userid.data).first()

        if user and user.id != current_user_id:
            raise ValidationError('This User ID is already taken. Please choose another one.')
