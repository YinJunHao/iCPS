from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField


class EditActionForm(FlaskForm):
    task_request_id = HiddenField('task_request_id')
    action_request_id = HiddenField('action_request_id')
    edit_item = SubmitField('Edit Definition')


class DeleteActionForm(FlaskForm):
    request_id = HiddenField('request_id')
    edit_task = SubmitField('Edit Definition')
    delete_item = SubmitField('Delete')


class DeleteActionDefinitionForm(FlaskForm):
    request_id = HiddenField('request_id')
    delete_item = SubmitField('Delete Definition')


class EditStepForm(FlaskForm):
    action_request_id = HiddenField('action_request_id')
    step_request_id = HiddenField('step_request_id')
    edit_item = SubmitField('Edit Step')


class ConfirmEditsForm(FlaskForm):
    confirm_edits = SubmitField('Confirm Edits')


class EditExecForm(FlaskForm):
    exec_request_id = HiddenField('exec_request_id')
    edit_item = SubmitField('Edit')
    delete_item = SubmitField('Delete')


class AddExecForm(FlaskForm):
    add_exec = SubmitField('Add New Executor Definition')
    confirm_add_exec = SubmitField('Confirm Changes')


class AddStepForm(FlaskForm):
    add_step = SubmitField('Add New Step List')


class AddActionForm(FlaskForm):
    add_action = SubmitField('Add New Action List')


class AddTaskForm(FlaskForm):
    add_task = SubmitField('Add New Task')
