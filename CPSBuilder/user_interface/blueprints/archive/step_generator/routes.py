from CPSBuilder.utils.archive.session_functions import *
from CPSBuilder.modules.archive.execution_module import ExecutionModule
from CPSBuilder.modules.archive.building_module import BuildingModule
from CPSBuilder.modules.archive.task_management_module import TaskManagementModule
from CPSBuilder.modules.archive.action_management_module import ActionManagementModule
from CPSBuilder.modules.archive.cloud_insert_module import CloudInsertModule
from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule
from CPSBuilder.modules.archive.context_aware_module import ContextAwareModule
from flask import Blueprint
from flask import render_template, request, flash, redirect, url_for
from CPSBuilder.blueprints.step_generator.forms import GetTaskForm, OptimizeActionForm
from CPSBuilder.blueprints.step_generator.forms import ChangeSoftwareForm, SubmitCancelForm, EditLineStepForm, SubmitJobForm, EditExecForm, ChangeExecChoiceForm
from CPSBuilder.utils.route import *
from pprint import pprint
import config

import logging
logger = logging.getLogger(__name__)

# config mongodb
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize blueprint
step_generator = Blueprint(
    'step_generator', __name__, template_folder='templates')

# initialize modules
context_aware_module = ContextAwareModule(client)
executor_mapping_module = ExecutorMappingModule(client)
cloud_insert_module = CloudInsertModule(client)
action_management_module = ActionManagementModule(client)
task_management_module = TaskManagementModule(client)
building_module = BuildingModule(client)
execution_module = ExecutionModule(client)


@step_generator.route('/sys_start', methods=['GET', 'POST'])
def system_start():
    executor_mapping_module.reset_system()
    session['actions_optimized'] = []
    # clear session
    sess_vars = ['action',
                 'action_sentences',
                 'exec_list',
                 'translated_list',
                 'rejected_step_id',
                 'step_list',
                 'step_id',
                 'step_rejected_selection',
                 'action_optimized'
                 ]
    session_pop(sess_vars)

    form = GetTaskForm(request.form)
    form.task.choices, _ = task_management_module.get_task_list()
    if request.method == 'POST':
        task = form.task.data
        session['task'] = task

        return redirect(url_for('step_generator.gen_action', task=task))
    return render_template('task_list.html', form=form)


@step_generator.route('/gen_action/', methods=['GET', 'POST'])
def gen_action():
    optimize_action_form = OptimizeActionForm(
        request.form, prefix="optimize_action")
    submit_job_form = SubmitJobForm(request.form, prefix="submit_job")
    task = request.args.get('task')
    task_sentence = task_management_module.get_task_sentence(task)
    action_list = task_management_module.get_action_list(task)
    action_var, action_sentences = get_var_and_sentence(action_list)
    session['action_list'] = action_list
    session['action_sentences'] = action_sentences
    action_management_module.update_availability_score()
    session['actions_optimized_idx'] = context_aware_module.get_list_of_optimized_indexes(
        action_var, session['actions_optimized'])
    # print(session['actions_optimized_idx'])
    if all(item for item in session['actions_optimized_idx']):
        complete_edit = True
    else:
        complete_edit = False
    if request.method == 'POST':
        if submit_job_form.submit_job.data:
            if complete_edit:
                # print('yay')
                # pprint(session['actions_optimized'])
                # actions_optimized is output of builder
                for action_exec in session['actions_optimized']:
                    # print(action_exec['action'], action_exec['step_list_id'], action_exec['user_id'])
                    # updating freq of optimized set to user_specific db (action-exec-collection
                    cloud_insert_module.insert_to_db(
                        action_exec['action'], action_exec['step_list_id'], action_exec['user_id'])
                # insert optimized set into job history
                # action_list contains the order of actions
                # action_optimized contains details of each action except its order
                db_id, job_id = execution_module.insert_running_job(
                    task, action_list, session['actions_optimized'], session['user_id'])
                #print(db_id, job_id)
                # to broadcast
                # todo: if these four files are split from this project, change the redirect to send request to assign_job api
                return redirect(url_for('job_execution.assign_job', job_id=job_id, user_id=session.get('user_id')))
            else:
                flash("Please generate executors for all steps.", "danger")

        else:
            action_seq = int(optimize_action_form.request_id.data)
            action = action_var[action_seq]
            action_sentence = action_sentences[action_seq]
            session['action'] = action
            session['action_sentence'] = action_sentence
            optimize = optimize_action_form.optimize_item.data
            use_existing = optimize_action_form.use_existing.data
            review_item = optimize_action_form.review_item.data

            if optimize:
                return redirect(url_for('step_generator.gen_step', action=action, action_seq=action_seq))
                #flash("user optimizing for step {}".format(action_sentences[action_seq]), "success")

            elif use_existing:
                step_list_id = cloud_insert_module.get_popular_exec_list(
                    session['user_id'], action)
                step_list, step_id, location_id = action_management_module.get_action_step_list(
                    action, step_list_id=step_list_id)
                exec_compound_list = executor_mapping_module.get_all_matched_exec(
                    step_list[0], user_id=session['user_id'], location_id=location_id[0])
                session['location_id'] = location_id[0]
                session['step_id'] = step_id[0]
                if exec_compound_list:
                    translated_compound_list = []
                    for exec_list in exec_compound_list:
                        translated_compound_list.append(
                            executor_mapping_module.translate_exec_list(exec_list))
                    session['exec_list'] = exec_compound_list
                    session['translated_list'] = translated_compound_list
                    session['step_list'] = step_list

                    return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))
                else:
                    flash(
                        'No registered config. Please generate executor setting', 'danger')
                #flash("user use existing for step {}".format(action_sentences[action_seq]), "danger")

            elif review_item:
                for action_optimized in session['actions_optimized']:
                    # pprint(action_optimized)
                    if action_optimized['action'] == action:
                        step_id = action_optimized['step_list_id']
                        location_id = action_optimized['location_id']
                        exec_list = action_optimized['exec_list']
                        step_list = cloud_insert_module.get_step_list(
                            exec_list)
                        translated_list = executor_mapping_module.translate_compound_exec_list(
                            exec_list)
                session['step_id'] = step_id
                session['exec_list'] = exec_list
                session['step_list'] = step_list
                session['translated_list'] = translated_list
                session['location_id'] = location_id
                return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))

    return render_template('action_list.html', complete_edit=complete_edit, task=task, task_sentence=task_sentence, optimize_action=optimize_action_form, submit_job=submit_job_form)


