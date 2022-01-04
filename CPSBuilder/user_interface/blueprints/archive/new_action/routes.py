from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from CPSBuilder.user_interface.blueprints.new_action.forms import EnterNewStepForm, EnterNewActionForm, ChooseRecommendationForm, AddRemoveSoftware, SubmitExecForm, NewTaskForm, NewActionForm,  StepListForm, ExecListForm
from CPSBuilder.utils.archive.module_functions import string2func_name, check_none, to_form_list
from CPSBuilder.utils.route import *

from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule
from CPSBuilder.modules.archive.action_management_module import ActionManagementModule
from CPSBuilder.modules.archive.resource_management_module import ResourceManagementModule
from CPSBuilder.modules.archive.task_management_module import TaskManagementModule


from pymongo import MongoClient
from pprint import pprint
import config

import logging
logger = logging.getLogger(__name__)

# initialize MongoDB Client
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize Blueprint
new_action = Blueprint('new_action', __name__, template_folder='templates')

# initialize modules
executor_mapping_module = ExecutorMappingModule(client)
resource_management_module = ResourceManagementModule(client)
action_management_module = ActionManagementModule(client)
task_management_module = TaskManagementModule(client)


@new_action.route('/add_task', methods=['GET', 'POST'])
def add_task():
    new_task_form = NewTaskForm(request.form)
    if request.method == 'POST':
        task_sentence = new_task_form.task.data
        task_sentence = task_sentence.title()
        task_var = string2func_name(task_sentence)
        session['task_sentences'] = task_sentence
        session['task_var'] = task_var

        if new_task_form.submit_task.data:
            return redirect(url_for('new_action.suggest_action', task_sentence=task_sentence, task_var=task_var))

    return render_template('add_task.html',  new_task_form=new_task_form)


@new_action.route('/suggest_action', methods=['GET', 'POST'])
def suggest_action():
    choose_recommendation_form = ChooseRecommendationForm(request.form)
    new_action_form = EnterNewActionForm(request.form)
    task_sentence = request.args.get('task_sentence')
    # print(task_sentence)
    task_var = request.args.get('task_var')
    recommendation_list = task_management_module.get_task_recommendation(
        task_sentence)
    # pprint(recommendation_list)
    if request.method == 'POST':
        if new_action_form.submit_choice.data:
            task_id = task_management_module.insert_task(
                task_var, task_sentence)
            return redirect(url_for('new_action.add_action', task_id=task_id, task_var=task_var, task_sentence=task_sentence))

        elif choose_recommendation_form.choose_recommendation.data:
            idx = int(choose_recommendation_form.request_id.data)
            chosen_recommendation = recommendation_list[idx]
            cur_list = pack_var_sentence(chosen_recommendation.get(
                'action_list'), chosen_recommendation.get('action_sentence'))
            session['cur_list'] = cur_list
            # print(cur_list)
            task_id = task_management_module.insert_task(
                task_var, task_sentence)
            return redirect(url_for('edit_definition.edit_action', task_var=task_var, task_sentence=task_sentence, task_id=task_id, cur_list=cur_list))

    return render_template('suggest_action.html', task_sentence=task_sentence, recommendation_list=recommendation_list, new_action_form=new_action_form, choose_recommendation_form=choose_recommendation_form)


@new_action.route('/add_action', methods=['GET', 'POST'])
def add_action():
    new_action_form = NewActionForm(request.form)

    task_var = request.args.get('task_var')
    task_sentence = request.args.get('task_sentence')
    task_id = request.args.get('task_id')

    if request.method == 'POST':
        if request.form['add_action'] == "add":
            new_action_form.action_list.append_entry()
        elif request.form['add_action'] == "subtract":
            new_action_form.action_list.pop_entry()
        elif request.form['add_action'] == "submit":
            action_sentence_list = new_action_form.action_list.data
            action_var_list = to_form_list(
                new_action_form.action_list.data, False)
            action_management_module.insert_action(
                task_id, task_var, action_var_list, action_sentence_list)
            return redirect(url_for('remove_action.list_actions'))
    return render_template('add_action.html', task_sentence=task_sentence, new_action_form=new_action_form)


