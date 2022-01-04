from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, validators, FloatField, ValidationError


class NewProcessForm(FlaskForm):
    task_name = StringField("Task name: ", validators=[
                             validators.InputRequired()])

class PhysicalResourceForm(FlaskForm):
    name = StringField("Name", validators=[validators.InputRequired()])
    type = SelectField("Type", choices=[])
    type_new = StringField("If the desired type is not found")
    position_sensor_tag = StringField("Position Sensor Tag (if none, leave blank)")
    location_id = SelectField("Location ID", choices=[])


class CyberResourceForm(FlaskForm):
    name = StringField("Name", validators=[validators.InputRequired()])
    type = SelectField("Type", choices=[])
    type_new = StringField("If desired type not found, enter here")
    param = StringField("Parameters")
    state = StringField("States")


class LocationResourceForm(FlaskForm):
    name = StringField("Name", validators=[validators.InputRequired()])
    type = SelectField("Type", choices=[])
    type_new = StringField("If the desired type is not found")
    position_x = FloatField("x", validators=[validators.InputRequired()])
    position_y = FloatField("y", validators=[validators.InputRequired()])
    position_z = FloatField("z", validators=[validators.InputRequired()])
    alpha = FloatField("α", validators=[validators.InputRequired()])
    beta = FloatField("β", validators=[validators.InputRequired()])
    gamma = FloatField("γ", validators=[validators.InputRequired()])
    length = FloatField("L.", validators=[validators.InputRequired()])
    width = FloatField("W.", validators=[validators.InputRequired()])
    height = FloatField("H.", validators=[validators.InputRequired()])