@step_generator.route('/gen_step/', methods=['GET', 'POST'])
def gen_step():
    # print(f'gen_step with {action}')
    action = request.args.get('action')
    action_seq = request.args.get('action_seq')
    form = EditLineStepForm(request.form)
    if session.get('rejected_step_id') is None or session.get('step_id') is None or session.get('step_list') is None:
        session['rejected_step_id'] = []
        action_details = context_aware_module.get_step_list(action)
        step_list = action_details.get('step_list')
        step_id = action_details.get('step_id')
        location_id = action_details.get('location_id')
        # print(step_list, step_id, location_id)
        if step_list and step_id and location_id:
            session['step_list'] = step_list
            session['step_id'] = step_id
            session['location_id'] = location_id
        else:
            flash('Error occured. Please contact your administrator', 'danger')
            return redirect(url_for('step_generator.gen_action', task=session['task']))

    translated_step_list = context_aware_module.get_sentence_one_list(
        session['step_list'])
    choices = []
    for i, step in enumerate(translated_step_list):
        choices.append((i, step))
    form.step_list.choices = choices

    if request.method == 'POST':
        if request.form['step_gen'] == 'regen_step':
            result = form.step_list.data
            # print(result)
            if session.get('step_rejected_selection') is None:
                session['step_rejected_selection'] = result
            else:
                if result != session['step_rejected_selection']:
                    session['rejected_step_id'] = []
                    session['step_rejected_selection'] = result
            # print(session['step_rejected_selection'])
            step_list, step_id = context_aware_module.check_steps(
                action, session['step_rejected_selection'], session['step_list'], session['rejected_step_id'])
            if step_list or step_id:
                session['rejected_step_id'].append(session['step_id'])
                session['step_list'], session['step_id'] = step_list, step_id
            else:
                flash(
                    "There is no more valid known variations. Please change selection.", 'danger')
            translated_step_list = context_aware_module.get_sentence_one_list(
                session['step_list'])
            choices = []
            for i, step in enumerate(translated_step_list):
                choices.append((i, step))
            form.step_list.choices = choices

            return redirect(url_for('step_generator.gen_step', action=action))

        if request.form['step_gen'] == 'gen_exec':
            return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))

    return render_template('step_list.html', form=form, sentences=translated_step_list)


