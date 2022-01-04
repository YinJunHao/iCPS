import os
from CPSBuilder.utils.route import *
from flask import render_template, request, flash, redirect, url_for, session, logging, Blueprint, jsonify
from flask import current_app as app
from CPSBuilder.user_interface.blueprints.processes.forms import NewProcessForm, PhysicalResourceForm, \
    LocationResourceForm, CyberResourceForm
from CPSBuilder.modules import visualizer, manager
from werkzeug.utils import secure_filename
import copy
import json

from pprint import pprint

import logging

logger = logging.getLogger(__name__)

# initialize MongoDB client
from pymongo import MongoClient
import config

client = MongoClient(config.mongo_ip, config.mongo_port)
process_display = visualizer.ProcessDisplay(client)
task_display = visualizer.TaskDisplay(client)
state_display = visualizer.StateDisplay(client)
step_display = visualizer.StepDisplay(client)
objective_display = visualizer.ObjectiveDisplay(client)
process_manager = manager.ProcessManager(client)
process_draft = manager.ProcessDraft(client)
excel_file_manager = manager.ExcelFileManager(client)
ontology_display = visualizer.OntologyVisualizer()
resource_display = visualizer.ResourceDisplay(client)
resource_insert = manager.ResourceInsert(client)
# initialize processes
processes = Blueprint("processes", __name__, static_folder="static", template_folder="templates")


@processes.route("/processes_list", methods=["GET", "POST"])
def processes_list():
    task_list = task_display.get_all_task_list()
    task_details = []
    if "task_id" in session:
        session.pop("task_id")
    if "process_details" in session:
        session.pop("process_details")
    for task in task_list:
        task_details.append(task_display.get_task_details(task[0]))
    return render_template("processes_list.html", task_list=task_list, task_details=task_details)


@processes.route("/process/<task>", methods=["GET", "POST"])
def process(task):
    task_details = process_format(task_display.get_process_details(task))
    robot_list = resource_display.get_all_resource_list("robot")
    hardware_list = resource_display.get_all_resource_list("hardware")
    human_list = resource_display.get_all_resource_list("human")
    physical_list = robot_list + hardware_list + human_list
    software_list = resource_display.get_all_resource_list("software")
    for state in task_details["state"]:
        for exec in state["exec"]:
            for physical in physical_list:
                if exec["physical_resource_id"] == physical["ID"]:
                    exec["physical_resource_name"] = physical["name"]
                    exec["physical_resource_class"] = physical["class"]
            for software in software_list:
                if exec['cyber_resource_id'] == software["ID"]:
                    exec["cyber_resource_name"] = software["name"]
    if request.method == "POST":
        if request.form.get("edit", None):
            if "new_process" in session:
                session.pop("new_process")
            return redirect(
                url_for("processes.edit_process", task=task))
        if request.form.get("conflict-check", None):
            print("conflict check")
    print(task_details)
    return render_template("process.html", task_details=task_details)


