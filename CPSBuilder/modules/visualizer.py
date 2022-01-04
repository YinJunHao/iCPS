"""
Program title: iCPS
Project title: CPS Builder
This script get doc from db col and package the contents for front-end UI display.
Written by Wong Pooi Mun.
"""

from CPSBuilder.utils.db import *
from CPSBuilder.utils.general import *

from bson import ObjectId
from pprint import pprint
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class Visualizer():
    """
        Contain common utils to translate items between var and sentence.
    """

    def __init__(self, client, test=False, demo=False):
        # initialize db
        if test:
            self.search_engine_db = client["test-search-engine"]
            self.process_db = client["test-process"]
            self.condition_db = client["test-condition"]
            self.resource_db = client["test-resource"]
            self.draft_db = client["test-draft"]
            self.job_db = client["test-job"]
            self.code_db = client["code"]  # don't need test db
            self.user_db = client["test-user"]
        else:
            self.search_engine_db = client["search-engine"]
            self.process_db = client["process"]
            self.condition_db = client["condition"]
            self.resource_db = client["resource"]
            self.draft_db = client["draft"]
            self.job_db = client["job"]
            self.code_db = client["code"]
            self.user_db = client['user']
        # initialize db col
        self.var_sentence_col = self.process_db["var-sentence"]
        self.task_token_col = self.search_engine_db["task-token"]
        self.objective_token_col = self.search_engine_db["objective-token"]
        self.step_token_col = self.search_engine_db["step-token"]
        self.task_objective_col = self.process_db["task-objective"]
        self.objective_content_col = self.process_db["objective-content"]
        self.step_col = self.process_db["step"]
        self.step_cond_col = self.process_db["step-cond"]
        self.step_param_col = self.process_db["step-param"]
        self.step_state_col = self.process_db["step-state"]
        self.state_exec_col = self.process_db["state-exec"]
        self.blocker_step_col = self.condition_db["isBlockedByStep"]
        self.blocker_state_col = self.condition_db["isBlockedByState"]
        self.pre_step_col = self.condition_db["hasPrerequisiteStep"]
        self.pre_state_col = self.condition_db["hasPrerequisiteState"]
        self.achieve_col = self.condition_db["isAchievedBy"]
        self.fail_col = self.condition_db["isFailedByState"]
        self.condition_db_dict = {
            "isBlockedByStep": self.blocker_step_col,
            "isBlockedByState": self.blocker_state_col,
            "hasPrerequisiteStep": self.pre_step_col,
            "hasPrerequisiteState": self.pre_state_col,
            "isAchievedBy": self.achieve_col,
            "isFailedByState": self.fail_col,
        }
        self.state_exec_col = self.process_db["state-exec"]
        self.physical_col = self.resource_db["physical"]
        self.cyber_col = self.resource_db["cyber"]
        self.location_col = self.resource_db["location"]
        self.db_dict = {
            "physical": self.physical_col,  # backup
            "human": self.physical_col,
            "robot": self.physical_col,
            "hardware": self.physical_col,
            "software": self.cyber_col,
            "location": self.location_col,
        }
        self.resource_draft_col = self.draft_db["resource"]
        self.process_draft_col = self.draft_db["process"]
        self.job_task_col = self.job_db["job-task"]
        self.status_col = self.code_db["status"]
        self.profile_col = self.user_db["profile"]


    def translate_var(self, var):
        """
        Translates the variable into a sentence.

        :param var: a string of word used to describe process components.
        :return:
        sentence: a string of words as stored in var-sentence col.
        """
        sentence_cursor = self.var_sentence_col.find({"var": var})
        res = next(sentence_cursor)
        sentence = res["sentence"]
        return sentence

    def get_var_list(self, ObjectId_list, db_col):
        """
        Deprecated.
        Gets var based on ObjectId.
        """
        var_list = list()
        for item_id in ObjectId_list:
            query = {
                "_id": ObjectId(item_id)
            }
            db_item = get_item(db_col, query)[0]
            var = db_item.get("var", None)
            var_list.append(var)
        return var_list

    def get_sentence_list(self, var_list):
        """
        Gets sentence based on var.
        """
        sentence_list = []
        for var in var_list:
            sentence = self.translate_var(var)
            sentence_list.append(sentence)
        return sentence_list

    def get_id_sentence_tuple_list(self, id_list, var_list):
        """
        Packages corresponding sentence to the var as a tuple.
        """
        sentence_list = self.get_sentence_list(var_list)
        id_sentence_list = zip(id_list, sentence_list)
        return id_sentence_list


