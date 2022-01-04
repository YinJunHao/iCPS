from CPSBuilder.utils.db import *
from CPSBuilder.utils.archive.module_functions import *
from CPSBuilder.modules.archive.action_management_module import ActionManagementModule
from collections import Counter

import logging
logger = logging.getLogger(__name__)


class TaskManagementModule():
    """
    Module manages everything relating to task and task-action pairs. \n
    TaskManagementModule uses some utils from ActionManagementModule
    """

    def __init__(self, client):
        self.task_collection = client['task-action']['task-action-pair']
        self.task_sentence = client['task-action']['task-sentence']
        self.translate_action = client['action-step']['action-sentence']
        self.token_db_task = client['search-engine']['task-token']
        self.action_management_module = ActionManagementModule(client)

    def insert_task(self, task_var, task_sentence):
        """
        Inserts a new task into the collection. A new translator will also be created.
        """
        # to task manager
        self.add_task_translator(task_var, task_sentence)
        inserted_id = str(self.add_task_collection(task_var))
        self.update_task_token_db(inserted_id, task_sentence)
        return inserted_id

    def add_task_collection(self, task_var):
        # to task manager as insert_task_objective
        post = {
            "task": task_var
        }
        _id = self.task_collection.insert_one(post)
        return _id.inserted_id

    def add_task_translator(self, task_var, task_sentence):
        # to manager, merged with insert_var_translation
        post = {
            "var": task_var,
            "sentence": task_sentence.title()
        }
        if self.task_sentence.find_one(post) is None:
            self.task_sentence.insert_one(post)
        return True

    def update_task_token_db(self, inserted_id, task_sentence):
        """
        Updates the token db for task-action pairs based on the task_sentence input. \n
        The inserted_id will be added to an existing entry in the collection. \n
        If collection is new, a new entry will be created.
        """
        # to task manager as insert_to_search_engine
        tokens = tokenize_sentence(task_sentence)
        for token in tokens:
            if self.token_db_task.count_documents({'_id': token}) == 0:
                post = {
                    '_id': token,
                    'action_list_id': [inserted_id]
                }
                self.token_db_task.insert_one(post)
            else:
                self.token_db_task.update_one({'_id': token}, {'$addToSet': {
                    'action_list_id': inserted_id
                }}, upsert=False)
        return

    def get_task_list(self):
        """
        Get all registered tasks form the collection. \n
        Returns 2 lists in the form: (task_variable, task_sentence), [list of task_ids]
        """
        # to task visualizer, as get_all_task_list
        task_out = []
        task_id_list = []
        for item in self.task_collection.find({"is_deleted": {"$ne": True}}):
            task_sentence = self.get_task_sentence(item['task'])
            task_id_list.append(str(item['_id']))
            task_out.append((item['task'], task_sentence))
        return task_out, task_id_list

    def get_task_sentence(self, task):
        # to visualizer, merge with get_sentence_list
        res = {}
        for item in self.task_sentence.find({'var': task}):
            res = item
        return res.get('sentence')

    def delete_task(self, task_id):
        # to task manager as delete_task_objective
        query = {'_id': ObjectId(task_id)}
        self.task_collection.update_one(query, {"$set": {
            "is_deleted": True
        }}, upsert=True)
        # pp.pprint(next(self.task_collection.find(query)))
        return

    def get_task_recommendation(self, task_sentence):
        """
        Uses the token to suggest a similar definition based on the task_sentence input. \n
        """
        # to context aware
        """ Input is tokenized """
        input_token = tokenize_sentence(task_sentence)
        hits = None
        res = []
        """ token is matched to the token_db """
        for token in input_token:
            for item in self.token_db_task.find({'_id': token}):
                try:
                    res += item.get('action_list_id')
                except:
                    pass
        """ 
        if there is no match, return False 
        if there is a match, sort matches based on the total number of matching task-action pairs 
        """
        if res == []:
            return res
        else:
            hits = Counter(res)
            search_result = []
            for key, value in hits.items():
                search_result.append((key, value))
            sorted_search = sorted(search_result, key=lambda tup: -tup[1])
            recommendations = []
            for key in sorted_search:
                for item in self.task_collection.find({'_id': ObjectId(key[0]), 'is_deleted': {'$ne': True}}):
                    item_sentence = self.get_task_sentence(item.get('task'))
                    action_list_sentence = []
                    # pprint(item)
                    action_list = item.get('action_list')
                    if action_list is not None:
                        for action in action_list:
                            action_sentence = self.get_action_sentence(action)
                            action_list_sentence.append(action_sentence)
                        item['action_sentence'] = action_list_sentence
                        item['task_sentence'] = item_sentence
                        recommendations.append(item)
            return recommendations

    def get_action_list(self, task, exempted_actions=None):
        """
        Get a list of action based on the task definition
        """
        # to visualizer
        task_action_list = get_item(self.task_collection, {
            'task': task, "is_deleted": {"$ne": True}})
        if exempted_actions is not None:
            out = []
            for action in task_action_list[0].get('action_list'):
                if action not in exempted_actions:
                    action_sentence = self.get_action_sentence(action)
                    out.append((action, action_sentence))
        else:
            out = []
            action_list = task_action_list[0].get('action_list')
            if action_list is not None:
                for action in action_list:
                    action_sentence = self.get_action_sentence(action)
                    out.append((action, action_sentence))
        return out

    def get_action_sentence(self, action_name):
        """
        Retrieves the translated sentence of the variable input
        """
        # to visualizer, merge with get_sentence_list (duplicate)
        # print(action_name)
        sentence_cursor = self.translate_action.find({'var': action_name})
        for item in sentence_cursor:
            res = item
        return res['sentence']

