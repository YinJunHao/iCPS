from CPSBuilder.utils.route import *
from CPSBuilder.modules.visualizer import ResourceDisplay
from CPSBuilder.modules.manager import ResourceUpdate, ResourceRemove, ResourceInsert, ResourceDraft
from CPSBuilder.user_interface.blueprints.resources.forms import PhysicalResourceForm, LocationResourceForm, CyberResourceForm


from pymongo import MongoClient
import datetime
from flask import Response, Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, json
import config
import copy
import logging
logger = logging.getLogger(__name__)

# initialize mongo client
client = MongoClient(config.mongo_ip, config.mongo_port)


resources = Blueprint("resources", __name__, template_folder="templates", static_folder="resources/static")

resource_display = ResourceDisplay(client)
resource_update = ResourceUpdate(client)
resource_remove = ResourceRemove(client)
resource_insert = ResourceInsert(client)
resource_draft = ResourceDraft(client)


# Main Resource Page
@resources.route("/all_resources", methods=["GET", "POST"])
def all_resources():
    if request.method == "POST":
        req = request.form.to_dict()
        resource_class = req["resource"]
        return redirect(url_for("resources.resource", resource_class=resource_class))
    return render_template("all_resources.html")


@resources.route("/all_resource/<resource_class>", methods=["GET", "POST"])
def resource(resource_class):
    resourcedb = resource_display.get_all_resource_list(resource_class)
    if request.method == "POST":
        if request.form.get("new", None):
            session["update_resource_draft"] = False
            return redirect(url_for("resources.new_resource", resource_class=resource_class))
        if request.form.get("activate", None):
            index = int(request.form["activate"])
            selected_resource = resourcedb[index]
            selected_resource["active"] = True
            selected_resource["available"] = True
            resource_id = str(selected_resource["_id"])
            resource_update.update_resource(resource_id, resource_class, session["user_id"], selected_resource)
            return redirect(url_for("resources.resource", resource_class=resource_class))
        elif request.form.get("deactivate", None):
            index = int(request.form["deactivate"])
            selected_resource = resourcedb[index]
            selected_resource["active"] = False
            selected_resource["available"] = None
            resource_id = str(selected_resource["_id"])
            resource_update.update_resource(resource_id, resource_class, session["user_id"], selected_resource)
            return redirect(url_for("resources.resource", resource_class=resource_class))
        elif request.form.get("edit", None):
            index = int(request.form["edit"])
            resource_id = resourcedb[index]["ID"]
            return redirect(url_for("resources.edit_resource", resource_class=resource_class, resource_id=resource_id))
        elif request.form.get("delete", None):
            index = int(request.form["delete"])
            selected_resource = resourcedb[index]
            resource_id = selected_resource["_id"]
            resource_remove.delete_resource(resource_id, resource_class)
            return redirect(url_for("resources.resource", resource_class=resource_class, resourcedb=resourcedb))
    return render_template("resource.html", resource_class=resource_class, resourcedb=resourcedb)


