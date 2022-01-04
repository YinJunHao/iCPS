"""
    Functions called in routes to aid in data formatting for better front-end presentation.
"""

from flask import session, flash
from nltk.corpus import stopwords
from CPSBuilder.modules.visualizer import ResourceDisplay
from pymongo import MongoClient

import config
import logging
logger = logging.getLogger(__name__)

# initialize mongo client
client = MongoClient(config.mongo_ip, config.mongo_port)

resource_display = ResourceDisplay(client)

def format_choice(input_list, sentence_db=None, full_list=None, original_value=None):
    """
    Formats the inputted list into a list of tuples in the form (item, item)
    """
    for item in input_list:
        if item == " " or item == "":
            input_list.remove(item)
    out = [(" ", " ")]
    if sentence_db is None:
        for item in input_list:
            out.append((item, item))
    elif sentence_db is "edit_resource":
        if original_value != " ":
            out.insert(0, (original_value, original_value))
        for item in input_list:
            if item != original_value:
                out.append((item, item))
    elif sentence_db is "location_id":
        if original_value is None:
            for item in input_list:
                out.append((item["ID"], item["ID"]))
        else:
            if original_value != " ":
                out.insert(0, (original_value, original_value))
            for item in input_list:
                if item["ID"] != original_value:
                    out.append((item["ID"], item["ID"]))
    #  todo: add functionality to translate and package
    return out


def add_empty_choice(input_list, sentence_db=None):
    """
       Adds an empty first choice to the list of tuples in the form (item, item)
    """

    output_list = input_list
    empty = (" ", " ")
    output_list.insert(0, empty)
    return output_list


def index_choice(input_list, from_n=0):
    """
    Formats the inputted list into a list of tuple in the form (index, item). "from_n" adjusts the first element of the index, default is 0.
    """
    out = []
    for i, item in enumerate(input_list):
        out.append((i + from_n, item))
    return out


def clear_session(is_log_out=False):
    if is_log_out:
        user_id = session['user_id']
        session.clear()
        session['user_id'] = user_id
    else:
        session.clear()


def get_var_and_sentence(var_sentence_list):
    """
    Splits a list of tuples in the form (variable, sentence) into separate lists.
    """
    var = []
    sentence = []
    for item in var_sentence_list:
        var.append(item[0])
        sentence.append(item[1])
    return var, sentence


def pack_var_sentence(var_list, sentence_list):
    """
    Combines the list of variables and sentences into a list of tuples in the form (variable, sentence)
    """
    out = []
    for item in zip(var_list, sentence_list):
        out.append(item)
    return out


def dict2table(item_dict):
    """
    Converts a dictionary into a list of tuples in the form (key, value)
    """
    return item_dict.items()

