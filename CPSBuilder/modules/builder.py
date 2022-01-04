from bson import ObjectId
from datetime import timedelta, datetime
import logging
from CPSBuilder.utils.db import *
import config
import requests
logger = logging.getLogger(__name__)


class Builder:
    def __init__(self, client, test=False, demo=False):
        # pass
        if test:
            self.job_db = client["test-job"]
            self.code_db = client["test-code"]
            self.ontology_db = client["test-ontology"]
        else:
            self.job_db = client["job"]
            self.code_db = client["code"]
            self.ontology_db = client["ontology"]
        self.job_task_col = self.job_db["job-task"]
        self.broadcast_buffer_col = self.job_db["broadcast-buffer"]
        self.state_buffer_col = self.job_db["state-buffer"]
        self.error_code_col = self.code_db["error-code"]

    def generate_job_id(self, user_id, dt):
        """
        Gets the new ID for the job that is to be added to the job history.
        """
        initial = "job_"
        num_id = self.get_max_id(self.job_db[user_id])
        num_id = str(num_id + 1).rjust(5, "0")  # deprecated
        return initial + user_id + "_" + dt

    def get_max_id(self, db):
        """
        Retrieves the highest numerical job ID in the database.
        """
        id_list = self.get_id_list(db)
        if len(id_list) == 0:
            return 0
        return max(id_list)

    def get_id_list(self, db):
        id_list = []
        for item in db.find():
            try:
                id_list.append(self.get_num_id(item.get('job_id')))
            except:
                pass
        return id_list

    def get_num_id(self, item_id):
        num_id = ''
        for char in item_id:
            # print(char)
            if char.isdigit():
                num_id += char
        # print(num_id)
        return int(num_id)


