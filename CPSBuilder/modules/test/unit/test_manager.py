import unittest
from pymongo import MongoClient
from bson import ObjectId
from pprint import pprint
from CPSBuilder.modules import manager
from CPSBuilder.utils import db
import config

client = MongoClient(config.mongo_ip, config.mongo_port)
client.drop_database("test-search-engine")
client.drop_database("test-process")
client.drop_database("test-condition")
client.drop_database("test-resource")
client.drop_database("test-var-sentence")
client.drop_database("test-user")

class TesterTask(unittest.TestCase):
    def setUp(self):
        self.insert = manager.TaskInsert(client, test=True)
        self.update = manager.TaskUpdate(client, test=True)
        self.remove = manager.TaskRemove(client, test=True)

    def test_tokenize_sentence(self):
        # punctuation marks are not excluded
        sentence = "This is example-string, and coffee."
        result = self.insert.tokenize_sentence(sentence)
        print(result)
        actual = ["example-string,", "coffee."]
        self.assertEqual(result, actual)

    def test_insert_var_translation(self):
        var_sentence_pair = ("example_var", "Example var")
        result = self.insert.insert_var_translation(var_sentence_pair)
        self.assertTrue(result)

    def test_insert_task_objective(self):
        # prepare input
        user_id = "user_id"
        new_info = {
            "var": "example_var_insert",
            "sentence": "Example var insert",
            "content_layer": "objective_layer_1",
            "content_index": [1]
        }
        content_index_ObjectId_dict = {
            1: "objectId"
        }
        r1 = self.insert.insert_task_objective(user_id, new_info, content_index_ObjectId_dict)
        self.assertTrue(ObjectId.is_valid(ObjectId(r1)))
        # check if content is added to token
        query = {"content": {"$all": [r1]}}
        sr1 = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertNotEqual(sr1, [])

    def test_update_task_objective_1(self):
        '''
        When there is no previous entry (check == [])
        :return:
        '''
        # prepare this entry
        user_id = "user_id"
        old_info = {
            "var": "example_var_old_2",
            "sentence": "Example var old 2",
            "content_layer": "objective_layer_2",
            "content_index": [1]
        }
        content_index_ObjectId_dict = {
            1: "objectId"
        }
        a1 = self.insert.insert_task_objective(user_id, old_info, content_index_ObjectId_dict)
        # check if content is added to token
        query = {"content": {"$all": [a1]}}
        sr1 = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertNotEqual(sr1, [])
        # update this entry
        new_info = {
            "var": "example_var_update_1",
            "sentence": "Example var update 1",
            "content_layer": "objective_layer_1",
            "content_index": [1]
        }
        task_objective_id = a1
        r1 = self.update.update_task_objective(user_id, old_info, new_info, task_objective_id,
                                               content_index_ObjectId_dict)
        self.assertEqual(r1, a1)
        # check if content is migrated to another token
        query = {"content": {"$all": [r1]}}
        sr2 = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertNotEqual(sr2, [])
        self.assertNotEqual(sr2, sr1)

    def test_update_task_objective_2(self):
        '''
        When there is no previous entry (check == [])
        :return:
        '''
        # prepare previous entry
        user_id = "user_id"
        new_info = {
            "var": "example_var_update_2",
            "sentence": "Example var update 2",
            "content_layer": "objective_layer_1",
            "content_index": [1]
        }
        content_index_ObjectId_dict = {
            1: "objectId"
        }
        a1 = self.insert.insert_task_objective(user_id, new_info, content_index_ObjectId_dict)
        # check if content is added to token
        query = {"content": {"$all": [a1]}}
        sr1 = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertNotEqual(sr1, [])
        # prepare this entry
        old_info = {
            "var": "example_var_old_2",
            "sentence": "Example var old 2",
            "content_layer": "objective_layer_2",
            "content_index": [1]
        }
        t_id = self.insert.insert_task_objective(user_id, old_info, content_index_ObjectId_dict)
        # check if content is added to token
        query = {"content": {"$all": [t_id]}}
        sr2 = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertNotEqual(sr2, [])
        # update this entry
        task_objective_id = a1
        r1 = self.update.update_task_objective(user_id, old_info, new_info, task_objective_id,
                                               content_index_ObjectId_dict)
        self.assertEqual(r1, a1)

    def test_delete_task_objective(self):
        user_id = "user_id"
        new_info = {
            "var": "example_var_delete",
            "sentence": "Example var delete",
            "content_layer": "objective_layer_1",
            "content_index": [1]
        }
        content_index_ObjectId_dict = {
            1: "objectId"
        }
        t_id = self.insert.insert_task_objective(user_id, new_info, content_index_ObjectId_dict)
        query = {"content": {"$all": [t_id]}}
        # check if content is added to token
        sr = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertNotEqual(sr, [])
        # delete item
        task_sentence = "Example var delete"
        task_objective_id = t_id
        self.remove.delete_task_objective(user_id, task_sentence, task_objective_id)
        # check if item is deleted
        r1 = db.get_item(client["test-process"]["task-objective"], new_info)
        self.assertEqual(r1, [])
        # check if content is remove from token
        r2 = db.get_item(client["test-search-engine"]["task-token"], query)
        self.assertEqual(r2, [])