def clean_request(item_dict, area):
    """
        Cleans the request form
    """
    if area == "process":
        for key, items in item_dict.items():
            if "," not in key:
                if key not in ["param", "state", "StepBlocker", "StateBlocker", "location_id"] and len(items) == 1:
                    item_dict[key] = items[0]
        for key, items in item_dict.items():
            if "new" in key:
                item_dict[key] = items[0]
        for key, items in item_dict.items():
            if key in ["StepBlocker", "StateBlocker"]:
                items = list(dict.fromkeys(items))
                for index, item in enumerate(items):
                    if item == "none":
                        items.pop(index)
                    else:
                        items[index] = int(item)
        for key, items in item_dict.items():
            if "hasPrerequisiteStep" in key:
                for key_1, items_1 in item_dict.items():
                    if "new" in key and "hasPrerequisiteStep" in key:
                        if items == items_1:
                            item_dict.pop(key_1)
            if "hasPrerequisiteState" in key:
                for key_1, items_1 in item_dict.items():
                    if "new" in key and "hasPrerequisiteState" in key:
                        if items == items_1:
                            item_dict.pop(key_1)
        new_key_list = []
        for key, items in item_dict.items():
            if "state-exec" in key:
                text = key.split(",")
                no = text[0]
                new_key = no + ",stateexec"
                new_key_list.append(new_key)
        for newkey in new_key_list:
            item_dict[newkey] = dict()
            item_dict[newkey]["exec"] = list()
        for key, items in item_dict.items():
            if "state-exec-setname" in key:
                text = key.split(",")
                no = text[0]
                temp_key = no + ",stateexec"
                item_dict[temp_key]["name"] = items[0]
            if "state-exec-type" in key:
                text = key.split(",")
                no = text[0]
                temp_key = no + ",stateexec"
                item_dict[temp_key]["type"] = items[0]
            if "state-exec-class" in key:
                text = key.split(",")
                no = text[0]
                temp_key = no + ",stateexec"
                if "diff" in key:
                    if items[0] != "":
                        item_dict[temp_key]["class"] = items[0]
                else:
                    item_dict[temp_key]["class"] = items[0]
            if "state-exec-physical-name" in key:
                text = key.split(",")
                no = text[0]
                temp_key = no + ",stateexec"
                for item in items:
                    temp_exec = dict()
                    temp_exec["physical-resource-id"] = item
                    item_dict[temp_key]["exec"].append(temp_exec)
            if "state-exec-software-name" in key:
                text = key.split(",")
                no = text[0]
                temp_key = no + ",stateexec"
                for idx, item in enumerate(items):
                    item_dict[temp_key]["exec"][idx]["software_resource_id"] = item
    if area == "resource":
        for key, items in item_dict.items():
            if key not in ["param", "state", "physical-resource-class", "physical-resource-id"] and len(items) == 1:
                item_dict[key] = items[0]
            if key in ["position_x_min", "position_y_min", "position_z_min", "alpha", "beta", "gamma", "length", "width", "height", "position_x_max", "position_y_max", "position_z_max"]:
                try:
                    item_dict[key] = float(item_dict[key])
                except ValueError:
                    pass
                if item_dict[key] == "":
                    item_dict[key] = None
            if key == "status":
                if int(item_dict[key]) == 1:
                    item_dict[key] = True
                else:
                    item_dict[key] = False
    return item_dict

def tokenize_sentence(sentence):
    """
    Splits the input sentence into words as tokens and removes stopwords defined in NLTK.

    For more info: https://pythonspot.com/nltk-stop-words/
    """
    word_list = sentence.lower().split(" ")
    filtered_words = [
        word for word in word_list if word not in stopwords.words('english')]
    return filtered_words

def translate_sentence_to_var(sentence):
    """
    Converts a translated sentence into a variable name in snake case (i.e. snake_case)
    """
    words = tokenize_sentence(sentence)
    out = ""
    for word in words:
        out += "_" + word
    return out[1:]

