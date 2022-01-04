from flask_wtf import FlaskForm
from wtforms import StringField, validators, FormField, FieldList, SubmitField
from wtforms import SelectField, HiddenField


class NewTaskForm(FlaskForm):
    task = StringField("New Task Name: ", validators=[
                       validators.InputRequired()])
    submit_task = SubmitField('Submit')
    recommendation_task = SubmitField('Recommend Steps')


class NewActionForm(FlaskForm):
    action_list = FieldList(StringField("Action: "), min_entries=1)


class StepListForm(FlaskForm):
    step_list = FieldList(StringField("Step: "), min_entries=1)


class ExecListForm(FlaskForm):
    choices = [
        ('hardware', 'Hardware'),
        ('robot', 'Robot'),
        ('human', 'Human')
    ]
    exec_class = SelectField('Executor Class: ', choices=choices)
    exec_type = SelectField('Executor Type: ', choices=[])
    dependency = SelectField('Dependencies (Must be from the past): ', choices=[(None, "None")])
    software = SelectField("Software: ", choices=[(None, "None")])


class SubmitExecForm(FlaskForm):
    submit_exec = SubmitField('Submit')


class AddRemoveSoftware(FlaskForm):
    add_software = SubmitField('Add More')
    remove_software = SubmitField('Remove')


class ChooseRecommendationForm(FlaskForm):
    request_id = HiddenField('choose_recommendation')
    choose_recommendation = SubmitField('Choose')


class EnterNewActionForm(FlaskForm):
    submit_choice = SubmitField('New Action List')


class EnterNewStepForm(FlaskForm):
    submit_choice = SubmitField('New Step List')