@processes.route("/edit_process/<task>/", methods=["GET", "POST"])
def edit_process(task):
    task_details = process_format(task_display.get_process_details(task))
    # layer_details = {}
    robot_list = resource_display.get_all_resource_list("robot")
    hardware_list = resource_display.get_all_resource_list("hardware")
    human_list = resource_display.get_all_resource_list("human")
    physical_list = robot_list + hardware_list + human_list
    software_list = resource_display.get_all_resource_list("software")
    location_list = resource_display.get_all_resource_list("location")
    for state in task_details["state"]:
        for exec in state["exec"]:
            for physical in physical_list:
                if exec["physical_resource_id"] == physical["ID"]:
                    exec["physical_resource_name"] = physical["name"]
                    exec["physical_resource_class"] = physical["class"]
            for software in software_list:
                if exec['cyber_resource_id'] == software["ID"]:
                    exec["cyber_resource_name"] = software["name"]
    index_dict = last_index_dict(task_details)
    robot_resource = dict()
    # robot_resource["location_id_choices"] = list()  # change this line when can get locaiton id list
    robot_resource["type_choices"] = resource_display.get_unique_resource_type("robot")
    human_resource = dict()
    # human_resource["location_id_choices"] = list()  # change this line when can get locaiton id list
    human_resource["type_choices"] = resource_display.get_unique_resource_type("human")
    hardware_resource = dict()
    # hardware_resource["location_id_choices"] = list()  # change this line when can get locaiton id list
    hardware_resource["type_choices"] = resource_display.get_unique_resource_type("hardware")
    physical_resource = dict()
    physical_resource["robot"] = name_and_ID_filter(resource_display.get_all_resource_list("robot"))
    physical_resource["hardware"] = name_and_ID_filter(resource_display.get_all_resource_list("hardware"))
    physical_resource["human"] = name_and_ID_filter(resource_display.get_all_resource_list("human"))
    software_resource = dict()
    software_resource["type_choices"] = resource_display.get_unique_resource_type("software")
    software_resource["software_choices"] = name_and_ID_filter(resource_display.get_all_resource_list("software"), cyber=True)
    location_resource_form = LocationResourceForm()
    location_resource_form.type.choices = format_choice(resource_display.get_unique_resource_type("location"))
    location_resource = name_and_ID_filter(location_list, location=True)
    state_class = dict()
    state_class["resource"] = state_display.get_unique_state_class("resource")
    state_class["job"] = state_display.get_unique_state_class("job")
    state_class["task"] = state_display.get_unique_state_class("task")
    if request.method == "POST":
        # if request.form.get("add-resource", None):
        #     req = clean_request(request.form.to_dict(flat=False), "resource")
        #     resource_class = req["resource-class"]
        #     if new_resource_validation(req, resource_class):
        #         new_info = {"name": req["name"]}
        #         # Getting form data
        #         if req["type_new"] == '':
        #             new_info["type"] = req["type"]
        #         else:
        #             new_info["type"] = req["type_new"]
        #         new_info["class"] = resource_class
        #         if resource_class in ["robot", "hardware", "human"]:
        #             # new_info["location_id"] = req["location_id"]
        #             new_info["active"] = req["status"]
        #             new_info["coordinate"] = {"position_sensor_tag": req["position_sensor_tag"]}
        #             new_info["coordinate"]["x"] = req["position_x"]
        #             new_info["coordinate"]["y"] = req["position_y"]
        #             new_info["coordinate"]["z"] = req["position_z"]
        #             # check coordinate
        #         elif resource_class == "software":
        #             new_info["param_var"] = req["param"]
        #             new_info["state_var"] = req["state"]
        #             new_info["directory"] = ''
        #             new_info["cyber_twin"] = ''
        #             new_info["physical_resource_id"] = req["physical-resource-id"]
        #         resource_insert.insert_resource(resource_class, session["user_id"], new_info)
        #         print("new resource added")
        # elif request.form.get("add-location", None):
        #     req = clean_request(request.form.to_dict(flat=False), "resource")
        #     resource_class = "location"
        #     new_info = {"name": req["name"]}
        #     new_info["class"] = resource_class
        #     new_info["position"] = {"x": req["position_x"]}
        #     new_info["position"]["y"] = req["position_y"]
        #     new_info["position"]["z"] = req["position_z"]
        #     new_info["orientation"] = {"alpha": req["alpha"]}
        #     new_info["orientation"]["beta"] = req["beta"]
        #     new_info["orientation"]["gamma"] = req["gamma"]
        #     new_info["size"] = {"length": req["length"]}
        #     new_info["size"]["width"] = req["width"]
        #     new_info["size"]["height"] = req["height"]
        #     if req["type_new"] == "":
        #         new_info["type"] = req["type"]
        #     else:
        #         new_info["type"] = req["type_new"]
        #     resource_insert.insert_resource(resource_class, session["user_id"], new_info)
        if request.form.get("cancel", None):
            return redirect(url_for("processes.process", task=task))
        elif request.form.get("delete", None):
            process_manager.remove_process(session["user_id"], task_details, task)
            return redirect(url_for("processes.processes_list"))
        else:
            req = request.form.to_dict(flat=False)
            req = clean_request(request.form.to_dict(flat=False), "process")
            pprint(req)
            for key, value in req.items():
                if "name" in key and "," not in key:
                    key_text = key.split("-")
                    # key_text[0] = translate_sentence_to_var(key_text[0])
                    if key_text[0] == "task":
                        task_details["task"]["sentence"] = value
                        task_details["task"]["var"] = translate_sentence_to_var(value)
                    else:
                        for layer in task_details[key_text[0]]:
                            if layer["index"] == int(key_text[2]):
                                layer["sentence"] = value
                                layer["var"] = translate_sentence_to_var(value)
                    print(key_text[0])
            # details = {}
            # prereqstate_list = []
            # for step in task_details["step"]:
            #     step_condition = {}
            #     for condition in task_details["condition"]:
            #         if step["step_cond_index"] == condition["index"]:
            #             step_condition["index"] = step["step_cond_index"]
            #     step_condition["isBlockedByStep_index"] = []
            #     step_condition["hasPrerequisiteStep_index"] = []
            #     step_condition["isBlockedByState_index"] = []
            #     step_condition["hasPrerequisiteState_index"] = []
            #     step_condition["isAchievedBy_index"] = []
            #     step_condition["isFailedByState_index"] = []
            #     for cont in task_details["step"]:
            #         if cont["index"] == step["index"]:
            #             cont["sentence"] = req["name"]
            #             cont["var"] = translate_sentence_to_var(req["name"])
            #             cont["location_id"] = req["location_id"]
            #     # For isblockbystep condition
            #     new = True
            #     for isblockbystep in session["process_details"]["isBlockedByStep"]:
            #         if isblockbystep["StepBlocker_index"] == req["StepBlocker"]:
            #             step_condition["isBlockedByStep_index"].append(isblockbystep["index"])
            #             new = False
            #     if new:
            #         new_isBlockedByStep = {}
            #         step_condition["isBlockedByStep_index"].append(new_index("isBlockedByStep"))
            #         new_isBlockedByStep["index"] = step_condition["isBlockedByStep_index"][0]
            #         new_isBlockedByStep["StepBlocker_index"] = req["StepBlocker"]
            #         session["process_details"]["isBlockedByStep"].append(new_isBlockedByStep)
            #         session["edit_process"] = True
            #     # For isblockbystate condition
            #     new = True
            #     for isblockbystate in session["process_details"]["isBlockedByState"]:
            #         if isblockbystate["StateBlocker_index"] == req["StateBlocker"]:
            #             step_condition["isBlockedByState_index"].append(isblockbystate["index"])
            #             new = False
            #     if new:
            #         new_isBlockedByState = {}
            #         step_condition["isBlockedByState_index"].append(new_index("isBlockedByState"))
            #         new_isBlockedByState["index"] = step_condition["isBlockedByState_index"][0]
            #         new_isBlockedByState["StateBlocker_index"] = req["StateBlocker"]
            #         session["process_details"]["isBlockedByState"].append(new_isBlockedByState)
            #         session["edit_process"] = True
            #     #  For has prerequisite step and has prerequisite state
            #     for key, item in req.items():
            #         if "hasPrerequisiteStep" in key or "hasPrerequisiteState" in key:
            #             text = key.split(",")
            #             cond = text[1]
            #             no = text[0]
            #             step_condition_text = cond + "_index"
            #             new = True
            #             if cond == "hasPrerequisiteStep":
            #                 for condition in session["process_details"]["hasPrerequisiteStep"]:
            #                     if condition["StepPrerequisite_index"] == item:
            #                         step_condition["hasPrerequisiteStep_index"].append(condition["index"])
            #                         new = False
            #             elif cond == "hasPrerequisiteState":
            #                 for condition in session["process_details"]["hasPrerequisiteState"]:
            #                     if condition["StatePrerequisite_index"] == item:
            #                         step_condition["hasPrerequisiteState_index"].append(condition["index"])
            #                         new = False
            #                         prereqstate_list.append((no, condition["index"]))
            #             if new:
            #                 new_prerequisite = {}
            #                 index = new_index(cond)
            #                 new_prerequisite["index"] = index
            #                 if cond == "hasPrerequisiteStep":
            #                     new_prerequisite["StepPrerequisite_index"] = item
            #                 elif cond == "hasPrerequisiteState":
            #                     new_prerequisite["StatePrerequisite_index"] = item
            #                 step_condition[step_condition_text].append(index)
            #                 prereqstate_list.append((no, index))
            #                 session["process_details"][cond].append(new_prerequisite)
            #                 session["edit_process"] = True
            #     # for isachieved by
            #     for key, item in req.items():
            #         if "isAchievedBy" in key:
            #             text = key.split(",")
            #             no = text[0]
            #             hasPrerequisiteState_index = []
            #             new = True
            #             for key1, item1 in req.items():
            #                 if "isAchievedPreregstateset" in key1:
            #                     text1 = key1.split(",")
            #                     no1 = text1[0]
            #                     if no1 == no:
            #                         hasPrerequisiteState_index = item1
            #             for no, item_list in enumerate(hasPrerequisiteState_index):
            #                 for index_list in prereqstate_list:
            #                     if index_list[0] == item_list:
            #                         hasPrerequisiteState_index[no] = index_list[1]
            #             for condition in session["process_details"]["isAchievedBy"]:
            #                 if condition["hasPrerequisiteState_index"] == hasPrerequisiteState_index and condition[
            #                     "StateCorrect_index"] == item:
            #                     step_condition["isAchievedBy_index"].append(condition["index"])
            #                     new = False
            #             if new:
            #                 new_isAchievedBy = {}
            #                 index = new_index("isAchievedBy")
            #                 new_isAchievedBy["index"] = index
            #                 new_isAchievedBy["StateCorrect_index"] = item
            #                 new_isAchievedBy["hasPrerequisiteState_index"] = hasPrerequisiteState_index
            #                 step_condition["isAchievedBy_index"].append(index)
            #                 session["process_details"]["isAchievedBy"].append(new_isAchievedBy)
            #                 session["edit_process"] = True
            #     # for isfailedbystate
            #     for key, item in req.items():
            #         if "isFailedByState" in key:
            #             text = key.split(",")
            #             no = text[0]
            #             hasPrerequisiteState_index = []
            #             StateCorrect_index = []
            #             StepReturn_index = []
            #             new = True
            #             for key1, item1 in req.items():
            #                 if "isFailedPreregstateset" in key1:
            #                     text1 = key1.split(",")
            #                     no1 = text1[0]
            #                     if no1 == no:
            #                         hasPrerequisiteState_index = item1
            #             for no, item_list in enumerate(hasPrerequisiteState_index):
            #                 for index_list in prereqstate_list:
            #                     if index_list[0] == item_list:
            #                         hasPrerequisiteState_index[no] = index_list[1]
            #             for key2, item2 in req.items():
            #                 if "isFailedIf" in key2:
            #                     text2 = key2.split(",")
            #                     no2 = text2[0]
            #                     if no2 == no:
            #                         StateCorrect_index = item2
            #             for key3, item3 in req.items():
            #                 if "StepReturn" in key3:
            #                     text3 = key3.split(",")
            #                     no3 = text3[0]
            #                     if no3 == no:
            #                         StepReturn_index = item3
            #             for condition in session["process_details"]["isFailedByState"]:
            #                 if condition["hasPrerequisiteState_index"] == hasPrerequisiteState_index and condition[
            #                     "StateCorrect_index"] == StateCorrect_index and condition[
            #                     "StateWrong_index"] == item and condition["StepReturn_index"] == StepReturn_index:
            #                     step_condition["isFailedByState_index"].append(condition["index"])
            #                     new = False
            #             if new:
            #                 new_isFailedByState = {}
            #                 index = new_index("isFailedByState")
            #                 new_isFailedByState["index"] = index
            #                 new_isFailedByState["StateWrong_index"] = item
            #                 new_isFailedByState["StateCorrect_index"] = StateCorrect_index
            #                 new_isFailedByState["hasPrerequisiteState_index"] = hasPrerequisiteState_index
            #                 new_isFailedByState["StepReturn_index"] = StepReturn_index
            #                 step_condition["isFailedByState_index"].append(index)
            #                 session["process_details"]["isFailedByState"].append(new_isFailedByState)
            #                 session["edit_process"] = True
            #     # for state
            #     for key, item in req.items():
            #         if "stateexec" in key:
            #             print("testhere")
            #             text = key.split(",")
            #             no = int(text[0])
            #             new = True
            #             for state in session["process_details"]["state"]:
            #                 if no == state["index"]:
            #                     state["var"] = item["name"]
            #                     state["class"] = item["class"]
            #                     state["type"] = item["type"]
            #                     state["exec"] = item["exec"]
            #                     new = False
            #                     session["edit_process"] = True
            #             if new:
            #                 new_state = dict()
            #                 new_state["index"] = no
            #                 new_state["var"] = item["name"]
            #                 new_state["class"] = item["class"]
            #                 new_state["type"] = item["type"]
            #                 new_state["exec"] = item["exec"]
            #                 session["process_details"]["state"].append(new_state)
            #                 session["edit_process"] = True
            #     for condition in session["process_details"]["condition"]:
            #         if condition["index"] == step_condition["index"]:
            #             condition = step_condition.copy()
            # elif layer == "task":
            #     session["process_details"]["task"]["sentence"] = req["name"]
            #     session["process_details"]["task"]["var"] = translate_sentence_to_var(req["name"])
            #     session["process_details"]["task"]["content_index"] = []
            #     for key, value in req.items():
            #         if key.isdigit():
            #             session["process_details"]["task"]["content_index"].append(int(key))
            #             index = int(key)
            #             for content in session["process_details"][layer_details["content_layer"]]:
            #                 if content["index"] == index:
            #                     content["sentence"] = value
            #                     content["var"] = translate_sentence_to_var(value)
            #                     session["edit_process"] = True
            #             details[key] = index
            #         if "new" in key:
            #             new_content = {}
            #             new_content["sentence"] = value
            #             new_content["var"] = translate_sentence_to_var(value)
            #             new_content["index"] = new_index(layer_details["content_layer"])
            #             new_content["layer"] = layer_details["content_layer"]
            #             new_content["content_layer"] = determine_layer(layer_details["content_layer"])
            #             new_content["content_index"] = []
            #             session["process_details"]["task"]["content_index"].append(new_content["index"])
            #             text = key.split(",")
            #             details[text[1]] = new_content["index"]
            #             session["process_details"][layer_details["content_layer"]].append(new_content.copy())
            #             session["edit_process"] = True
            # else:
            #     for cont in session["process_details"][layer]:
            #         if cont["index"] == layer_details["index"]:
            #             cont["sentence"] = req["name"]
            #             cont["var"] = translate_sentence_to_var(req["name"])
            #             cont["content_index"] = []
            #             for key, value in req.items():
            #                 if key.isdigit():
            #                     cont["content_index"].append(int(key))
            #                     index = int(key)
            #                     for content in session["process_details"][layer_details["content_layer"]]:
            #                         if index == content["index"]:
            #                             content["sentence"] = value
            #                             content["var"] = translate_sentence_to_var(value)
            #                             session["edit_process"] = True
            #                     details[key] = index
            #                 if "new" in key:
            #                     new_content = {}
            #                     new_content["sentence"] = value
            #                     new_content["var"] = translate_sentence_to_var(value)
            #                     new_content["index"] = new_index(layer_details["content_layer"])
            #                     new_content["layer"] = layer_details["content_layer"]
            #                     if layer_details["content_layer"] == "step":
            #                         new_content["location_id"] = []
            #                         new_content["state_exec_index"] = []
            #                         new_content["step_param_index"] = []
            #                         new_content["step_cond_index"] = []
            #                         new_content["step_condition"] = {}
            #                         new_content["state_exec"] = []
            #                         new_content["step_param"] = []
            #                     else:
            #                         new_content["content_layer"] = determine_layer(layer_details["content_layer"])
            #                         new_content["content_index"] = []
            #                     cont["content_index"].append(new_content["index"])
            #                     text = key.split(",")
            #                     details[text[1]] = new_content["index"]
            #                     session["process_details"][layer_details["content_layer"]].append(
            #                         new_content.copy())
            #                     session["edit_process"] = True
            if request.form.get("save-draft", None):
                info = {}
                info["var"] = task_details["task"]["var"]
                info["sentence"] = task_details["task"]["sentence"]
                info["draft"] = task_details
                if "new_process" in session:
                    session.pop("new_process")
                    process_draft.insert_draft(session["user_id"], info)
                if "draft_process" in session:
                    process_draft.update_draft(task_details["task"]["_id"], task_details)
                    session.pop("draft_process")
                session.pop("edit_process")
                session.pop("process_details")
                return redirect(url_for("processes.processes_list"))
            if request.form.get("confirm", None):
                # old_info = process_format(task_display.get_process_details(task))
                # process_manager.update_process(session["user_id"],
                #                                old_info, task_details, task)
                # if "new_process" in session:
                #     session.pop("new_process")
                # if "draft_process" in session:
                #     process_draft.archive_submitted_draft(task_details["task"]["_id"], task_details)
                #     session.pop("draft_process")
                # session.pop("edit_process")
                # session.pop("process_details")
                return redirect(url_for("processes.process", task=task))
    print(index_dict)
    return render_template("edit_process.html", task_details=task_details, robot_resource=robot_resource,
                           human_resource=human_resource, hardware_resource=hardware_resource,
                           software_resource=software_resource, location_resource_form=location_resource_form,
                           state_class=state_class, physical_resource=physical_resource, location_resource=location_resource, index_dict=index_dict)