def process_format(process_details):
    """
       Adds index to the process details when given from the back end to the front end
    """
    details = dict(process_details)
    for key, value in details.items():
        if key == "task":
            value["index"] = 0
            value["_id"] = str(value["_id"])
            layer = int(value["content_layer"][16:]) + 1
            value["layer_no"] = layer
        else:
            for num, content in enumerate(value, start=0):
                print(value)
                content["index"] = num
                content["_id"] = str(content["_id"])
    for key, value in details.items():
        if key == "task":
            content_index = []
            for content in details[value["content_layer"]]:
                if content["_id"] in value["content_ObjectId"]:
                    content_index.append(content["index"])
            value["content_index"] = content_index
        elif key == "step":
            for cont in value:
                # step_state_index = []
                # for content in details["state"]:
                #     if content["_id"] in cont["step_state_ObjectId"]:
                #         step_state_index.append(content["index"])
                # cont["step_state_index"] = step_state_index
                state_exec_index = []
                for content in details["state"]:
                    if content["_id"] in cont["state_exec_ObjectId"]:
                        state_exec_index.append(content["index"])
                cont["state_exec_index"] = state_exec_index
                step_param_index = []
                for content in details["parameter"]:
                    if content["_id"] in cont["step_param_ObjectId"]:
                        step_param_index.append(content["index"])
                cont["step_param_index"] = step_param_index
                for content in details["condition"]:
                    if content["_id"] == cont["step_cond_ObjectId"]:
                        cont["step_cond_index"] = content["index"]
        elif key == "state" or key == "parameter":
            continue
        elif key == "condition":
            for cont in value:
                isBlockedByStep_index = []
                for content in details["isBlockedByStep"]:
                    if content["_id"] in cont["isBlockedByStep_ObjectId"]:
                        isBlockedByStep_index.append(content["index"])
                cont["isBlockedByStep_index"] = isBlockedByStep_index
                hasPrerequisiteStep_index = []
                for content in details["hasPrerequisiteStep"]:
                    if content["_id"] in cont["hasPrerequisiteStep_ObjectId"]:
                        hasPrerequisiteStep_index.append(content["index"])
                cont["hasPrerequisiteStep_index"] = hasPrerequisiteStep_index
                isBlockedByState_index = []
                for content in details["isBlockedByState"]:
                    if content["_id"] in cont["isBlockedByState_ObjectId"]:
                        isBlockedByState_index.append(content["index"])
                cont["isBlockedByState_index"] = isBlockedByState_index
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                isAchievedBy_index = []
                for content in details["isAchievedBy"]:
                    if content["_id"] in cont["isAchievedBy_ObjectId"]:
                        isAchievedBy_index.append(content["index"])
                cont["isAchievedBy_index"] = isAchievedBy_index
                isFailedByState_index = []
                for content in details["isFailedByState"]:
                    if content["_id"] in cont["isFailedByState_ObjectId"]:
                        isFailedByState_index.append(content["index"])
                cont["isFailedByState_index"] = isFailedByState_index
        elif key == "isBlockedByStep":
            for cont in value:
                StepBlocker_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepBlocker_ObjectId"]:
                        StepBlocker_index.append(content["index"])
                cont["StepBlocker_index"] = StepBlocker_index
        elif key == "hasPrerequisiteStep":
            for cont in value:
                StepPrerequisite_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepPrerequisite_ObjectId"]:
                        StepPrerequisite_index.append(content["index"])
                cont["StepPrerequisite_index"] = StepPrerequisite_index
        elif key == "isBlockedByState":
            for cont in value:
                StateBlocker_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateBlocker_ObjectId"]:
                        StateBlocker_index.append(content["index"])
                cont["StateBlocker_index"] = StateBlocker_index
        elif key == "hasPrerequisiteState":
            for cont in value:
                StatePrerequisite_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StatePrerequisite_ObjectId"]:
                        StatePrerequisite_index.append(content["index"])
                cont["StatePrerequisite_index"] = StatePrerequisite_index
        elif key == "isAchievedBy":
            for cont in value:
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                StateCorrect_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateCorrect_ObjectId"]:
                        StateCorrect_index.append(content["index"])
                cont["StateCorrect_index"] = StateCorrect_index
        elif key == "isFailedByState":
            for cont in value:
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                StateCorrect_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateCorrect_ObjectId"]:
                        StateCorrect_index.append(content["index"])
                cont["StateCorrect_index"] = StateCorrect_index
                StateWrong_index =[]
                for content in details["state"]:
                    if content["_id"] in cont["StateWrong_ObjectId"]:
                        StateWrong_index.append(content["index"])
                cont["StateWrong_index"] = StateWrong_index
                StepReturn_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepReturn_ObjectId"]:
                        StepReturn_index.append(content["index"])
                cont["StepReturn_index"] = StepReturn_index
        else:
            for cont in value:
                content_index = []
                for content in details[cont["content_layer"]]:
                    if content["_id"] in cont["content_ObjectId"]:
                        content_index.append(content["index"])
                cont["content_index"] = content_index
    return details

