from flask import Blueprint, render_template, request, redirect, url_for, flash

from CPSBuilder.utils.archive.module_functions import *
from CPSBuilder.utils.route import *

from CPSBuilder.modules.archive.action_management_module import ActionManagementModule
from CPSBuilder.modules.archive.task_management_module import TaskManagementModule
from CPSBuilder.modules.archive.resource_management_module import ResourceManagementModule
from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule


from CPSBuilder.user_interface.blueprints.edit_definition.forms import EditListElementForm, ExecListForm

import config

import logging
logger = logging.getLogger(__name__)

# config mongodb
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize blueprint
edit_definition = Blueprint(
    'edit_definition', __name__, template_folder='templates')

# initialize modules
action_management_module = ActionManagementModule(client)
task_management_module = TaskManagementModule(client)
resource_management_module = ResourceManagementModule(client)
executor_mapping_module = ExecutorMappingModule(client)


@edit_definition.route('/edit_action', methods=['GET', 'POST'])
def edit_action():
    task_var = request.args.get('task_var')
    task_sentence = request.args.get('task_sentence')
    task_id = request.args.get('task_id')
    cur_action_var_sentence_list = session.get('cur_list', None)

    if cur_action_var_sentence_list is None:
        cur_action_var_sentence_list = task_management_module.get_action_list(
            task_var)
    action_var_list, action_sentence_list = get_var_and_sentence(
        cur_action_var_sentence_list)

    edit_element_form = EditListElementForm(request.form)

    if request.method == 'POST':
        if edit_element_form.add_element.data:
            idx = edit_element_form.element_idx.data
            action_sentence = edit_element_form.new_element.data.title()
            action_var = string2func_name(action_sentence)
            if idx.isdigit():
                idx = int(idx)
                if idx > len(action_var_list):
                    flash('Invalid Index', 'danger')
                elif idx > 0:
                    action_var_list.insert(idx - 1, action_var)
                    action_sentence_list.insert(idx - 1, action_sentence)
                else:
                    action_var_list.append(action_var)
                    action_sentence_list.append(action_sentence)
            else:
                action_var_list.append(action_var)
                action_sentence_list.append(action_sentence)
            session['cur_list'] = pack_var_sentence(
                action_var_list, action_sentence_list)
            return redirect(url_for('edit_definition.edit_action', task_var=task_var, task_sentence=task_sentence, task_id=task_id))

        elif edit_element_form.remove_element.data:
            idx = edit_element_form.element_idx.data
            if idx.isdigit():
                idx = int(idx)
                if idx > len(action_var_list):
                    flash('Invalid Index', 'danger')
                elif idx > 0:
                    del action_var_list[idx-1]
                    del action_sentence_list[idx-1]
                else:
                    del action_var_list[-1]
                    del action_sentence_list[-1]
            else:
                del action_var_list[-1]
                del action_sentence_list[-1]
            session['cur_list'] = pack_var_sentence(
                action_var_list, action_sentence_list)
            return redirect(url_for('edit_definition.edit_action', task_var=task_var, task_sentence=task_sentence, task_id=task_id))

        elif edit_element_form.submit_configuration.data:
            action_management_module.insert_action(
                task_id, task_var, action_var_list, action_sentence_list)
            session.pop('cur_list', None)
            return redirect(url_for("remove_action.list_actions"))
        elif edit_element_form.cancel_edit.data:
            session.pop('cur_list', None)
            return redirect(url_for("remove_action.list_actions"))
    return render_template('edit_action.html', edit_element_form=edit_element_form, task_sentence=task_sentence, action_sentence_list=action_sentence_list)


