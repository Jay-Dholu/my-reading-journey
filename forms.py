from wtforms import StringField, PasswordField, TextAreaField, FileField, DecimalField, DateField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from flask_wtf.file import FileAllowed, FileRequired
from flask_wtf import FlaskForm


class SignUp(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    userid = StringField(label='User ID', validators=[DataRequired(), Length(2, 20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(8, 30)])
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), Length(8, 30), EqualTo('password', message="Passwords didn't matched!")])
    submit = SubmitField(label='Sign Up')


class Login(FlaskForm):
    email = StringField(label='Email')
    userid = StringField(label='User ID')
    password = PasswordField(label='Password', validators=[DataRequired(), Length(8, 30)])
    submit = SubmitField(label='Login')

    def validate(self, extra_validators=None):
        # Call the default validator
        if not super().validate():
            return False

        # Custom logic: ensure at least one of email or userid is filled
        if not self.email.data and not self.userid.data:
            raise ValidationError("Either Email or User ID must be filled.")

        return True


class Book(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    author = StringField(label='Author')
    genre = StringField(label='Genre')
    rating = DecimalField(label='Rating', places=1, validators=[NumberRange(min=0, max=5)], default=0)
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
