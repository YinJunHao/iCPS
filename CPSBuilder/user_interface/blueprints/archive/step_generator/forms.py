from flask_wtf import FlaskForm
from wtforms import SelectField, RadioField, SubmitField, validators, SelectMultipleField, HiddenField
from wtforms.widgets.core import ListWidget, CheckboxInput


class GetActionForm(FlaskForm):
    action = SelectField(
        "Select Action",
        choices=[]
    )


class GetTaskForm(FlaskForm):
    task = SelectField(
        "Select Task",
        choices=[]
    )


class MultipleCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class GetStepForm(FlaskForm):
    step = RadioField(
        "Select Preferred Scenario",
        choices=[],
        validators=[validators.InputRequired()]
    )


class SubmitCancelForm(FlaskForm):
    accept = SubmitField('Accept')
    cancel = SubmitField('Cancel')


class EditLineStepForm(FlaskForm):
    step_list = MultipleCheckboxField("Generated step", coerce=int)


class OptimizeActionForm(FlaskForm):
    request_id = HiddenField('request_id')
    optimize_item = SubmitField('Optimize')
    review_item = SubmitField('Review')
    use_existing = SubmitField('Use Existing')


class SubmitJobForm(FlaskForm):
    submit_job = SubmitField('Submit Job')


class EditExecForm(FlaskForm):
    step_request_id = HiddenField('step_request_id')
    exec_request_id = HiddenField('exec_request_id')
    edit_exec = SubmitField('Edit Executor')
    edit_software = SubmitField('Edit Software')
    allow_alternative = SubmitField(' ')


class ChangeSoftwareForm(FlaskForm):
    new_software = RadioField(
        "Select New Software",
        choices=[],
        validators=[validators.InputRequired()]
    )


class ChangeExecChoiceForm(FlaskForm):
    new_exec = RadioField(
        "Select New Executor",
        choices=[],
        validators=[validators.InputRequired()]
    )
