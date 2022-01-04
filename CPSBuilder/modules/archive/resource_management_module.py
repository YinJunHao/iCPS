from CPSBuilder.utils.archive.module_functions import *
from CPSBuilder.modules.archive.cyber_twin_module import CyberTwinModule
from bson import ObjectId

import logging
logger = logging.getLogger(__name__)


class ResourceManagementModule():
    """
    Updates the dynamic status of step-exec pairs in the database. \n
    If a specific step-exec pair is not available, it will not be picked during pair generation.
    """

    def __init__(self, client):
        self.step_exec = client['action-step']['step-exec-pair']
        self.translate_step = client['action-step']['step-sentence']
        self.action_collection = client['action-step']['action-step-pair']
        self.human = client['resources']['human_resources']
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.software = client['resources']['software_resources']
        self.task_action = client['task-action']['task-action-pair']
        self.token_db_action = client['search-engine']['action-token']
        self.cyber_twin_module = CyberTwinModule(client)

    def add_step_exec(self, step, exec_class, exec_type, dependency, software_id, software_name, item_id=None):
        """
        Adds/Updates a  step-executor pair into the database. \n
        Params: \n
        step: Step variable to be added. \n
        exec_class: Class of executor that will perform the step \n
        exec_type: Type of executor that will perform the step \n
        dependency: Step name, if any, of a step this step is dependent on for execution. \n
        software_id: ID of software that will be used by the executor \n
        software_name: Name of software that will be used by the executor \n 
        Returns: \n
        False: if insertion/update is failed \n
        True: is insertion/update is successful.
        """
        # to step_manager as insert_step_exec
        try:
            post = {
                "step": step,
                "type": exec_class,
                "executor": exec_type,
                "dependency": dependency,
                "software_id": software_id,
                "software_name": software_name
            }
            # pp.pprint(post)
            if item_id is None:
                if self.step_exec.find_one(post) is None:
                    self.step_exec.insert_one(post)
            else:
                self.step_exec.update_one({'_id': ObjectId(item_id)}, {
                                              '$set': post}, upsert=False)
        except Exception as e:
            print(e)
            return False
        return True

    def get_software_name(self, software_id):
        """
        Retrieves the name of a software based on the software ID.
        """
        # to visualizer
        res_curs = self.software.find({"ID": software_id})
        try:
            out = next(res_curs).get('name')
            return out
        except Exception as e:
            print(e)
            return None

    def get_software_list(self):
        """
        Get a list of all registered software. \n
        Output format: "<software_id> - <software_name>"
        """
        # to visualizer
        software_id_list = []
        software_choice_format = []
        for software_details in self.software.find({'is_deleted': {'$ne': True}}):
            if software_details.get('ID') not in software_id_list:
                software_name = software_details.get('name')
                software_id = software_details.get('ID')
                software_id_list.append(software_id)
                software_choice_format.append(
                    (software_id, f"{software_id} - {software_name}"))
            else:
                pass
        # pprint(software_choice_format)
        return software_choice_format

    def add_step_translator(self, step):
        """
        Adds a new unique step variable translator.
        """
        # to manager as insert_var_translation
        post = {
            "var": step[0],
            "sentence": step[1].title()
        }
        if self.translate_step.find_one(post) is None:
            self.translate_step.insert_one(post)
        # pp.pprint(post)
        return True

    def edit_step_list(self, query, step_var_list, location_id = None):
        """
        Update step list for a specific query
        """
        # to objective_manager as update_objective_content
        self.action_collection.update_one(query, {'$set': {
            'step_list': step_var_list,
            'location_id': location_id
        }}, upsert=True)
        return True

    def get_resource_type(self, item_id):
        """
        Retrieves resource type based on the item ID
        """
        # Deprecated
        type_out = None
        if item_id[0] == 'A':
            type_out = 'human'
        elif item_id[0] == 'H':
            type_out = 'hardware'
        elif item_id[0] == 'E':
            type_out = 'robot'
        return type_out

    def add_action_collection(self, action_name, step_list):
        """
        Adds a new action-step pair collection.
        """
        # to objective_manager as insert_objective_content
        post = {
            "step_list": step_list,
            "action": action_name
        }
        # pp.pprint(post)
        _id = self.action_collection.insert_one(post)
        return _id.inserted_id

    def insert_step(self, action_var, action_sentence, step_list, step_sentence, location_id=None, action_id=None, edit=False):
        """
        Edits/Add a new step list into an action variable. \n
        If a new list is added, token DB for action-step pairs is also updated.
        """
        # to objective_manager, split and merged into insert_objective_content and update_objective_content
        if edit:
            # print(action_id)
            query = {
                '_id': ObjectId(action_id),
                'action': action_var
            }
            self.edit_step_list(query, step_list, location_id)
            inserted_id = action_id
        else:
            inserted_id = str(self.add_action_collection(
                action_var, step_list))
            self.update_action_token_db(inserted_id, action_sentence)
        for step in zip(step_list, step_sentence):
            self.add_step_translator(step)
        return inserted_id

    def update_action_token_db(self, inserted_id, action_sentence):
        """
        Updates the token database using the inputted action sentence.
        """
        # to objective_manager as update_objective_token
        tokens = tokenize_sentence(action_sentence)
        for token in tokens:
            if self.token_db_action.count_documents({'_id': token}) == 0:
                post = {
                    '_id': token,
                    'step_list_id': [inserted_id]
                }
                self.token_db_action.insert_one(post)
            else:
                self.token_db_action.update_one({'_id': token}, {'$addToSet': {
                    'step_list_id': inserted_id
                }}, upsert=False)
        return

    def delete_step_exec(self, item_id):
        """
        Delete a step-exec pair based on the ID.
        """
        # to step_manager
        query = {'_id': ObjectId(item_id)}
        self.step_exec.delete_one(query)
        return True

    def get_all_step_exec_pair(self, step, location_id):
        """
        Get all step-exec pair that fulfills the step and location_id. \n
        All pairs are returned in a list.
        """
        # deprecated
        # print(f'get_all_step_exec_pair {step} at {location_id}')
        out = []
        for step_exec_pair in self.step_exec.find({'step': step, 'avail_score': {'$gte': 0}}):
            out.append(step_exec_pair)
        # print(out)
        return out

    def get_valid_step_exec_pair(self, step, location_id):
        """
        Get the step-exec pair with the highest availability score. \n
        If two pairs has the same score, the one listed first will be returned
        """
        # deprecated
        # self.get_step_score(step, location_id)
        max_score = 0
        out = None
        for item in self.step_exec.find({'step': step, 'avail_score': {'$gte': 0}}):
            # pprint(item)
            if item['avail_score'] > max_score:
                out = item
                max_score = item['avail_score']
        return out

    def get_all_valid_step_exec_pair(self, step, location_id):
        """
        Retrieves all records with availability score > 0 based on the step.
        """
        # deprecated
        # self.update_availability_score(step, location_id)
        out = []
        for item in self.step_exec.find({'step': step, 'avail_score': {'$gte': 0}}):
            post = {
                'type': item.get('type'),
                'executor': item.get('executor'),
                'step': item.get('step')
            }
            out.append(post)
        return out

    def get_software(self, step, executor_type):
        """
        Retrieves the software based on step and executor_type.
        """
        # deprecated
        for item in self.step_exec.find({'step': step, 'type': executor_type}):
            return item['software_id']

    # def update_availability_score(self, step_var, location_id):
    #     score = -1
    #     print(f'update_availability_score_step with {location_id}')
    #     for item in self.step_exec.find({'step': step_var}):
    #         item_id = item['_id']
    #         score = self.get_step_score(item, location_id)
    #         self.step_exec.update_one({'_id': item_id}, {'$set':{
    #             'avail_score':score
    #         }}, upsert = True)
    #         # if (item.get('step') == 'place_source') or (item.get('step') == 'stir_substance'):
    #         #     print(item['step'], item['step'], item['executor'], location_id, score)
    #     return True

    def get_step_score(self, step_exec_pair, location_id):
        """
        Retrieves the availability score for the inputted step-executor pair and location_id
        """
        # todo: to context_aware
        out = 0
        # print('get_step_score_step')
        exec_list = []
        exec_type = step_exec_pair.get('executor')
        entry_id = step_exec_pair.get('_id')
        if step_exec_pair.get('type') == 'human':
            exec_list = ['user']
        elif step_exec_pair.get('type') == 'robot':
            exec_list = self.cyber_twin_module.get_avail_robot(
                exec_type, location_id)
        elif step_exec_pair.get('type') == 'hardware':
            exec_list = self.cyber_twin_module.get_avail_hardware(
                exec_type, location_id)

        # if step_exec_pair.get('step') == 'place_source':
            # print(f"{step_exec_pair['step']} with {step_exec_pair['type']} has at {location_id}")
            # print(exec_list)

        if exec_list == []:
            out = -1
        else:
            out += len(exec_list)
        # if (step_exec_pair.get('step') == 'input_settings') or (step_exec_pair.get('step') == 'heat_object'):
        #     print(step_exec_pair.get('type'))
        #     print('step score')
        #     pprint(out)
        #     pprint(step_exec_pair)
        #     print(entry_id)
            # self.step_exec.update_one({'_id': ObjectId(entry_id)}, {'$set':{
            #     'test':out
            # }}, upsert = True)
        self.step_exec.update_one({'_id': ObjectId(entry_id)}, {'$set': {
            'avail_score': out
        }}, upsert=True)
        return out