def process_format_start(process_details):
    """
       Adds index to the process details when given from the back end to the front end
       Adds the status before optimising
    """
    details = dict(process_details)
    for key, value in details.items():
        if key == "task":
            value["index"] = 0
            value["_id"] = str(value["_id"])
            layer = int(value["content_layer"][16:]) + 1
            value["layer_no"] = layer
            value["status"] = False
        else:
            for num, content in enumerate(value, start=0):
                content["status"] = False
                content["index"] = num
                content["_id"] = str(content["_id"])
    for key, value in details.items():
        if key == "task":
            content_index = []
            for content in details[value["content_layer"]]:
                if content["_id"] in value["content_ObjectId"]:
                    content_index.append(content["index"])
            value["content_index"] = content_index
        elif key == "step":
            for cont in value:
                # step_state_index = []
                # for content in details["state"]:
                #     if content["_id"] in cont["step_state_ObjectId"]:
                #         step_state_index.append(content["index"])
                # cont["step_state_index"] = step_state_index
                state_exec_index = []
                for content in details["state"]:
                    if content["_id"] in cont["state_exec_ObjectId"]:
                        state_exec_index.append(content["index"])
                cont["state_exec_index"] = state_exec_index
                step_param_index = []
                for content in details["parameter"]:
                    if content["_id"] in cont["step_param_ObjectId"]:
                        step_param_index.append(content["index"])
                        cont["param"].append(content["param"])
                cont["step_param_index"] = step_param_index
                for content in details["condition"]:
                    if content["_id"] == cont["step_cond_ObjectId"]:
                        cont["step_cond_index"] = content["index"]
        elif key == "state" or key == "parameter":
            continue
        elif key == "condition":
            for cont in value:
                isBlockedByStep_index = []
                for content in details["isBlockedByStep"]:
                    if content["_id"] in cont["isBlockedByStep_ObjectId"]:
                        isBlockedByStep_index.append(content["index"])
                cont["isBlockedByStep_index"] = isBlockedByStep_index
                hasPrerequisiteStep_index = []
                for content in details["hasPrerequisiteStep"]:
                    if content["_id"] in cont["hasPrerequisiteStep_ObjectId"]:
                        hasPrerequisiteStep_index.append(content["index"])
                cont["hasPrerequisiteStep_index"] = hasPrerequisiteStep_index
                isBlockedByState_index = []
                for content in details["isBlockedByState"]:
                    if content["_id"] in cont["isBlockedByState_ObjectId"]:
                        isBlockedByState_index.append(content["index"])
                cont["isBlockedByState_index"] = isBlockedByState_index
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                isAchievedBy_index = []
                for content in details["isAchievedBy"]:
                    if content["_id"] in cont["isAchievedBy_ObjectId"]:
                        isAchievedBy_index.append(content["index"])
                cont["isAchievedBy_index"] = isAchievedBy_index
                isFailedByState_index = []
                for content in details["isFailedByState"]:
                    if content["_id"] in cont["isFailedByState_ObjectId"]:
                        isFailedByState_index.append(content["index"])
                cont["isFailedByState_index"] = isFailedByState_index
        elif key == "isBlockedByStep":
            for cont in value:
                StepBlocker_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepBlocker_ObjectId"]:
                        StepBlocker_index.append(content["index"])
                cont["StepBlocker_index"] = StepBlocker_index
        elif key == "hasPrerequisiteStep":
            for cont in value:
                StepPrerequisite_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepPrerequisite_ObjectId"]:
                        StepPrerequisite_index.append(content["index"])
                cont["StepPrerequisite_index"] = StepPrerequisite_index
        elif key == "isBlockedByState":
            for cont in value:
                StateBlocker_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateBlocker_ObjectId"]:
                        StateBlocker_index.append(content["index"])
                cont["StateBlocker_index"] = StateBlocker_index
        elif key == "hasPrerequisiteState":
            for cont in value:
                StatePrerequisite_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StatePrerequisite_ObjectId"]:
                        StatePrerequisite_index.append(content["index"])
                cont["StatePrerequisite_index"] = StatePrerequisite_index
        elif key == "isAchievedBy":
            for cont in value:
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                StateCorrect_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateCorrect_ObjectId"]:
                        StateCorrect_index.append(content["index"])
                cont["StateCorrect_index"] = StateCorrect_index
        elif key == "isFailedByState":
            for cont in value:
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                StateCorrect_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateCorrect_ObjectId"]:
                        StateCorrect_index.append(content["index"])
                cont["StateCorrect_index"] = StateCorrect_index
                StateWrong_index =[]
                for content in details["state"]:
                    if content["_id"] in cont["StateWrong_ObjectId"]:
                        StateWrong_index.append(content["index"])
                cont["StateWrong_index"] = StateWrong_index
                StepReturn_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepReturn_ObjectId"]:
                        StepReturn_index.append(content["index"])
                cont["StepReturn_index"] = StepReturn_index
        else:
            for cont in value:
                content_index = []
                for content in details[cont["content_layer"]]:
                    if content["_id"] in cont["content_ObjectId"]:
                        content_index.append(content["index"])
                cont["content_index"] = content_index
    return details

def new_index(layer):
    """
           Adds index to the new content in process details
    """
    loop = True
    index = 0
    while loop:
        loop = False
        for content in session["process_details"][layer]:
            if content["index"] == index:
                loop = True
                break
        index += 1
    index -= 1
    return index