@new_action.route('/suggest_step', methods=['GET', 'POST'])
def suggest_step():
    choose_recommendation_form = ChooseRecommendationForm(request.form)
    new_step_form = EnterNewStepForm(request.form)

    action_var = request.args.get('action_var')
    action_sentence = request.args.get('action_sentence')
    recommendation_list = action_management_module.get_action_recommendation(
        action_sentence)
    pprint(recommendation_list)
    if request.method == 'POST':
        if new_step_form.submit_choice.data:
            return redirect(url_for('new_action.add_step', action_var=action_var, action_sentence=action_sentence))

        elif choose_recommendation_form.choose_recommendation.data:
            idx = int(choose_recommendation_form.request_id.data)
            chosen_recommendation = recommendation_list[idx]
            print(f"index is {idx}")
            pprint(chosen_recommendation)
            action_id = resource_management_module.insert_step(action_var, action_sentence, chosen_recommendation.get(
                'step_list'), chosen_recommendation.get('step_sentence'))
            cur_list = pack_var_sentence(chosen_recommendation.get(
                'step_list'), chosen_recommendation.get('step_sentence'))
            session['cur_list'] = cur_list
            return redirect(url_for('edit_definition.edit_step', chosen_id=action_id, action_var=action_var, action_sentence=action_sentence))

    return render_template('suggest_step.html', action_sentence=action_sentence, recommendation_list=recommendation_list, choose_recommendation_form=choose_recommendation_form, new_step_form=new_step_form)


@new_action.route('/add_step', methods=['GET', 'POST'])
def add_step():
    form = StepListForm(request.form)
    action_var = request.args.get('action_var')
    action_sentence = request.args.get('action_sentence')
    if request.method == 'POST':
        if request.form['add_step'] == "add":
            form.step_list.append_entry()
        elif request.form['add_step'] == "subtract":
            form.step_list.pop_entry()
        elif request.form['add_step'] == "submit":
            filt = check_none(form.step_list.data)
            step_sentence = form.step_list.data
            step_var_list = to_form_list(form.step_list.data, False)
            resource_management_module.insert_step(
                action_var=action_var, action_sentence=action_sentence, step_list=step_var_list, step_sentence=step_sentence)
            return redirect(url_for('remove_action.list_step'))
    return render_template('add_step.html', action_sentence=action_sentence, form=form)


@new_action.route('/add_exec', methods=['GET', 'POST'])
def add_exec():
    step_var = request.args.get('step_var')
    step_sentence = request.args.get('step_sentence')
    step_var_list = request.args.getlist('step_var_list')
    step_sentence_list = action_management_module.get_with_sentence(
        step_var_list, False)
    step_list = action_management_module.get_with_sentence(
        step_var_list)
    chosen_exec_id = request.args.get('chosen_exec_id')

    # print(chosen_exec_id)
    submit_exec_form = SubmitExecForm(request.form)
    add_remove_software = AddRemoveSoftware(request.form)

    exec_list_form = ExecListForm(request.form)
    exec_list_form.exec_type.choices = executor_mapping_module.get_unique_exec_name()
    exec_list_form.exec_class.default
    exec_list_form.software.choices += resource_management_module.get_software_list()
    for step in zip(step_var_list, step_sentence_list):
        # print(step)
        exec_list_form.dependency.choices.append(step)
    if request.method == 'POST':
        # if add_remove_software.add_software.data:
        #     exec_list_form.software.append_entry()
        #     return redirect(url_for('new_action.add_exec', step_var = step_var, step_sentence = step_sentence, step_var_list = step_var_list))
        # elif add_remove_software.remove_software.data:
        #     exec_list_form.software.pop_entry()
        #     return redirect(url_for('new_action.add_exec', step_var = step_var, step_sentence = step_sentence, step_var_list = step_var_list))
        if submit_exec_form.submit_exec.data:
            exec_class = exec_list_form.exec_class.data
            exec_type = exec_list_form.exec_type.data
            dependency = exec_list_form.dependency.data
            software_id = exec_list_form.software.data
            if software_id != "":
                software_name = resource_management_module.get_software_name(
                    software_id)
            else:
                software_name = "None"
            if resource_management_module.add_step_exec(step=step_var, exec_class=exec_class, exec_type=exec_type, dependency=dependency, software_id=software_id, software_name=software_name, item_id=chosen_exec_id):
                return redirect(url_for('remove_action.list_exec', step_var=step_var, step_sentence=step_sentence, step_var_list=step_var_list))
            else:
                flash("Error updating to database. Please try again", "danger")
    # return "yay"
    return render_template('add_exec.html', step_sentence=step_sentence, add_remove_software=add_remove_software, submit_exec_form=submit_exec_form, exec_list_form=exec_list_form, action_sentences=step_sentence, step_list=step_sentence_list)


@new_action.route('/exec_type/<string:exec_class>')
def exec_type(exec_class):
    exec_list = executor_mapping_module.get_unique_exec_name(exec_class)

    execArray = []

    for executor in exec_list:
        execObj = {}
        execObj['val'] = executor[0]
        execObj['name'] = executor[0]
        execArray.append(execObj)

    return jsonify({'executors': execArray})
