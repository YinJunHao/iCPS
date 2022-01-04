from CPSBuilder.utils.db import *
from CPSBuilder.utils.archive.module_functions import *
from bson import ObjectId
from collections import Counter

from CPSBuilder.modules.archive.resource_management_module import ResourceManagementModule

import logging
logger = logging.getLogger(__name__)


class ActionManagementModule():
    """
    Updates any dynamic status of the central database.
    E.g. resource availability for different step lists. Resource status.

    use some function in cyber twin to update "availability"
    # availability 1: Resource is functioning well
    # availability 0: Resource breaks down (cannot be used)

    # change the term "status" to "assigned" in db
    # assigned 1: Resource is not assigned to any step within an action
    # assigned 0: Resource is assigned to a step (steps with dependency) within an action

    use some function in cyber twin to update "status"
    # status 1: Resource is idle, can be used for work
    # status 0: Resource is engaged in another work
    don't use this when building; use this only in interoperation for cognitive engine to decide on next step
    """

    def __init__(self, client):
        self.step_exec = client['action-step']['step-exec-pair']
        self.action_step = client['action-step']['action-step-pair']
        self.translate_step = client['action-step']['step-sentence']
        self.translate_action = client['action-step']['action-sentence']
        self.human = client['resources']['human_resources']
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.task_collection = client['task-action']['task-action-pair']
        self.resource_management_module = ResourceManagementModule(client)
        self.token_db_action = client['search-engine']['action-token']

    def get_all_step(self):
        """
        Get all stepes registered on the database \n
        Returns: \n
        Two tuple in the form (idx, translated sentence) and (MongoID, step variable)
        Deprecated.
        """
        sentence_tuple = []
        var_id_tuple = []
        added_step = []
        idx = 0
        for step_exec_pair in self.step_exec.find():
            if step_exec_pair.get('step') not in added_step:
                pair_id = str(step_exec_pair.get('_id'))
                step_var = step_exec_pair.get('step')
                step_sentence = self.get_step_sentence(step_var)
                sentence_tuple.append((idx, step_sentence))
                var_id_tuple.append((pair_id, step_var))
                added_step.append(step_var)
                idx += 1
                # print(len(sentence_tuple), len(var_id_tuple))
        return sentence_tuple, var_id_tuple

    def register_software(self, step_var, software_name, software_id):
        """
        Registers a software to a specific step. \n
        Note: Deprecated - Method not used
        """
        post = {
            "monitor_software_name": software_name,
            "monitor_software_id": software_id
        }
        self.step_exec.update_many({'step': step_var}, {
                                       '$addToSet': post}, upsert=True)

    def decouple_software(self, step_var, software_name, software_id):
        """
        Removes a software from a specific step. \n
        Note: Deprecated - Method not used
        """
        post = {
            "monitor_software_name": software_name,
            "monitor_software_id": software_id
        }
        self.step_exec.update_many(
            {'step': step_var}, {'$pull': post})

    def insert_action(self, task_id, task_var, action_var_list, action_sentence_list):
        """
        Inserts an action list to a task. At the same time, inserts a varible to sentence translator should an appropriate translator does not exist.
        """
        # to task_manager as update_task_objective
        query = {
            '_id': ObjectId(task_id),
            'task': task_var
        }
        self.edit_action_collection(query, action_var_list)
        for action_var, action_sentence in zip(action_var_list, action_sentence_list):
            self.add_action_translator(action_var, action_sentence)
        return True

    def edit_action_collection(self, query, action_var_list):
        """
        Edit existing action list given a set of query.
        """
        # to task_manager, merged into update_task_objective
        self.task_collection.update_one(query, {'$set': {
            'action_list': action_var_list
        }}, upsert=True)
        return True

    def add_action_collection(self, action_name, step_list):
        """
        Inserts a step list to a specific action. 
        Deprecated.
        """
        post = {
            "step_list": step_list,
            "action": action_name
        }
        # pp.pprint(post)
        _id = self.action_step.insert_one(post)
        return _id.inserted_id

    def add_action_translator(self, action_name, action_sentence):
        """
        Inserts an action variable to sentence translator if an appropriate one does not exist.
        """
        # to manager, merged with insert_var_translation
        post = {
            "var": action_name,
            "sentence": action_sentence.title()
        }
        if self.translate_action.find_one(post) is None:
            self.translate_action.insert_one(post)
        # pp.pprint(post)
        return True

    def update_availability_score(self):
        """
        Updates the availability score of an action. Returns true if the update is successful. \n
        Read README for more information on availability score.
        """
        # todo: to context_aware
        # print('update_availability_score_action')
        for item in self.action_step.find():
            id = str(item['_id'])
            location_id = item.get('location_id', None)
            step_list = item.get('step_list', None)
            if (step_list is None) or (location_id is None):
                score = 0
            else:
                # print(f'update_availability_score_action with {item["action"]} at {location_id}')
                score = self.get_availability_score(
                    step_list, location_id)/len(step_list)
            self.action_step.update_one({'_id': ObjectId(id)}, {'$set': {
                # 'avail_score': 1
                'avail_score': score
            }}, upsert=True)
        return True

    def get_availability_score(self, step_list, location_id):
        """
        Retrieves the total availability score of a list of steps. \n
        Generally, only called from update_availability_score method.
        """
        # todo: to context_aware
        # print(f'get_availability_score_action with {location_id}')
        out = 0
        score = 0
        for step in step_list:
            step_exec_list = get_item(
                self.step_exec, {'step': step})
            # if (step == "place_source") or (step == "stir_substance"):
            #     pprint(step_exec_list)
            for step_exec in step_exec_list:
                score = self.resource_management_module.get_step_score(
                    step_exec, location_id)
                # if (step_exec.get('step') == 'place_source') or (step_exec.get('step') == 'stir_substance'):
                #     print(f"score for {step_exec['step']} with {step_exec['executor']}: {score}")
                #     pprint(step_exec)
                #     print('\n')
                if score > 0:
                    out += score
            # if (step == 'place_source') or  (step == 'stir_substance'):
            #     print(f"out for {step}:  {str(out)}")
        return out

    def get_max_score_item(self, action_step_list):
        """
        Retrieves the action-step pair with the highest availability score. \n
        This pairing is then used to process the step.
        """
        # todo: to context_aware
        self.update_availability_score()
        max_score = 0
        out = None
        for item in action_step_list:
            if item['avail_score'] > max_score:
                out = item
                max_score = item['avail_score']
        return out

    def get_action_step_curs(self, query=None):
        return self.action_step.find(query)

    def get_step_exec_curs(self, query=None):
        return self.step_exec.find(query)

    def get_step_exec(self, step=None, item_id=None):
        """
        Retrieves a list of all step-exec pairing for a specific step.
        """
        # to step manager
        out = []
        id_list = []
        query = {"is_deleted": {"$ne": True}}
        if step is not None:
            query['step'] = step
        elif item_id is not None:
            query['_id'] = ObjectId(item_id)
        for item in self.get_step_exec_curs(query):
            out.append(item)
            id_list.append(item['_id'])
        return out

    def get_action_step_list(self, action, sentence=False, step_list_id=None):
        """
        Retrieves all step lists for an action. \n
        Sentence modifier determines whether the step lists are returned with their translations as a tuple.
        """
        # to objective manager as get_objective_details_list
        # todo: outputs are very different
        if step_list_id is None:
            query = {'action': action, "is_deleted": {"$ne": True}}
        else:
            query = {"_id": ObjectId(step_list_id)}
        curs = self.get_action_step_curs(query)
        out = []
        id_out = []
        location_out = []
        for item in curs:
            location_out.append(item.get('location_id'))
            if sentence:
                step_list = item.get('step_list', None)
                if step_list is not None:
                    out.append(self.get_with_sentence(step_list))
                    id_out.append(str(item['_id']))
            else:
                out.append(item['step_list'])
                id_out.append(str(item['_id']))
        return out, id_out, location_out

    def get_with_sentence(self, step_list, as_tuple=True):
        """
        Get a tuple consisting of (varible, translated variable).  \n
        Generally is to be used as input in Flask Forms
        """
        # to step manager as get_sentence_list
        out = []
        for step in step_list:
            # print(step)
            sentence = self.get_step_sentence(step)
            if as_tuple:
                out.append((step, sentence))
            else:
                out.append(sentence)
        return out

    def get_step_sentence(self, step):
        """
        Translates variable to a readable sentence as defined in the database
        """
        # to manager, as get_sentence_list, merged with get_action_sentence
        sentence_cursor = self.translate_step.find({'var': step})
        res_list = []

        res = next(sentence_cursor)
        return res['sentence']

    def delete_action(self, action, action_id=None, var_idx=None, query={}):
        """
        Performs logical deletion of action-step pair
        """
        # to objective_manager as delete_objective_content
        if action_id == None:
            query['action'] = action
        else:
            query['_id'] = ObjectId(action_id)
        self.action_step.update_many(query, {"$set": {
            "is_deleted": True
        }}, upsert=True)
        return

    def delete_step(self, step):
        """
        Performs logical deletion of step-exec pair
        Deprecated.
        """
        query = {'step': step}
        self.step_exec.update_many(query,  {"$set": {
            "is_deleted": True
        }}, upsert=True)
        return

    def get_action_sentence(self, action_var):
        """
        Retrieves translation for specific variables.
        """
        # to manager, as get_sentence_list, merged with get_step_sentence
        sentence_cursor = self.translate_action.find({'var': action_var})
        for item in sentence_cursor:
            res = item
        return res['sentence']

    def get_action_recommendation(self, action_sentence):
        """
        Retrieves action recommendations based on action name input. \n
        Inputs are tokenized and matched against a database of known tokens.
        """
        # to context aware
        input_token = tokenize_sentence(action_sentence)
        hits = None
        res = []
        for token in input_token:
            for item in self.token_db_action.find({'_id': token}):
                try:
                    res += item.get('step_list_id')
                except:
                    pass
        if res == []:
            return []
        else:
            hits = Counter(res)
            search_result = []
            for key, value in hits.items():
                search_result.append((key, value))
            sorted_search = sorted(search_result, key=lambda tup: -tup[1])
            recommendations = []
            for key in sorted_search:
                for item in self.action_step.find({'_id': ObjectId(key[0]), 'is_deleted': {'$ne': True}}):
                    item_sentence = self.get_action_sentence(
                        item.get('action'))
                    step_list_sentence = []
                    step_list = item.get('step_list')
                    if step_list is not None:
                        for step in step_list:
                            step_sentence = self.get_step_sentence(
                                step)
                            step_list_sentence.append(step_sentence)
                        item['step_sentence'] = step_list_sentence
                        item['action_sentence'] = item_sentence
                        recommendations.append(item)
        return recommendations