@resources.route("/resources_type/<resource_class>/new_resource", methods=["GET", "POST"])
def new_resource(resource_class):
    # Instantiate a blank new_info and get the full draft list
    draft_list = resource_display.get_draft(session["user_id"], resource_class)
    physical_resource = dict()
    physical_resource["robot"] = name_and_ID_filter(resource_display.get_all_resource_list("robot"))
    physical_resource["hardware"] = name_and_ID_filter(resource_display.get_all_resource_list("hardware"))
    physical_resource["human"] = name_and_ID_filter(resource_display.get_all_resource_list("human"))
    # Get which form to use depending on which class
    if resource_class in ["robot", "hardware", "human"]:
        form = PhysicalResourceForm()
    elif resource_class == "software":
        form = CyberResourceForm()
        form.physical_resource.choices = []
    else:
        form = LocationResourceForm()
    if session["update_resource_draft"]:
        form.type.choices = format_choice(resource_display.get_unique_resource_type(resource_class),
                                          sentence_db="edit_resource", original_value=session["resource_draft"]["type"])
        if resource_class in ["robot", "hardware", "human"]:
            form.location_id.choices = format_choice(resource_display.get_all_resource_list("location"), sentence_db="location_id", original_value=session["resource_draft"]["location_id"])
    else:
        form.type.choices = format_choice(resource_display.get_unique_resource_type(resource_class))
        if resource_class in ["robot", "hardware", "human"]:
            form.location_id.choices = format_choice(resource_display.get_all_resource_list("location"), sentence_db="location_id")
    session["update_new_resource"] = False
    # if form.validate_on_submit():
    #     print("test")
    if request.method == "POST":
        req = clean_request(request.form.to_dict(flat=False), "resource")
        print(req)
        if request.form.get("add-new", None):
            if new_resource_validation(req, resource_class):
                session["update_new_resource"] = False
                new_info = {"name": req["name"]}
                # Getting form data
                if req["type_new"] == '':
                    new_info["type"] = req["type"]
                else:
                    new_info["type"] = req["type_new"]
                new_info["class"] = resource_class
                if resource_class in ["robot", "hardware", "human"]:
                    new_info["location_id"] = req["location_id"]
                    new_info["active"] = req["status"]
                    new_info["coordinate"] = {"position_sensor_tag": req["position_sensor_tag"]}
                    # new_info["coordinate"]["x"] = req["position_x"]
                    # new_info["coordinate"]["y"] = req["position_y"]
                    # new_info["coordinate"]["z"] = req["position_z"]
                    # check coordinate
                elif resource_class == "software":
                    new_info["param_var"] = req["param"]
                    new_info["state_var"] = req["state"]
                    new_info["directory"] = ''
                    new_info["cyber_twin"] = ''
                    new_info["physical_resource_id"] = req["physical-resource-id"]
                else:
                    new_info["position"] = {"x_min": req["position_x_min"]}
                    new_info["position"]["y_min"] = req["position_y_min"]
                    new_info["position"]["z_min"] = req["position_z_min"]
                    new_info["position"]["x_max"] = req["position_x_max"]
                    new_info["position"]["y_max"] = req["position_y_max"]
                    new_info["position"]["z_max"] = req["position_z_max"]
                    new_info["orientation"] = {"alpha": req["alpha"]}
                    new_info["orientation"]["beta"] = req["beta"]
                    new_info["orientation"]["gamma"] = req["gamma"]
                    # new_info["size"] = {"length": req["length"]}
                    # new_info["size"]["width"] = req["width"]
                    # new_info["size"]["height"] = req["height"]
                if session["update_resource_draft"]:
                    draft_ObjectId = draft_list[session["resource_draft_index"]]["_id"]
                    resource_draft.discard_draft(draft_ObjectId)
                resource_insert.insert_resource(resource_class, session["user_id"], new_info)
                return redirect(url_for("resources.resource", resource_class=resource_class))
            else:
                session["update_new_resource"] = True
                session["resource_draft"] = req
        if request.form.get("delete-draft", None):
            draft_ObjectId = draft_list[int(request.form["delete-draft"])]["_id"]
            resource_draft.discard_draft(draft_ObjectId)
            return redirect(
                url_for("resources.new_resource", resource_class=resource_class, form=form, draft_list=draft_list))
        if request.form.get("save-draft", None):
            info = {}
            info["class"] = resource_class
            info["type"] = req["type"]
            info["name"] = req["name"]
            info["draft"] = req
            resource_draft.insert_draft(session["user_id"], info)
            return redirect(
                url_for("resources.new_resource", resource_class=resource_class, form=form, draft_list=draft_list))
        if request.form.get("update-draft", None):
            info = {}
            session["update_resource_draft"] = False
            info["class"] = resource_class
            info["type"] = req["type"]
            info["name"] = req["name"]
            info["draft"] = copy.deepcopy(req)
            resource_draft.update_draft(draft_list[session["resource_draft_index"]]["_id"], info)
            return redirect(
                url_for("resources.new_resource", resource_class=resource_class, form=form, draft_list=draft_list))
        if request.form.get("edit-draft", None):
            session["update_resource_draft"] = True
            session["resource_draft_index"] = int(request.form["edit-draft"])
            session["resource_draft"] = draft_list[int(request.form["edit-draft"])]["draft"]
            return redirect(
                url_for("resources.new_resource", resource_class=resource_class, form=form, draft_list=draft_list))
        if request.form.get("cancel", None):
            session["update_resource_draft"] = False
            session["update_new_resource"] = False
            return redirect(url_for("resources.resource", resource_class=resource_class))
    return render_template("new_resource.html", resource_class=resource_class, form=form, draft_list=draft_list, physical_resource=physical_resource)