def determine_layer(layer):
    """
            Finds the child layer
    """
    if layer == "objective_layer_1":
        content_layer = "step"
    else:
        text = layer.split("_")
        number = int(text[2]) - 1
        content_layer = "objective_layer_" + str(number)
    return content_layer

def determine_parent_layer(layer):
    """
            Finds the parent layer, for new layer creation
    """
    text = layer.split("_")
    number = int(text[2]) + 1
    parent_layer = "objective_layer_" + str(number)
    return parent_layer

def empty_process(name):
    """
            Creates a new empty process
    """
    process_details = {}
    process_details["task"] = {}
    process_details["task"]["var"] = translate_sentence_to_var(name)
    process_details["task"]["sentence"] = name
    process_details["task"]["layer"] = "task"
    process_details["task"]["content_layer"] = "objective_layer_1"
    process_details["task"]["content_ObjectId"] = []
    process_details["task"]["index"] = 0
    process_details["task"]["layer_no"] = 2
    process_details["objective_layer_1"] = []
    process_details["step"] = []
    process_details["state"] = []
    process_details["parameter"] = []
    process_details["condition"] = []
    process_details["isBlockedByStep"] = []
    process_details["hasPrerequisiteStep"] = []
    process_details["isBlockedByState"] = []
    process_details["hasPrerequisiteState"] = []
    process_details["isAchievedBy"] = []
    process_details["isFailedByState"] = []

    return process_details

def new_resource_validation(req, resource_class):
    """
                Validation for new resource creation
        """
    validation = True
    if req["name"] == "":
        flash("Please input a name", "danger")
    if req["type"] == " " and req["type_new"] == "":
        flash("Please input a type", "danger")
        validation = False
    if resource_class in ["robot", "hardware", "human"]:
        # if req["position_sensor_tag"] == "none":
            # if req["position_x"] == None and req["position_y"] == None and req["position_z"] == None:
            #     flash("Please input either a position sensor tag or coordinates", "danger")
            # else:
            #     test = True
            #     location_db = resource_display.get_all_resource_list("location")
            #     for location in location_db:
            #         x_start = location["position"]["x"]
            #         x_end = location["position"]["x"] + location["size"]["length"]
            #         y_start = location["position"]["y"]
            #         y_end = location["position"]["y"] + location["size"]["width"]
            #         z_start = location["position"]["z"]
            #         z_end = location["position"]["z"] + location["size"]["height"]
            #         if req["position_x"] < x_start or req["position_x"] > x_end:
            #             test = False
            #         if req["position_y"] < y_start or req["position_y"] > y_end:
            #             test = False
            #         if req["position_z"] < z_start or req["position_z"] > z_end:
            #             test = False
            #     if not test:
            #         flash("Position is not valid", "danger")
        if req["position_sensor_tag"] == "none" and req["location_id"] == " ":
            validation = False
            flash("Please input a Position Sensor Tag or Location ID", "danger")
    # if resource_class == "location":
    #     if isinstance(req["position_x"], (type(None), float)) and isinstance(req["position_y"], (
    #             type(None), float)) and isinstance(req["position_z"], (type(None), float)):
    #         pass
    #     else:
    #         flash("Coordinate is not a number", "danger")
    #         validation = False
    if resource_class == "location":
        if isinstance(req["position_x_min"], (type(None), float)) and isinstance(req["position_y_min"], (
                type(None), float)) and isinstance(req["position_z_min"], (type(None), float)) and isinstance(
            req["position_x_max"], (type(None), float)) and isinstance(req["position_y_max"],
                                                                       (type(None), float)) and isinstance(
            req["position_z_max"], (type(None), float)):
            if float(req["position_x_min"]) >= float(req["position_x_max"]):
                flash("Axis x is not logical", "danger")
            if float(req["position_y_min"]) >= float(req["position_y_max"]):
                flash("Axis y is not logical", "danger")
            if float(req["position_z_min"]) >= float(req["position_z_max"]):
                flash("Axis z is not logical", "danger")
        else:
            flash("Position is not a number", "danger")
            validation = False
        if isinstance(req["alpha"], (type(None), float)) and isinstance(req["beta"], (
                type(None), float)) and isinstance(req["gamma"], (type(None), float)):
            pass
        else:
            print(type(req["alpha"]))
            flash("Angle is not a number", "danger")
            validation = False
        # if isinstance(req["length"], (type(None), float)) and isinstance(req["width"], (
        #         type(None), float)) and isinstance(req["height"], (type(None), float)):
        #     pass
        # else:
        #     flash("Size is not a number", "danger")
            validation = False
    if resource_class == "software":
        if len(req["param"]) == 1:
            if req["param"][0] == "":
                flash("Please enter a parameter", "danger")
                validation = False
        if len(req["state"]) == 1:
            if req["state"][0] == "":
                flash("Please enter a state", "danger")
                validation = False
        if len(req["physical-resource-id"]) == 1:
            if req["physical-resource-id"][0] == "":
                flash("Please specify a physical resource this software belongs to", "danger")
                validation = False
    return validation


