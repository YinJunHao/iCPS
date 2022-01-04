from flask import Blueprint, render_template, session

import logging

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__, static_folder="static", template_folder="templates")


@main.route("/")
def index():
    return render_template("home.html")


@main.route("/about")
def about():
    return render_template("about.html")