class JobBuilder(Builder):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_job(self, user_id, job_name, job_details):
        """
        Insert job to two collections of job db:
        - Details of task in job-task col
        - List of task in job in <user_id> col
        Create buffers required for process control.
        :param user_id:
        :param task_list:
        :return:
        """
        dt = datetime.now()
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S").__str__()
        dt_id = dt.strftime("%Y%m%d%H%M%S").__str__()
        job_id = self.generate_job_id(user_id, dt_id)
        task_ObjectIds = list()
        for process_details in job_details:
            post = self.package_single_task(user_id, job_id, process_details, dt_str)
            _id = self.job_task_col.insert_one(post)
            task_ObjectId = str(_id.inserted_id)
            self.create_broadcast_buffer(job_id, task_ObjectId)  # create buffer for process control
            self.create_state_buffer(task_ObjectId)  # create buffer for process control
            task_ObjectIds.append(task_ObjectId)
        post = self.package_single_job(job_id, task_ObjectIds, dt_str)
        post["job_name"] = job_name
        _id = self.job_db[user_id].insert_one(post)
        job_ObjectId = str(_id.inserted_id)
        return job_id

    def terminate_job(self, job_ObjectId, user_id):
        """
        Terminate all processes related to the selected job.
        :param job_ObjectId: string of job ObjectId
        :param user_id: user who submitted the job
        :return:
        """
        query = {
            "_id": ObjectId(job_ObjectId),
            "status": "pending"
        }
        new_info = {
            "status": "terminated"
        }
        job_details = get_item(self.job_db[user_id], query)[0]  # should only have one
        if len(job_details) == 0:  # end termination
            logger.error(f"[{job_ObjectId}] in {user_id} is not a running job. Cannot be terminated.")
            return False
        else:  # terminate job and tasks
            self.job_db[user_id].update_one(query, {"$set": new_info})
            task_ObjectIds = job_details["task_ObjectId"]
            for task_ObjectId in task_ObjectIds:
                query["_id"]: ObjectId(task_ObjectId)  # only change object id in the query
                self.job_task_col.update_one(query, {"$set": new_info})
                self.flag_termination_in_state_buffer(task_ObjectId)
            return True

    def package_single_task(self, user_id, job_id, process_details, dt):
        """
        Packages a single task to be inserted into the job database.
        :param user_id: user who submitted the job
        :param job_id: generated job id
        :param process_details: process details from job tab
        :param dt: start datetime
        :return:
        post: packed details for one task with a blank datetime and status for each component
        """
        task = {
            "user_id": user_id,
            "job_id": job_id,
            "var": process_details["task"]["var"],
            "content": process_details["task"]["content_index"],
            "datetime_start": None,
            "datetime_end": None,
            "status": "pending",
        }
        objective = {
            "objective_layer_1": list()     # dummy to show format
        }
        for key, component_list in process_details.items():
            if key[:len("obj")] == "obj":
                objective_layer = key
                objective[objective_layer] = [
                    {
                        "index": objective_dict["index"],
                        "var": objective_dict["var"],
                        "content": objective_dict["content_index"],
                        "datetime_start": None,
                        "datetime_end": None,
                        "status": "pending"
                    }
                    for objective_dict in component_list
                ]
        step = {
            "step": list()      # dummy to show format
        }
        for step_dict in process_details["step"]:  # for each step
            packaged_step = self.package_single_step(step_dict)
            step["step"].append(packaged_step)
        metadata = {
            "job_submission_timestamp": dt,
        }
        post = {**task, **objective, **step, **metadata}
        return post

    @ staticmethod
    def package_single_step(data):
        idx = 0  # initialize
        for step_exec in data["exec"]:
            if step_exec["same_as_exec_index"] is not None:
                main_exec_idx = step_exec["same_as_exec_index"]
                main_step_exec = data["exec"][main_exec_idx]
                if main_step_exec.get("filtered_state", None) is None:  # no list yet
                    main_step_exec["filtered_state"] = [step_exec["state"]]  # create list
                else:
                    main_step_exec["filtered_state"].append(step_exec["state"])  # append to main list
            else:  # step_exec is the main exec
                step_exec["index"] = idx
                idx += 1
                if step_exec.get("filtered_state", None) is None:  # no list yet
                    step_exec["filtered_state"] = [step_exec["state"]]  # create list
                else:
                    step_exec["filtered_state"].append(step_exec["state"])  # append to own list
        # Remove step_exec after combining with main exec
        data["exec"] = [step_exec for step_exec in data["exec"] if step_exec["same_as_exec_index"] is None]
        step = {
            "index": data["index"],
            "var": data["var"],
            "location_id": data["location_id"],
            "datetime_start": None,
            "datetime_end": None,
            "status": "pending",
            "param": data["param"],  # select from step_param doc
            "exec": [
                {
                    "index": step_exec["index"],
                    "same_as_step_index": step_exec["same_as_step_index"],  # arranged on ui
                    "state": step_exec["filtered_state"],  # combine states from same as exec_index into here
                    "preferred_exec": step_exec["preferred_exec"],  # arranged by executor mapping and ui
                    "alternative_exec": step_exec["alternative_exec"],  # arranged by executor mapping and ui
                    "actual_exec": {
                        "ID": None,
                        "class": None,
                        "type": None
                    },
                    "status": "pending"
                }
                for step_exec in data["exec"]
            ]
        }
        return step

    def create_broadcast_buffer(self, job_id, task_ObjectId):
        query = {
            "job_id": job_id
        }
        doc_list = get_item(self.broadcast_buffer_col, query)
        if len(doc_list) == 0:  # not created previously
            post = {
                "job_id": job_id,
                "blocker_list": list(),
                "output_list": list(),
                "to_be_broadcast": list()
            }
            self.broadcast_buffer_col.insert_one(post)
        new_info = {
            "$push": {
                "to_be_broadcast": {
                    "task_ObjectId": task_ObjectId,
                    "step_list": list()
                }
            }
        }
        self.broadcast_buffer_col.update_one(query, new_info)

    def create_state_buffer(self, task_ObjectId):
        post = {
            "task_ObjectId": task_ObjectId,
            "job_terminated": False,
            "state_buffer": list(),
            "can_be_collected": False
        }
        self.state_buffer_col.insert_one(post)

    def package_single_job(self, job_id, task_ObjectIds, dt):
        job = {
            "job_id": job_id,  # todo: find where to get this
            "status": "pending",
            "task_ObjectId": [str(task_ObjectId) for task_ObjectId in task_ObjectIds]
        }
        metadata = {
            "job_submission_timestamp": dt,
        }
        post = {**job, **metadata}
        return post

    def flag_termination_in_state_buffer(self, task_ObjectId):
        query = {
            "task_ObjectId": task_ObjectId
        }
        new_info = {
            "job_terminated": True
        }
        self.state_buffer_col.update_one(query, {"$set": new_info})


