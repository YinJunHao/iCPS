from pymongo import MongoClient
from subprocess import call
# from CPSBuilder.utils.session_functions import *
# from CPSBuilder.modules.execution_module import ExecutionModule
# from CPSBuilder.modules.building_module import BuildingModule
# from CPSBuilder.modules.task_management_module import TaskManagementModule
# from CPSBuilder.modules.action_management_module import ActionManagementModule
# from CPSBuilder.modules.cloud_insert_module import CloudInsertModule
# from CPSBuilder.modules.executor_mapping_module import ExecutorMappingModule
# from CPSBuilder.modules.context_aware_module import ContextAwareModule
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, json
from CPSBuilder.user_interface.blueprints.start.forms import NewJobForm
# from CPSBuilder.user_interface.blueprints.start.forms import GetTaskForm, GetActionForm, OptimizeActionForm
# from CPSBuilder.user_interface.blueprints.start.forms import ChangeSoftwareForm, SubmitCancelForm, EditLineStepForm, SubmitJobForm, EditExecForm, ChangeExecChoiceForm
from CPSBuilder.utils.route import *
from CPSBuilder.modules import visualizer, manager, executor_mapper, builder
from pprint import pprint
import config
import time

import logging

logger = logging.getLogger(__name__)

# config mongodb
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize blueprint
start = Blueprint('start', __name__, static_folder='static', template_folder='templates')

# initialize modules
process_display = visualizer.ProcessDisplay(client)
task_display = visualizer.TaskDisplay(client)
state_display = visualizer.StateDisplay(client)
step_display = visualizer.StepDisplay(client)
objective_display = visualizer.ObjectiveDisplay(client)
job_display = visualizer.JobDisplay(client)
executor = executor_mapper.ExecutorMapper(client)
build = builder.JobBuilder(client)
ontology = builder.OntologyBuilder(client)
# building_module = BuildingModule(client)
# execution_module = ExecutionModule(client)


@start.route('/system_start', methods=['GET', 'POST'])
def system_start():
    new_job = NewJobForm(request.form)
    new_job.available_task.choices = task_display.get_all_task_list()
    add_empty_choice(new_job.available_task.choices)
    task_details = []
    for task in new_job.available_task.choices:
        if task[1] != " ":
            task_details.append(task_display.get_task_details(task[0]))
        else:
            task_details.append("")
    if request.method == 'POST':
        req = request.form.to_dict()
        if new_job_validation(req):
            processes = list(req['continue'].split(","))
            session["new_job"] = dict()
            session["new_job"]["job_list"] = list()
            for task in processes:
                added_task = dict()
                added_task["task_id"] = str(task)
                added_task["task_details"] = job_process_format(job_display.get_process_details_for_job(str(task)))
                session["new_job"]["job_list"].append(added_task)
            print("test")
            pprint(session["new_job"]["job_list"])
            session["new_job"]["job_name"] = req["job_name"]
            session["new_job"]["job_status"] = False
            session["builder"] = False
            return redirect(url_for('start.optimise', job_name=req["job_name"]))
    return render_template('system_start.html', new_job=new_job, task_details=task_details)


@start.route('/optimise/<job_name>', methods=['GET', 'POST'])
def optimise(job_name):
    session["new_job"]["job_status"] = True
    session["builder"] = True
    # check if all task is optimised or not
    for task in session["new_job"]['job_list']:
        if not task["task_details"]["task"]["status"]:
            session["new_job"]["job_status"] = False
    if request.method == 'POST':
        if request.form.get("optimise", None):
            return redirect(url_for("start.optimise_process", job_name=job_name, number=request.form["optimise"]))
        if request.form.get("assigned", None):
            number = int(request.form["assigned"])
            session["new_job"]["job_list"][number]["status"] = True
            session["builder"] = False
            return redirect(url_for("start.optimise", job_name=job_name))
        if request.form.get("reset", None):
            number = int(request.form["reset"])
            withdraw_task = process_format_start(task_display.get_process_details(session["new_job"]["job_list"][number]["task_id"]))
            session["new_job"]["job_list"][number]["task_details"] = withdraw_task
            session["new_job"]["job_list"][number]["status"] = False
            session["builder"] = False
            return redirect(url_for("start.optimise", job_name=job_name))
        if request.form.get("confirm", None):
            print("Job Submitted")
            user_id = session["user_id"]
            job_details = list()
            for task in session["new_job"]["job_list"]:
                job_details.append(task["task_details"])
            job_id = build.insert_job(user_id, job_name, job_details)
            ontology.insert_ontology(user_id, job_id, job_details)
            session["new_job"] = dict()
            return redirect(url_for("start.confirmation"))
    return render_template('optimise.html')


