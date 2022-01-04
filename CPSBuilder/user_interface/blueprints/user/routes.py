from flask import Blueprint
from flask import render_template, request, flash, redirect, url_for, session, logging
from flask_wtf import FlaskForm
from CPSBuilder.user_interface.blueprints.user.forms import RegisterForm, LoginForm, EditProfile, ChangePassword


from CPSBuilder.modules.auth_module import AuthModule
from CPSBuilder.modules import visualizer, manager

import logging
logger = logging.getLogger(__name__)

#initialize MongoDB client
from pymongo import MongoClient
import config
client = MongoClient(config.mongo_ip, config.mongo_port)

#initialize user
user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

#initialize modules
auth_module = AuthModule(client)
profile_display = visualizer.ProfileVisualizer(client)
profile_manager = manager.ProfileManager(client)


@user.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate():
            name = form.name.data
            user_id = form.user_id.data
            password = form.password.data
            position = form.position.data
            if auth_module.register_user(name, user_id, password, position):
                flash("You are now registered", "success")
                # session["user_id"] = user_id
            else:
                flash("This ID is already registered", "danger")
                return render_template("register.html", form=form)
            return redirect(url_for("user.login"))
        else:
            flash("Validation failed", "danger")
    return render_template("register.html", form=form)

@user.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method =="POST" and form.validate():
        user_id = form.user_id.data
        password = form.password.data
        if auth_module.login_user(user_id, password):
            profile_details = profile_display.get_profile(user_id)
            session["user_id"] = user_id
            print(profile_details)
            session["is_admin"] = profile_details["is_admin"]
            return redirect(url_for("main.index"))
        else:
            flash("Wrong Username or Password", "danger")
    return render_template("login.html", form=form)


@user.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@user.route("/user/<user_id>", methods = ["GET", "POST"])
def profile(user_id):
    profile_details = profile_display.get_profile(user_id)
    if request.method == "POST":
        if request.form.get("password", None):
            return redirect(url_for("user.change_password", user_id=user_id))
        if request.form.get("edit", None):
            return redirect(url_for("user.edit_profile", user_id=user_id))
    return render_template("profile.html", profile_details=profile_details)


@user.route("/user/<user_id>/edit", methods = ["GET", "POST"])
def edit_profile(user_id):
    profile_details = profile_display.get_profile(user_id)
    form = EditProfile()
    if request.method == "POST":
        if request.form.get("confirm", None):
            new_info = dict()
            new_info["name"] = form.name.data
            new_info["position"] = form.position.data
            profile_manager.edit_profile(user_id, new_info)
            flash("Profile Edited", "success")
            return redirect(url_for("user.profile", user_id=user_id))
    return render_template("edit_profile.html", profile_details=profile_details, form=form)


@user.route("/user/<user_id>/change_password", methods = ["GET", "POST"])
def change_password(user_id):
    profile_details = profile_display.get_profile(user_id)
    form = ChangePassword()
    if request.method == "POST":
        if request.form.get("confirm", None) and form.validate():
            password_old = form.old_password.data
            password_new = form.new_password.data
            password_confirm = form.confirm_password.data
            if password_new == password_confirm:
                if auth_module.change_password(user_id, password_old, password_new, profile_details["name"]):
                    flash("Password Changed", "success")
                    return redirect(url_for("user.profile", user_id=user_id))
                else:
                    flash("Wrong Password", "danger")
            else:
                flash("Passwords do not match", "danger")
    return render_template("change_password.html", profile_details=profile_details, form=form)