class OntologyBuilder(Builder):
    '''
    Package process data from front-end to structure of ontology data.
    The ontology data will be used by Process Control CognitiveEngine to build OWL ontology.
    '''

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_ontology(self, user_id, job_id, task_list):
        """
        Create ontology for process control and insert docs into db collection for each task.
        :param job_id: Human readable id generated from JobBuilder
        :param task_list:
        :return:
        """
        for process_details in task_list:  # each task
            # method = "cognitive engine"   # default
            method = "sequencer"     # test CT
            col_name = f"{process_details['task']['var']}"
            if col_name in self.ontology_db.list_collection_names():
                print(f"Ontology for task {col_name} has already existed! Using existing ontology.")
            else:
                post_dict = self.build_ontology(process_details)
                for key in post_dict:
                    self.ontology_db[col_name].insert_one(post_dict[key])  # insert value of post_dict as doc
                print(f"Ontology for task {col_name} created.")
            res = self.start_process_control(
                method, user_id, job_id, process_details['task']['_id'], process_details['task']['var'], col_name)
            print(res)

    def start_process_control(self, method, user_id, job_id, task_ObjectId, task_var, task_onto_col_name):
        post = {
            "method": method,
            "user_id": user_id,
            "job_id": job_id,
            "task_ObjectId": task_ObjectId,
            "task_var": task_var,
            "task_onto_col_name": task_onto_col_name,
        }
        print(f'{user_id}-{job_id}-{task_var}: start process controller: {method}')
        # logger.info(f'{user_id}-{job_id}-{task_var}: start process controller: {method}')
        headers = {'Content-Type': 'application/json'}
        address = f'http://{config.cognitive_engine_ip}:{config.cognitive_engine_port}/api/job-execution/start-process-control'
        try:
            res = requests.post(
                address, data=json.dumps(post), headers=headers)
            return res
        except requests.exceptions.RequestException:
            return "No Connection to process controller", None, None

    def build_ontology(self, process_data):
        post_dict = dict()
        post_dict["NamedObjectiveLayer"] = self.package_objective_layers(process_data)
        post_dict["NamedStep"] = self.package_step(process_data["step"])
        post_dict["NamedState"] = self.package_state(
            process_data["state"],
            process_data["step"]
        )
        state_index_var_dict = self.get_index_var_dict(process_data["state"])
        step_index_sentence_dict = self.get_index_sentence_dict(process_data["step"])
        post_dict["isBlockedByStep"] = self.package_isBlockedByStep(
            process_data["isBlockedByStep"],
            step_index_sentence_dict,
            process_data["condition"],
            process_data["step"]
        )
        post_dict["hasPrerequisiteStep"] = self.package_hasPrerequisiteStep(
            process_data["hasPrerequisiteStep"],
            step_index_sentence_dict,
            process_data["condition"],
            process_data["step"]
        )
        post_dict["isBlockedByState"] = self.package_isBlockedByState(
            process_data["isBlockedByState"],
            process_data["condition"],
            process_data["step"]
        )
        post_dict["hasPrerequisiteState"] = self.package_hasPrerequisiteState(
            process_data["hasPrerequisiteState"],
            process_data["condition"],
            process_data["step"]
        )
        post_dict["isAchievedBy"] = self.package_isAchievedBy(
            process_data["isAchievedBy"],
            process_data["condition"],
            process_data["step"],
            state_index_var_dict
        )
        post_dict["isFailedByState"] = self.package_isFailedByState(
            process_data["isFailedByState"],
            process_data["condition"],
            process_data["step"],
            state_index_var_dict
        )
        # post_dict["ResourceCatalogue"] = self.package_resource_catalogue(process_data["state"])
        return post_dict

    def get_index_var_dict(self, data):
        index_list = [
            details["index"]
            for details in data
        ]
        var_list = [
            details["var"]
            for details in data
        ]
        index_var_dict = dict(zip(index_list, var_list))
        return index_var_dict

    def get_index_sentence_dict(self, data):
        index_list = [
            details["index"]
            for details in data
        ]
        sentence_list = [
            details["sentence"]
            for details in data
        ]
        index_sentence_dict = dict(zip(index_list, sentence_list))
        return index_sentence_dict

    def package_objective_layers(self, process_data):
        objective_layer_list = [  # get list of dict of objectives into a list from process data
            data  # place list of objective details of that layer
            for component, data in process_data.items()
            if component[0:len("obj")] == "obj"  # find dict key that is "objective_layer_N", where N is layer num
        ]
        post = {  # prepare empty dict for the loop below to append into
            "Layer": [],
            "NamedObjective": [],
            "isAchievedBy": []
        }
        for layer, objective in enumerate(objective_layer_list):  # many dicts within a list to be added
            post = self.package_objective_layer(layer, objective, post)
        return post

    def package_objective_layer(self, layer, data, post):
        '''
        Package the post in the same way as would have gotten from the excel.
        All variables in post are in sentence format.
        '''
        for details in data:
            rep = len(details["content_index"])  # find out num of reps unique values have to be replicated
            post["Layer"] = post["Layer"] + [layer] * rep  # replicate the unique values
            post["NamedObjective"] = post["NamedObjective"] + [details["sentence"]] * rep  # replicate the unique values
            post["isAchievedBy"] = post["isAchievedBy"] + details["content_index"]
        return post

    def package_step(self, data):
        '''
        Package the post in the same way as would have gotten from the excel.
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "isAtLocation": []
        }
        for details in data:
            rep = len([details["location_id"]])  # find out num of reps unique values have to be replicated
            post["NamedStep"] = post["NamedStep"] + [details["sentence"]] * rep  # replicate the unique values
            post["isAtLocation"] = post["isAtLocation"] + [details["location_id"]]
        return post

    def package_state(self, data, step):
        '''
        Package the post in the same way as would have gotten from the excel.
        All variables in post are in sentence format.
        '''
        post = {
            "NamedState": [],
            "Superclass": [],
            "Type": [],
            "PhyResource": [],
            "PhyResourceClass": [],
            "CyberResource": []
        }
        for details in data:
            rep = len(details["exec"])  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for step_dict in step:
                if details["index"] in step_dict["state_exec_index"]:
                    step_sentence = step_dict["sentence"]
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedState"] = post["NamedState"] + [details["var"]] * rep  # replicate the unique values
                post["Superclass"] = post["Superclass"] + [details["class"]] * rep  # replicate the unique values
                post["Type"] = post["Type"] + [details["type"]] * rep  # replicate the unique values
        return post

    def package_isBlockedByStep(self, data, step_index_sentence_dict, condition, step):
        '''
        Package the post in the same way as would have gotten from the excel.
        (before the variables are replaced by their respective object ids).
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "isBlockedByStep": [],
            "StepBlocker": [],
        }
        for details in data:
            rep = len(details["StepBlocker_index"])  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for condition_dict in condition:
                if details["index"] in condition_dict["isAchievedBy_index"]:
                    for step_dict in step:
                        if condition_dict["index"] == step_dict["step_cond_index"]:
                            step_sentence = step_dict["sentence"]
                            break
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedStep"] = post["NamedStep"] + [step_sentence] * rep  # replicate the unique values
                post["isBlockedByStep"] = post["isBlockedByStep"] + [step_index_sentence_dict[details["index"]]]
                post["StepBlocker"] = post["StepBlocker"] + details["StepBlocker_index"]
        return post

    def package_hasPrerequisiteStep(self, data, step_index_sentence_dict, condition, step):
        '''
        Package the post in the same way as would have gotten from the excel.
        (before the variables are replaced by their respective object ids).
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "hasPrerequisiteStep": [],
            "StepPrerequisite": [],
        }
        for details in data:
            rep = len(details["StepPrerequisite_index"])  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for condition_dict in condition:
                if details["index"] in condition_dict["isAchievedBy_index"]:
                    for step_dict in step:
                        if condition_dict["index"] == step_dict["step_cond_index"]:
                            step_sentence = step_dict["sentence"]
                            break
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedStep"] = post["NamedStep"] + [step_sentence] * rep  # replicate the unique values
                post["hasPrerequisiteStep"] = post["hasPrerequisiteStep"] + [step_index_sentence_dict[details["index"]]]
                post["StepPrerequisite"] = post["StepPrerequisite"] + details["StepPrerequisite_index"]
        return post

    def package_isBlockedByState(self, data, condition, step):
        '''
        Package the post in the same way as would have gotten from the excel.
        (before the variables are replaced by their respective object ids).
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "isBlockedByState": [],
            "StateBlocker": [],
        }
        for details in data:
            rep = len(details["StateBlocker_index"])  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for condition_dict in condition:
                if details["index"] in condition_dict["isAchievedBy_index"]:
                    for step_dict in step:
                        if condition_dict["index"] == step_dict["step_cond_index"]:
                            step_sentence = step_dict["sentence"]
                            break
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedStep"] = post["NamedStep"] + [step_sentence] * rep  # replicate the unique values
                post["isBlockedByState"] = post["isBlockedByState"] + [details["index"]]
                post["StateBlocker"] = post["StateBlocker"] + details["StateBlocker_index"]
        return post

    def package_hasPrerequisiteState(self, data, condition, step):
        '''
        Package the post in the same way as would have gotten from the excel.
        (before the variables are replaced by their respective object ids).
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "hasPrerequisiteState": [],
            "StatePrerequisite": [],
        }
        for details in data:
            rep = len(details["StatePrerequisite_index"])  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for condition_dict in condition:
                if details["index"] in condition_dict["isAchievedBy_index"]:
                    for step_dict in step:
                        if condition_dict["index"] == step_dict["step_cond_index"]:
                            step_sentence = step_dict["sentence"]
                            break
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedStep"] = post["NamedStep"] + [step_sentence] * rep  # replicate the unique values
                post["hasPrerequisiteState"] = post["hasPrerequisiteState"] + [details["index"]]
                post["StatePrerequisite"] = post["StatePrerequisite"] + details["StatePrerequisite_index"]
        return post

    def package_isAchievedBy(self, data, condition, step, state_index_var_dict):
        '''
        Package the post in the same way as would have gotten from the excel.
        (before the variables are replaced by their respective object ids).
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "isAchievedBy": [],
            "hasPrerequisiteState": [],
            "StateCorrect": [],
        }
        for details in data:
            max_len = max(
                len(details["StateCorrect_index"]),
                len(details["hasPrerequisiteState_index"])
            )
            rep = max_len  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for condition_dict in condition:
                if details["index"] in condition_dict["isAchievedBy_index"]:
                    for step_dict in step:
                        if condition_dict["index"] == step_dict["step_cond_index"]:
                            step_sentence = step_dict["sentence"]
                            break
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedStep"] = post["NamedStep"] + [step_sentence] * rep  # replicate the unique values
                post["isAchievedBy"] = post["isAchievedBy"] + [details["index"]]  # todo: make it repeat to fill forward list
                # append None to remaining of list that is shorter than the max list
                temp_list = details["hasPrerequisiteState_index"] + [None] * (
                        rep - len(details["hasPrerequisiteState_index"]))
                temp_list = [state_index_var_dict[index] for index in temp_list]
                post["hasPrerequisiteState"] = post["hasPrerequisiteState"] + temp_list
                temp_list = details["StateCorrect_index"] + [None] * (rep - len(details["StateCorrect_index"]))
                temp_list = [state_index_var_dict[index] for index in temp_list]
                post["StateCorrect"] = post["StateCorrect"] + temp_list
        return post

    def package_isFailedByState(self, data, condition, step, state_index_var_dict):
        '''
        Package the post in the same way as would have gotten from the excel.
        (before the variables are replaced by their respective object ids).
        All variables in post are in sentence format.
        '''
        post = {
            "NamedStep": [],
            "isFailedByState": [],
            "hasPrerequisiteState": [],
            "StateCorrect": [],
            "StateWrong": [],
        }
        for details in data:
            max_len = max(
                len(details["StateCorrect_index"]),
                len(details["StateWrong_index"]),
                len(details["hasPrerequisiteState_index"])
            )
            rep = max_len  # find out num of reps unique values have to be replicated
            # find which step has this condition and put the step sentence into a list
            step_sentence = None
            for condition_dict in condition:
                if details["index"] in condition_dict["isAchievedBy_index"]:
                    for step_dict in step:
                        if condition_dict["index"] == step_dict["step_cond_index"]:
                            step_sentence = step_dict["sentence"]
                            break
                    break
            # only record cond that the step uses
            if step_sentence is not None:
                post["NamedStep"] = post["NamedStep"] + [step_sentence] * rep  # replicate the unique values
                post["isFailedByState"] = post["isFailedByState"] + [details["index"]]
                # append None to remaining of list that is shorter than the max list
                temp_list = details["hasPrerequisiteState_index"] + [None] * (
                        rep - len(details["hasPrerequisiteState_index"]))
                post["hasPrerequisiteState"] = post["hasPrerequisiteState"] + temp_list
                temp_list = details["StateCorrect_index"] + [None] * (rep - len(details["StateCorrect_index"]))
                temp_list = [state_index_var_dict[index] for index in temp_list]
                post["StateCorrect"] = post["StateCorrect"] + temp_list
                temp_list = details["StateWrong_index"] + [None] * (rep - len(details["StateWrong_index"]))
                temp_list = [state_index_var_dict[index] for index in temp_list]
                post["StateWrong"] = post["StateWrong"] + temp_list
        return post

    def package_resource_catalogue(self, state_data):
        post = {
            "Resource": [],
            "Class": []
        }
        exec_list = list()
        for details in state_data:
            exec_list.append(
                (r["type"], r["class"])  # append tuple
                for r in details["exec"]
            )
        exec_list = set(exec_list)  # remove duplicates
        post["Resource"] = [tup[0] for tup in exec_list]
        post["Class"] = [tup[1] for tup in exec_list]
        return post
