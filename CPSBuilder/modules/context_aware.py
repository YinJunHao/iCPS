from CPSBuilder.utils.db import *

from collections import Counter

import logging
logger = logging.getLogger(__name__)


class ContextAware():
    def __init__(self, client, test=False, demo=False):
        # initialize db
        if test:
            self.search_engine_db = client['test-search-engine']
            self.process_db = client['test-process']
            self.condition_db = client['test-condition']
        else:
            self.search_engine_db = client['search-engine']
            self.process_db = client['process']
            self.condition_db = client['condition']
        self.task_token_col = self.search_engine_db['task-token']
        self.objective_token_col = self.search_engine_db['objective-token']
        self.step_token_col = self.search_engine_db['step-token']
        self.task_objective_col = self.process_db['task-objective']
        self.objective_content_col = self.process_db['objective-content']
        self.step_col = self.process_db['step']
        self.step_state_col = self.process_db['step-state']
        self.state_exec_col = self.process_db['state-exec']


class InternalContextAware(ContextAware):
    """

        Allow awareness on the internal context of processes and conditions used in designing a task.

    """
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def suggest_component_using_token(self, token_list, process_layer):
        """
        Suggest components based on tokens in search engine db.

        Get search results which is a list of tuple (component ObjectId, number of hits)
        and return a list of string form ObjectId.
        """
        search_result = self.get_search_engine_results(token_list, process_layer)
        component_ids = [
            tup[0]
            for tup in search_result
        ]
        return component_ids

    def check_conflict(self, target_layer, target_index, process_details):
        """
        Check for conflict in a loop until no new conflict is detected and returns a list of tuple.

        Process details is the dict that is given from the front-end.
        Initiate the loop with the target component that was changed on the front end.
        Use a for loop to enter specific utils to check for conflicts based on the target layer.
        Add the list of detected conflicts from those utils to the existing conflict list.
        This includes the newly detected conflicts to be looped.
        The loop ends when there are no longer new conflicts detected.
        """
        conflict_list = [(target_layer, target_index)]
        for tup in conflict_list:
            if tup[0][:4] == "step"[:4] or tup[0][:4] == "objective"[:4] or tup[0][:4] == "task"[:4]:
                results = self.check_conflict_for_process(tup[0], tup[1], process_details)
                conflict_list += results
            if tup[0] == "step" or tup[0] == "state" or tup[0] == "hasPrerequisiteState":
                results = self.check_conflict_for_step(tup[0], tup[1], process_details)
                conflict_list += results
            if tup[0][:4] != "objective"[:4] or tup[0][:4] != "task"[:4]:
                results = self.check_conflict_for_step(tup[0], tup[1], process_details)
                conflict_list += results
        conflict_list = list(set(conflict_list))
        return conflict_list

    def get_search_engine_results(self, token_list, process_layer):
        """
        Query search engine based on the process layer and returns a list of tuple.

        Select the db col based on process layer.
        Find item in the selected db col using each token in the token list.
        Extract the list of content id from each doc returned from the db col.
        Package the string form of content ObjectId in tuple with the number of hits.
        Sort the tuple in descending order of the number of hits.
        Return the sorted list of tuple.
        """
        if process_layer == "task":
            db_col = self.task_token_col
        elif process_layer == "step":
            db_col = self.step_token_col
        else:   # objective
            db_col = self.objective_token_col
        doc_list_list = [
            get_item(db_col, {"_id": token})   # should either have none or only one
            for token in token_list
        ]
        content_id_list = [
            doc_list[0]["content"]  # must have content for this type of col
            for doc_list in doc_list_list
            if len(doc_list) != 0
        ]
        if len(content_id_list) == 0:
            return []
        else:
            hits = Counter(content_id_list)
            results = [
                (item_id, hit_num)
                for item_id, hit_num in hits.items()
            ]
            results = sorted(results, key=lambda tup: -tup[1])
            return results

    def check_conflict_for_process(self, target_layer, target_index, process_details):
        """
        Check usage of target component in the process and return a list of tuple.

        Process details is the dict that is given from the front-end.
        Deduce the affected layer based on the target layer the component is in, either step, objective or task.
        Loop through the affected layers to see which component has the target as its content.
        If the target is in its content, append the affected component in the conflict list as a tuple.
        Return that list of tuple.
        """
        conflict_list = list()
        affected_layer = [
            layer
            for layer, info in process_details
            if info.get("content_layer") == target_layer    # if layer is task, then return []
        ]
        if type(process_details[affected_layer]) == list:
            for component in process_details[affected_layer]:
                if target_index in component["content_index"]:
                    conflict = (affected_layer, component["index"])
                    conflict_list.append(conflict)
        else:   # dict which is task layer
            if target_index in process_details[affected_layer]["content_index"]:
                conflict = (affected_layer, process_details[affected_layer]["index"])
                conflict_list.append(conflict)
        return conflict_list

    def check_conflict_for_step(self, target_layer, target_index, process_details):
        """
        Check usage of target component among the steps and return a list of tuple.

        Process details is the dict that is given from the front-end.
        Deduce the affected layer based on the target layer the component is in, either state, parameter, condition
        or the six conditions.
        Loop through the affected layers to see which component has the target as its content.
        If the target is in its content, append the affected component in the conflict list as a tuple.
        Return that list of tuple.
        """
        conflict_list = list()
        if target_layer == "state":
            for component in process_details["step"]:
                if target_index in component["step_state_index"]:
                    conflict = ("step", component["index"])
                    conflict_list.append(conflict)
        if target_layer == "parameter":
            for component in process_details["step"]:
                if target_index in component["step_param_index"]:
                    conflict = ("step", component["index"])
                    conflict_list.append(conflict)
        if target_layer == "condition":
            for component in process_details["step"]:
                if target_index in component["step_cond_index"]:
                    conflict = ("step", component["index"])
                    conflict_list.append(conflict)
        else:   # the 6 conditions
            for component in process_details["condition"]:
                if target_index in component[f"{target_layer}_index"]:
                    conflict = ("condition", component["index"])
                    conflict_list.append(conflict)
        return conflict_list

    def check_conflict_for_condition(self, target_layer, target_index, process_details):
        """
        Check usage of target component among the components and return a list of tuple.

        Process details is the dict that is given from the front-end.
        Deduce the affected layer based on the target layer the component is in, either step, state
        or hasPrerequisiteState.
        Loop through the affected layers to see which component has the target as its content.
        If the target is in its content, append the affected component in the conflict list as a tuple.
        Return that list of tuple.
        :return:
        """
        conflict_list = list()
        if target_layer == "step":
            for component in process_details["isBlockedByStep"]:
                if target_index in component["StepBlocker_index"]:
                    conflict = ("isBlockedByStep", component["index"])
                    conflict_list.append(conflict)
            for component in process_details["hasPrerequisiteStep"]:
                if target_index in component["StepPrerequisite_index"]:
                    conflict = ("hasPrerequisiteStep", component["index"])
                    conflict_list.append(conflict)
        elif target_layer == "state":
            for component in process_details["isBlockedByState"]:
                if target_index in component["StateBlocker_index"]:
                    conflict = ("isBlockedByState", component["index"])
                    conflict_list.append(conflict)
            for component in process_details["hasPrerequisiteState"]:
                if target_index in component["StatePrerequisite_index"]:
                    conflict = ("hasPrerequisiteState", component["index"])
                    conflict_list.append(conflict)
            for component in process_details["isAchievedBy"]:
                if target_index in component["StateCorrect_index"]:
                    conflict = ("isAchievedBy", component["index"])
                    conflict_list.append(conflict)
            for component in process_details["isFailedByState"]:
                if target_index in component["StateCorrect_index"]:
                    conflict = ("isFailedByState", component["index"])
                    conflict_list.append(conflict)
                if target_index in component["StateWrong_index"]:
                    conflict = ("isFailedByState", component["index"])
                    conflict_list.append(conflict)
        elif target_layer == "hasPrerequisiteState":
            for component in process_details["isAchievedBy"]:
                if target_index in component["hasPrerequisiteState_index"]:
                    conflict = ("isAchievedBy", component["index"])
                    conflict_list.append(conflict)
            for component in process_details["isFailedByState"]:
                if target_index in component["hasPrerequisiteState_index"]:
                    conflict = ("isFailedByState", component["index"])
                    conflict_list.append(conflict)
        return conflict_list