@processes.route("/new_process", methods=["GET", "POST"])
def new_process():
    new_form = NewProcessForm()
    draft_list = process_display.get_all_draft_list(session["user_id"])
    if request.method == "POST":
        if request.form.get("submit-file", None):
            file = request.files["file"]
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["excel_dir"], filename))
            f = f"{config.excel_dir}/{filename}"
            temp = excel_file_manager.import_excel_workbook(f)
            process_new = ontology_display.visualize_ontology(temp, filename)
            pprint(process_new)
            session["process_details"] = process_new
            return redirect(
                url_for("processes.edit_process", name=0, layer="task",
                        task="new_process"))
        if request.form.get("submit-manual", None):
            task_name = request.form["task_name"]
            session["process_details"] = empty_process(task_name)
            session["new_process"] = True
            session["edit_process"] = True
            return redirect(
                url_for("processes.edit_process", name=0, layer="task",
                        task="new_process"))
        if request.form.get("edit-draft", None):
            index = int(request.form["edit-draft"])
            session["process_details"] = process_format(draft_list[index]["draft"])
            session["edit_process"] = True
            session["draft_process"] = True
            return redirect(
                url_for("processes.edit_process", name=0, layer="task",
                        task="new_process"))
        if request.form.get("duplicate-draft", None):
            index = int(request.form["duplicate-draft"])
            new_id = str(process_draft.duplicate_draft(draft_list[index]["_id"]))
            new_draft = process_display.get_one_draft(session["user_id"], new_id)
            session["process_details"] = process_format(new_draft["draft"])
            session["new_process"] = True
            session["edit_process"] = True
            return redirect(
                url_for("processes.edit_process", name=0, layer="task",
                        task="new_process"))
        if request.form.get("delete-draft", None):
            index = int(request.form["delete-draft"])
            draft_ObjectId = draft_list[index]["_id"]
            info = draft_list[index]["draft"]
            process_draft.discard_draft(draft_ObjectId, info)
            return redirect(url_for("processes.new_process"))
    return render_template("new_process.html", new_form=new_form, draft_list=draft_list)


