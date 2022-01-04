from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule
from CPSBuilder.modules.archive.action_management_module import ActionManagementModule
from CPSBuilder.modules.archive.task_management_module import TaskManagementModule

from CPSBuilder.utils.db import *

import logging
logger = logging.getLogger(__name__)


class ContextAwareModule():
    """
    Module deals with any dynamic needs of the CPS builder with regards to task, actions, and stepes
    """

    def __init__(self, client):
        self.action_collection = client['action-step']['action-step-pair']
        self.translate_step = client['action-step']['step-sentence']
        self.translate_action = client['action-step']['action-sentence']
        self.executor_mapping_module = ExecutorMappingModule(client)
        self.action_management_module = ActionManagementModule(client)
        self.task_management_module = TaskManagementModule(client)

    def get_action_sentence_list(self, action_list):
        """
        Get translated sentences from a list of action variables
        """
        action_out = []

        for action_var in action_list:
            action_sentence = self.get_action_sentence(action_var)
            action_out.append(action_sentence)
            # print(action_out)
        return action_out

    def get_step_list(self, action):
        """
        Get a step list based on availability score
        """
        # Current iteration cannot generate unique step list from scratch
        # Pulls data from cloud
        action_step_list = get_item(self.action_collection, {
                                        'action': action, 'is_deleted': {'$ne': True}})
        # pprint(action_step_list)
        action_step_pair = self.action_management_module.get_max_score_item(
            action_step_list)
        if action_step_pair is not None:
            out = {
                "step_list": action_step_pair.get('step_list'),
                "step_id": str(action_step_pair.get('_id')),
                "location_id": action_step_pair.get('location_id')
            }
        else:
            out = {
                "step_list": False,
                "step_id": False,
                "location_id": False
            }
        # pprint(out)
        return out

    def get_sentence_list(self, action_step_list):
        """
        Retrieves a list of sentence based on a list of actions and stepes.
        """
        out = []
        for action_step_pair in action_step_list:
            tmp = []
            for step in action_step_pair:
                sentence = self._get_step_sentence(step)
                tmp.append(sentence)
            out.append(tmp)
        return out

    def get_sentence_one_list(self, step_list):
        """
        Retrieves a list of translated stepes based on a step variable list
        """
        out = []
        for step in step_list:
            sentence = self._get_step_sentence(step)
            out.append(sentence)
        return out

    def get_action_sentence(self, action_name):
        """
        Retrieves a translation for an action variable.
        """
        # print(action_name)
        sentence_cursor = self.translate_action.find({'var': action_name})
        # print(action_name)
        for item in sentence_cursor:
            res = item
        return res['sentence']

    def _get_step_sentence(self, step):
        """
        Retrieves a translation for a step variable
        """
        sentence_cursor = self.translate_step.find({'var': step})
        # print(step)
        for item in sentence_cursor:
            res = item
        return res['sentence']

    def check_steps(self, action, steps, step, rejected_step_ids):
        """
        Confirms that the returned step have not been selected before and is a valid step for the action
        """
        ne_filter = [{"action": action}, {'is_deleted': {'$ne': True}}]
        for rejected_step_id in rejected_step_ids:
            # print(rejected_step_id)
            ObjectId(rejected_step_id)
            ne_filter.append({"_id": {"$ne": ObjectId(rejected_step_id)}})
        query = {"$and": ne_filter}
        out = []
        for valid_step_list in self.action_collection.find(query):
            idx_check = True
            if valid_step_list['avail_score'] == -1:
                idx_check = False
            elif steps == []:
                idx_check = True
            elif len(valid_step_list['step_list']) >= steps[-1] + 1:
                for step_num in steps:
                    if step[step_num] != valid_step_list['step_list'][step_num]:
                        idx_check = False
            else:
                idx_check = False
            if idx_check:
                out.append(valid_step_list)
        if len(out) == 0:
            return False, False
        else:
            out_item = self.action_management_module.get_max_score_item(out)
            return out_item['step_list'], str(out_item['_id'])

    def get_list_of_optimized_indexes(self, action_list, actions_optimized):
        """
        Checks whether all action has been optimized and returns a list of boolean variables corresponding to the action
        """
        # print(len(actions_optimized))
        # pprint(actions_optimized)
        out = [False]*len(action_list)
        for idx, action in enumerate(action_list):
            for action_optimized in actions_optimized:
                # pprint(action_optimized)
                if int(action_optimized['action_seq']) == idx:
                    out[idx] = True
        # print(out)
        return out
