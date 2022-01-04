from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class SeeDetailForm(FlaskForm):
    request_id = HiddenField("request_id")
    see_detail = SubmitField("Details")
    see_progress = SubmitField("See Progress")


class CloseDetailForm(FlaskForm):
    close_detail = SubmitField("Close")
