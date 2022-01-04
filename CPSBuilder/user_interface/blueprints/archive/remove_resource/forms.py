from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, SelectField, SelectMultipleField, validators
from wtforms.widgets.core import ListWidget, CheckboxInput


class ResourceTypeForm(FlaskForm):
    choose_software = SubmitField('Software')
    choose_hardware = SubmitField('Hardware')
    choose_robot = SubmitField('Robot')
    choose_workcell = SubmitField('Workcell')


class MultipleCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class RobotOptionForm(FlaskForm):
    robot_list = MultipleCheckboxField("Robot list", coerce=int)


class HardwareOptionForm(FlaskForm):
    hardware_list = MultipleCheckboxField("Hardware list", coerce=int)


class SoftwareOptionForm(FlaskForm):
    software_list = MultipleCheckboxField("Software list", coerce=int)


class WorkcellOptionForm(FlaskForm):
    workcell_list = MultipleCheckboxField("Workcell List", coerce=int)


class EquipmentDetailsForm(FlaskForm):
    equipment_request_id = HiddenField("equipment_request_id")
    equipment_details = SubmitField("See Details")


class EquipmentDetailsOptionForm(FlaskForm):
    equipment_details = MultipleCheckboxField(
        "Registered Equipment List", coerce=int)