class JobDisplay(Visualizer):
    """
        Gets and packages job history or running jobs.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        self.task_display = TaskDisplay(client, test, demo)

    def get_process_details_for_job(self, task_ObjectId):
        process_details = self.task_display.get_process_details(task_ObjectId)
        # For each step component,
        for step in process_details["step"]:
            # Replace step_param_ObjectId with list of param dict
            step["param"] = [
                param   # Append param dict
                for param in process_details["parameter"]   # Loop dict in parameter list
                if param["_id"] in step["step_param_ObjectId"]
            ]
            # Add exec list with state_exec dict as element
            step["state"] = [
                state  # Append state dict
                for state in process_details["state"]  # Loop dict in state list
                if str(state["_id"]) in step["state_exec_ObjectId"]
            ]
        return process_details

    def get_running_job(self, user_id):
        """
        Gets pending jobs that are submitted by the user.
        """
        db_col = self.job_db[user_id]
        query = {
            "status": "pending"
        }
        job_list = get_item(db_col, query)
        status_sentence = self.get_status_sentence("pending")
        for job in job_list:
            job["status"] = status_sentence
        return job_list

    def get_job_history(self, user_id):
        """
        Gets history of job that are no longer running and are submitted by the user.
        """
        db_col = self.job_db[user_id]
        query = {
            "status": {"$ne": "pending"}
        }
        job_list = get_item(db_col, query)
        for job in job_list:
            job["status"] = self.get_status_sentence(job["status"])
        return job_list

    def get_job_task(self, job_id):
        """
        Gets task of the job with var and status translated to sentences.
        """
        query = {
            "job_id": job_id,
        }
        task_list = get_item(self.job_task_col, query)
        for task in task_list:
            task["status"] = self.get_status_sentence(task["status"])
            task["sentence"] = self.translate_var(task["var"])
            objective_layer_key_list = self.get_objective_layer_key(task)
            for key in objective_layer_key_list:
                for objective in task[key]:
                    objective["status"] = self.get_status_sentence(objective["status"])
                    objective["sentence"] = self.translate_var(objective["var"])
            for step in task["step"]:
                step["status"] = self.get_status_sentence(step["status"])
                step["sentence"] = self.translate_var(step["var"])
        return task_list

    def get_status_sentence(self, status):
        """
        Converts status into sentence of state code.
        """
        print(status)
        doc = get_item(self.status_col, {"code": status})[0]
        sentence = doc["sentence"]
        return sentence

    def get_objective_layer_key(self, task_details):
        """
        Gets the list of keys that start with "obje...".
        """
        key_list = [
            key
            for key, value in task_details.items()
            if key[:4] == "objective"[:4]
        ]
        return key_list


class ProcessDisplay(Visualizer):
    """
        Contain common utils to extract and package contents for process display.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_all_draft_list(self, user_id):
        """
        Gets process draft list that is created by the user.
        """
        db = self.process_draft_col
        query = {
            "user_id": user_id,
            "submission_timestamp": {"$exists": False},
            "deletion_timestamp": {"$exists": False}
        }
        draft_list = get_item(db, query)
        # pp.pprint(draft_list)
        return draft_list

    def get_one_draft(self, user_id, draft_ObjectId):
        """
        Gets one process draft details that is created by the user based on ObjectId to be displayed on the front end.
        """
        db = self.process_draft_col
        query = {
            "_id": ObjectId(draft_ObjectId),
            "user_id": user_id,
            "submission_timestamp": {"$exists": False},
            "deletion_timestamp": {"$exists": False}
        }
        draft_list = get_item(db, query)
        draft = draft_list[0]  # should only have one
        return draft

    def update_tag_orphan(self, process_details):
        """
        Loop through process details to update tag_orphan of process components.
        """
        content_layer = process_details["task"]["content_layer"]
        parent_layer = "task"
        process_details[content_layer], process_details[parent_layer] = self.update_tag_orphan_based_on_id(
            content_layer, process_details[content_layer], [process_details[parent_layer]])
        max_layer = int(content_layer[len("objective_layer_"):])
        for i in range(max_layer):
            parent_layer = f"objective_layer_{i+1}"
            if i == 0:
                content_layer = "step"
            else:
                content_layer = f"objective_layer_{i}"
            process_details[content_layer], process_details[parent_layer] = self.update_tag_orphan_based_on_id(
                content_layer, process_details[content_layer], process_details[parent_layer])
        return process_details

    def update_tag_orphan_based_on_id(self, content_layer, child_layer_item_list, parent_layer_item_list):
        """
        Update tag_orphan from True to False if parent is found.

        Loop the parent list, if child ObjectId is found in the list, then change tag to False.
        """
        for parent_item in parent_layer_item_list:
            if parent_item["content_layer"] == content_layer:
                for child_item in child_layer_item_list:
                    if str(child_item["_id"]) in parent_item["content_ObjectId"]:
                        child_item["tag_orphan"] = False
        return child_layer_item_list, parent_layer_item_list

    def replace_id_with_content(self, objective):
        """
        Replaces content object ids with item queried from content db col.

        In the dict of an objective, "content_ObjectId" is replaced with "content".
        content_ObjectId = [object id 1, object id 2, ...]
        content_dict_list = [(content detail 1 as stored in the db), ...]
        """
        objective["content"] = list()
        if objective["content_layer"] == "step":
            db_col = self.step_col
        else:
            db_col = self.objective_content_col
        for item_id in objective["content_ObjectId"]:
            query = {
                "_id": ObjectId(item_id),
                "is_deleted": {"$ne": True}
            }
            content = get_item(db_col, query)[0]
            content["sentence"] = self.translate_var(content["var"])
            objective["content"].append(content)
        objective.pop("content_ObjectId")
        return objective

    def get_step_ObjectIds_in_task(self, task_ObjectId):
        """
        Gets all steps of one task.

        From task, iterate getting details of content_ObjectId from process db until step layer is reached.
        steps = [as stored in the step_col]
        """
        query = {
            "_id": ObjectId(task_ObjectId)
        }
        task = get_item(self.task_objective_col, query)[0]  # only one return
        objectives = [  # there is at least one middle layer of objective
            get_item(self.objective_content_col, {"_id": ObjectId(content_ObjectId)})[0]
            for content_ObjectId in task["content_ObjectId"]
        ]
        step_ObjectIds = list()  # initialize
        for objective in objectives:  # iterate until step layer is reached
            if objective["content_layer"] == "step":
                step_ObjectIds = step_ObjectIds + objective["content_ObjectId"]
            else:
                objectives.append(  # keep appending the subsequent middle layers to the end of objectives list loop
                    get_item(self.objective_content_col, {"_id": ObjectId(content_ObjectId)})[0]
                    for content_ObjectId in objective["content_ObjectId"]
                )
        return step_ObjectIds

    def get_step_detail(self, db_col, detail_ObjectId_list):
        """
        Gets conditions of each step item in terms of variable lists based on object ids.

        Step details are conditions, param, exec and state, as stored in the db.
        """
        for detail_ObjectId in detail_ObjectId_list:
            print(get_item(db_col, {
                "_id": ObjectId(detail_ObjectId),
                "is_deleted": {"$ne": True}
            }))
        step_detail_list = [
            get_item(db_col, {
                "_id": ObjectId(detail_ObjectId),
                "is_deleted": {"$ne": True}
            })[0]  # only one item returned
            for detail_ObjectId in detail_ObjectId_list
        ]
        return step_detail_list

    def get_condition_details_id(self, condition_dict):
        """
        Gets details of step conditions in ObjectId.

        Iterate step conditions, use ObjectId of the condition to get condition doc as in db.
        The condition doc contains details (steps and states) in ObjectId.
        """
        temp_dict = dict()
        for c_name_id, c_id_list in condition_dict.items():
            suffix_to_skip = len(c_name_id) - len("_ObjectId")
            c_name = c_name_id[:suffix_to_skip]
            if c_name in list(self.condition_db_dict.keys()):
                temp_dict[c_name] = [  # get list of dicts of ObjectIds of condition detail (state/step)
                    get_item(
                        self.condition_db_dict[c_name],  # condition col
                        {
                            "_id": ObjectId(c_id),
                            "is_deleted": {"$ne": True}
                        }
                    )[0]  # only one item returned
                    for c_id in c_id_list
                ]
        condition_dict = {**condition_dict, **temp_dict}
        return condition_dict

    def replace_id_with_pre_state_set(self, condition_dict):
        """
        Replaces "hasPrerequisiteState" ObjectIds with condition doc as in db col.

        The original condition dict has the list of ObjectIds of "hasPrerequisiteState" condition.
        Replace those ids with details that can be found from the database.
        """
        for c_name, c in condition_dict.items():
            if c_name in list(self.condition_db_dict.keys()):
                # if the condition needs pre-state set as details
                if any(True for c_set in c for var_key in c_set if var_key in ["hasPrerequisiteState_ObjectId"]):
                    for idx, c_set in enumerate(condition_dict[c_name]):
                        c_set["hasPrerequisiteState"] = [
                            get_item(
                                self.condition_db_dict["hasPrerequisiteState"], {"_id": ObjectId(pre_state_id)}
                            )[0]  # only one item returned
                            for pre_state_id in c_set["hasPrerequisiteState_ObjectId"]
                        ]
                        # remove original pre-state details list from condition dict
                        c_set.pop("hasPrerequisiteState_ObjectId")
        return condition_dict

    def replace_id_with_state(self, condition_dict):
        """
        Replaces state ObjectIds with state details of that task.
        """
        suffix_to_skip = len("_ObjectId")
        for c_name, c_id_list in condition_dict.items():
            if c_name in list(self.condition_db_dict.keys()):
                # if the condition has state as details
                state_detail_key_list = [
                    detail_key_id[:(len(detail_key_id) - suffix_to_skip)]  # this will be step_detail_key
                    for detail_key_id in condition_dict[c_name][0]  # from the first element of list
                    if detail_key_id[0:5] == "State"[0:5]
                ]  # example: StateBlocker, StateCorrect, etc. ...
                for idx, c_set in enumerate(condition_dict[c_name]):  # for each set
                    for state_detail_key in state_detail_key_list:  # if [] then this will be skipped
                        c_set[state_detail_key] = [
                            get_item(
                                self.state_exec_col, {"_id": ObjectId(step_id)}
                            )[0]  # only one item returned
                            for step_id in c_set[f"{state_detail_key}_ObjectId"]
                        ]
                        # remove original pre-state details list from condition dict
                        c_set.pop(f"{state_detail_key}_ObjectId")
        return condition_dict

    def replace_id_with_step(self, condition_dict):
        """
        Replaces step ObjectIds with step details of that task.
        """
        suffix_to_skip = len("_ObjectId")
        for c_name, c_id_list in condition_dict.items():
            if c_name in list(self.condition_db_dict.keys()):
                # if the condition has step as details
                step_detail_key_list = [
                    detail_key_id[:(len(detail_key_id) - suffix_to_skip)]  # this will be step_detail_key
                    for detail_key_id in condition_dict[c_name][0]  # from the first element of list
                    if detail_key_id[0:4] == "Step"[0:4]
                ]  # example: StepBlocker, StepPrerequisite, etc. ...
                for idx, c_set in enumerate(condition_dict[c_name]):  # for each set
                    for step_detail_key in step_detail_key_list:  # if [] then this will be skipped
                        c_set[step_detail_key] = [
                            get_item(
                                self.step_col, {"_id": ObjectId(step_id)}
                            )[0]  # only one item returned
                            for step_id in c_set[f"{step_detail_key}_ObjectId"]
                        ]
                        for step in c_set[step_detail_key]:
                            step["sentence"] = self.translate_var(step["var"])
                        # remove original pre-state details list from condition dict
                        c_set.pop(f"{step_detail_key}_ObjectId")
        return condition_dict