@start.route('/optimise/<job_name>/<number>', methods=['GET', 'POST'])
def optimise_process(job_name, number):
    print("Optimising Job with process number " + str(number))
    number = int(number)
    # Need 2 loops because task is not the first thing on the dictionary
    for key, value in session["new_job"]["job_list"][number]["task_details"].items():
        if "objective" in key:
            for objective in value:
                objective["status"] = True
                for content in session["new_job"]["job_list"][number]["task_details"][objective["content_layer"]]:
                    if content["index"] in objective["content_index"]:
                        if not content["status"]:
                            objective["status"] = False
    for key, value in session["new_job"]["job_list"][number]["task_details"].items():
        if key == "task":
            value["status"] = True
            for content in session["new_job"]["job_list"][number]["task_details"][value["content_layer"]]:
                if content["index"] in value["content_index"]:
                    if not content["status"]:
                        value["status"] = False
    if session["new_job"]["job_list"][number]["task_details"]["task"]["status"]:
        session["new_job"]["job_list"][number]["status"] = True
    else:
        session["new_job"]["job_list"][number]["status"] = False
    session["builder"] = False
    if request.method == 'POST':
        if request.form.get("optimise", None):
            step_index = request.form["optimise"]
            return redirect(url_for("start.select_location", job_name=job_name, number=number, step_index=step_index))
        if request.form.get("assigned", None):
            for step in session["new_job"]["job_list"][number]["task_details"]["step"]:
                if int(request.form["assigned"]) == step["index"]:
                    step["status"] = True
                    session["builder"] = False
                    return redirect(url_for("start.optimise_process", job_name=job_name, number=number))
    return render_template('optimise_process.html', number=number)

@start.route('/optimise/<job_name>/<number>/<step_index>/select_location', methods=['GET', 'POST'])
def select_location(job_name, number, step_index):
    location_list = session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)]["location_list"]
    if request.method == 'POST':
        index = request.form["location"]
        location = location_list[int(index)]
        session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)]["location_id"] = location
        session["builder"] = False
        return redirect(url_for("start.optimise_step", job_name=job_name, number=number, step_index=step_index, location=location))
    return render_template('select_location.html', location_list=location_list)


@start.route('/optimise/<job_name>/<number>/<step_index>/<location>', methods=['GET', 'POST'])
def optimise_step(job_name, number, step_index, location):
    print("Optimising step with step index number "+str(step_index))
    # check whether optimising said step will make the objective status true
    # step = step_display.get_step_details(session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)]["_id"])
    # state_exec_list = executor.package_step_exec_in_one_step(step)
    state_exec_list = executor.package_step_exec_in_one_step(session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)])
    step_list = session["new_job"]["job_list"][int(number)]["task_details"]["step"]
    executor_list = session["new_job"]["job_list"][int(number)]["task_details"]["state"]
    if request.method == "POST":
        if request.form.get("cancel", None):
            return redirect(url_for("start.select_location", job_name=job_name, number=number, step_index=step_index))
        if request.form.get("confirm", None):
            req = request.form.to_dict()
            exec_temp = state_exec_list["exec"].copy()
            print(req)
            parameter = req["parameter"].split(",")
            param = dict()
            param["var"] = parameter[0]
            param["type"] = parameter[1]
            session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)]["param"] = param
            for key, value in req.items():
                if "same-as-step-index" in key or "same-as-exec-index" in key:
                    temp_key_list = key.split(",")
                    temp_key = temp_key_list[0]
                    index = int(temp_key_list[1])
                    if value == "None":
                        same_as_index = None
                    else:
                        same_as_index = int(value)
                    for exec in exec_temp:
                        if index == exec["index"]:
                            exec[temp_key] = same_as_index
                if "preferred-exec" in key:
                    temp_key_list = key.split(",")
                    temp_key = temp_key_list[0]
                    index = int(temp_key_list[1])
                    for exec in exec_temp:
                        if index == exec["index"]:
                            preferred_exec = exec["preferred_exec"][int(index)]
                            exec["preferred_exec"] = preferred_exec
            if "alternative-exec" in req:
                alternative_exec_index = request.form.getlist("alternative-exec")
                alternative_exec_list = dict()
                for alt_index in alternative_exec_index:
                    temp_key_list = alt_index.split(",")
                    exec_key = temp_key_list[0]
                    alt_exec_index = int(temp_key_list[1])
                    if exec_key in alternative_exec_list:
                        alternative_exec_list[exec_key].append(alt_exec_index)
                    else:
                        alternative_exec_list[exec_key] = list()
                        alternative_exec_list[exec_key].append(alt_exec_index)
                for key, value in alternative_exec_list.items():
                    exec_index = int(key)
                    alternative_exec = list()
                    for exec in exec_temp:
                        if exec_index == exec["index"]:
                            for idx in value:
                                alternative_exec.append(exec["alternative_exec"][idx])
                    for exec in exec_temp:
                        if exec_index == exec["index"]:
                            exec["alternative_exec"] = alternative_exec
            for exec in exec_temp:
                if exec["same_as_exec_index"] is not None:
                    exec["preferred_exec"] = None
                    exec["alternative_exec"] = None
            session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)]["exec"] = exec_temp
            session["new_job"]["job_list"][int(number)]["task_details"]["step"][int(step_index)]["status"] = True
            session["builder"] = False
            return redirect(url_for("start.optimise_process", job_name=job_name, number=number))
    return render_template('optimise_step.html', step_index=step_index, state_exec_list=state_exec_list, step_list=step_list, executor_list=executor_list)


@start.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if request.method == 'POST':
        if request.form.get("home", None):
            return redirect(url_for("main.index"))
        if request.form.get("running-processes", None):
            print("Redirect to running processes page, to be done in phase 2")
            return redirect(url_for("running.running_jobs"))
    return render_template('confirmation.html')