@resources.route("/resources_type/<resource_class>/edit_resource/<resource_id>", methods=["GET", "POST"])
def edit_resource(resource_class, resource_id):
    editing_resource = resource_display.get_one_resource(resource_class, resource_id)
    physical_resource = dict()
    physical_resource["robot"] = name_and_ID_filter(resource_display.get_all_resource_list("robot"))
    physical_resource["hardware"] = name_and_ID_filter(resource_display.get_all_resource_list("hardware"))
    physical_resource["human"] = name_and_ID_filter(resource_display.get_all_resource_list("human"))
    # Define form
    if resource_class in ["robot", "hardware", "human"]:
        form = PhysicalResourceForm()
        form.location_id.choices = format_choice(resource_display.get_all_resource_list("location"), sentence_db="location_id", original_value=editing_resource["location_id"])
    elif resource_class == "software":
        form = CyberResourceForm()
    else:
        form = LocationResourceForm()
    form.type.choices = format_choice(resource_display.get_unique_resource_type(resource_class), sentence_db="edit_resource", original_value=editing_resource["type"])
    if request.method == "POST":
        if request.form.get("confirm-changes", None):
            req = clean_request(request.form.to_dict(flat=False), "resource")
            print(req)
            if new_resource_validation(req, resource_class):
                editing_resource["name"] = req["name"]
                if req["type_new"] == '':
                    editing_resource["type"] = req["type"]
                else:
                    editing_resource["type"] = req["type_new"]
                if resource_class in ["robot", "hardware", "human"]:
                    # editing_resource["location_id"] = req["location_id"]
                    editing_resource["coordinate"]["position_sensor_tag"] = req["position_sensor_tag"]
                    editing_resource["coordinate"]["x"] = req["position_x"]
                    editing_resource["coordinate"]["y"] = req["position_y"]
                    editing_resource["coordinate"]["z"] = req["position_z"]
                elif resource_class == "software":
                    editing_resource["param_var"] = req["param"]
                    editing_resource["state_var"] = req["state"]
                    editing_resource["directory"] = ''
                    editing_resource["cyber_twin"] = ''
                else:
                    editing_resource["position"]["x"] = req["position_x"]
                    editing_resource["position"]["y"] = req["position_y"]
                    editing_resource["position"]["z"] = req["position_z.data"]
                    editing_resource["orientation"]["alpha"] = req["alpha.data"]
                    editing_resource["orientation"]["beta"] = req["beta.data"]
                    editing_resource["orientation"]["gamma"] = req["gamma.data"]
                    editing_resource["size"]["length"] = req["length.data"]
                    editing_resource["size"]["width"] = req["width.data"]
                    editing_resource["size"]["height"] = req["height.data"]
                resource_id = str(editing_resource["_id"])
                resource_update.update_resource(resource_id, resource_class, session["user_id"], editing_resource)
                return redirect(url_for("resources.resource", resource_class=resource_class))
        if request.form.get("cancel", None):
            session["update_resource_draft"] = False
            session["update_new_resource"] = False
            return redirect(url_for("resources.resource", resource_class=resource_class))
    return render_template("edit_resource.html", resource_class=resource_class, editing_resource=editing_resource,
                           form=form, physical_resource=physical_resource)




