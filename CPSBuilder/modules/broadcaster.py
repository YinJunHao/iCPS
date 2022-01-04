from CPSBuilder.utils.db import *

from datetime import datetime
from flask import Response
import requests
import time

import logging

logger = logging.getLogger(__name__)


class Broadcaster:
    """
        Broadcast step that can be executed to the cyber twins and watch over their competition for the step.
    """

    def __init__(self, client, test=False, demo=False):
        if test:
            self.job_db = client["test-job"]
            self.scoreboard_db = client["test-scoreboard"]
        else:
            self.job_db = client["job"]
            self.scoreboard_db = client["scoreboard"]
        self.job_task_col = self.job_db["job-task"]
        self.broadcast_col = self.job_db["broadcast"]
        self.broadcast_buffer_col = self.job_db["broadcast-buffer"]

    def broadcast_step(self):
        """
        Broadcast step that can be executed at that moment.
        """
        task_ObjectIds = self.get_incomplete_task_ids()
        task_step_dict_list = self.get_next_step_from_buffer(task_ObjectIds)
        posts = list()
        for task_step_dict in task_step_dict_list:
            posts += self.gather_step_details(task_step_dict)
        self.broadcast_col.insert_many(posts)

    def cancel_step(self):
        """
        Cancel step from broadcast that cannot be executed anymore at that moment.
        """
        task_ObjectIds = self.get_incomplete_task_ids()
        task_step_dict_list = self.get_removed_step_from_buffer(task_ObjectIds)
        task_step_resource_dict_list = self.remove_step_from_broadcast(task_step_dict_list)

    def announce_winner(self):
        """
        Announce winner of the competition for items in broadcast.
        """
        col_name_list = self.scoreboard_db.collection_names()
        for col_name in col_name_list:
            words = col_name.split("-")
            task_ObjectId = words[0]
            step_index = int(words[1])
            exec_index = int(words[2])
            resource_score_dict_list = self.collect_scoreboard_results(col_name)
            self.drop_scoreboard_for_item(task_ObjectId, step_index, exec_index)
            results_details = self.pick_scoreboard_winner(
                task_ObjectId, step_index, exec_index, resource_score_dict_list)
            self.update_winner_in_broadcast(task_ObjectId, step_index, exec_index, results_details)

    def get_incomplete_task_ids(self):
        """
        Get a list of ObjectId of incomplete tasks from db col.

        :return:
        task_ObjectIds: a list of ObjectId of incomplete tasks
        """
        query = {
            "status": "pending"
        }
        doc_list = get_item(self.job_task_col, query)
        task_ObjectIds = [
            str(doc["_id"])
            for doc in doc_list
        ]
        return task_ObjectIds

    def get_next_step_from_buffer(self, task_ObjectIds):
        """
        Get non-empty step_list from broadcast buffer for each task and move it to review_list.

        :param task_ObjectIds:  a list of ObjectId of incomplete tasks
        :return:
        task_step_dict_list: a list of dict that contains task_ObjectId and step_list as from the buffer
        """
        task_step_dict_list = list()
        for task_ObjectId in task_ObjectIds:
            query = {
                "task_ObjectId": task_ObjectId,
                "step_list": {"$ne": []}  # only find doc that's not empty
            }
            doc = get_item(self.broadcast_buffer_col, query)[0]  # should only have one item
            task_step_dict = {
                "task_ObjectId": task_ObjectId,
                "step_list": doc["step_list"]
            }
            task_step_dict_list.append(task_step_dict)
            # move step_list to review_list
            query = {
                "_id": doc["_id"]
            }
            new_info = {
                "step_list": [],
                "review_list": doc["step_list"]
            }
            self.broadcast_buffer_col.update_one(query, {"$set": new_info})
        return task_step_dict_list

    def gather_step_details(self, task_step_dict):
        """
        Gather step details from task and package the details into format to be broadcast.

        Get task details of the task ObjectId.
        Iterate through the step_list of that task.
        For each step, first, get the general details of the step, then iterate through the list of exec needed
        for the step. Append the general details of the step to the details of exec.
        After the iterations, add the obtained list to the step_details_list until the for loop is complete.

        :param task_step_dict: dict that contains task_ObjectId and step_list as from the buffer
        :return:
        step_details_list: a list of details of steps that can be executed at that moment
        """
        step_details_list = list()
        query = {
            "_id": ObjectId(task_step_dict["task_ObjectId"])
        }
        task_details = get_item(self.job_task_col, query)[0]  # should only have one item
        for step_index in task_step_dict["step_list"]:
            step_details = {
                "task_ObjectId": task_step_dict["task_ObjectId"],
                "job_id": task_details["job_id"],
                "step_index": step_index,
                "step_var": task_details["step"][int(step_index)]["var"],
                "location_id": task_details["step"][int(step_index)]["location_id"],
                "param": task_details["step"][int(step_index)]["param"],
                "given_up": False,
                "winner": None,
                "broadcast_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
                "is_deleted": False
            }
            temp_list = list()
            exec_list = task_details["step"][int(step_index)]["exec"]
            for exec_dict in exec_list:
                exec_details = {
                    "exec_index": exec_dict["index"],
                    "same_as_step": exec_dict["same_as_step"],
                    "state": exec_dict["state"],
                    "preferred_exec": exec_dict["preferred_exec"],
                    "alternative_exec": exec_dict["alternative_exec"],
                }
                temp_list.append({**step_details, **exec_details})
                # hold competition
                self.create_scoreboard_for_item(task_step_dict["task_ObjectId"], step_index, exec_dict["index"])
            step_details_list += temp_list
        return step_details_list

    def create_scoreboard_for_item(self, task_ObjectId, step_index, exec_index):
        """
        Create a collection for competition participants to report their success rate for the step execution.

        :param task_ObjectId: ObjectId of an incomplete task
        :param step_index: step index in the task
        :param exec_index: exec index in the step
        """
        col_name = f"{task_ObjectId}-{step_index}-{exec_index}"
        post = dict()   # insert empty post to open db col
        self.scoreboard_db[col_name].insert_one(post)

    def get_removed_step_from_buffer(self, task_ObjectIds):
        """
        Get step indexes that are removed from the broadcast buffer step_list.

        Iterate the list of task_ObjectIds.
        Get doc of the task_ObjectId from broadcast buffer col.
        Compare review_list with step_list.
        If step_index in the review_list is not in the step_list, append it to removed_step_list.
        Packaged the list into task_step_dict_list.

        :param task_ObjectIds:  a list of ObjectId of incomplete tasks
        :return:
        task_step_dict_list: a list of dict that contains task_ObjectId and step_list as from the buffer
        """
        task_step_dict_list = list()
        for task_ObjectId in task_ObjectIds:
            query = {
                "task_ObjectId": task_ObjectId,
                "step_list": {"$ne": []},  # only find doc that's not empty
                "review_list": {"$ne": []}  # only find doc that's not empty
            }
            doc = get_item(self.broadcast_buffer_col, query)[0]  # should only have one item
            removed_step_list = [
                step
                for step in doc["review_list"]
                if step not in doc["step_list"]
            ]
            task_step_dict = {
                "task_ObjectId": task_ObjectId,
                "step_list": removed_step_list
            }
            task_step_dict_list.append(task_step_dict)
        return task_step_dict_list

    def remove_step_from_broadcast(self, task_step_dict_list):
        """
        Remove step from broadcast col.

        Iterate the task_step_dict_list and the step_list in each dict.
        Get the list of doc of that task and step_index, meaning one doc for each exec_index.
        Iterate the doc_list.
        If winner has been announced and is_deleted is True, check if the resource has completed that step.
        If resource has completed that step, exec_has_reported will be True.
        If exec_has_reported is True, then continue to the next element in the iteration.
        If exec_has_reported is False, then record the announced winner as resource in task_step_resource_dict_list.
        If winner has not been announced or announced by is_deleted is False, delete the broadcast item and
        drop the scoreboard col.

        :param task_step_dict_list: a list of dict that contains task_ObjectId and step_list as from the buffer
        :return:
        task_step_resource_dict_list: a list of dict that contains task_ObjectId and step_list as from the buffer and
        resource_id.
        """
        task_step_resource_dict_list = list()
        for task_step_dict in task_step_dict_list:
            for step in task_step_dict["step_list"]:
                query = {
                    "task_ObjectId": task_step_dict["task_ObjectId"],
                    "step_index": step,
                }
                doc_list = get_item(self.broadcast_col, query)    # doc of all exec_index
                for doc in doc_list:    # for each exec_index
                    if (doc.get("winner", None) is not None) and (doc.get("is_deleted", False) is True):
                        # winner resource has grabbed the item
                        exec_has_reported = self.check_exec_status_in_step(doc)
                        if exec_has_reported:
                            continue
                        else:   # todo: think of how to inform (or don't need to) resources to cancel step
                            task_step_dict["resource"]["ID"] = doc["winner"]  # add to dict for informing resource later
                            task_step_resource_dict_list.append(task_step_dict)
                    else:
                        # winner resource is not decided yet
                        new_info = {"is_deleted": True}
                        self.broadcast_col.update_one(query, {"$set": new_info})
                        self.drop_scoreboard_for_item(doc["task_ObjectId"], doc["step_index"], doc["exec_index"])
        return task_step_resource_dict_list

    def check_exec_status_in_step(self, details):
        """
        Check in job-task col if resource has reported its states to the process controller.

        :param details: doc as in broadcast
        :return:
        True if resource has reported
        False if resource has not reported
        """
        query = {
            "_id": ObjectId(details["task_ObjectId"]),
        }
        doc = get_item(self.job_task_col, query)[0]    # should only have one item
        step_index = details["step_index"]
        exec_index = details["exec_index"]
        status = doc["step"][step_index]["exec"][exec_index]["status"]
        return status

    def drop_scoreboard_for_item(self, task_ObjectId, step_index, exec_index):
        """
        Create a collection for competition participants to report their success rate for the step execution.

        :param task_ObjectId: ObjectId of an incomplete task
        :param step_index: step index in the task
        :param exec_index: exec index in the step
        """
        col_name = f"{task_ObjectId}-{step_index}-{exec_index}"
        post = dict()  # insert empty post to open db col
        self.scoreboard_db[col_name].insert_one(post)

    def collect_scoreboard_results(self, col_name):
        """
        Get all items in the db col until there are items in it.

        :param col_name: name of db col
        :return:
        doc_list: a list of doc in the db col
        """
        doc_list = list()
        while len(doc_list) == 0:   # keep waiting until there is entry
            doc_list = get_item(self.scoreboard_db[col_name], {})   # all items in scoreboard
            time.sleep(3)
        return doc_list

    def pick_scoreboard_winner(self, task_ObjectId, step_index, exec_index, resource_score_dict_list):
        """
        Select the winner of the scoreboard competition for the broadcast item.

        Create a dict of general details of the broadcast item as results_details.
        Extract all success_rate into a score_list.
        Get the maximum value from the score_list.
        Find resources that has success_rate same as the maximum score.
        Add the resource details as in the scoreboard into the results_details

        :param task_ObjectId: string of task ObjectId
        :param step_index: step index in the task
        :param exec_index: exec index in the step
        :param resource_score_dict_list: a list of dict that contains resources that are participating in the
        competition and success_rate of the resource in executing the item
        :return:
        results_details: a dict of details of broadcast items and winner resource and its success rate
        """
        results_details = {
            "task_ObjectId": task_ObjectId,
            "step_index": step_index,
            "exec_index": exec_index
        }
        score_list = [
            resource_score_dict["success_rate"]
            for resource_score_dict in resource_score_dict_list
        ]
        max_score = max(score_list)
        winner_dict_list = [
            resource_score_dict
            for resource_score_dict in resource_score_dict_list
            if resource_score_dict["success_rate"] == max_score
        ]
        if len(winner_dict_list) > 1:   # there is more than one winner, pick the first one
            results_details = {**results_details, **winner_dict_list[0]}
        return results_details

    def update_winner_in_broadcast(self, task_ObjectId, step_index, exec_index, results_details):
        """
        Update broadcast with the winner resource ID.

        :param task_ObjectId: string of task ObjectId
        :param step_index: step index in the task
        :param exec_index: exec index in the step
        :param results_details: a dict of details of broadcast items and winner resource and its success rate
        """
        query = {
            "task_ObjectId": task_ObjectId,
            "step_index": step_index,
            "exec_index": exec_index
        }
        new_info = {
            "winner": results_details["resource_id"]
        }
        self.broadcast_col.update_one(query, {"$set": new_info})