def name_and_ID_filter(input_list, cyber=False, location=False):
    """
        filters out name and ID for select choice
    """
    new_list = list()
    if location:
        for item in input_list:
            new_list.append(item["ID"])
    else:
        for item in input_list:
            temp_dict = dict()
            temp_dict["name"] = item["name"]
            temp_dict["ID"] = item["ID"]
            if cyber:
                temp_dict["physical_resource_id"] = item["physical_resource_id"]
            new_list.append(temp_dict)
    return new_list

def job_process_format(process):
    """
        Format the process for job optimisation
    """
    details = process.copy()
    for key, item in details.items():
        if key in "step" or "objective" in key:
            for condition in item:
                condition["status"] = False
        if key == "task":
            item["status"] = False
    for key, item in details.items():
        if key != "task":
            for content in item:
                content["_id"] = str(content["_id"])
    for key, value in details.items():
        if key == "task":
            value["index"] = 0
            value["_id"] = str(value["_id"])
            layer = int(value["content_layer"][16:]) + 1
            value["layer_no"] = layer
        else:
            for num, content in enumerate(value, start=0):
                content["index"] = num
                content["_id"] = str(content["_id"])
    for key, value in details.items():
        if key == "task":
            content_index = []
            for content in details[value["content_layer"]]:
                if content["_id"] in value["content_ObjectId"]:
                    content_index.append(content["index"])
            value["content_index"] = content_index
        elif key == "step":
            for cont in value:
                # step_state_index = []
                # for content in details["state"]:
                #     if content["_id"] in cont["step_state_ObjectId"]:
                #         step_state_index.append(content["index"])
                # cont["step_state_index"] = step_state_index
                state_exec_index = []
                for content in details["state"]:
                    if content["_id"] in cont["state_exec_ObjectId"]:
                        state_exec_index.append(content["index"])
                cont["state_exec_index"] = state_exec_index
                step_param_index = []
                for content in details["parameter"]:
                    if content["_id"] in cont["step_param_ObjectId"]:
                        step_param_index.append(content["index"])
                        cont["param"].append(content["param"])
                cont["step_param_index"] = step_param_index
                for content in details["condition"]:
                    if content["_id"] == cont["step_cond_ObjectId"]:
                        cont["step_cond_index"] = content["index"]
                cont["location_list"] = cont["location_id"]
                cont.pop("location_id")
        elif key == "state" or key == "parameter":
            continue
        elif key == "condition":
            for cont in value:
                isBlockedByStep_index = []
                for content in details["isBlockedByStep"]:
                    if content["_id"] in cont["isBlockedByStep_ObjectId"]:
                        isBlockedByStep_index.append(content["index"])
                cont["isBlockedByStep_index"] = isBlockedByStep_index
                hasPrerequisiteStep_index = []
                for content in details["hasPrerequisiteStep"]:
                    if content["_id"] in cont["hasPrerequisiteStep_ObjectId"]:
                        hasPrerequisiteStep_index.append(content["index"])
                cont["hasPrerequisiteStep_index"] = hasPrerequisiteStep_index
                isBlockedByState_index = []
                for content in details["isBlockedByState"]:
                    if content["_id"] in cont["isBlockedByState_ObjectId"]:
                        isBlockedByState_index.append(content["index"])
                cont["isBlockedByState_index"] = isBlockedByState_index
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                isAchievedBy_index = []
                for content in details["isAchievedBy"]:
                    if content["_id"] in cont["isAchievedBy_ObjectId"]:
                        isAchievedBy_index.append(content["index"])
                cont["isAchievedBy_index"] = isAchievedBy_index
                isFailedByState_index = []
                for content in details["isFailedByState"]:
                    if content["_id"] in cont["isFailedByState_ObjectId"]:
                        isFailedByState_index.append(content["index"])
                cont["isFailedByState_index"] = isFailedByState_index
        elif key == "isBlockedByStep":
            for cont in value:
                StepBlocker_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepBlocker_ObjectId"]:
                        StepBlocker_index.append(content["index"])
                cont["StepBlocker_index"] = StepBlocker_index
        elif key == "hasPrerequisiteStep":
            for cont in value:
                StepPrerequisite_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepPrerequisite_ObjectId"]:
                        StepPrerequisite_index.append(content["index"])
                cont["StepPrerequisite_index"] = StepPrerequisite_index
        elif key == "isBlockedByState":
            for cont in value:
                StateBlocker_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateBlocker_ObjectId"]:
                        StateBlocker_index.append(content["index"])
                cont["StateBlocker_index"] = StateBlocker_index
        elif key == "hasPrerequisiteState":
            for cont in value:
                StatePrerequisite_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StatePrerequisite_ObjectId"]:
                        StatePrerequisite_index.append(content["index"])
                cont["StatePrerequisite_index"] = StatePrerequisite_index
        elif key == "isAchievedBy":
            for cont in value:
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                StateCorrect_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateCorrect_ObjectId"]:
                        StateCorrect_index.append(content["index"])
                cont["StateCorrect_index"] = StateCorrect_index
        elif key == "isFailedByState":
            for cont in value:
                hasPrerequisiteState_index = []
                for content in details["hasPrerequisiteState"]:
                    if content["_id"] in cont["hasPrerequisiteState_ObjectId"]:
                        hasPrerequisiteState_index.append(content["index"])
                cont["hasPrerequisiteState_index"] = hasPrerequisiteState_index
                StateCorrect_index = []
                for content in details["state"]:
                    if content["_id"] in cont["StateCorrect_ObjectId"]:
                        StateCorrect_index.append(content["index"])
                cont["StateCorrect_index"] = StateCorrect_index
                StateWrong_index =[]
                for content in details["state"]:
                    if content["_id"] in cont["StateWrong_ObjectId"]:
                        StateWrong_index.append(content["index"])
                cont["StateWrong_index"] = StateWrong_index
                StepReturn_index = []
                for content in details["step"]:
                    if content["_id"] in cont["StepReturn_ObjectId"]:
                        StepReturn_index.append(content["index"])
                cont["StepReturn_index"] = StepReturn_index
        else:
            for cont in value:
                content_index = []
                for content in details[cont["content_layer"]]:
                    if content["_id"] in cont["content_ObjectId"]:
                        content_index.append(content["index"])
                cont["content_index"] = content_index
    return details