class TaskDisplay(ProcessDisplay):
    """
        Get and package contents of task to be displayed on UI.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_process_details(self, task_ObjectId):
        """
        Get process components and details of components and package it into process_details dict format.

        Create dictionary.
        Get the list of components of all layers and rearrange them in dict according to their layers.
        Iterate through each step and get step details.
        Iterate through each condition and get the sets of condition.

        :param task_ObjectId:
        :return:
        process_details: as documented in data schema
        """
        process_details = {
            "condition": list(),
            "parameter": list(),
            "state": list(),
            "isBlockedByStep": list(),
            "hasPrerequisiteStep": list(),
            "isBlockedByState": list(),
            "hasPrerequisiteState": list(),
            "isAchievedBy": list(),
            "isFailedByState": list(),
        }
        component_list = self.get_process_components(task_ObjectId)
        layer_list = [
            component["layer"]
            for component in component_list
        ]
        layer_list = unique(layer_list)
        for layer in layer_list:
            process_details[layer] = [
                component
                for component in component_list
                if component["layer"] == layer
            ]
        process_details["task"] = process_details["task"][0]    # only one task
        process_details = self.update_tag_orphan(process_details)   # find parents and update tag_orphan
        process_details["task"] = process_details["task"][0]
        for step in process_details["step"]:
            process_details["condition"] += self.get_step_detail(self.step_cond_col, [step["step_cond_ObjectId"]])
            process_details["parameter"] += self.get_step_detail(self.step_param_col, step["step_param_ObjectId"])
            # step_state = self.get_step_detail(self.step_state_col, [step["step_state_ObjectId"]])[0]
            # process_details["state"] += self.get_step_detail(self.state_exec_col, step_state["state_exec_ObjectId"])
            # # add state_exec_ObjectId to step
            # step["state_exec_ObjectId"] = step_state["state_exec_ObjectId"]
            process_details["state"] += self.get_step_detail(self.state_exec_col, [step["state_exec_ObjectId"]])
        for condition in process_details["condition"]:
            for condition_id in condition["isBlockedByStep_ObjectId"]:
                process_details["isBlockedByStep"] += get_item(
                    self.condition_db_dict["isBlockedByStep"], {
                        "_id": ObjectId(condition_id)
                    }
                )
            for condition_id in condition["hasPrerequisiteStep_ObjectId"]:
                process_details["hasPrerequisiteStep"] += get_item(
                    self.condition_db_dict["hasPrerequisiteStep"], {
                        "_id": ObjectId(condition_id)
                    }
                )
            for condition_id in condition["isBlockedByState_ObjectId"]:
                process_details["isBlockedByState"] += get_item(
                    self.condition_db_dict["isBlockedByState"], {
                        "_id": ObjectId(condition_id)
                    }
                )
            for condition_id in condition["hasPrerequisiteState_ObjectId"]:
                process_details["hasPrerequisiteState"] += get_item(
                    self.condition_db_dict["hasPrerequisiteState"], {
                        "_id": ObjectId(condition_id)
                    }
                )
            for condition_id in condition["isAchievedBy_ObjectId"]:
                process_details["isAchievedBy"] += get_item(
                    self.condition_db_dict["isAchievedBy"], {
                        "_id": ObjectId(condition_id)
                    }
                )
            for condition_id in condition["isFailedByState_ObjectId"]:
                process_details["isFailedByState"] += get_item(
                    self.condition_db_dict["isFailedByState"], {
                        "_id": ObjectId(condition_id)
                    }
                )
        return process_details

    def get_process_components(self, task_ObjectId):
        """
        Get sentence and layer of process components to be displayed in a tree.

        :return:
        component_list: a list of dict of process components
        """
        query = {
            "_id": ObjectId(task_ObjectId),
            "is_deleted": {"$ne": True}
        }
        task = get_item(self.task_objective_col, query)[0]  # only one return
        component_list = [task]
        component_list[0]["_id"] = str(task["_id"])  # front-end can only read string
        component_list[0]["sentence"] = self.translate_var(task["var"])
        for component in component_list:
            if component.get("content_ObjectId", None) is not None:
                for content in component["content_ObjectId"]:
                    query = {
                        "_id": ObjectId(content)
                    }
                    if component["content_layer"] == "step":
                        content_details = get_item(self.step_col, query)[0]
                    else:  # objective layers
                        content_details = get_item(self.objective_content_col, query)[0]
                    content_details["sentence"] = self.translate_var(content_details["var"])
                    content_details["tag_orphan"] = True   # will be updated as False when parent is found
                    component_list.append(
                        content_details
                    )
        return component_list

    def get_all_task_list(self):
        """
        Get all tasks from db collections.

        :return:
        id_sentence_list: a list of tuple of string ObjectId for reference and sentence for display
        """
        query = {
            "is_deleted": {"$ne": True}
        }
        item_list = get_item(self.task_objective_col, query)
        var_list = []
        id_list = []
        for item in item_list:
            var_list.append(item["var"])
            id_list.append(str(item["_id"]))
        id_sentence_list = self.get_id_sentence_tuple_list(id_list, var_list)
        id_sentence_list = list(id_sentence_list)
        return id_sentence_list

    def get_task_list(self, task_var, task_objective_ObjectId=None):
        """
        Gets a list of items with same variable.

        :return:
        item_list = [item1, item2, ...] with same var
        """
        query = {
            "var": task_var,
            "is_deleted": {"$ne": True}
        }
        if task_objective_ObjectId is not None:
            query["_id"] = ObjectId(task_objective_ObjectId)
        item_list = get_item(self.task_objective_col, query)
        return item_list

    def get_task_details(self, task_ObjectId):
        """
        Gets details of one step item.

        :param task_ObjectId: string of _id
        :return:
        task: a dict as stored in the db with a list of content_dict(s) that are as stored in the db.
        """
        query = {
            "_id": ObjectId(task_ObjectId),
            "is_deleted": {"$ne": True}
        }
        task = get_item(self.task_objective_col, query)[0]  # only one return
        task["sentence"] = self.translate_var(task["var"])
        task = self.replace_id_with_content(task)
        return task


class ObjectiveDisplay(ProcessDisplay):
    """
        Get and package contents of objective to be displayed on UI.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_objective_list(self, objective_var, objective_content_ObjectId=None):
        """
        Gets list of items with same variable.

        :return:
        item_list: list of step doc with same var
        """
        query = {
            "var": objective_var,
            "is_deleted": {"$ne": True}
        }
        if objective_content_ObjectId is not None:
            query["_id"] = ObjectId(objective_content_ObjectId)
        item_list = get_item(self.objective_content_col, query)
        return item_list

    def get_objective_details(self, objective_ObjectId):
        """
        Gets details of one objective item.

        :return:
        objective: dict as stored in the db with a list of content_dict(s) that are as stored in the db
        """
        query = {
            "_id": ObjectId(objective_ObjectId),
            "is_deleted": {"$ne": True}
        }
        objective = get_item(self.objective_content_col, query)[0]  # only one return
        objective["sentence"] = self.translate_var(objective["var"])
        objective = self.replace_id_with_content(objective)
        return objective