class TesterObjective(unittest.TestCase):
    def setUp(self):
        self.insert = manager.ObjectiveInsert(client, test=True)
        self.update = manager.ObjectiveUpdate(client, test=True)
        self.remove = manager.ObjectiveRemove(client, test=True)
        self.top_insert = manager.TaskInsert(client, test=True)
        self.top_update = manager.TaskUpdate(client, test=True)
        self.top_remove = manager.TaskRemove(client, test=True)

    def test_insert_objective_content(self):
        content_index_ObjectId_dict = {
            0: "id1",
            1: "content_id"
        }
        user_id = "user_id"
        new_info = {
            "var": "example_var_insert",
            "sentence": "Example var insert",
            "content_layer": "objective_layer_1",
            "content_index": [1]
        }
        r1 = self.insert.insert_objective_content(user_id, new_info, content_index_ObjectId_dict)
        self.assertTrue(ObjectId.is_valid(ObjectId(r1)))
        query = {"content": {"$all": [r1]}}
        sr1 = db.get_item(client["test-search-engine"]["objective-token"], query)
        self.assertNotEqual(sr1, [])

    def test_insert_objective_contents(self):
        content_index_ObjectId_dict = {
            0: "id1",
            1: "content_id"
        }
        user_id = "user_id"
        index = 0
        new_info = [
            {
                "index": index,
                "var": "example_var_insert",
                "sentence": "Example var insert",
                "content_layer": "objective_layer_1",
                "content_index": [1]
            }
        ]
        r1 = self.insert.insert_objective_contents(user_id, new_info, content_index_ObjectId_dict)
        r2 = list(r1.values())
        for r in r2:
            self.assertTrue(ObjectId.is_valid(ObjectId(r)))
        r3 = list(r1.keys())
        for r in r3:
            self.assertEqual(r, index)

    def test_update_objective_contents(self):
        '''
        When there is no previous entry (check == [])
        :return:
        '''
        # prepare this entry
        content_index_ObjectId_dict = {
            0: "id1",
            1: "id2"
        }
        user_id = "user_id"
        old_info = [
            {
                "index": 1,
                "var": "example_var_old_2",
                "sentence": "Example var old 2",
                "content_layer": "objective_layer_2",
                "content_index": [1]
            },
            {}
        ]
        a1 = self.insert.insert_objective_contents(user_id, old_info[:1], content_index_ObjectId_dict)
        a1 = list(a1.values())[0]
        old_info[0]["_id"] = a1
        # check if content is added to token
        query = {"content": {"$all": [a1]}}
        sr1 = db.get_item(client["test-search-engine"]["objective-token"], query)
        self.assertNotEqual(sr1, [])
        # update this entry
        new_info = [
            {
                "_id": a1,
                "index": 1,
                "var": "example_var_update_1",
                "sentence": "Example var update 1",
                "content_layer": "objective_layer_1",
                "content_index": [0]
            },
            {
                "_id": a1,
                "index": 1,
                "var": "example_var_update_1",
                "sentence": "Example var update 1",
                "content_layer": "objective_layer_1",
                "content_index": [0]
            }
        ]
        r1 = self.update.update_objective_contents(user_id, old_info, new_info, content_index_ObjectId_dict)
        r1 = list(r1.values())
        for r in r1:
            self.assertTrue(ObjectId.is_valid(ObjectId(r)))
            # check if content is migrated to another token
            query = {"content": {"$all": [r]}}
            sr2 = db.get_item(client["test-search-engine"]["objective-token"], query)
            self.assertNotEqual(sr2, [])
            self.assertNotEqual(sr2, sr1)

    def test_delete_objective_content(self):
        user_id = "user_id"
        new_info = {
            "var": "example_var_delete",
            "sentence": "Example var delete",
            "content_layer": "objective_layer_1",
            "content_index": [1]
        }
        content_index_ObjectId_dict = {
            1: "objectId"
        }
        t_id = self.insert.insert_objective_content(user_id, new_info, content_index_ObjectId_dict)
        query = {"content": {"$all": [t_id]}}
        # check if content is added to token
        sr = db.get_item(client["test-search-engine"]["objective-token"], query)
        self.assertNotEqual(sr, [])
        # delete item
        task_sentence = "Example var delete"
        task_objective_id = t_id
        self.remove.delete_objective_content(task_sentence, task_objective_id)
        # check if item is deleted
        r1 = db.get_item(client["test-process"]["objective-content"], new_info)
        self.assertEqual(r1, [])
        # check if content is remove from token
        r2 = db.get_item(client["test-search-engine"]["objective-token"], query)
        self.assertEqual(r2, [])


