"""
Program title: iCPS
Project title: CPS Builder
This script confirms the status of resources and maps them to steps as executors.
Written by Wong Pooi Mun.
"""

from CPSBuilder.utils.db import *

from collections import Counter
import requests

import logging
logger = logging.getLogger(__name__)


class ExecutorMapper:
    """

        Double check status of resources and map suitable resources as executors for processes in job.

    """

    def __init__(self, client, test=False, demo=False):
        if test:
            self.resource_db = client["test-resource"]
            self.job_db = client["test-job"]
        else:
            self.resource_db = client["resource"]
            self.job_db = client["job"]
        self.physical_col = self.resource_db["physical"]
        self.cyber_col = self.resource_db["cyber"]
        self.location_col = self.resource_db["location"]
        self.broadcast_col = self.job_db["broadcast"]

    def package_step_exec_in_one_step(self, step):
        """
        Package list of executor details that can perform the step.

        For each step dict, create empty exec list.
        Iterate through state list of a step, and map possible executors to the step.
        Fill in details needed as exec dict for job details.
        List possible_executor_list as both preferred_exec and alternative_exec for selection choice in form.
        When exec list is formed, remove state in step dict.
        If no resource is available for that state, possible_executor_list becomes False.
        If no resource is available for that step, then all possible_executor_list is False.

        :param step: one step from process details packed by job visualizer and obtained from route
        :return:
        step: step details with added exec list
        """
        step["exec"] = list()
        for state_exec in step["state"]:
            possible_executor_list = self.map_exec_to_step(state_exec, step["location_id"])     # selected from ui.
            exec_dict = {
                "index": state_exec["index"],
                "same_as_step_index": None,
                "same_as_exec_index": None,
                "state": {
                    "class": state_exec["class"],
                    "type": state_exec["type"]
                },
                "preferred_exec": possible_executor_list,
                "alternative_exec": possible_executor_list
            }
            step["exec"].append(exec_dict)
        step.pop("state")
        if all(exec_dict["preferred_exec"] is False for exec_dict in step["exec"]):
            print(f"There is no available executor for this step {step['var']} (index {step['index']}!")
        return step

    def map_exec_to_step(self, state_exec, location_id):
        """
        Map suitable resources as a list of executor details that will perform the step.

        Create empty possible_exec_list.
        For each state_exec dict, get exec requirements from exec dict.
        Iterate through the requirements, to filter the list of physical resources in db based on physical and
        cyber requirements.
        The list obtained based on physical requirements is placed in a temp list.
        Add and package details of resources (as needed in the job-task) that are in both temp_list and
        software["physical_resource_id"] into possible_exec_list.

        :param state_exec: one dict in process_details["step"]["state"]
        :param location_id: as listed in the elements of process_details["step"]
        :return:
        possible_exec_list: list of exec dict for one state_exec in a step
        """
        possible_exec_list = list()     # initialize
        requirements_options = state_exec["exec"]
        # print(requirements_options)
        for option_id_dict in requirements_options:     # for each dict in list
            query = {
                "ID": option_id_dict["physical_resource_id"],
                "available": True,
                "online": True,
                "location_id": location_id,
                "is_deleted": {"$ne": True}
            }
            physical_option_list = get_item(self.physical_col, query)
            if len(physical_option_list) > 0:
                physical_option = physical_option_list[0]   # Should only have one
            else:
                physical_option = None
            query = {
                "ID": option_id_dict["cyber_resource_id"],
                "class": "software",
                "is_deleted": {"$ne": True}
            }
            cyber_option = get_item(self.cyber_col, query)[0]  # should only have one item
            print(physical_option)
            if len(cyber_option["physical_resource_id"]) != 0 and physical_option is not None:
                if physical_option["ID"] in cyber_option["physical_resource_id"]:   # double check
                    temp_list = [   # filter resource list based on physical requirement
                        {   # package filtered list with info needed in job-task col
                            "physical_resource_id": physical_option["ID"],
                            "physical_resource_class": physical_option["class"],
                            "physical_resource_type": physical_option["type"],
                            "physical_resource_name": physical_option["name"],
                            "cyber_resource_id": cyber_option["ID"],
                            "cyber_resource_class": cyber_option["class"],
                            "cyber_resource_type": cyber_option["type"],
                            "cyber_resource_name": cyber_option["name"]
                        }
                    ]
                    possible_exec_list += temp_list
        if len(possible_exec_list) == 0:
            # possible_exec_list = False
            logger.error(f"No unassigned resource available to detect state {state_exec['class']}!")
        return possible_exec_list

    def check_online_resource(self):
        """
        Check if resource with online status stays online.

        Get all doc of physical resource in db col.
        Contact each resource to check connectivity.
        If resource can be contacted, then update resource's online status in db col and hold onto
        all broadcast items with resource as preferred_exec.
        If resource cannot be contacted, then update resource's online status in db col and give up on
        all broadcast items with resource as preferred_exec.
        """
        query = {
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.physical_col, query)
        for doc in doc_list:
            connected = self.contact_resource(doc["ID"], doc["address"]["ip"], doc["address"]["port"])
            query = {
                "_id": doc["_id"]
            }
            if connected:
                new_info = {
                    "online": True
                }
            else:   # cannot be contacted
                new_info = {
                    "online": False,
                    "available": None
                }
                self.hold_onto_broadcast(doc["ID"])
            self.physical_col.update_one(query, {"$set": new_info})

    def count_total_available_resource(self):
        """
        Count total number of available and online resource of the same class and type.

        Get all doc of physical resource in the db col.
        Extract the class and type of each doc and package them into tuples.
        Count the total number of appearance of each tup in the list.
        Return the count in the dict with the tup.

        :return:
        total_resource_dict: dict of resource tup (class, type) and count number
        """
        query = {
            "available": True,
            "online": True,
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.physical_col, query)
        total_resource_tup_list = [
            (doc["class"], doc["type"])
            for doc in doc_list
        ]
        total_resource_dict = dict(Counter(total_resource_tup_list))
        return total_resource_dict

    def record_location_content(self):
        """
        Record physical resources in their respective location as location content.

        Get all doc of location in the db col.
        Iterate through the doc to count the total available and online resources in a location and get those resource
        info.
        Update the count and info to the location doc as content and content info.

        :return:
        location_content: dict of resource tup (class, type) and count number
        """
        location_content = dict()
        query = {
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.physical_col, query)
        for doc in doc_list:
            total_resource_dict, info_list = self.count_total_available_resource_in_location(doc["ID"])
            query = {
                "_id": doc["_id"]
            }
            new_info = {
                "content": total_resource_dict,
                "content_info": info_list
            }
            self.location_col.update_one(query, {"$set": new_info})
            location_content = {**location_content, **total_resource_dict}
        return location_content

    def contact_resource(self, cyber_twin_id, cyber_twin_ip, cyber_twin_port):
        """
        Contact resource to check connectivity.

        :param cyber_twin_id: ID
        :param cyber_twin_ip: ip address for connection
        :param cyber_twin_port: port number for connection
        :return:
        True if connection is successful.
        False if connection has failed.
        """
        try:
            requests.get(
                f"http://{cyber_twin_ip}:{cyber_twin_port}/api/cyber-twin/test-connection")
            logger.info(
                f"Detected connection for {cyber_twin_id} at {cyber_twin_ip}:{cyber_twin_port}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(
                f"No connection for {cyber_twin_id} at {cyber_twin_ip}:{cyber_twin_port}")
            return False

    def give_up_on_broadcast(self, cyber_twin_id):
        """
        Give up on all broadcast items with the resource as preferred_exec.

        :param cyber_twin_id: ID
        :return:
        """
        query = {
            'preferred_exec.ID': cyber_twin_id,
            'is_deleted': {'$ne': True}
        }
        self.broadcast_col.update_many(query, {'$set': {'given_up': True}})
        logger.info(f"{cyber_twin_id} has given up on all broadcast items")

    def hold_onto_broadcast(self, cyber_twin_id):
        """
        Give up on all broadcast items with the resource as preferred_exec.

        :param cyber_twin_id: ID
        :return:
        """
        query = {
            'preferred_exec.ID': cyber_twin_id,
            'is_deleted': {'$ne': True}
        }
        self.broadcast_col.update_many(query, {'$set': {'given_up': False}})
        logger.info(f"{cyber_twin_id} is holding onto all broadcast items")

    def count_total_available_resource_in_location(self, location_id):
        """
        Count the number of available resource of the same class and type in a location.

        Get all doc of physical resource in the db col.
        Extract the class and type of each doc and package them into tuples.
        Count the total number of appearance of each tup in the list.
        Return the count in the dict with the tup and the doc list of the query.

        :param location_id: as listed in the elements of process_details["step"]
        :return:
        total_resource_dict: dict of resource tup (class, type) and count number
        doc_list: list of available and online resources in the location
        """
        query = {
            "available": True,
            "online": True,
            "location_id": location_id,
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.physical_col, query)
        total_resource_tup_list = [
            (doc["class"], doc["type"])
            for doc in doc_list
        ]
        total_resource_dict = dict(Counter(total_resource_tup_list))
        return total_resource_dict, doc_list





