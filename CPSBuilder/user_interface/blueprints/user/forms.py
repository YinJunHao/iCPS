from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField, SelectField


class RegisterForm(FlaskForm):
    name = StringField("Name: ", validators=[validators.InputRequired()])
    position = SelectField("Position: ", choices=[("Lecturer", "Lecturer"), ("Research Engineer", "Research Engineer"),
                                                  ("PhD Student", "PhD Student"), ("Master Student", "Master Student"),
                                                  ("FYP Student", "FYP Student"), ("Others", "Others")])
    user_id = StringField("User ID: ", validators=[validators.InputRequired()])
    password = PasswordField("Password: ", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Passwords do not match.")
    ])
    confirm = PasswordField("Confirm Password: ")


class LoginForm(FlaskForm):
    user_id = StringField("User ID: ", validators=[validators.InputRequired()])
    password = PasswordField("Password: ", validators=[validators.InputRequired()])


class EditProfile(FlaskForm):
    name = StringField("Name: ", validators=[validators.InputRequired()])
    position = SelectField("Position: ", choices=[("Lecturer", "Lecturer"), ("Research Engineer", "Research Engineer"),
                                                  ("PhD Student", "PhD Student"), ("Master Student", "Master Student"),
                                                  ("FYP Student", "FYP Student"), ("Others", "Others")])


class ChangePassword(FlaskForm):
    old_password = PasswordField("Old Password: ", validators=[validators.InputRequired()])
    new_password = PasswordField("New Password: ", validators=[validators.InputRequired(),
                                                             validators.EqualTo("confirm_password",
                                                                                message="Passwords must match")])
    confirm_password = PasswordField("Confirm Password: ", validators=[validators.InputRequired(),
                                                                     validators.EqualTo("new_password",
                                                                                        message="Passwords must match")])
