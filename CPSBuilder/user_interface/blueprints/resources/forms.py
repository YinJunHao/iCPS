from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, validators, FloatField, ValidationError, DecimalField, SubmitField

def number_check(form, field):
    if not isinstance(field.data, int) or not isinstance(field.data, float):
        raise ValidationError("Input must be a number")


class PhysicalResourceForm(FlaskForm):
    name = StringField("Name")
    type = SelectField("Type", choices=[])
    type_new = StringField("If the desired type is not found, enter here")
    position_sensor_tag = StringField("Position Sensor Tag (input Location if none)")
    position_x = FloatField("x")
    position_y = FloatField("y")
    position_z = FloatField("z")
    status = SelectField("Status", coerce=int, choices=[(1, "Active"), (0, "Inactive")])
    submit = SubmitField("Add New Resource")
    location_id = SelectField("Location ID", choices=[])


class CyberResourceForm(FlaskForm):
    name = StringField("Name")
    type = SelectField("Type", choices=[])
    type_new = StringField("If desired type not found, enter here")
    param = StringField("Parameters")
    state = StringField("States")
    physical_resource = SelectField("Software for Physical Resource/s", choices=[])


class LocationResourceForm(FlaskForm):
    name = StringField("Name")
    type = SelectField("Type", choices=[])
    type_new = StringField("If the desired type is not found, enter here")
    position_x_min = FloatField("x min")
    position_y_min = FloatField("y min")
    position_z_min = FloatField("z min")
    position_x_max = FloatField("x max")
    position_y_max = FloatField("y max")
    position_z_max = FloatField("z max")
    alpha = FloatField("α")
    beta = FloatField("β")
    gamma = FloatField("γ")
    length = FloatField("Length")
    width = FloatField("Width")
    height = FloatField("Height")

    # def validate_name(self, name):
    #     if len(name.data) == 0:
    #         raise ValidationError('Name must be less than 50 characters')