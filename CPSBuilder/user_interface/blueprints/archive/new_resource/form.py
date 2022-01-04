from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, SelectMultipleField, ValidationError


class NewRobotForm(FlaskForm):
    robot_name = StringField("Robot name: ", validators=[
                             validators.InputRequired()])
    robot_type_new = StringField(
        "If the desired type is not among the choices, enter it below:")
    robot_type = SelectField("Choose robot type: ", choices=[])
    position_sensor_tag = StringField("Position sensor tag (if None, leave blank): ")
    location_id = SelectField("Choose location_id: ", choices=[])
    submit_robot = SubmitField('Submit')


class NewHardwareForm(FlaskForm):
    hardware_name = StringField("Hardware name: ", validators=[
                                validators.InputRequired()])
    hardware_type_new = StringField(
        "If the desired type is not among the choices, enter it below:")
    hardware_type = SelectField("Choose hardware type: ", choices=[])
    position_sensor_tag = StringField("Position sensor tag (if None, leave blank): ")
    location_id = SelectField("Choose location_id: ", choices=[])
    submit_hardware = SubmitField('Submit')


class NewSoftwareForm(FlaskForm):
    software_name = StringField(
        "Enter software/script name: ", validators=[validators.InputRequired()])
    software_type = SelectField("Choose software/script type: ", choices=[])
    software_type_new = StringField(
        "If the desired type is not among the choices, enter it below:")

    # software_step = SelectMultipleField("Choose the step where software is used", choices=[], validators=[validators.InputRequired()])
    submit_software = SubmitField('Submit')


class ResourceTypeForm(FlaskForm):
    choose_software = SubmitField('Software')
    choose_hardware = SubmitField('Hardware')
    choose_robot = SubmitField('Robot')

def length_check(min = -1, max= -1):
    message = 'stupid'
    def _length_check(FlaskForm, field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            flash(message)
    return _length_check

def numeric_check(message = 'stupid. numbers please'):
    def _numeric_check(FlaskForm, field):
        field_input = field.data
        try:
            numeric_field = float(field_input)
        except:
            print(message)
            flash(f"{field.name}: ' + message, 'danger')
            raise ValidationError(message)
    return _numeric_check

class NewWorkcellForm(FlaskForm):
    workcell_id = SelectField("Choose workcell: ", choices=[])
    workcell_id_new = StringField(
        "If the workcell ID is not among the listed IDs, enter ID below:")
    location_name = StringField("Enter location name", validators=[
                                validators.InputRequired()])
    x_min = StringField("x_min", validators=[
        validators.InputRequired(), numeric_check()])
    x_max = StringField("x_max", validators=[
        validators.InputRequired(), numeric_check()])
    y_min = StringField("y_min", validators=[
        validators.InputRequired(), numeric_check()])
    y_max = StringField("y_max", validators=[
        validators.InputRequired(), numeric_check()])
    z_min = StringField("z_min", validators=[
        validators.InputRequired(), numeric_check()])
    z_max = StringField("z_max", validators=[
        validators.InputRequired(), numeric_check()])
    submit_workcell = SubmitField('Submit')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if (self.x_min.data >= self.x_max.data) or (self.y_min.data >= self.y_max.data) or (self.z_min.data >= self.z_max.data):
            message = "Maximum value must be larger than minimum value."
            print(message)
            flash(message, 'danger')
            return False
        else:
            return True


class NewEquipmentDetailsForm(FlaskForm):
    equipment_id = SelectField("Choose Equipment ID")
    submit_equipment = SubmitField("Register Equipment")
