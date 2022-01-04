'''
This script is specific to simple decision tree inference method using if-else.
Create/Edit a new script, ontology map and cognitive engine according to each new system.
Ensure that the script matches the input-output required by CPSBuilder and cyber twins.
'''

from CPSBuilder.modules.archive.resource_delete_module import ResourceDeleteModule
from CPSBuilder.modules.archive.resource_management_module import ResourceManagementModule
from archive.CognitiveEngine.functions.db_functions import *

import logging
logger = logging.getLogger(__name__)


class CognitiveEngine():
    def __init__(self, client):
        self.resources_dict = {
            "hardware": "hardware_resources",
            "robot": "robot",
            "human": "human_resources"
        }
        self.job_history = client['job-history']
        self.resources = client['resources']
        self.resource_management_module = ResourceManagementModule(client)
        self.resource_delete_module = ResourceDeleteModule(client)

    def get_next_step(self, job_id, user_id, step_status, action_seq, step_seq, total_action_count, total_step_count):
        logger.info(f"[{job_id}]: Getting next action-step...")
        # 1. Get the inferred_step_status, next_action_seq, and next_step_seq from get_inference_class.
        # todo: find ways to infer multiple possible next action-step as list or something
        inferred_step_status, next_action_seq, next_step_seq = self.get_inference_class(
            job_id, user_id, step_status, action_seq, step_seq, total_action_count, total_step_count)
        logger.info(
            f"[{job_id}]: Inferred as status: {inferred_step_status}, action: {next_action_seq}, step: {next_step_seq}"
        )
        # todo: handle last step completion >> next_action_seq: 'job_done' and next_step_seq: 'job_done'
        if next_action_seq is not None and next_step_seq is not None:
            if next_action_seq != "job_done" and next_step_seq != "job_done":   # if not completed
                logger.info(
                    f"[{job_id}]: Checking availability of resources for action: {next_action_seq}, step: {next_step_seq}..."
                )
                # 2. Using the inferred action seq and step seq, check the available resource.
                # todo: filter down multiple next to multiple next that's available
                paths_with_conditions_met = self.check_availability(job_id, user_id, next_action_seq, next_step_seq)
                logger.info(
                    f"[{job_id}]: Availablity checked! Number of paths that met the conditions: {paths_with_conditions_met}"
                            )
                # 3. If multiple steps are possible, pick one to broadcast
                if paths_with_conditions_met is not None:
                    chosen_path = 1
                else:
                    chosen_path = None
                # 4. Return the inferred_step_status, next_action_seq, and next_step_seq only
                # if there is available resource.
                if chosen_path is None:
                    next_action_seq = None
                    next_step_seq = None
            else:   # if completed
                pass
        logger.info(
            f"[{job_id}]: In conclusion, status: {inferred_step_status}, action: {next_action_seq}, "
            f"step: {next_step_seq}"
        )
        return inferred_step_status, next_action_seq, next_step_seq

    def check_availability(self, job_id, user_id, next_action_seq, next_step_seq):
        # Get action details from the job_history db to get preferred exec and location id
        action_details = self.get_next_action_details(job_id, user_id, next_action_seq, next_step_seq)
        logger.info(f"[{job_id}]: Action details obtained!")
        preferred_exec_list = self.get_next_exec(job_id, action_details, next_step_seq)
        location_id = self.get_next_location(job_id, action_details)
        num_available_exec = self.count_available_exec(job_id, preferred_exec_list, location_id)
        logger.info(f"[{job_id}]: Number of available resources: {num_available_exec}")
        # Check if there are steps that don't have available executor
        for num in num_available_exec:
            if num == 0:
                return None     # no paths with conditions met
        return 1     # there are paths with conditions met

    def count_available_exec(self, job_id, preferred_exec_list, location_id):
        # Check the resource db for available exec based on type (same as alternative list)
        available_exec = []
        num_available_exec = []
        for exec_idx, exec_details in enumerate(preferred_exec_list):
            logger.info(f"[{job_id}]: Executor is {exec_details}")
            if exec_details.get("type") is not None:  # this is true for hardware and robot only
                col = self.resources_dict[exec_details["class"]]
                db = self.resources[col]
                query = {
                    "type": exec_details["type"],
                    "location_id": location_id,
                    "availability": "1",
                    "status": "1"
                }
                available_exec.append(get_item(db, query))  # returns the list of executors in the list of exec_seq
                num_available_exec.append(len(available_exec[exec_idx]))
                logger.info(f"[{job_id}]: Available stuff: ({num_available_exec}) {available_exec}")
            else:  # this is true for human only
                available_exec.append(exec_details["ID"])      # in this case, there is only one available exec
                num_available_exec.append(len(available_exec[exec_idx]))
        return num_available_exec

    def get_next_action_details(self, job_id, user_id, next_action_seq, next_step_seq):
        db = self.job_history[user_id]
        query = {
            "job_id": job_id
        }
        job_details = get_item(db, query)
        action_details = job_details[0]["action_details_list"][next_action_seq]
        return action_details

    def get_next_exec(self, job_id, action_details, next_step_seq):
        exec_list = action_details["action_exec"][next_step_seq]["exec_list"]
        pprint(exec_list)
        preferred_exec_list = []
        for exec_details in exec_list:
            preferred_exec_list.append(exec_details["preferred_exec"])
        logger.info(f"[{job_id}]: Preferred list is {preferred_exec_list}")
        return preferred_exec_list

    def get_next_location(self, job_id, action_details):
        location_id = action_details.get("location_id")
        logger.info(f"[{job_id}]: Location is at {location_id}")
        return location_id

    def get_prev_step(self, job_id, user_id, action_seq, step_seq):
        """convert from 0-base numbering to 1-base numbering"""
        action_step_num = action_seq + 1
        step_step_num = step_seq + 1

        prev_action_step_num = action_step_num - 1
        prev_step_step_num = step_step_num - 1

        step_name = None
        if (action_seq == 0) and (step_seq == 0):
            step_name = "0-0"
        elif step_seq == 0:
            try:
                job_details = next(
                    self.job_history[user_id].find({'job_id': job_id}))
            except StopIteration:
                return None
            prev_action_details = job_details['action_details_list'][prev_action_step_num - 1]
            step_details = prev_action_details['action_exec']
            total_step_count = len(step_details)
            step_name = f"{str(prev_action_step_num)}-{str(total_step_count)}"
        else:
            step_name = f"{str(action_step_num)}-{str(prev_step_step_num)}"
        return step_name

    def get_exec_id_list(self, job_id, user_id, action_seq, step_seq):
        """
        Retrieves the list of actual executor ids from the job history database. \n
        Returns a list of executor IDs.
        """
        job_history = self.job_history[user_id]
        try:
            job_details = next(job_history.find({'job_id': job_id}))
        except StopIteration:
            return None
        exec_list = job_details['action_details_list'][action_seq]['action_exec'][step_seq]['exec_list']
        exec_id_list = []
        for exec_details in exec_list:
            if exec_details['actual_exec'] is not None:
                exec_id_list.append(exec_details['actual_exec'])
            else:
                exec_id_list.append(exec_details['preferred_exec']['ID'])
            # print(exec_details)
        return exec_id_list

    def get_exec_details_list(self, job_id, user_id, action_seq, step_seq):
        """
        Retrieves the details of actual executors responsible for the step. \n
        Returns a list of executor details.
        """
        exec_id_list = self.get_exec_id_list(
            job_id, user_id, action_seq, step_seq)
        if exec_id_list is not None:
            exec_detail_list = []
            for exec_id in exec_id_list:
                resource_class = self.resource_management_module.get_resource_type(
                    exec_id)
                resource_details = self.resource_delete_module.get_item_details(
                    resource_class, {'ID': exec_id})[0]
                resource_details['class'] = resource_class  # huh?
                exec_detail_list.append(resource_details)
            return exec_detail_list
        else:
            return exec_id_list

    def check_step_status(self, job_id, user_id, action_seq, step_seq):
        """
        Checks whether all executors have completed the step successfully.
        """
        job_details_curs = self.job_history[user_id].find({'job_id': job_id}, {
            '_id': 0
        })
        try:
            step_completion_flag = True
            job_details = next(job_details_curs)
            exec_list = job_details['action_details_list'][action_seq]['action_exec'][step_seq]['exec_list']
            logger.info(f'{job_id}-{user_id}: exec_list = {exec_list}')
            for executor in exec_list:
                if executor.get('exec_step_status', None) != 'completed':
                    step_completion_flag = False
            if step_completion_flag:
                return "completed"
            else:
                return "failed"
        except StopIteration as e:
            logger.error(f'{job_id} for user {user_id} not found in database.')

    def check_step_completion(self, job_id, user_id, action_seq, step_seq):
        """
        Checks whether all executors have completed this step
        """
        job_details_curs = self.job_history[user_id].find({'job_id': job_id}, {
            '_id': 0
        })
        try:
            step_completion_flag = True
            job_details = next(job_details_curs)
            exec_list = job_details['action_details_list'][action_seq]['action_exec'][step_seq]['exec_list']
            logger.info(f'{job_id}-{user_id}: exec_list = {exec_list}')
            for executor in exec_list:
                if executor.get('exec_step_status', None) is None:
                    step_completion_flag = False
            return step_completion_flag
        except StopIteration as e:
            logger.error(f'{job_id} for user {user_id} not found in database.')

    def get_inference_class(self, job_id, user_id, step_status, action_seq, step_seq, total_action_count, total_step_count):
        """
        Based on the input, determine whether the step is completed or not. \n
        Returns 3 items: (step_completion_status, next_action_seq, next_step_seq)
        """
        # todo: Change this algorithm to let CE know that no steps are skipped
        prev_step_num = self.get_prev_step(
            job_id, user_id, action_seq, step_seq)
        if prev_step_num == "0-0":
            item_status_name = "process_start_" + job_id
            item_status_class = "ProcessStart"
        else:
            item_status_name = "post_step" + str(prev_step_num) + "_" + job_id
            item_status_class = "PostStep" + str(prev_step_num)

        # resource_name = user_id
        # resource_class = resource_type

        resource_name = []
        resource_class = []

        # create content to be sent to Java
        exec_detail_list = self.get_exec_details_list(
            job_id, user_id, action_seq, step_seq)  # get [{details of exec 1}, {details of exec 2}, ...]
        if exec_detail_list is not None:
            for exec_detail in exec_detail_list:
                resource_class_tmp = exec_detail.get('item_type', False)    # huh?
                if not resource_class_tmp:
                    resource_class_tmp = exec_detail.get('class')
                resource_name_tmp = exec_detail.get('ID')
                resource_name.append(resource_name_tmp)     # get [ID 1, ID 2, ...]
                resource_class.append(resource_class_tmp.title())   # get [class 1, class 2, ...]
        else:
            print(f'Job ID {job_id} not found')
        if step_status == "completed":
            step_completion_name = "complete_action_" + job_id
            step_completion_class = "CompleteAction"
        else:
            step_completion_name = "failed_action_" + job_id
            step_completion_class = "FailedAction"

        step_status_name = "job_status_" + job_id

        post = {
            "jobId": job_id,
            "itemStatusName": item_status_name,
            "itemStatusClass": item_status_class,
            "resourceName": resource_name,
            "resourceClass": resource_class,
            "stepCompletionName": step_completion_name,
            "stepCompletionClass": step_completion_class,
            "stepStatusName": step_status_name
        }
        logger.info(f'{job_id}-{user_id}: cognitive engine input: {post}')
        # todo: change this to if-else start
        match = False
        if action_seq == 0 and step_seq == 0:
            if post["itemStatusClass"] == "ProcessStart":
                match = True
        elif action_seq == 1 and step_seq == 0:
            if post["itemStatusClass"] == f"PostStep1-1":
                match = True
        elif action_seq == 2 and step_seq == 0:
            if post["itemStatusClass"] == f"PostStep2-1":
                match = True
        elif action_seq == 3 and step_seq == 0:
            if post["itemStatusClass"] == f"PostStep3-1":
                match = True
        elif action_seq == 4 and step_seq == 0:
            if post["itemStatusClass"] == f"PostStep4-1":
                match = True

        if match:
            if post["stepCompletionClass"] == "CompleteAction":
                match_complete = True
                match_fail = False
            elif post["stepCompletionClass"] == "FailedAction":
                match_complete = False
                match_fail = True
        else:
            match_complete = False
            match_fail = False

        # headers = {'Content-Type': 'application/json'}
        # try:
        #     res = requests.post(
        #         f'http://{config.cognitive_engine_ip}:{config.cognitive_engine_port}/api/reasoner/get-reasoning', data=json.dumps(post), headers=headers)
        # except requests.exceptions.RequestException:
        #     return "No Connection to cognitive engine", None, None
        # the end of sending content to Java

        # After the decision tree does the inference, a list of classes (cognitive engine class) will be returned.
        # todo: remove this chunk
        # res_json = json.loads(res.text)
        # job_id = res_json.get('jobId')
        # prefix = res_json.get('prefix') + "#"
        # class_list_dirty = res_json.get('classList')
        # class_list = []
        # # cuts the long return into list of shorter class name
        # for item in class_list_dirty:
        #     class_list.append(item.replace(prefix, ''))
        #
        # step_complete_regex = re.compile('Step(\d+-\d+)Complete$')
        # step_fail_regex = re.compile('Step(\d+-\d+)Failed$')

        # todo: remove this for loop
        # todo: use a function to do if-else and return step_complete
        # for class_item in class_list:
        # """ check if there is a job complete among the classes """
        # match_complete = step_complete_regex.match(class_item)  # match is regex function
        # match_complete will be True if the class_item has the expression defined in step_complete_regex
        # todo: if step completed, match_complete is True
        if match_complete:
            next_action_seq, next_step_seq = self.get_next_step_complete(
                job_id, user_id, action_seq, step_seq, total_action_count, total_step_count)
            print(f"completed, {next_action_seq}, {next_step_seq}")
            return "completed", next_action_seq, next_step_seq
        # match_fail = step_fail_regex.match(class_item)
        # match_fail will be True if the class_item has the expression defined in step_fail_regex
        # todo: if step failed, match_fail is True
        if match_fail:
            next_action_seq, next_step_seq = self.get_next_step_failed(
                job_id, user_id, action_seq, step_seq, total_step_count)
            print(f"failed, {action_seq}, {step_seq}")
            return "failed", action_seq, step_seq
            # return "failed", 0, 0
        return "No Match", None, None
        # todo: change this to if-else end

    def get_exec_total_count(self, job_id, user_id, action_seq, step_seq):
        try:
            job_details = next(
                self.job_history[user_id].find({'job_id': job_id}))
        except StopIteration:
            return None
        exec_list = job_details['action_details_list'][action_seq]['action_exec'][step_seq]['exec_list']
        return len(exec_list)

    def clear_actual_exec(self, job_id, user_id, action_seq, step_seq):
        '''
        Every time the step is going to be broadcast, remove actual_exec and exec_step_status
        :param job_id:
        :param user_id:
        :param action_seq:
        :param step_seq:
        :return:
        '''
        exec_total_count = self.get_exec_total_count(
            job_id, user_id, action_seq, step_seq)
        for exec_index in range(exec_total_count):
            try:
                self.job_history[user_id].update_one({"job_id": job_id}, {"$set": {
                    f"action_details_list.{action_seq}.action_exec.{step_seq}.exec_list.{exec_index}.actual_exec": None,
                    f"action_details_list.{action_seq}.action_exec.{step_seq}.exec_list.{exec_index}.exec_step_status": None
                }},
                    upsert=False
                )
            except Exception as e:
                logger.error(
                    'failed to clear executor for {job_id} by {user_id} at {action_seq}-{step_seq}')
                logger.error(e)
                return False
        return True

    def get_next_step_failed(self, job_id, user_id, action_seq, step_seq, total_step_count):
        """
        Retrieves next step if the step has failed. \n
        The next step is retrieved by assuming that the current step can be repeated.
        """
        next_action_seq = None
        next_step_seq = None

        """ convert total_action_count and total_step_count to 0-base """
        final_step_seq = total_step_count - 1

        next_action_seq = action_seq
        next_step_seq = step_seq

        while not self.clear_actual_exec(job_id, user_id, next_action_seq, next_step_seq):
            logger.info(
                f'attempting to clear executor for {job_id} by {user_id} at {next_action_seq}-{next_step_seq}')

        return next_action_seq, next_step_seq

    def get_next_step_complete(self, job_id, user_id, action_seq, step_seq, total_action_count, total_step_count):
        """
        Retrieves the next step if the step is completed \n
        """
        next_action_seq = None
        next_step_seq = None

        """ convert total_action_count and total_step_count to 0-base """
        final_action_seq = total_action_count - 1
        final_step_seq = total_step_count - 1

        if step_seq + 1 > final_step_seq:
            if action_seq + 1 > final_action_seq:
                next_action_seq = "job_done"
                next_step_seq = "job_done"
                return next_action_seq, next_step_seq
            else:
                next_action_seq = action_seq + 1
                next_step_seq = 0
        else:
            next_action_seq = action_seq
            next_step_seq = step_seq + 1

        while not self.clear_actual_exec(job_id, user_id, next_action_seq, next_step_seq):
            logger.info(
                f'attempting to clear executor for {job_id} by {user_id} at {next_action_seq}-{next_step_seq}')

        return next_action_seq, next_step_seq