@step_generator.route('/gen_exec/', methods=['GET', 'POST'])
def gen_exec():
    form = SubmitCancelForm(request.form)
    edit_exec_form = EditExecForm(request.form)
    # request arg gets data from the page before redirected to here
    action = request.args.get('action')
    action_seq = request.args.get('action_seq')

    if (session.get('translated_list') is None) or (session.get('exec_list') is None):
        print(f"Creating translated and exec_list for action {action} at action_seq: {action_seq}")
        logger.info(f"Creating translated and exec_list for action {action} at action_seq: {action_seq}")
        exec_compound_list = executor_mapping_module.get_all_matched_exec(
            session['step_list'], user_id=session['user_id'], location_id=session['location_id'])
        translated_compound_list = []
        # print(exec_compound_list)
        for exec_list in exec_compound_list:
            print(f"at exec_list gen exec route {exec_list}")
            # todo: robot category always have avail_score = -1. Remember to debug!!!
            if exec_list:
                for exec in exec_list:
                    if not exec:
                        session['rejected_step_id'].append(session['step_id'])
                        flash('All available executors have been assigned to some dependent steps,'
                              'not enough available executors, this step is not valid')
                        return redirect(url_for('step_generator.gen_step', action=action))
                translated_list = executor_mapping_module.translate_exec_list(
                    exec_list)
                # pprint(translated_list)
                translated_compound_list.append(translated_list)
                executor_mapping_module.reset_system()
            else:
                session['rejected_step_id'].append(session['step_id'])
                flash('Not all executors are present, this step is not valid')
                return redirect(url_for('step_generator.gen_step', action=action))
        session['exec_list'] = exec_compound_list
        session['translated_list'] = translated_compound_list
    pprint(session['translated_list'])
    if request.method == 'POST':
        print('post')
        # print(edit_exec_form.allow_alternative.data)
        if edit_exec_form.allow_alternative.data:
            exec_idx = int(edit_exec_form.exec_request_id.data)
            step_idx = int(edit_exec_form.step_request_id.data)
            
            session['exec_list'][step_idx][exec_idx]['allow_alternative_exec'] = not session['exec_list'][step_idx][exec_idx]['allow_alternative_exec']
            session['translated_list'][step_idx][exec_idx]['allow_alternative_exec'] = not session['translated_list'][step_idx][exec_idx]['allow_alternative_exec']
            
            # Add this flag if you are editing an element of the key and not assigning a new value to the key.
            session.modified = True
            
            logger.info(f"Changing alternative executor setting for step:{step_idx}, exec:{exec_idx} to {session['exec_list'][step_idx][exec_idx]['allow_alternative_exec']}")

            return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))

        elif edit_exec_form.edit_software.data:
            software_edit_inner_idx = int(edit_exec_form.exec_request_id.data)
            software_edit_outer_idx = int(edit_exec_form.step_request_id.data)
            return redirect(url_for('step_generator.edit_software', action=action, action_seq=action_seq, software_edit_outer_idx=software_edit_outer_idx, software_edit_inner_idx=software_edit_inner_idx))

        elif edit_exec_form.edit_exec.data:
            exec_choice_outer_idx = int(edit_exec_form.step_request_id.data)
            exec_choice_inner_idx = int(edit_exec_form.exec_request_id.data)
            return redirect(url_for('step_generator.edit_exec', action=action, action_seq=action_seq, exec_choice_outer_idx=exec_choice_outer_idx, exec_choice_inner_idx=exec_choice_inner_idx))
        
        elif request.form.get('accept_cancel') == "accept":
            action_optimized_idx = cloud_insert_module.get_actions_optimized_idx(
                action_seq, session.get('actions_optimized', None))
            if action_optimized_idx:
                session['actions_optimized'][action_optimized_idx]['exec_list'] = session['exec_list']
            else:
                to_session = {
                    "action_seq": action_seq,
                    "action": session['action'],
                    "step_list_id": session['step_id'],
                    "exec_list": session['exec_list'],
                    "user_id": session['user_id'],
                    "location_id": session['location_id']
                }
                session['actions_optimized'].append(to_session)
            session.pop('translated_list', None)
            session.pop('exec_list', None)
            session.pop('rejected_step_id', None)
            session.pop('step_id', None)
            session.pop('step_list', None)
            session.pop('location_id', None)
            # pprint(session['actions_optimized'])
            return redirect(url_for('step_generator.gen_action', task=session['task']))

    return render_template('exec_list.html', form=form, edit_exec_form=edit_exec_form)