class StepDisplay(ProcessDisplay):
    """
        Get and package contents of step to be displayed on UI.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_step_list(self, step_var, step_ObjectId=None):
        """
        Gets list of items with same variable.

        :return:
        item_list: list of step doc with same var
        """
        query = {
            "var": step_var,
            "is_deleted": {"$ne": True}
        }
        if step_ObjectId is not None:
            query["_id"] = ObjectId(step_ObjectId)
        item_list = get_item(self.step_col, query)
        return item_list

    def get_step_details(self, step_ObjectId):
        """
        Gets details of one step item.

        :return:
        step: dict as stored in the db with a lists of step details(s) that are as stored in the db
        """
        query = {
            "_id": ObjectId(step_ObjectId),
            "is_deleted": {"$ne": True}
        }
        step = get_item(self.step_col, query)[0]  # only one return
        step["sentence"] = self.translate_var(step["var"])
        # details = {}
        # ObjectId input to get_step_detail must be an array
        step["step_condition"] = self.get_step_detail(self.step_cond_col, [step["step_cond_ObjectId"]])[0]
        step["step_condition"] = self.get_condition_details_id(step["step_condition"])
        step["step_condition"] = self.replace_id_with_pre_state_set(step["step_condition"])
        step["step_condition"] = self.replace_id_with_step(step["step_condition"])
        step["step_condition"] = self.replace_id_with_state(step["step_condition"])
        step["step_param"] = self.get_step_detail(self.step_param_col, step["step_param_ObjectId"])
        step_state = self.get_step_detail(self.step_state_col, [step["step_state_ObjectId"]])[0]
        step["state_exec"] = self.get_step_detail(self.state_exec_col, step_state["state_exec_ObjectId"])
        return step


class StateDisplay(ProcessDisplay):
    """
        Get and package contents of state to be displayed on UI.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_state_list(self, state_var, state_exec_ObjectId=None):
        """
        Gets list of items with same variable.

        item_list: a list of state doc with same var
        """
        query = {
            "var": state_var,
            "is_deleted": {"$ne": True}
        }
        if state_exec_ObjectId is not None:
            query["_id"] = ObjectId(state_exec_ObjectId)
        item_list = get_item(self.state_exec_col, query)
        return item_list

    def get_states_in_task(self, task_ObjectId):
        """
        Gets all the states assigned to a task.

        :return:
        state_exec_list: dict of doc as stored in state_exec_col
        """
        step_ObjectIds = self.get_step_ObjectIds_in_task(task_ObjectId)
        steps = [  # get steps based on object id
            get_item(self.step_col, {
                "_id": ObjectId(step_ObjectId),
                "is_deleted": {"$ne": True}
            })[0]
            for step_ObjectId in step_ObjectIds
        ]
        state_exec_list = list()
        for step in steps:
            step_state = self.get_step_detail(step["step_state_ObjectId"])[0]
            state_exec_list.append(
                get_item(self.state_exec_col, {
                    "_id": ObjectId(state_exec_ObjectId),
                    "is_deleted": {"$ne": True}
                })[0]
                for state_exec_ObjectId in step_state["state_exec_ObjectId"]
            )
        return state_exec_list

    def get_unique_state_class(self, state_type):
        """
        Gets unique resource type (camera, actuator, ...) according to the resource class input as set.
        """
        db_col = self.state_exec_col
        query = {
            "type": state_type,
            "is_deleted": {"$ne": True}
        }
        states = get_item(db_col, query)
        s_class = [
            state["class"]
            for state in states
        ]
        s_class = list(set(s_class))  # set only returns unique item in list
        return s_class