@edit_definition.route('/edit_step', methods=['GET', 'POST'])
def edit_step():
    chosen_id = request.args.get('chosen_id')
    # print(chosen_id)
    chosen_step_list = session.get('chosen_step_list')
    action_var = request.args.get('action_var')
    action_sentence = request.args.get('action_sentence')
    location_id = request.args.get('location_id')
    cur_step_var_sentence_list = session.get('cur_list', None)
    # print(action_var)
    if cur_step_var_sentence_list is None:
        cur_step_var_sentence_list = chosen_step_list
    step_var_list, step_sentence_list = get_var_and_sentence(
        cur_step_var_sentence_list)

    edit_element_form = EditListElementForm(request.form, location_id=location_id)

    form_choices = format_choice(executor_mapping_module.get_location_ids())
    # pprint(form_choices)
    edit_element_form.location_id.choices += form_choices
    if request.method == 'POST':
        new_location_id = edit_element_form.location_id.data
        if edit_element_form.add_element.data:
            idx = edit_element_form.element_idx.data
            step_sentence = edit_element_form.new_element.data.title()
            step_var = string2func_name(step_sentence)
            if idx.isdigit():
                idx = int(idx)
                if idx > len(step_var_list):
                    flash('Invalid Index', 'danger')
                elif idx > 0:
                    step_var_list.insert(idx - 1, step_var)
                    step_sentence_list.insert(idx - 1, step_sentence)
                else:
                    step_var_list.append(step_var)
                    step_sentence_list.append(step_sentence)
            else:
                step_var_list.append(step_var)
                step_sentence_list.append(step_sentence)
            session['cur_list'] = pack_var_sentence(
                step_var_list, step_sentence_list)
            return redirect(url_for('edit_definition.edit_step', action_var=action_var, action_sentence=action_sentence, chosen_id=chosen_id, location_id=location_id))

        elif edit_element_form.remove_element.data:
            idx = edit_element_form.element_idx.data
            if idx.isdigit():
                idx = int(idx)
                if idx > len(step_var_list):
                    flash('Invalid Index', 'danger')
                elif idx > 0:
                    del step_var_list[idx-1]
                    del step_sentence_list[idx-1]
                else:
                    del step_var_list[-1]
                    del step_sentence_list[-1]
            else:
                del step_var_list[-1]
                del step_sentence_list[-1]
            session['cur_list'] = pack_var_sentence(
                step_var_list, step_sentence_list)
            return redirect(url_for('edit_definition.edit_step', action_var=action_var, action_sentence=action_sentence, chosen_id=chosen_id, location_id=location_id))

        elif edit_element_form.submit_configuration.data:
            returned_id = resource_management_module.insert_step(
                action_var=action_var, action_sentence=action_sentence, step_list=step_var_list, step_sentence=step_sentence_list, action_id=chosen_id, location_id=new_location_id, edit=True)
            # print(returned_id)
            session.pop('cur_list', None)
            return redirect(url_for("remove_action.list_step"))

        elif edit_element_form.cancel_edit.data:
            session.pop('cur_list', None)
            return redirect(url_for("remove_action.list_step"))

    return render_template('edit_step.html', edit_element_form=edit_element_form, step_sentence_list=step_sentence_list, action_sentence=action_sentence, location_id=location_id)


@edit_definition.route('/edit_executor', methods=['GET', 'POST'])
def edit_executor():

    chosen_id = request.args.get('chosen_exec_id')
    step_var = request.args.get('step_var')
    step_sentence = request.args.get('step_sentence')
    step_var_sentence_list = session.get('step_var_sentence_list')
    step_var_list, step_sentence_list = get_var_and_sentence(
        step_var_sentence_list)
    cur_list = session.get('chosen_exec')
    cur_list.pop('avail_score', None)
    cur_list.pop('mutable', None)
    cur_list.pop('step', None)
    cur_list_table = dict2table(cur_list)
    print(cur_list)

    edit_exec_form = ExecListForm(request.form, software_id=cur_list.get('software_id'))

    edit_exec_form.dependency.choices += step_var_sentence_list
    edit_exec_form.exec_type.choices += executor_mapping_module.get_unique_exec_name()
    edit_exec_form.software_id.choices += [(None, "None")]
    edit_exec_form.software_id.choices += resource_management_module.get_software_list()
    if request.method == 'POST':
        if edit_exec_form.apply_changes.data:
            new_list = session.get('chosen_exec')
            if edit_exec_form.exec_class.data:
                exec_class = edit_exec_form.exec_class.data
                new_list['type'] = exec_class
            if edit_exec_form.exec_type.data:
                exec_type = edit_exec_form.exec_type.data
                new_list['executor'] = exec_type
            if edit_exec_form.dependency.data:
                dependency = edit_exec_form.dependency.data
                if dependency == "None":
                    dependency = None
                new_list['dependency'] = dependency
            if edit_exec_form.software_id.data:
                software_id = edit_exec_form.software_id.data
                new_list['software_id'] = software_id
                new_list['software_name'] = resource_management_module.get_software_name(
                    software_id)
            session['chosen_exec'] = new_list
            return redirect(url_for('edit_definition.edit_executor', chosen_exec_id=chosen_id, step_var=step_var, step_sentence=step_sentence))
        elif edit_exec_form.submit_changes.data:
            resource_management_module.add_step_exec(step_var, cur_list.get('type'), cur_list.get('executor'), cur_list.get(
                'dependency'), cur_list.get('software_id'), cur_list.get('software_name'), item_id=chosen_id)
            return redirect(url_for('remove_action.list_exec', step_var=step_var, step_sentence=step_sentence, step_var_list=step_var_list))
    return render_template('edit_exec_definition.html', step_sentence=step_sentence, cur_list=cur_list_table, edit_exec_form=edit_exec_form)