def status_check(process):
    """
        Check the status of the process:
    """
    final_layer = process["task"]["content_layer"]
    layer = "objective_layer_1"
    content_layer = "step"
    test = True
    while test:
        if content_layer == final_layer:
            temp = True
            for objective in process[content_layer]:
                if not objective["status"]:
                    temp = False
            if temp:
                process["task"]["status"] = True
            test = False
        else:
            for objective in process[layer]:
                temp = True
                for content in process[content_layer]:
                    if content["_id"] in objective["content_ObjectId"]:
                        if not content["status"]:
                            temp = False
                if temp:
                    objective["status"] = True
        content_layer = layer
        new_number = int(layer[16:]) + 1
        layer = "objective_layer_" + str(new_number)
    return process

def new_job_validation(req):
    """
            Validates new job
        """
    validation = True
    if req["job_name"] == "":
        validation = False
        flash("Please give a name to the job", "danger")
    if req["continue"] == "":
        validation = False
        flash("Please queue at least 1 task", "danger")
    return validation


def last_index_dict(task_details):
    """
        Returns a dictionary with the last indexes of each layer
    """

    index_dict = dict()
    index_dict["task"] = task_details["task"]["index"]
    for key,value in task_details.items():
        max_val = 0
        if "objective" in key:
            for content in value:
                if content["index"] > max_val:
                    max_val = content["index"]
            index_dict[key] = max_val
    max_val = 0
    for step in task_details["step"]:
        if step["index"] > max_val:
            max_val = step["index"]
    index_dict["step"] = max_val
    return index_dict