@step_generator.route('/edit_exec', methods=['GET', 'POST'])
def edit_exec():

    exec_choice_outer_idx = int(request.args.get('exec_choice_outer_idx'))
    exec_choice_inner_idx = int(request.args.get('exec_choice_inner_idx'))
    action = request.args.get('action')
    action_seq = request.args.get('action_seq')

    change_exec_form = ChangeExecChoiceForm(request.form)
    # pprint(session['exec_list'])

    old_exec = session['exec_list'][exec_choice_outer_idx][exec_choice_inner_idx]
    step = session['exec_list'][exec_choice_outer_idx][exec_choice_inner_idx].get(
        'step_var')
    translated_step = session['translated_list'][exec_choice_outer_idx][exec_choice_inner_idx].get(
        'step_sentence')
    exec_class = session['exec_list'][exec_choice_outer_idx][exec_choice_inner_idx].get(
        'class')
    exec_id = session['exec_list'][exec_choice_outer_idx][exec_choice_inner_idx].get(
        'ID')

    possible_exec_list = executor_mapping_module.get_alternative_exec_list(
        step, session['user_id'], exec_class, exec_id)
    exec_list = session['exec_list']
    # pprint(session['exec_list'][session['exec_edit_idx']])
    if possible_exec_list is None:
        flash(f"No alternative executor for {translated_step}", "danger")
        return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))
    form_choices = index_choice(possible_exec_list)
    change_exec_form.new_exec.choices = form_choices

    if (request.method == 'POST'):
        try:
            new_exec = possible_exec_list[int(change_exec_form.new_exec.data)]
            # pprint(old_exec)
            new_exec_formatted = executor_mapping_module.edit_exec(
                old_exec, new_exec, session['user_id'], session['location_id'])
            # pp.pprint(new_exec_formatted)
            exec_list[exec_choice_outer_idx][exec_choice_inner_idx] = new_exec_formatted
            session['exec_list'] = exec_list
            session['translated_list'] = executor_mapping_module.translate_compound_exec_list(
                exec_list)
            # pp.pprint(session['exec_list'])
            # print("\n")
            return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))
        except ValueError:
            flash(f"Please choose a valid executor", "danger")
    return render_template('edit_exec.html', translated_step=translated_step, possible_exec_list=possible_exec_list, change_exec_form=change_exec_form)


@step_generator.route('/edit_software', methods=['GET', 'POST'])
def edit_software():
    software_edit_inner_idx = int(request.args.get('software_edit_inner_idx'))
    software_edit_outer_idx = int(request.args.get('software_edit_outer_idx'))
    action = request.args.get('action')
    action_seq = request.args.get('action_seq')

    change_software_form = ChangeSoftwareForm(request.form)
    submit_cancel_form = SubmitCancelForm(request.form)
    step_var = session['exec_list'][software_edit_outer_idx][software_edit_inner_idx].get(
        'step_var')
    step_sentence = session['translated_list'][software_edit_outer_idx][software_edit_inner_idx].get(
        'step_sentence')

    exec_class = session['exec_list'][software_edit_outer_idx][software_edit_inner_idx].get(
        'class')
    logger.info(
        f"edit software for {step_var} and for executor class {exec_class}")

    software_list = building_module.get_software_list(step_var, exec_class)
    software_list_default = [{
        'name': 'No Software',
        'id': '',
        'input': '',
        'output': ''
    }]
    software_list = software_list_default + software_list
    software_list_choices = index_choice(software_list)
    change_software_form.new_software.choices = software_list_choices
    exec_list = session['exec_list']
    if (submit_cancel_form.accept.data):
        # print('waowo')
        try:
            new_software = software_list[int(
                change_software_form.new_software.data)]
            if new_software.get('name') == 'No Software':
                new_software['name'] = ''
            exec_list[software_edit_outer_idx][software_edit_inner_idx]['software'] = new_software.get(
                'name')
            session['exec_list'] = exec_list
            session['translated_list'] = executor_mapping_module.translate_compound_exec_list(
                exec_list)
            # pp.pprint(session['exec_list'])
            return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))
        except ValueError:
            flash(f"Please choose a valid executor", "danger")
    elif submit_cancel_form.cancel.data:
        return redirect(url_for('step_generator.gen_exec', action=action, action_seq=action_seq))
    return render_template('edit_software.html', step_sentence=step_sentence, submit_cancel_form=submit_cancel_form, change_software_form=change_software_form, software_list=software_list)
