from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
import app


class RegistrationForm(FlaskForm):
    name = StringField("Name", [DataRequired()])
    email = StringField("Email", [Email()])
    status = SelectField(
        "Status",
        choices=[("client", "Client"), ("employee", "Employee")],
        validators=[DataRequired()],
    )
    password = PasswordField("Password", [DataRequired()])
    confirmed_password = PasswordField(
        "Repeat Password", [EqualTo("password", "Passwords must match.")]
    )
    submit = SubmitField("Register")

    def check_name(self, name):
        user = app.User.query.filter_by(vardas=name.data).first()
        if user:
            raise ValidationError(
                "Name is already used, please choose a different name."
            )

    def check_email(self, el_pastas):
        user = app.User.query.filter_by(el_pastas=el_pastas.data).first()
        if user:
            raise ValidationError(
                "This email is already used, please choose a different email or try to login."
            )


class LoginForm(FlaskForm):
    email = StringField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    remember = BooleanField("Remember me")
    status = SelectField(
        "Status",
        choices=[("client", "Client"), ("employee", "Employee")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Login")
