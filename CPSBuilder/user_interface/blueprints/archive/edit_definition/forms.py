from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.widgets.core import ListWidget, CheckboxInput


class EditListElementForm(FlaskForm):
    new_element = StringField('Item to be added:')
    element_idx = StringField(
        'Enter item index to edit. Defaults to the last item.')
    location_id = SelectField(
        'Location where the action is executed:', choices=[(None, 'None')])
    add_element = SubmitField('Add')
    remove_element = SubmitField('Remove')
    submit_configuration = SubmitField('Submit')
    cancel_edit = SubmitField('Cancel')


class ExecListForm(FlaskForm):
    choices = [
        (False, ''),
        ('hardware', 'Hardware'),
        ('robot', 'Robot'),
        ('human', 'Human')
    ]
    exec_class = SelectField('Executor Class: ', choices=choices)
    exec_type = SelectField('Executor Type: ', choices=[(False, '')])
    dependency = SelectField('Dependencies: ', choices=[
                             (None, 'None')])
    software_id = SelectField("Software: ", choices=[])
    apply_changes = SubmitField('Apply Changes')
    submit_changes = SubmitField('Submit')