class ExternalContextAware(ContextAware):
    """

        Allow awareness on the external context when deciding on processes and conditions to be used in a job.

    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def generate_avail_p(self, location_content_dict, total_resource_dict):
        """
        Called in a thread to generate available probabilities (avail_p) for process components.

        :param location_content_dict:
        :param total_resource_dict:
        :return:
        """
        self.generate_avail_p_per_step(location_content_dict, total_resource_dict)
        self.generate_avail_p_per_objective()
        self.generate_avail_p_per_task()

    def generate_avail_p_per_task(self):
        """
        Generate probability of available resources that can achieve the task.

        Find all not deleted tasks from the db.
        Iterate through the docs to generate the availability probability of the task.
        Select db col based on content layer of the task.
        Iterate through the content ObjectIds to generate a list of availability probability of the content in the
        task.
        Get the multiplication of all probabilities to find the probability of intersection.
        Update the doc with the obtained availability probability.
        """
        query = {
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.task_objective_col, query)
        for doc in doc_list:
            if doc["content_layer"] == "step":
                db_col = self.step_col  # to access content doc
            else:   # objective
                db_col = self.objective_content_col  # to access content doc
            content_doc_list = [   # list of possible content per task
                get_item(db_col, {"_id": ObjectId(content_ObjectId), "is_deleted": {"$ne": True}})[0]   # only one item
                for content_ObjectId in doc["content_ObjectId"]
            ]
            p_list = [
                content_doc["avail_p"]
                for content_doc in content_doc_list
            ]
            probability = self.multiple_list(p_list)    # intersection of all state avail probability
            query = {
                "_id": doc["_id"],
                "is_deleted": {"$ne": True}
            }
            new_info = {
                "avail_p": probability
            }
            self.objective_content_col.update_one(query, {"$set": new_info})

    def generate_avail_p_per_objective(self):
        """
        Generate probability of available resources that can achieve the objective.

        Find all not deleted objectives from the db.
        Iterate through the docs to generate the availability probability of the objective.
        Select db col based on content layer of the objective.
        Iterate through the content ObjectIds to generate a list of availability probability of the content in the
        objective.
        Get the multiplication of all probabilities to find the probability of intersection.
        Update the doc with the obtained availability probability.
        """
        query = {
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.objective_content_col, query)
        for doc in doc_list:
            if doc["content_layer"] == "step":
                db_col = self.step_col
            else:   # objective
                db_col = self.objective_content_col
            content_doc_list = [   # possible content per objective
                get_item(db_col, {"_id": ObjectId(content_ObjectId), "is_deleted": {"$ne": True}})[0]   # only one item
                for content_ObjectId in doc["content_ObjectId"]
            ]
            p_list = [
                content_doc["avail_p"]
                for content_doc in content_doc_list
            ]
            probability = self.multiple_list(p_list)    # intersection of all avail probabilities
            query = {
                "_id": doc["_id"],
                "is_deleted": {"$ne": True}
            }
            new_info = {
                "avail_p": probability
            }
            self.objective_content_col.update_one(query, {"$set": new_info})

    def generate_avail_p_per_step(self, location_content_dict, total_resource_dict):
        """
        Generate probability of available resources that can perform the step.

        Find all not deleted steps from the db.
        Iterate through the docs to generate the availability probability of the step.
        Get the step-state doc ObjectId.
        Get the list of state-exec ObjectIds from the step-state doc and get the state-exec docs.
        Iterate through the list of state-exec docs to generate a list of availability probability of the states
        that has to be detected in the step.
        Get the multiplication of all probabilities to find the probability of intersection.
        Update the doc with the obtained availability probability.

        :param location_content_dict: {<location_id>: {(<r_class>, <r_type>): <number of available resources>}}
        :param total_resource_dict: {(<r_class>, <r_type>): <number of available resources>}
        """
        query = {
            "is_deleted": {"$ne": True}
        }
        doc_list = get_item(self.step_col, query)
        for doc in doc_list:
            query = {
                "_id": ObjectId(doc["step_state_ObjectId"]),
                "is_deleted": {"$ne": True}
            }
            step_state_doc = get_item(self.step_state_col, query)[0]   # should only have one item
            state_exec_doc_list = [   # state per step
                get_item(self.state_exec_col, {"_id": ObjectId(state_exec_ObjectId)})[0]   # should only have one item
                for state_exec_ObjectId in step_state_doc["state_exec_ObjectId"]
            ]
            p_list = [  # probability of all states for a step
                self.generate_avail_p_per_state(
                    state_exec_doc["exec"], doc["location_id"], location_content_dict, total_resource_dict)
                for state_exec_doc in state_exec_doc_list
            ]
            probability = self.multiple_list(p_list)    # intersection of all avail probabilities
            query = {
                "_id": doc["_id"],
                "is_deleted": {"$ne": True}
            }
            new_info = {
                "avail_p": probability
            }
            self.step_col.update_one(query, {"$set": new_info})

    def generate_avail_p_per_state(self, exec_dict_list, location_id_list, location_content_dict, total_resource_dict):
        """
        Generate probability of available resources that can detect the state.

        Package dictionary of resources in list of tuples.
        Iterate through each location in the list to get a list of probability of the locations with available
        resources.
        Select the maximum probability from the list.

        :param exec_dict_list: list of exec dict that states class, type and software id
        :param location_id_list: list of location
        :param location_content_dict: {<location_id>: {(<r_class>, <r_type>): <number of available resources>}}
        :param total_resource_dict: {(<r_class>, <r_type>): <number of available resources>}
        """
        resource_list = [  # tuple (class, type) of resource corresponding to the probability in p list
            (exec_dict["class"], exec_dict["type"])
            for exec_dict in exec_dict_list
        ]
        p_list = [  # probability of all locations with available resources
            self.generate_avail_p_per_location(  # get max probability that resource is avail and in loc
                resource_list, location_id, location_content_dict, total_resource_dict)
            for location_id in location_id_list
        ]
        probability = self.max_list(p_list)
        return probability

    def generate_avail_p_per_location(self, resource_list, location_id, location_content_dict, total_resource_dict):
        """
        Generate probability of resources in the location is available.

        Extract dictionary of content in the location that is in tuple and number of available resources.
        Get a list of probability of the resources being in the location.
        Select the maximum probability from the list.

        :param resource_list: list of tuple (<r_class>, <r_type>)
        :param location_id: unique id of the location
        :param location_content_dict: {<location_id>: {(<r_class>, <r_type>): <number of available resources>}}
        :param total_resource_dict: {(<r_class>, <r_type>): <number of available resources>}
        """
        content_dict = location_content_dict.get("location_id", None)  # list of dict of tuple and num of resource
        if content_dict is not None:
            p_list = [
                self.calculate_probability(content_dict[tup], total_resource_dict[tup])
                for tup in resource_list
            ]
            probability = self.max_list(p_list)  # get max probability that resource is avail and in loc
        else:
            probability = 0
        return probability

    def calculate_probability(self, x, y):
        p = x/y
        return p

    def multiple_list(self, x_list):
        y = 1
        for x in x_list:
            y *= x
        return y

    def max_list(self, x_list):
        y = max(x_list)
        return y
