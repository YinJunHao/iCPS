from flask import Blueprint, render_template, request, redirect, url_for, flash
from CPSBuilder.utils.route import *
from CPSBuilder.modules.action_management_module import ActionManagementModule
from CPSBuilder.modules.task_management_module import TaskManagementModule
from CPSBuilder.modules.resource_management_module import ResourceManagementModule
from CPSBuilder.user_interface.blueprints.remove_action.forms import AddTaskForm, AddStepForm, AddExecForm, EditExecForm, ConfirmEditsForm, DeleteActionDefinitionForm, EditStepForm, EditActionForm, DeleteActionForm


import config

import logging
logger = logging.getLogger(__name__)

# initialize mongo client
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize blueprint
remove_action = Blueprint('remove_action', __name__,
                          template_folder='templates')

# initialize modules
action_management_module = ActionManagementModule(client)
task_management_module = TaskManagementModule(client)
resource_management_module = ResourceManagementModule(client)


@remove_action.route('/list_actions', methods=['GET', 'POST'])
def list_actions():
    edit_action_form = EditActionForm(request.form)
    delete_action_form = DeleteActionForm(request.form)
    add_task_form = AddTaskForm(request.form)

    task_list, task_id_list = task_management_module.get_task_list()
    session['task_list'] = task_list
    action_list = []
    for task in task_list:
        action_list.append(task_management_module.get_action_list(task[0]))
    session['action_list'] = action_list
    if request.method == 'POST':
        # print(delete_action_form.edit_task.data)
        # print(delete_action_form.delete_item.data)
        if delete_action_form.delete_item.data:
            idx = int(delete_action_form.request_id.data)
            task_id = task_id_list[idx]
            task_var = task_list[idx][0]
            task_sentence = task_list[idx][1]
            # print(idx)
            if task_list[idx][0] == 'artificial_trachea':
                flash("You are not allowed to delete the definition", "danger")
            else:
                flash("Deleted", "success")
                task_management_module.delete_task(task_id_list[idx])
            return redirect(url_for('remove_action.list_actions'))

        elif delete_action_form.edit_task.data:
            idx = int(delete_action_form.request_id.data)
            task_id = task_id_list[idx]
            task_var = task_list[idx][0]
            task_sentence = task_list[idx][1]
            return redirect(url_for('edit_definition.edit_action', task_id=task_id, task_var=task_var, task_sentence=task_sentence))

        elif add_task_form.add_task.data:
            return redirect(url_for('new_action.add_task'))

        else:
            action_idx = int(edit_action_form.action_request_id.data)
            task_idx = int(edit_action_form.task_request_id.data)
            task_id = task_id_list[task_idx]
            session['task_var'] = task_list[task_idx][0]
            session['task_sentences'] = task_list[task_idx][1]
            session['chosen_action'] = action_list[task_idx][action_idx]
            return redirect(url_for('remove_action.list_step', task_id=task_id))
    return render_template('list_actions.html', task_list=task_list, action_list=action_list, edit_action_form=edit_action_form, delete_action_form=delete_action_form, add_task_form=add_task_form)


@remove_action.route('/list_step', methods=['GET', 'POST'])
def list_step():
    edit_step_form = EditStepForm(request.form)
    delete_action_form = DeleteActionForm(request.form)
    confirm_edits_form = ConfirmEditsForm(request.form)
    add_new_step_form = AddStepForm(request.form)

    task_id = request.args.get('task_id')
    chosen_action_var = session['chosen_action'][0]
    chosen_action_sentence = session['chosen_action'][1]
    step_lists, action_step_id_list, location_list = action_management_module.get_action_step_list(
        chosen_action_var, sentence=True)
    session['step_lists'] = step_lists

    # pp.pprint(step_sentence_list)
    if request.method == 'POST':
        if delete_action_form.delete_item.data:
            idx = int(delete_action_form.request_id.data)
            # chosen_step_list = step_lists[idx]
            chosen_action_step_id = action_step_id_list[idx]
            # step_var_list, step_sentence_list = get_var_and_sentence(chosen_step_list)
            # pp.pprint(query)
            action_management_module.delete_action(
                chosen_action_var, action_id=chosen_action_step_id, var_idx=idx + 1)
            return redirect(url_for('remove_action.list_step'))

        elif delete_action_form.edit_task.data:
            idx = int(delete_action_form.request_id.data)
            step_list_id = action_step_id_list[idx]
            location_id = location_list[idx]
            session['chosen_step_list'] = step_lists[idx]
            return redirect(url_for('edit_definition.edit_step', action_var=chosen_action_var, action_sentence=chosen_action_sentence, chosen_id=step_list_id, location_id=location_id))

        elif confirm_edits_form.confirm_edits.data:
            # print('click')
            return redirect(url_for('remove_action.list_actions'))

        elif add_new_step_form.add_step.data:
            return redirect(url_for('new_action.suggest_step', action_var=chosen_action_var, action_sentence=chosen_action_sentence))

        else:
            action_idx = int(edit_step_form.action_request_id.data)
            step_idx = int(edit_step_form.step_request_id.data)
            step_var = step_lists[action_idx][step_idx][0]
            step_sentence = step_lists[action_idx][step_idx][1]
            step_var_list, step_sentence_list = get_var_and_sentence(
                step_lists[:][action_idx])
            return redirect(url_for('remove_action.list_exec', step_var=step_var, step_sentence=step_sentence, step_var_list=step_var_list))
    return render_template('list_step.html', location_list=location_list, add_new_step_form=add_new_step_form, action_sentence=chosen_action_sentence, edit_step_form=edit_step_form, delete_action_form=delete_action_form, confirm_edits_form=confirm_edits_form)


@remove_action.route('/list_exec', methods=['GET', 'POST'])
def list_exec():
    edit_exec_form = EditExecForm(request.form)
    add_exec_form = AddExecForm(request.form)
    step_var = request.args.get('step_var')
    step_sentence = request.args.get('step_sentence')
    step_var_list = request.args.getlist('step_var_list')
    step_sentence_list = action_management_module.get_with_sentence(
        step_var_list, False)

    exec_list = action_management_module.get_step_exec(step_var)
    if request.method == "POST":
        if add_exec_form.add_exec.data:
            return redirect(url_for('new_action.add_exec', step_var=step_var, step_sentence=step_sentence, step_var_list=step_var_list))

        elif edit_exec_form.delete_item.data:
            exec_index = int(edit_exec_form.exec_request_id.data)
            chosen_exec_id = str(exec_list[exec_index]['_id'])
            resource_management_module.delete_step_exec(chosen_exec_id)
            return redirect(url_for('remove_action.list_exec', step_var=step_var, step_sentence=step_sentence, step_var_list=step_var_list))

        elif edit_exec_form.edit_item.data:
            session['step_var_sentence_list'] = pack_var_sentence(
                step_var_list, step_sentence_list)
            exec_index = int(edit_exec_form.exec_request_id.data)
            chosen_exec = exec_list[exec_index]
            chosen_exec_id = str(chosen_exec.pop('_id'))
            session['chosen_exec'] = chosen_exec
            return redirect(url_for('edit_definition.edit_executor', chosen_exec_id=chosen_exec_id, step_var=step_var, step_sentence=step_sentence))

        elif add_exec_form.confirm_add_exec.data:
            return redirect(url_for('remove_action.list_step'))
    return render_template('list_exec.html', add_exec_form=add_exec_form, edit_exec_form=edit_exec_form, step_sentence=step_sentence, exec_list=exec_list)