# if layer == "task":
    #     layer_details = session["process_details"]["task"].copy()
    # else:
    #     for content in session["process_details"][layer]:
    #         if content["index"] == int(name):
    #             layer_details = content.copy()
    # if layer != "step":
    #     layer_details["content"] = []
    #     for cont_index in session["process_details"][layer_details["content_layer"]]:
    #         if cont_index["index"] in layer_details["content_index"]:
    #             layer_details["content"].append(cont_index.copy())
    #     for cont in layer_details["content"]:
    #         if cont["layer"] != "step":
    #             cont["content_details"] = []
    #             for content in session["process_details"][cont["content_layer"]]:
    #                 if content["index"] in cont["content_index"]:
    #                     cont["content_details"].append(content.copy())
    #         else:
    #             for step in session["process_details"]["step"]:
    #                 if step["index"] == cont["index"]:
    #                     cont["content_details"] = step.copy()
    #             for condition in session["process_details"]["condition"]:
    #                 if condition["index"] == cont["step_cond_index"]:
    #                     cont["content_details"]["step_condition"] = condition.copy()
    #             cont["content_details"]["step_param"] = []
    #             for param in session["process_details"]["parameter"]:
    #                 if param["index"] in cont["step_param_index"]:
    #                     cont["content_details"]["step_param"].append(param.copy())
    #             cont["content_details"]["state_exec"] = []
    #             for state in session["process_details"]["state"]:
    #                 if state["index"] in cont["state_exec_index"]:
    #                     cont["content_details"]["state_exec"].append(state.copy())
    # else:
    #     # First Layer of the step details
    #     layer_details["step_param"] = []
    #     for param in session["process_details"]["parameter"]:
    #         if param["index"] in layer_details["step_param_index"]:
    #             layer_details["step_param"].append(param.copy())
    #     layer_details["state_exec"] = []
    #     for state in session["process_details"]["state"]:
    #         if state["index"] in layer_details["state_exec_index"]:
    #             state_exec = state.copy()
    #             for physical in physical_list:
    #                 for executor in state["exec"]:
    #                     print(executor)
    #                     if executor["physical_resource_id"] == physical["ID"]:
    #                         executor["physical_resource_class"] = physical["class"]
    #                         executor["physical_resource_name"] = physical["name"]
    #             for software in software_list:
    #                 for executor in state["exec"]:
    #                     if executor["cyber_resource_id"] == software["ID"]:
    #                         executor["cyber_resource_name"] = software["name"]
    #             layer_details["state_exec"].append(state_exec)
    #     for condition in session["process_details"]["condition"]:
    #         if condition["index"] == layer_details["step_cond_index"]:
    #             layer_details["step_condition"] = condition.copy()
    #     if not layer_details["step_condition"]:
    #         layer_details["step_condition"]["isBlockedByStep_index"] = []
    #         layer_details["step_condition"]["isBlockedByStep"] = {}
    #         layer_details["step_condition"]["isBlockedByStep"]["StepBlocker_index"] = []
    #         layer_details["step_condition"]["hasPrerequisiteStep_index"] = []
    #         layer_details["step_condition"]["isBlockedByState_index"] = []
    #         layer_details["step_condition"]["isBlockedByState"] = {}
    #         layer_details["step_condition"]["isBlockedByState"]["StateBlocker_index"] = []
    #         layer_details["step_condition"]["hasPrerequisiteState_index"] = []
    #         layer_details["step_condition"]["isAchievedBy_index"] = []
    #         layer_details["step_condition"]["isFailedByState_index"] = []
    #     # Step condition details
    #     for stepblocker_index in session["process_details"]["isBlockedByStep"]:
    #         if stepblocker_index["index"] in layer_details["step_condition"]["isBlockedByStep_index"]:
    #             layer_details["step_condition"]["isBlockedByStep"] = stepblocker_index.copy()
    #     layer_details["step_condition"]["isBlockedByStep"]["StepBlocker"] = []
    #     for step in session["process_details"]["step"]:
    #         if step["index"] in layer_details["step_condition"]["isBlockedByStep"]["StepBlocker_index"]:
    #             layer_details["step_condition"]["isBlockedByStep"]["StepBlocker"].append(step.copy())
    #     layer_details["step_condition"]["hasPrerequisiteStep"] = []
    #     for prereqstep_index in session["process_details"]["hasPrerequisiteStep"]:
    #         if prereqstep_index["index"] in layer_details["step_condition"]["hasPrerequisiteStep_index"]:
    #             layer_details["step_condition"]["hasPrerequisiteStep"].append(prereqstep_index.copy())
    #     for prereqstep in layer_details["step_condition"]["hasPrerequisiteStep"]:
    #         prereqstep["StepPrerequisite"] = []
    #         for step in session["process_details"]["step"]:
    #             if step["index"] in prereqstep["StepPrerequisite_index"]:
    #                 prereqstep["StepPrerequisite"].append(step.copy())
    #     for stateblocker_index in session["process_details"]["isBlockedByState"]:
    #         if stateblocker_index["index"] in layer_details["step_condition"]["isBlockedByState_index"]:
    #             layer_details["step_condition"]["isBlockedByState"] = stateblocker_index.copy()
    #     layer_details["step_condition"]["isBlockedByState"]["StateBlocker"] = []
    #     for state in session["process_details"]["state"]:
    #         if state["index"] in layer_details["step_condition"]["isBlockedByState"]["StateBlocker_index"]:
    #             layer_details["step_condition"]["isBlockedByState"]["StateBlocker"].append(state.copy())
    #     layer_details["step_condition"]["hasPrerequisiteState"] = []
    #     for prereqstate_index in session["process_details"]["hasPrerequisiteState"]:
    #         if prereqstate_index["index"] in layer_details["step_condition"]["hasPrerequisiteState_index"]:
    #             layer_details["step_condition"]["hasPrerequisiteState"].append(prereqstate_index.copy())
    #     for prereqstate in layer_details["step_condition"]["hasPrerequisiteState"]:
    #         prereqstate["StatePrerequisite"] = []
    #         for state in session["process_details"]["state"]:
    #             if state["index"] in prereqstate["StatePrerequisite_index"]:
    #                 prereqstate["StatePrerequisite"].append(state.copy())
    #     layer_details["step_condition"]["isAchievedBy"] = []
    #     for statecorrect_index in session["process_details"]["isAchievedBy"]:
    #         if statecorrect_index["index"] in layer_details["step_condition"]["isAchievedBy_index"]:
    #             layer_details["step_condition"]["isAchievedBy"].append(statecorrect_index.copy())
    #     for statecorrect in layer_details["step_condition"]["isAchievedBy"]:
    #         statecorrect["StateCorrect"] = []
    #         statecorrect["hasPrerequisiteState"] = []
    #         for state in session["process_details"]["state"]:
    #             if state["index"] in statecorrect["StateCorrect_index"]:
    #                 statecorrect["StateCorrect"].append(state.copy())
    #         for prereqstate in session["process_details"]["hasPrerequisiteState"]:
    #             if prereqstate["index"] in statecorrect["hasPrerequisiteState_index"]:
    #                 statecorrect["hasPrerequisiteState"].append(prereqstate.copy())
    #         for prereqstate_forstatecorrect in statecorrect["hasPrerequisiteState"]:
    #             prereqstate_forstatecorrect["StatePrerequisite"] = []
    #             for state in session["process_details"]["state"]:
    #                 if state["index"] in prereqstate["StatePrerequisite_index"]:
    #                     prereqstate_forstatecorrect["StatePrerequisite"].append(state.copy())
    #     layer_details["step_condition"]["isFailedByState"] = []
    #     for statewrong_index in session["process_details"]["isFailedByState"]:
    #         if statewrong_index["index"] in layer_details["step_condition"]["isFailedByState_index"]:
    #             layer_details["step_condition"]["isFailedByState"].append(statewrong_index.copy())
    #     for statewrong in layer_details["step_condition"]["isFailedByState"]:
    #         statewrong["StateCorrect"] = []
    #         statewrong["hasPrerequisiteState"] = []
    #         statewrong["StateWrong"] = []
    #         statewrong["StepReturn"] = []
    #         for state in session["process_details"]["state"]:
    #             if state["index"] in statewrong["StateCorrect_index"]:
    #                 statewrong["StateCorrect"].append(state.copy())
    #         for state in session["process_details"]["state"]:
    #             if state["index"] in statewrong["StateWrong_index"]:
    #                 statewrong["StateWrong"].append(state.copy())
    #         for prereqstate in session["process_details"]["hasPrerequisiteState"]:
    #             if prereqstate["index"] in statewrong["hasPrerequisiteState_index"]:
    #                 statewrong["hasPrerequisiteState"].append(prereqstate.copy())
    #         for step in session["process_details"]["step"]:
    #             if step["index"] in statewrong["StepReturn_index"]:
    #                 statewrong["StepReturn"].append(step.copy())
