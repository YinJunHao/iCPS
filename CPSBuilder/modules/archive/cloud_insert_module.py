from pymongo import MongoClient
from CPSBuilder.utils.db import *

import logging
logger = logging.getLogger(__name__)


class CloudInsertModule():
    def __init__(self, client):
        self.action_exec = client['action-exec-collection']

    def insert_to_db(self, action, step_list_id, user_id):
        """
        Inserts the built job definition to calculate the frequency score.
        """
        query = {
            "action": action,
            "step_list_id": step_list_id
        }
        res_cursor = self.action_exec[user_id].find(query)
        res = []
        for item in res_cursor:
            res.append(item)
        if len(res) == 0:  # unique step list
            query['freq'] = 1
            self.action_exec[user_id].insert(query)
        else:  # existing step list
            self.action_exec[user_id].update_one(query, {'$inc': {'freq': 1}})

    def get_popular_exec_list(self, user_id, action):
        """
        Retrieves action_definition with the highest frequency score.
        """
        cursor = self.action_exec[user_id].find({"action": action})
        step_list_id = None
        max_freq = 0
        for item in cursor:
            if item['freq'] > max_freq:
                step_list_id = item['step_list_id']
                max_freq = item['freq']
        return step_list_id

    def get_actions_optimized_idx(self, action_seq, actions_optimized=None):
        """
        Returns an index of the element in actions_optimized for the specified action
        """
        if actions_optimized == None:
            return False
        for i, action_optimized in enumerate(actions_optimized):
            if action_optimized['action_seq'] == action_seq:
                return i
            else:
                return False

    def get_step_list(self, step_exec_list):
        """
        Retrieves the step list from the list of step-executor pairs
        """
        step_list = []
        for step_exec in step_exec_list:
            step_list.append(step_exec[0].get('step_var'))
        return step_list