class TesterStep(unittest.TestCase):
    def setUp(self):
        self.insert = manager.StepInsert(client, test=True)
        self.update = manager.StepUpdate(client, test=True)

    def test_replace_state_with_id(self):
        # prepare state id
        state = {
            "var": "a1",
            "index": 0
        }
        _id = client["test-process"]["state-exec"].insert_one(state)
        a1_id = str(_id.inserted_id)
        # prepare input
        state_var_ObjectId_dict = {
            0: a1_id
        }
        condition_dict = {
            "isBlockedByState": [
                {
                    "index": 0,
                    "StateBlocker": [0]  # var of state
                }
            ],
            "hasPrerequisiteState": [
                {
                    "index": 0,
                    "StatePrerequisite": [0]  # var of state
                }
            ],
            "isAchievedBy": [
                {
                    "index": 0,
                    "hasPrerequisiteState": [0],
                    "StateCorrect": [0]  # var of state
                }
            ],
            "isFailedByState": [
                {
                    "index": 0,
                    "hasPrerequisiteState": [0],
                    "StateCorrect": [0],  # var of state
                    "StateWrong": [0]  # var of state
                }
            ]
        }
        # test
        r1 = self.insert.replace_state_with_id(state_var_ObjectId_dict, condition_dict)
        state_c_list = [
            "isBlockedByState",
            "hasPrerequisiteState",
            "isAchievedBy",
            "isFailedByState",
        ]
        for c_name, c_set in r1.items():
            if c_name in state_c_list:
                for c_dict in c_set:
                    for var_key, id_list in c_dict.items():
                        if var_key[0:5] == "State"[0:5]:
                            for r in id_list:
                                self.assertTrue(ObjectId.is_valid(r))

    def test_replace_step_with_id(self):
        # prepare state id
        step = {
            "var": "s1",
            "index": 0
        }
        _id = client["test-process"]["step"].insert_one(step)
        s1_id = str(_id.inserted_id)
        # prepare input
        step_index_ObjectId_dict = {
            0: s1_id
        }
        condition_dict = {
            "isBlockedByStep": [
                {
                    "StepBlocker": [0]  # var of step
                }
            ],
            "isBlockedByState": [
                {
                    "StateBlocker_ObjectId": ["state_id"]  # id of state
                }
            ],
            "hasPrerequisiteStep": [
                {
                    "StepPrerequisite_ObjectId": [0]  # var of step
                }
            ],
            "hasPrerequisiteState": [
                {
                    "StatePrerequisite_ObjectId": ["state_id"]  # id of state
                }
            ],
        }
        # test
        r1 = self.insert.replace_step_with_id(step_index_ObjectId_dict, condition_dict)
        step_c_list = [
            "isBlockedByStep",
            "hasPrerequisiteStep",
            "isAchievedBy",
            "isFailedByState",
        ]
        for c_name, c_set in r1.items():
            if c_name in step_c_list:
                for c_dict in c_set:
                    for var_key, id_list in c_dict.items():
                        if var_key[0:5] == "Step"[0:5]:
                            for r in id_list:
                                self.assertTrue(ObjectId.is_valid(r))

    def test_replace_pre_state_set_with_details(self):
        condition_dict = {
            'hasPrerequisiteState': [{'StatePrerequisite_ObjectId': ['state_ObjectId'],
                                      'index': 0}],
            'hasPrerequisiteStep': [{'StepPrerequisite_ObjectId': ['step_ObjectId'],
                                     'index': 0}],
            'isAchievedBy': [{'StateCorrect_ObjectId': ['state_ObjectId'],
                              'hasPrerequisiteState': [0],
                              'index': 0}],
            'isBlockedByState': [{'StateBlocker_ObjectId': ['state_ObjectId'],
                                  'index': 0}],
            'isBlockedByStep': [{'StepBlocker_ObjectId': ['step_ObjectId'], 'index': 0}],
            'isFailedByState': [{'StateCorrect_ObjectId': ['state_ObjectId'],
                                 'StateWrong_ObjectId': ['state_ObjectId'],
                                 'hasPrerequisiteState': [0],
                                 'index': 0}]
        }
        r1 = self.insert.replace_pre_state_set_with_details(condition_dict)
        a1 = {
            "isAchievedBy": [{'StateCorrect_ObjectId': ['state_ObjectId'],
                              'hasPrerequisiteState': [
                                  {
                                      'StatePrerequisite_ObjectId': ['state_ObjectId'],
                                      'index': 0
                                  }
                              ],
                              'index': 0}],
            "isFailedByState": [{'StateCorrect_ObjectId': ['state_ObjectId'],
                                 'StateWrong_ObjectId': ['state_ObjectId'],
                                 'hasPrerequisiteState': [
                                     {
                                         'StatePrerequisite_ObjectId': ['state_ObjectId'],
                                         'index': 0
                                     }
                                 ],
                                 'index': 0}]
        }
        self.assertCountEqual(r1["isAchievedBy"], a1["isAchievedBy"])
        self.assertCountEqual(r1["isFailedByState"], a1["isFailedByState"])

    def test_replace_pre_state_set_with_id(self):
        # prepare input
        user_id = "user_id"
        condition_dict = {
            "hasPrerequisiteState": [
                {
                    "index": 0,
                    "StatePrerequisite": [0]  # index of state
                }
            ],
            "isAchievedBy": [
                {
                    "index": 0,
                    "hasPrerequisiteState": [  # detail of hasPrerequisiteState
                        {
                            "index": 0,
                            "StatePrerequisite": [0]  # index of state
                        }
                    ],
                    "StateCorrect": [0]  # index of state
                }
            ],
            "isFailedByState": [
                {
                    "index": 0,
                    "hasPrerequisiteState": [  # detail of hasPrerequisiteState
                        {
                            "index": 0,
                            "StatePrerequisite": [0]  # index of state
                        }
                    ],
                    "StateCorrect": [0],  # index of state
                    "StateWrong": [0]  # index of state
                }
            ]
        }
        # test
        condition_dict = self.insert.replace_pre_state_set_with_id(user_id, condition_dict)
        # check results
        for c_set in condition_dict["isAchievedBy"]:
            id_list = c_set["hasPrerequisiteState_ObjectId"]
            for r in id_list:
                self.assertTrue(ObjectId.is_valid(r))
        for c_set in condition_dict["isFailedByState"]:
            id_list = c_set["hasPrerequisiteState_ObjectId"]
            for r in id_list:
                self.assertTrue(ObjectId.is_valid(r))

    def test_insert_condition(self):
        # prepare input
        user_id = "user_id"
        condition_dict = {
            'hasPrerequisiteState': [{'StatePrerequisite_ObjectId': ['state_ObjectId'],
                                      'index': 0}],
            'hasPrerequisiteStep': [{'StepPrerequisite_ObjectId': ['step_ObjectId'],
                                     'index': 0}],
            'isAchievedBy': [{'StateCorrect_ObjectId': ['state_ObjectId'],
                              'hasPrerequisiteState': [0],
                              'index': 0}],
            'isBlockedByState': [{'StateBlocker_ObjectId': ['state_ObjectId'],
                                  'index': 0}],
            'isBlockedByStep': [{'StepBlocker_ObjectId': ['step_ObjectId'], 'index': 0}],
            'isFailedByState': [{'StateCorrect_ObjectId': ['state_ObjectId'],
                                 'StateWrong_ObjectId': ['state_ObjectId'],
                                 'hasPrerequisiteState': [0],
                                 'index': 0}]
        }
        # test
        r1 = self.insert.insert_condition(user_id, condition_dict)
        for c_name, id_list in r1.items():
            for r in id_list:
                self.assertTrue(ObjectId.is_valid(r))

    def test_get_step_details(self):
        # prepare step ids
        steps = [
            {
                "step_param_ObjectId": [1],
                "step_cond_ObjectId": 0,
                "step_state_ObjectId": 0
            },
            {
                "step_param_ObjectId": [1],
                "step_cond_ObjectId": 1,
                "step_state_ObjectId": 1
            }
        ]
        _id = client["test-process"]["step"].insert_many(steps)
        step_ObjectIds = [str(inserted_id) for inserted_id in _id.inserted_ids]
        # test
        print(step_ObjectIds)
        r1, r2, r3 = self.insert.get_step_details(step_ObjectIds)
        self.assertCountEqual(r1, [0, 1])
        self.assertCountEqual(r2, [1, 1])
        self.assertCountEqual(r3, [0, 1])

    def test_insert_step_without_condition(self):
        # prepare state id
        state = {
            "index": 0,
            "var": "a1",
            "exec": [
                {
                    "class": "hardware",
                    "type": "camera",
                    "software_id": "S0000",
                }
            ]
        }
        _id = client["test-process"]["state-exec"].insert_one(state)
        a1_id = str(_id.inserted_id)
        # prepare input
        state_index_ObjectId_dict = {
            0: a1_id,
        }
        parameter = [
            {
                "index": 1,
                "var": "param_v",
                "type": "param_t"
            }
        ]
        step = {
            "index": 0,
            "var": "example_var",
            "sentence": "Example var",
            "location_id": ["loc1"],
            "step_param_index": [1],
            "step_state_index": 0
        }
        user_id = "user_id"
        # test
        r1 = self.insert.insert_step_without_condition(user_id, step, parameter, state_index_ObjectId_dict)
        self.assertTrue(ObjectId.is_valid(ObjectId(r1)))
        query = {"content": {"$all": [r1]}}
        sr1 = db.get_item(client["test-search-engine"]["step-token"], query)
        self.assertNotEqual(sr1, [])

    def test_replace_with_id_in_condition(self):
        # prepare input
        state_index_ObjectId_dict = {
            0: "state_ObjectId",
        }
        step_index_ObjectId_dict = {
            0: "step_ObjectId"
        }
        condition = [
            {
                "index": 0,
                "isBlockedByStep_index": [0],
                "hasPrerequisiteStep_index": [0],
                "isBlockedByState_index": [0],
                "hasPrerequisiteState_index": [0],
                "isAchievedBy_index": [0],
                "isFailedByState_index": [0],
            }
        ]
        isBlockedByStep = [
            {
                "index": 0,
                "StepBlocker": [0]  # var of step
            }
        ]
        isBlockedByState = [
            {
                "index": 0,
                "StateBlocker": [0]  # var of state
            }
        ]
        hasPrerequisiteStep = [
            {
                "index": 0,
                "StepPrerequisite": [0]  # var of step
            }
        ]
        hasPrerequisiteState = [
            {
                "index": 0,
                "StatePrerequisite": [0]  # var of state
            }
        ]
        isAchievedBy = [
            {
                "index": 0,
                "hasPrerequisiteState": [0],
                "StateCorrect": [0]  # var of state
            }
        ]
        isFailedByState = [
            {
                "index": 0,
                "hasPrerequisiteState": [0],
                "StateCorrect": [0],  # var of state
                "StateWrong": [0]  # var of state
            }
        ]
        user_id = "user_id"
        new_info_list = {
            "condition": condition,
            "isBlockedByStep": isBlockedByStep,
            "hasPrerequisiteStep": hasPrerequisiteStep,
            "isBlockedByState": isBlockedByState,
            "hasPrerequisiteState": hasPrerequisiteState,
            "isAchievedBy": isAchievedBy,
            "isFailedByState": isFailedByState
        }

        r1 = self.insert.replace_with_id_in_condition(user_id, state_index_ObjectId_dict, step_index_ObjectId_dict,
                                                      condition[0], new_info_list)
        print(r1)

    def test_insert_step_cond(self):
        # prepare state id
        state = {
            "index": 0,
            "var": "a1",
            "exec": [
                {
                    "class": "hardware",
                    "type": "camera",
                    "software_id": "S0000",
                }
            ]
        }
        _id = client["test-process"]["state-exec"].insert_one(state)
        a1_id = str(_id.inserted_id)
        # prepare input
        state_index_ObjectId_dict = {
            0: a1_id,
        }
        index_ObjectId_dict = {
            0: "step_ObjectId"
        }
        condition = [
            {
                "index": 0,
                "isBlockedByStep_index": [0],
                "hasPrerequisiteStep_index": [0],
                "isBlockedByState_index": [0],
                "hasPrerequisiteState_index": [0],
                "isAchievedBy_index": [0],
                "isFailedByState_index": [0],
            }
        ]
        isBlockedByStep = [
            {
                "index": 0,
                "StepBlocker": [0]  # var of step
            }
        ]
        isBlockedByState = [
            {
                "index": 0,
                "StateBlocker": [0]  # var of state
            }
        ]
        hasPrerequisiteStep = [
            {
                "index": 0,
                "StepPrerequisite": [0]  # var of step
            }
        ]
        hasPrerequisiteState = [
            {
                "index": 0,
                "StatePrerequisite": [0]  # var of state
            }
        ]
        isAchievedBy = [
            {
                "index": 0,
                "hasPrerequisiteState_index": [0],
                "StateCorrect": [0]  # var of state
            }
        ]
        isFailedByState = [
            {
                "index": 0,
                "hasPrerequisiteState": [0],
                "StateCorrect": [0],  # var of state
                "StateWrong": [0]  # var of state
            }
        ]
        step = [
            {
                "index": 0,
                "step_cond_index": 0,
            }
        ]
        user_id = "user_id"
        new_info_list = {
            "step": step,
            "condition": condition,
            "isBlockedByStep": isBlockedByStep,
            "hasPrerequisiteStep": hasPrerequisiteStep,
            "isBlockedByState": isBlockedByState,
            "hasPrerequisiteState": hasPrerequisiteState,
            "isAchievedBy": isAchievedBy,
            "isFailedByState": isFailedByState
        }
        r1 = self.insert.insert_step_cond(user_id, step[0]["step_cond_index"], new_info_list, state_index_ObjectId_dict,
                                          index_ObjectId_dict)
        print(r1)
        self.assertTrue(ObjectId.is_valid(r1))

    def test_insert_step(self):
        # prepare state id
        state = {
            "index": 0,
            "var": "a1",
            "exec": [
                {
                    "class": "hardware",
                    "type": "camera",
                    "software_id": "S0000",
                }
            ]
        }
        _id = client["test-process"]["state-exec"].insert_one(state)
        a1_id = str(_id.inserted_id)
        # prepare input
        state_index_ObjectId_dict = {
            0: a1_id,
        }
        parameter = [
            {
                "index": 1,
                "var": "param_v",
                "type": "param_t"
            }
        ]
        condition = [
            {
                "index": 0,
                "isBlockedByStep_index": [0],
                "hasPrerequisiteStep_index": [0],
                "isBlockedByState_index": [0],
                "hasPrerequisiteState_index": [0],
                "isAchievedBy_index": [0],
                "isFailedByState_index": [0],
            }
        ]
        isBlockedByStep = [
            {
                "index": 0,
                "StepBlocker": [0]  # var of step
            }
        ]
        isBlockedByState = [
            {
                "index": 0,
                "StateBlocker": [0]  # var of state
            }
        ]
        hasPrerequisiteStep = [
            {
                "index": 0,
                "StepPrerequisite": [0]  # var of step
            }
        ]
        hasPrerequisiteState = [
            {
                "index": 0,
                "StatePrerequisite": [0]  # var of state
            }
        ]
        isAchievedBy = [
            {
                "index": 0,
                "hasPrerequisiteState_index": [0],
                "StateCorrect": [0]  # var of state
            }
        ]
        isFailedByState = [
            {
                "index": 0,
                "hasPrerequisiteState": [0],
                "StateCorrect": [0],  # var of state
                "StateWrong": [0]  # var of state
            }
        ]
        step = [
            {
                "index": 0,
                "var": "example_var",
                "sentence": "Example var",
                "location_id": ["loc1"],
                "step_param_index": [1],
                "step_cond_index": 0,
                "step_state_index": 0
            }
        ]
        user_id = "user_id"
        new_info_list = {
            "step": step,
            "state": state,
            "parameter": parameter,
            "condition": condition,
            "isBlockedByStep": isBlockedByStep,
            "hasPrerequisiteStep": hasPrerequisiteStep,
            "isBlockedByState": isBlockedByState,
            "hasPrerequisiteState": hasPrerequisiteState,
            "isAchievedBy": isAchievedBy,
            "isFailedByState": isFailedByState
        }

        # test
        r1 = self.insert.insert_steps(user_id, new_info_list, state_index_ObjectId_dict)
        print(r1)
        for key, val in r1.items():
            self.assertTrue(ObjectId.is_valid(ObjectId(val)))
            query = {"content": {"$all": [val]}}
            sr1 = db.get_item(client["test-search-engine"]["step-token"], query)
            self.assertNotEqual(sr1, [])