class ResourceDisplay(Visualizer):
    """
        Get and package contents of resource to be displayed on UI.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_all_resource_list(self, resource_class):
        """
        Gets all resource list according to query.
        """
        db = self.db_dict[resource_class]
        if resource_class == "physical":
            query = {
                "is_deleted": {"$ne": True},
            }
        else:
            query = {
                "class": resource_class,
                "is_deleted": {"$ne": True},
            }
        resource_list = get_item(db, query)
        resource_list = self.deduce_status(resource_list)
        return resource_list

    def get_one_resource(self, resource_class, resource_id):
        """
        Gets one resource details based on ObjectId to be displayed on the front end.
        """
        db = self.db_dict[resource_class]
        if resource_class == "physical":
            query = {
                "ID": resource_id,
                "is_deleted": {"$ne": True},
            }
        else:
            query = {
                "ID": resource_id,
                "class": resource_class,
                "is_deleted": {"$ne": True},
            }
        resource_list = get_item(db, query)
        resource_list = self.deduce_status(resource_list)
        resource = resource_list[0]  # should only have one
        return resource

    def get_resource_list(self, resource_class):
        """
        Deprecated.
        Gets resource list to be chosen from select field in forms.
        """
        out_list = []
        db = self.db_dict[resource_class]
        if resource_class == "physical":
            query = {
                "is_deleted": {"$ne": True},
            }
        else:
            query = {
                "class": resource_class,
                "is_deleted": {"$ne": True},
            }
        db_list = get_item(db, query)
        for idx, item in enumerate(db_list):
            value = idx
            label = [item.get("ID"), item.get("_id")]
            out_list.append((str(value), label))
        # pp.pprint(out_list)
        return out_list

    def get_draft(self, user_id, resource_class):
        """
        Get resource draft list based on resource_class.
        :param resource_class:
        :return:
        """
        out_list = []
        db = self.resource_draft_col
        query = {
            "user_id": user_id,
            "class": resource_class,
            "submission_timestamp": {"$exists": False},
            "deletion_timestamp": {"$exists": False}
        }
        out_list = get_item(db, query)
        # pp.pprint(out_list)
        return out_list

    def get_unique_resource_type(self, resource_class):
        """
        Gets unique resource type (camera, actuator, ...) according to the resource class input as set.
        """
        db_col = self.db_dict[resource_class]
        query = {
            "class": resource_class,
            "is_deleted": {"$ne": True}
        }
        resources = get_item(db_col, query)
        r_type = [
            resource["type"]
            for resource in resources
        ]
        r_type = list(set(r_type))  # set only returns unique item in list
        return r_type

    def deduce_status(self, resource_dict_list):
        """
        Overwrites resource status (active and available) if resource is offline.

        :param resource_dict_list: a list of doc in dict as in resource db col
        :return:
        resource_dict_list: modified list of doc in dict as in resource db col
        """
        for resource_dict in resource_dict_list:
            if "online" in resource_dict:
                if not resource_dict["online"]:
                    resource_dict["active"] = False
                    resource_dict["available"] = None
        return resource_dict_list


class OntologyVisualizer():
    """
        Package ontology data into process data structure format for front-end.
    """

    def __init__(self):
        self.condition_list = [
            "isBlockedByStep",
            "hasPrerequisiteStep",
            "isBlockedByState",
            "hasPrerequisiteState",
            "isAchievedBy",
            "isFailedByState",
        ]

    def visualize_ontology(self, onto_data, task_var):
        """
        Packages ontology data into process data structure format for front-end.

        step_state_dict: keys are step sentences; values are lists of state indexes of that step
        """
        process = dict()
        process["step"], step_sentence_index_dict = self.package_empty_step(onto_data["NamedStep"])
        process["state"], state_var_index_dict = self.package_state(onto_data["NamedState"])
        process["condition"] = self.package_empty_step_cond(step_sentence_index_dict)
        step_state_dict = self.package_empty_step_state(step_sentence_index_dict)
        for condition in self.condition_list:
            process[condition] = self.package_condition(
                onto_data[condition], condition, step_sentence_index_dict, state_var_index_dict)
            process["condition"] = self.package_step_cond(
                process["condition"], process[condition], condition)
            step_state_dict = self.package_step_state(step_state_dict, process[condition])
        process["step"] = self.package_step(process["step"], step_state_dict, process["condition"])
        process["parameter"] = list()
        process["objective"], process["step"] = self.package_objective(
            onto_data["NamedObjectiveLayer"], process["step"])
        objectives = process.pop("objective")
        process["task"], process["step"] = self.package_task(
            onto_data["NamedObjectiveLayer"], task_var, process["step"], objectives)
        process = {**process, **objectives}
        return process

    def package_empty_step(self, post):
        """
        Packages the post in the same way as would have gotten from the front end

        All variables in post are in sentence format.
        Get unique elements of the list as steps.
        Iterate through the list.
        Package the sentence and location_id into a dict for each unique element.
        Start the details with a default step -1 block.
        Add the details into the dict.
        Zip the sentence list and index list into sentence_index_dict.
        """
        steps = post["NamedStep"]
        unique_steps = unique(steps)
        details = [
            {
                "sentence": "-1",
                "layer": "step",
                "location_id": [],
                "index": 0,
                "state_exec_index":[0],
                "step_cond_index": 0,
                "step_param_index": [],
                "tag_orphan": True  # this tag will be updated when parent is found
            }
        ]
        for idx, unique_step in enumerate(unique_steps):
            detail_dict = {
                "sentence": str(unique_step),
                "layer": "step",
                "tag_orphan": True,  # this tag will be updated when parent is found
                "location_id": [
                    post["isAtLocation"][idx]
                    for idx, step in enumerate(post["NamedStep"])
                    if unique_step == step
                ],
                "index": idx + 1
            }
            details.append(detail_dict)
        sentence_index_dict = {
            detail["sentence"]: detail["index"]
            for detail in details
        }
        return details, sentence_index_dict

    def package_state(self, post):
        """
        Packages the post in the same way as would have gotten from the front end.

        All variables in post are in sentence format.
        Zip state, superclass and type as a tuple and put them into a list.
        Get unique elements of the list as unique_state_detail.
        Iterate through the list.
        Start the details with a default step -1 block.
        Get the details for that unique tuple.
        Zip the var list and index list into var_index_dict.
        """
        state_detail = list(zip(post["NamedState"], post["Superclass"], post["Type"]))
        unique_state_detail = unique(state_detail)
        details = [
            {
                "var": "-1",
                "class": "default",
                "type": "task",
                "exec": [],
                "index": 0
            }
        ]
        for idx, unique_tuple in enumerate(unique_state_detail):
            if unique_tuple[1] != "NamedState":  # not the state class
                detail_dict = {
                    "var": unique_tuple[0],
                    "class": unique_tuple[1],
                    "type": unique_tuple[2],
                    "exec": [
                        {
                            "class": post["PhyResourceClass"][idx],
                            "type": post["PhyResource"][idx],
                            "software_id": post["CyberResource"][idx]
                        }
                        for idx, tup in enumerate(state_detail)
                        if unique_tuple == tup  # if tup is still the same as the unique tup in the loop
                    ],
                    "index": idx + 1
                }
                details.append(detail_dict)
        var_index_dict = {
            detail["var"]: detail["index"]
            for detail in details
        }
        return details, var_index_dict

    def package_condition(self, post, condition, step_sentence_index_dict, state_var_index_dict):
        """
        Packages the post in the same way as would have gotten from the front end.

        All variables in post are in sentence format and not ObjectId.
        Zip step and condition as a tuple and put them into a list.
        Get unique elements of the list as unique_step_condition.
        Iterate through the list.
        Get the details for that unique tuple.
        Replace "hasPrerequisiteState" with its index.
        """
        step_condition = list(zip(post["NamedStep"], post[condition]))
        unique_step_condition = unique(step_condition)
        temp_details = list()  # keys and values are the same as key of onto data
        post.pop("NamedStep")
        post.pop(condition)
        for unique_pair in unique_step_condition:
            detail_dict = {
                "step": unique_pair[0],
                condition: unique_pair[1]
            }
            for key, val in post.items():
                detail_dict[key] = unique([
                    post[key][idx]
                    for idx, pair in enumerate(step_condition)
                    if unique_pair == pair  # if tup is still the same as the unique tup in the loop
                ])
            temp_details.append(detail_dict)
        details = temp_details.copy()  # keys and values are in the format of process data
        for idx, detail in enumerate(details):
            detail["index"] = int(detail[condition])
            detail.pop(condition)
            if detail.get("hasPrerequisiteState", None) is not None:
                detail["hasPrerequisiteState_index"] = [
                    int(item)
                    for item in detail["hasPrerequisiteState"]
                ]
                detail.pop("hasPrerequisiteState")
            detail = self.replace_condition_step_with_index(detail, step_sentence_index_dict)
            detail = self.replace_condition_state_with_index(detail, state_var_index_dict)
            details[idx] = detail
        return details

    def replace_condition_step_with_index(self, c_set, sentence_index_dict):
        """
        Replaces step with the corresponding index.
        """
        c_set_new = c_set.copy()
        for key, val in c_set.items():
            # if the condition has step as details
            if key[0:4] == "Step"[0:4]:
                step_list = val  # example: StateBlocker, StateCorrect, etc. ...
                c_set_new[f"{key}_index"] = [
                    sentence_index_dict[str(step_sentence)]  # step index
                    for step_sentence in step_list
                ]
                # remove original pre-state details list from condition dict
                c_set_new.pop(key)
        return c_set_new

    def replace_condition_state_with_index(self, c_set, var_index_dict):
        """
        Replaces state with the corresponding index.
        """
        c_set_new = c_set.copy()
        for key, val in c_set.items():
            # if the condition has step as details
            if key[0:4] == "State"[0:4]:
                state_list = val  # example: StateBlocker, StateCorrect, etc. ...
                c_set_new[f"{key}_index"] = [
                    var_index_dict[str(state_var)]  # step index
                    for state_var in state_list
                ]
                # remove original pre-state details list from condition dict
                c_set_new.pop(key)
        return c_set_new

    def package_empty_step_cond(self, step_sentence_index_dict):
        """
        Prepares a list of empty dict for conditions to be added later.
        """
        details = [
            {
                "step": sentence,
                "index": index  # index of step-cond is the same as index of step
            }
            for sentence, index in step_sentence_index_dict.items()
        ]
        return details

    def package_empty_step_state(self, step_sentence_index_dict):
        """
        Prepares a dict of empty list for states to be added later.
        """
        details = {
            sentence: list()  # list of state will be appended later on
            for sentence in step_sentence_index_dict
        }
        return details

    def package_step_cond(self, details, condition_data, condition):
        """
        Add condition indexes for the steps.
        """
        for detail in details:  # for every step-cond dict
            detail[f"{condition}_index"] = [
                data["index"]
                for data in condition_data
                if data["step"] == detail["step"]  # append data to step-cond dict of that step
            ]
        return details

    def package_step_state(self, details, condition_data):
        """
        Add state index to the condition details.
        """
        state_detail_key_list = [
            key for key in condition_data[0]  # from the first element of list
            if key[0:5] == "State"[0:5]
        ]  # example: StateBlocker, StateCorrect, etc. ...
        if len(state_detail_key_list) != 0:
            for c_set in condition_data:  # for each set
                for state_detail_key in state_detail_key_list:
                    details[c_set["step"]] = details[c_set["step"]] + c_set[state_detail_key]
                details[c_set["step"]] = unique(details[c_set["step"]])
        return details

    def package_step(self, details, step_state_dict, condition_data_list):
        """
        Add step index to the condition details.
        """
        for detail in details:  # for every step-cond dict
            if detail["sentence"] != "-1":  # skip default step block
                detail[f"state_exec_index"] = [
                    step_state_dict[step]  # array of state index
                    for step in step_state_dict  # key is step, value is list of states
                    if step == detail["sentence"]  # append data to step-cond dict of that step
                ][0]
                detail[f"step_cond_index"] = [
                    condition_data["index"]  # array of step-cond data
                    for condition_data in condition_data_list
                    if condition_data["step"] == detail["sentence"]  # append data to step-cond dict of that step
                ][0]
                detail[f"step_param_index"] = []
        return details

    def package_objective(self, post, step_details):
        """
        Packages the post in the same way as would have gotten from the front end.

        All variables in post are in sentence format.
        Zip layer and objective as a tuple and put them into a list.
        Get unique elements of the list as unique_layer_objective.
        Iterate through the list.
        For each unique tuple, check the content_layer, for the content of layer 1 is step, while the rest is objective.
        Get the contents for that unique tuple.
        Sort the objectives and their contents based on layer number.
        Replace content sentences with content indexes.
        """
        Layer = [int(layer) for layer in post["Layer"]]
        layer_objective = list(zip(Layer, post["NamedObjective"]))
        unique_layer_objective = unique(layer_objective)
        temp_details = list()  # unsorted objectives (all layers in one list)
        for idx, unique_pair in enumerate(unique_layer_objective):
            detail_dict = {
                "sentence": unique_pair[1],
                "layer": f"objective_layer_{unique_pair[0]}",
                "index": idx,
                "tag_orphan": True,  # this tag will be updated when parent is found
            }
            if unique_pair[0] == 1:
                detail_dict["content_layer"] = "step"
            else:
                detail_dict["content_layer"] = f"objective_layer_{unique_pair[0]-1}"
            detail_dict["content"] = unique([
                post["isAchievedBy"][idx]
                for idx, pair in enumerate(layer_objective)
                if unique_pair == pair  # if tup is still the same as the unique tup in the loop
            ])
            temp_details.append(detail_dict)
        details = dict()  # sort objectives based on layer number into dict of lists of dicts
        max_layer = max(Layer)
        for layer in range(max_layer):
            details[f"objective_layer_{layer+1}"] = [
                objective
                for objective in temp_details
                if objective["layer"] == f"objective_layer_{layer+1}"  # if that dict belongs to that layer num
            ]
        details, step_details = self.replace_content_step_with_index(details, step_details)
        details, details = self.replace_content_objective_with_index(details, details)
        return details, step_details

    def package_task(self, post, task_var, step_details, objective_details):
        """
        Packages the post in the same way as would have gotten from the front end.
        
        Replace content sentences with content indexes.
        """
        max_layer = max(post["Layer"])
        details = {
            "sentence": task_var,
            "layer": "task",
            "content_layer": f"objective_layer_{max_layer}",
            "content": [  # objectives of the max layer
                objective_sentence
                for idx, objective_sentence in enumerate(post["NamedObjective"])
                if post["Layer"][idx] == max_layer
            ],
            "index": 0
        }
        temp = {"task": [details]}  # format data to use function
        temp, step_details = self.replace_content_step_with_index(temp, step_details)
        temp, objective_details = self.replace_content_objective_with_index(temp, objective_details)
        details = temp["task"][0]
        return details, step_details

    def replace_content_step_with_index(self, details, step_details):
        """
        Replaces content that belongs to objective with the matching index of the objective sentence.

        Loop through details dict to get the list of objective component.
        For each objective component, if the content layer is not step, then it is objective_layer_N.
        Get list of content_index using list comprehension.
        For each objective sentence, and for each objective component of the content_layer, if the objective sentence
        is the same as the sentence in the objective component, append the index of the objective component into the
        list.
        Update orphan tag for children.

        :param details: objective dict
        :param step_details: step dict
        :return:
        details = objective dict with content_index and without content
        step_details = step dict with updated tag_orphan
        """
        for layer, objective_list in details.items():
            for objective in objective_list:
                if objective["content_layer"] == "step":
                    objective["content_index"] = [
                        step["index"]
                        for content in objective["content"]
                        for step in step_details
                        if content == step["sentence"]
                    ]
                    for step in step_details:
                        if step["sentence"] in objective["content"]:
                            step["tag_orphan"] = False
                    objective.pop("content")
        return details, step_details

    def replace_content_objective_with_index(self, details, objective_details):
        """
        Replaces content that belongs to objective with the matching index of the objective sentence.

        Loop through details dict to get the list of objective component.
        For each objective component, if the content layer is not step, then it is objective_layer_N.
        Get list of content_index using list comprehension.
        For each objective sentence, and for each objective component of the content_layer, if the objective sentence
        is the same as the sentence in the objective component, append the index of the objective component into the
        list.
        Update orphan tag for children.

        :param details: task or objective dict
        :param objective_details: objective dict
        :return:
        details = task or objective dict with content_index and without content
        objective_details = objective dict with updated tag_orphan
        """
        for layer, objective_list in details.items():
            for objective in objective_list:
                if objective["content_layer"] != "step":
                    content_layer = objective['content_layer']
                    objective["content_index"] = [
                        content_objective["index"]
                        for content in objective["content"]
                        for content_objective in objective_details[content_layer]
                        if content == content_objective["sentence"]
                    ]
                    for content_objective in objective_details[content_layer]:
                        if content_objective["sentence"] in objective["content"]:
                            content_objective["tag_orphan"] = False
                    objective.pop("content")
        return details, objective_details


class ProfileVisualizer(Visualizer):
    """
        Get and package profile to be displayed on UI.
    """
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_profile(self, user_id):
        """
              Retrieves details of the user.
        """
        found_user = []
        for item in self.profile_col.find({'user_id': user_id}):
            found_user.append(item)
        if len(found_user) == 0:
            return False
        else:
            details = found_user[0]  # should only have one
            details.pop("_id")
        return details
