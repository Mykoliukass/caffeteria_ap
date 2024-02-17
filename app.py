import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    current_user,
    logout_user,
    login_user,
    UserMixin,
    login_required,
)
import forms

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = "4654f5dfadsrfasdr54e6rae"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "restaurant_online.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "prisijungti"
login_manager.login_message_category = "info"


class UserRole(Enum):
    CLIENT = "client"
    EMPLOYEE = "employee"


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(20), unique=True, nullable=False)
    email = db.Column("Email address", db.String(120), unique=True, nullable=False)
    password = db.Column("Password", db.String(60), unique=True, nullable=False)
    status = db.Column(db.String(10), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        coded_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        status = form.status.data or "client"
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=coded_password,
            status=status,
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration was successful! You may login", "success")
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Failed to login, please check your details again", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")


# Uncomment the route if you want to include it
# @app.route("/irasai")
# @login_required
# def irasai():
#     return render_template("irasai.html", title="Įrašai")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=8000, debug=True)