class TesterState(unittest.TestCase):
    def setUp(self):
        self.insert = manager.StateInsert(client, test=True)
        self.update = manager.StateUpdate(client, test=True)
        self.remove = manager.StateRemove(client, test=True)

    def test_insert_state_exec(self):
        # prepare info
        user_id = "user_id"
        new_info = {
            "var": "A1",
            "sentence": "A1",
            "class": "A",
            "type": "resource",
            "exec": [
                {
                    "ID": "id",
                    "name": "name",
                    "class": "hardware",
                    "type": "camera",
                    "software_id": "software",
                }
            ],
            "index": 0
        }
        # insert
        r1 = self.insert.insert_state_exec(user_id, new_info)
        self.assertTrue(ObjectId.is_valid(ObjectId(r1)))
        r2 = db.get_item(client["test-process"]["state-exec"], {"_id": ObjectId(r1)})[0]
        r3 = r2.get("exec")
        self.assertEqual(r3, new_info["exec"])


class TesterResource(unittest.TestCase):
    def setUp(self):
        self.insert = manager.ResourceInsert(client, test=True)
        self.update = manager.TaskUpdate(client, test=True)
        self.remove = manager.TaskRemove(client, test=True)

    def test_physical_post(self):
        # prepare input
        event = "insert"
        user_id = "user_id"
        new_info = {
            "name": "example_var",
            "type": "example_task",
            "class": "hardware",
            "position_sensor_tag": "example_tag",
            "location_id": "example_location"
        }
        # test
        r1, _ = self.insert.physical_post(event, user_id, new_info)
        # check
        r1.pop("ID")
        r1.pop("last_update")
        r1.pop("creation_timestamp")
        a1 = {
            'name': "example_var",
            'type': "example_task",
            'class': "hardware",
            'assigned': '1',
            'availability': '1',
            'status': '1',
            'online': False,
            'location_id': "example_location",
            'address': {
                'ip': None,
                'port': None
            },
            'coordinate': {
                'x': 0,
                'y': 0,
                'z': 0,
                'position_sensor_tag': "example_tag"
            },
            'settings': {},
            "created_by": user_id,
            "last_updated_by": user_id,
        }
        self.assertCountEqual(r1, a1)

    def test_cyber_post(self):
        # prepare input
        event = "insert"
        user_id = "user_id"
        new_info = {
            "name": "example_var",
            "type": "example_task",
            "class": "software",
            "param_var": "param",
            "state_var_list": ["state"],
            "directory_list": ["dir"],
            "cyber_twin_list": ["ct"]
        }
        # test
        r1, _ = self.insert.cyber_post(event, user_id, new_info)
        # check
        r1.pop("ID")
        r1.pop("last_update")
        r1.pop("creation_timestamp")
        a1 = {
            "name": "example_var",
            "type": "example_task",
            "class": "software",
            "param_var": "param",
            "state_var": ["state"],
            "directory": ["dir"],
            "cyber_twin": ["ct"],
            "created_by": user_id,
            "last_updated_by": user_id,
        }
        self.assertCountEqual(r1, a1)

    def test_get_new_id(self):
        r_class = "hardware"
        r1 = self.insert.get_new_id(r_class)
        a1 = "H00001"
        self.assertEqual(r1, a1)

    def test_insert_resource(self):
        # prepare input
        resource_class = "hardware"
        user_id = "user_id"
        new_info = {
            "name": "example_var",
            "type": "example_task",
            "class": "hardware",
            "position_sensor_tag": "example_tag",
            "location_id": "example_location"
        }
        # test
        r1 = self.insert.insert_resource(resource_class, user_id, new_info)
        # check
        self.assertTrue(ObjectId.is_valid(ObjectId(r1)))


class TesterProfile(unittest.TestCase):
    def setUp(self):
        self.edit = manager.ProfileManager(client, test=True)

    def test_edit_profile(self):
        # prepare input
        new_info = {
            "user_id": "user_id",
            "name": "test profile",
            "position": "test position",
            "is_admin": True
        }
        # test
        check = self.edit.edit_profile("user_id", new_info)
        # check
        self.assertEqual(check, "user_id")



if __name__ == '__main__':
    unittest.main()
