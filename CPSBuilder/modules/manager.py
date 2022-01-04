"""
Program title: iCPS
Project title: CPS Builder
This script manages changes of iCPS components in the database.
Written by Wong Pooi Mun.
"""

from CPSBuilder.utils.db import *
from CPSBuilder.utils.general import *
import config

from bson import ObjectId
from datetime import datetime
from pathlib import Path
from pprint import pprint
import pandas as pd

from nltk.corpus import stopwords
import nltk
import logging
logger = logging.getLogger(__name__)

nltk.download('stopwords')


class Manager():
    """
        Contain common utils to translate, get, insert, update and sort items to and from database.
    """

    def __init__(self, client, test=False, demo=False):
        # initialize db
        if test:
            self.search_engine_db = client['test-search-engine']
            self.process_db = client['test-process']
            self.condition_db = client['test-condition']
            self.resource_db = client['test-resource']
            self.user_db = client['test-user']
        else:
            self.search_engine_db = client['search-engine']
            self.process_db = client['process']
            self.condition_db = client['condition']
            self.resource_db = client['resource']
            self.user_db = client['user']
        # initialize db collections
        self.var_sentence_col = self.process_db['var-sentence']
        self.task_token_col = self.search_engine_db['task-token']
        self.objective_token_col = self.search_engine_db['objective-token']
        self.step_token_col = self.search_engine_db['step-token']
        self.task_objective_col = self.process_db['task-objective']
        self.objective_content_col = self.process_db['objective-content']
        self.step_col = self.process_db['step']
        self.step_cond_col = self.process_db['step-cond']
        self.step_param_col = self.process_db['step-param']
        self.state_exec_col = self.process_db['state-exec']
        self.blocker_step_col = self.condition_db['isBlockedByStep']
        self.blocker_state_col = self.condition_db['isBlockedByState']
        self.pre_step_col = self.condition_db['hasPrerequisiteStep']
        self.pre_state_col = self.condition_db['hasPrerequisiteState']
        self.achieve_col = self.condition_db['isAchievedBy']
        self.fail_col = self.condition_db['isFailedByState']
        self.condition_col_dict = {
            "isBlockedByStep": self.blocker_step_col,
            "isBlockedByState": self.blocker_state_col,
            "hasPrerequisiteStep": self.pre_step_col,
            "hasPrerequisiteState": self.pre_state_col,
            "isAchievedBy": self.achieve_col,
            "isFailedByState": self.fail_col,
        }
        self.physical_col = self.resource_db['physical']
        self.cyber_col = self.resource_db['cyber']
        self.location = self.resource_db['location']
        self.db_dict = {
            "human": self.physical_col,
            "robot": self.physical_col,
            "hardware": self.physical_col,
            "software": self.cyber_col,
            "location": self.location,
        }

        self.profile_col = self.user_db["profile"]

    def tokenize_sentence(self, sentence):
        """
        Splits the input sentence into words as tokens and removes stopwords defined in NLTK.

        For more info: https://pythonspot.com/nltk-stop-words/
        """
        word_list = sentence.lower().split(" ")
        filtered_words = [
            word for word in word_list if word not in stopwords.words('english')]
        return filtered_words

    def insert_var_translation(self, var_sentence_pair):
        """
        Adds a new unique variable to sentence translation.
        """
        post = {
            "var": var_sentence_pair[0],
            "sentence": var_sentence_pair[1].title()
        }
        if self.var_sentence_col.find_one(post) is None:
            self.var_sentence_col.insert_one(post)
        # pp.pprint(post)
        return True

    def translate_var(self, var):
        '''
        Translate the variable into a sentence.
        '''
        # todo: shift executor mapping get sentences into here as well.
        sentence_cursor = self.var_sentence_col.find({'var': var})
        res_list = []
        res = next(sentence_cursor)
        sentence = res['sentence']
        return sentence

    def get_var_list(self, ObjectId_list, db_col):
        '''
        Get var based on ObjectId.
        '''
        var_list = []
        for id in ObjectId_list:
            query = {
                "_id": ObjectId(id)
            }
            db_item = get_item(db_col, query)[0]
            var = db_item.get("var", None)
            var_list.append(var)
        return var_list

    def get_sentence_list(self, var_list):
        '''
        Get sentence based on var.
        '''
        sentence_list = []
        for var in var_list:
            sentence = self.translate_var(var)
            sentence_list.append(sentence)
        return sentence_list

    def get_var_sentence_tuple_list(self, var_list):
        sentence_list = self.get_sentence_list(var_list)
        var_sentence_list = zip(var_list, sentence_list)
        return var_sentence_list

    def get_all_item_list(self, db_col):
        '''
        Get all tasks in the db collection.
        var_sentence_list = [(var1, sentence1), (var2, sentence2), ...]
        item_list = [
            {
            "var":    , ... important note is this var dict in the list.
        }
        ]        '''
        query = {
            "is_deleted": {"$ne": True}
        }
        item_list = get_item(db_col, query)
        var_list = []
        id_list = []
        for item in item_list:
            var_list.append(item["var"])
            id_list.append(str(item["_id"]))
        var_sentence_list = self.get_var_sentence_tuple_list(var_list)
        return list(var_sentence_list), id_list

    def check_item_existence(self, db_col, post):
        # check if exact same post in in db before inserting a new one
        query = post
        if query.get("last_update", None) is not None:
            query.pop("last_update")
        if query.get("last_updated_by", None) is not None:
            query.pop("last_updated_by")
        if query.get("creation_timestamp", None) is not None:
            query.pop("creation_timestamp")
        if query.get("created_by", None) is not None:
            query.pop("created_by")
        check = get_item(db_col, query)
        return check

    def insert_unique_post(self, db_col, post):
        post2 = post.copy()
        check = self.check_item_existence(db_col, post2)
        if len(check) == 0:  # no previous entry
            use_existing = False
            _id = db_col.insert_one(post)
            inserted_id = str(_id.inserted_id)
        else:
            use_existing = True
            inserted_id = str(check[0]["_id"])
        return inserted_id, use_existing

    def update_unique_post(self, db_col, post, old_inserted_id):
        query = {
            '_id': ObjectId(old_inserted_id),
        }
        post2 = post.copy()
        check = self.check_item_existence(db_col, post2)
        if len(check) == 0:     # if no previous entry, then update this
            use_existing = False
            inserted_id = old_inserted_id
            db_col.update_one(query, {"$set": post}, upsert=True)
        else:   # if there was previous entry, then remove this and use the previous entry
            use_existing = True
            new_inserted_id = str(check[0]["_id"])
            inserted_id = new_inserted_id
        return inserted_id, use_existing

    def update_total_usage(self, db_col, item_id, increment):
        query = {
            "_id": ObjectId(item_id)
        }
        new_info = {
            "total_usage": increment
        }
        update_one(db_col, query, new_info, method="$inc")

    def update_usage_in_task(self, db_col, item_id, increment):
        query = {
            "_id": ObjectId(item_id)
        }
        new_info = {
            "usage_in_task": increment
        }
        update_one(db_col, query, new_info, method="$inc")

    def sort_id_usage_count(self, new_ids, old_ids, new_count, old_count):
        '''
        Sort id with change in usage count (increment/decrement)
        :param new_ids: = [to be inserted ids, to be updated ids]
        :param old_ids: = [to be updated ids, to be removed ids]
        :param new_count:  = [len(to be inserted ids), len(to be updated ids)]
        :param old_count:  = [len(to be updated ids), len(to be removed ids)]
        :return:
        '''
        updated_id_with_increment = [
            step_id
            for step_id in new_ids[new_count[0]:]
            if step_id not in old_ids[:old_count[0]]
        ]
        increment_ids = union(new_ids[:new_count[0]], updated_id_with_increment)
        updated_id_with_decrement = [
            step_id
            for step_id in old_ids[:old_count[0]]
            if step_id not in new_ids[new_count[0]:]
        ]
        decrement_ids = union(old_ids[old_count[0]:], updated_id_with_decrement)
        return increment_ids, decrement_ids

    def sort_new_info(self, old_info_list, new_info_list):
        '''
        Sort the order of new info according to events.
        :param
        Order of step_details in old_info_list corresponds to new_info_list.
        Both lists include index which is the original order when on the front end.
        The indexes are used to pair the corresponding step with the upper objective layer.
        Both lists include step ObjectId.
        If the event is insert, old_info_list[idx] == {} and new_info_list != {}.
        If the event is remove, new_info_list == {} and old_info_list != {}.
        :return
        sorted_info = [to be inserted new_info, to be updated new_info]
        info_count = [len(to be inserted new_info), len(to be updated new_info)]
        '''
        # Sort ObjectId of step items according to events
        to_be_inserted = [
            new_info_list[idx]
            for idx, details in enumerate(old_info_list)  # for each step
            if details == {} and new_info_list[idx] != {}
        ]
        to_be_updated = [
            new_info_list[idx]
            for idx, details in enumerate(old_info_list)  # for each step
            if details != {} and new_info_list[idx] != {}
        ]
        sorted_info = union(to_be_inserted, to_be_updated)
        info_count = [len(to_be_inserted), len(to_be_updated)]
        index_order = [new_info["index"] for new_info in sorted_info]
        return sorted_info, info_count, index_order

    def sort_old_id(self, old_info_list, new_info_list):
        '''
        Sort the order of ObjectId according to events.
        :param
        Order of step_details in old_info_list corresponds to new_info_list.
        Both old_info_list and new_info_list includes step ObjectId.
        If the event is insert, old_info_list[idx] == {} and new_info_list != {}.
        If the event is remove, new_info_list == {} and old_info_list != {}.
        :return
        sorted_info = [to be updated new_info, to be removed new_info]
        sorted_id = [to be updated ids, to be removed ids]
        info_count = [len(to be updated new_info), len(to be removed new_info)]
        '''
        to_be_removed = [
            new_info_list[idx]
            for idx, details in enumerate(old_info_list)  # for each step
            if details != {} and new_info_list[idx] == {}
        ]
        to_be_updated = [
            new_info_list[idx]
            for idx, details in enumerate(old_info_list)  # for each step
            if details != {} and new_info_list[idx] != {}
        ]
        sorted_info = union(to_be_updated, to_be_removed)
        sorted_id = [str(info["_id"]) for info in sorted_info]
        info_count = [len(to_be_updated), len(to_be_removed)]
        return sorted_id, info_count


class ProcessManager():
    def __init__(self, client, test=False, demo=False):
        # insert modules
        self.state_insert = StateInsert(client, test, demo)
        self.step_insert = StepInsert(client, test, demo)
        self.objective_insert = ObjectiveInsert(client, test, demo)
        self.task_insert = TaskInsert(client, test, demo)
        # update modules
        self.state_update = StateUpdate(client, test, demo)
        self.step_update = StepUpdate(client, test, demo)
        self.objective_update = ObjectiveUpdate(client, test, demo)
        self.task_update = TaskUpdate(client, test, demo)
        # remove modules
        self.state_remove = StateRemove(client, test, demo)
        self.step_remove = StepRemove(client, test, demo)
        self.objective_remove = ObjectiveRemove(client, test, demo)
        self.task_remove = TaskRemove(client, test, demo)

    def insert_process(self, user_id, info):
        state_index_id_dict = self.state_insert.insert_state_execs(user_id, info["state"])
        step_index_id_dict = self.step_insert.insert_steps(user_id, info, state_index_id_dict)
        content_index_id_dict = step_index_id_dict
        max_layer = int(info["task"]["content_layer"][:len("objective_layer_")])
        for layer in range(0, max_layer):   # from 0 to max_layer -1
            content_index_id_dict = self.objective_insert.insert_objective_contents(
                user_id, info[f"objective_layer_{layer+1}"], content_index_id_dict)
        task_ObjectId = self.task_insert.insert_task_objective(user_id, info["task"], content_index_id_dict)
        return task_ObjectId

    def update_process(self, user_id, old_info, new_info, task_ObjectId):
        state_index_id_dict = self.state_update.update_state_execs(user_id, old_info["state"], new_info["state"])
        step_index_id_dict = self.step_update.update_steps(user_id, old_info, new_info, state_index_id_dict)
        content_index_id_dict = step_index_id_dict
        old_max_layer = int(old_info["task"]["content_layer"][len("objective_layer_"):])
        new_max_layer = int(new_info["task"]["content_layer"][len("objective_layer_"):])
        for layer in range(0, new_max_layer):   # from 0 to max_layer -1
            if layer+1 <= old_max_layer:
                content_index_id_dict = self.objective_update.update_objective_contents(
                    user_id, old_info[f"objective_layer_{layer+1}"], new_info[f"objective_layer_{layer+1}"],
                    content_index_id_dict)
            else:
                content_index_id_dict = self.objective_insert.insert_objective_contents(
                    user_id, new_info[f"objective_layer_{layer+1}"], content_index_id_dict)
        task_ObjectId = self.task_update.update_task_objective(
            user_id, old_info["task"], new_info["task"], task_ObjectId, content_index_id_dict)
        return task_ObjectId

    def remove_process(self, user_id, info, task_ObjectId):
        self.state_remove.remove_from_task(user_id, info["state"])
        self.step_remove.remove_from_task(user_id, info)
        max_layer = int(info["task"]["content_layer"][:len("objective_layer_")])
        for layer in range(0, max_layer):   # from 0 to max_layer -1
            self.objective_remove.remove_from_task(user_id, info[f"objective_layer_{layer+1}"])
        self.task_remove.delete_task_objective(user_id, info["task"]["sentence"], task_ObjectId)


class TaskManager(Manager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_to_search_engine(self, tokens, inserted_task_content_id):
        for token in tokens:
            query = {
                '_id': token
            }
            if self.task_token_col.count_documents(query) == 0:
                post = {
                    '_id': token,
                    'content': [inserted_task_content_id]
                }
                self.task_token_col.insert_one(post)
            else:
                new_info = {
                    'content': inserted_task_content_id
                }
                self.task_token_col.update_one(query, {'$addToSet': new_info}, upsert=False)

    def remove_from_search_engine(self, tokens, inserted_task_content_id):
        for token in tokens:
            query = {
                '_id': token
            }
            trash = {
                'content': inserted_task_content_id
            }
            self.task_token_col.update_one(query, {'$pull': trash})


class TaskInsert(TaskManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_task_objective(self, user_id, new_info, content_index_ObjectId_dict):
        """
        Adds a new task-objective pair.
        """
        content_ObjectId = [
            content_index_ObjectId_dict[content_index]
            for content_index in new_info["content_index"]
        ]
        post = {
            "var": new_info["var"],
            "layer": "task",
            "content_layer": new_info["content_layer"],
            "content_ObjectId": content_ObjectId,
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "created_by": user_id,
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # pp.pprint(post)
        inserted_id, use_existing = self.insert_unique_post(self.task_objective_col, post)
        if not use_existing:
            self.update_search_engine(inserted_id, new_info["sentence"])
            self.insert_var_translation((new_info["var"], new_info["sentence"]))
        return inserted_id

    def update_search_engine(self, inserted_task_objective_id, task_sentence):
        """
        Updates the token database using the input objective sentence.
        """
        tokens = self.tokenize_sentence(task_sentence)
        self.insert_to_search_engine(tokens, inserted_task_objective_id)


class TaskUpdate(TaskManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def update_task_objective(self, user_id, old_info, new_info, task_objective_id, content_index_ObjectId_dict):
        """
        Update content (objective) list for a specific query
        """
        content_ObjectId = [
            content_index_ObjectId_dict[content_index]
            for content_index in new_info["content_index"]
        ]
        post = {
            "var": new_info["var"],
            "layer": "task",
            "content_layer": new_info["content_layer"],
            "content_ObjectId": content_ObjectId,
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        old_inserted_id = task_objective_id
        # check if exact same post in in db before inserting a new one
        inserted_id, use_existing = self.update_unique_post(self.task_objective_col, post, old_inserted_id)
        if not use_existing:
            if new_info["var"] != old_info["var"]:
                self.update_search_engine(old_inserted_id, old_inserted_id, old_info["sentence"], new_info["sentence"])
                self.insert_var_translation((new_info["var"], new_info["sentence"]))
        else:
            self.update_search_engine(old_inserted_id, inserted_id, old_info["sentence"], new_info["sentence"])
        return inserted_id

    def update_search_engine(self, old_inserted_id, new_inserted_id, old_sentence, new_sentence):
        """
        Updates the token database using the input sentence.
        """
        old_tokens = self.tokenize_sentence(old_sentence)
        new_tokens = self.tokenize_sentence(new_sentence)
        to_be_removed = [token for token in old_tokens if token not in new_tokens]     # tokens to be removed
        to_be_updated = [token for token in new_tokens if token not in old_tokens]     # tokens to be updated
        self.remove_from_search_engine(to_be_removed, old_inserted_id)
        self.insert_to_search_engine(to_be_updated, new_inserted_id)


class TaskRemove(TaskManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def delete_task_objective(self, user_id, task_sentence, task_objective_id):
        """
        Performs logical deletion of doc.
        Called manually by user.
        """
        from pprint import pprint
        query = {
            '_id': ObjectId(task_objective_id)
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "deleted_by": user_id
        }
        self.task_objective_col.update_many(query, {"$set": new_info}, upsert=True)
        inserted_id = task_objective_id
        self.update_search_engine(inserted_id, task_sentence)

    def update_search_engine(self, inserted_task_objective_id, task_sentence):
        """
        Updates the token database using the input task sentence.
        """
        tokens = self.tokenize_sentence(task_sentence)
        self.remove_from_search_engine(tokens, inserted_task_objective_id)


class ObjectiveManager(Manager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_to_search_engine(self, tokens, inserted_objective_content_id):
        for token in tokens:
            query = {
                '_id': token
            }
            if self.objective_token_col.count_documents(query) == 0:
                post = {
                    '_id': token,
                    'content': [inserted_objective_content_id]
                }
                self.objective_token_col.insert_one(post)
            else:
                new_info = {
                    'content': inserted_objective_content_id
                }
                self.objective_token_col.update_one(query, {'$addToSet': new_info}, upsert=False)

    def remove_from_search_engine(self, tokens, inserted_objective_content_id):
        for token in tokens:
            query = {
                '_id': token
            }
            trash = {
                'content': inserted_objective_content_id
            }
            self.objective_token_col.update_one(query, {'$pull': trash})

    def update_usage_count(self, user_id, item_ids, increment):
        db_col = self.objective_content_col
        post = {
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # update usage count
        for item_id in item_ids:
            self.update_total_usage(db_col, item_id, increment)
        for item_id in unique(item_ids):
            self.update_usage_in_task(db_col, item_id, increment)
            query = {
                "_id": ObjectId(item_id)
            }
            update_one(db_col, query, post)  # update meta details


class ObjectiveInsert(ObjectiveManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_objective_contents(self, user_id, new_info_list, content_index_ObjectId_dict, usage_count=True):
        '''
        Each new_info of step/objective has an unique index attached to it.
        The unique indexes indicates which objective/task it's assigned to.
        '''
        inserted_id_list = [
            self.insert_objective_content(user_id, new_info, content_index_ObjectId_dict)
            for new_info in new_info_list
        ]
        index_order = [
            new_info["index"]
            for new_info in new_info_list
        ]
        index_inserted_id_dict = dict(zip(index_order, inserted_id_list))    # for updating objective-content
        # update usage count
        if usage_count:
            self.update_usage_count(user_id, inserted_id_list, +1)
        return index_inserted_id_dict

    def insert_objective_content(self, user_id, new_info, content_index_ObjectId_dict):
        """
        Adds a new objective-content pair .
        """
        content_ObjectId = [
            content_index_ObjectId_dict[content_index]
            for content_index in new_info["content_index"]
        ]
        post = {
            "var": new_info["var"],
            "layer": new_info["layer"],
            "content_layer": new_info["content_layer"],
            "content_ObjectId": content_ObjectId,
            "created_by": user_id,
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__()
        }
        # pp.pprint(post)
        inserted_id, use_existing = self.insert_unique_post(self.objective_content_col, post)
        if not use_existing:     # no previous entry
            self.update_search_engine(inserted_id, new_info["sentence"])
            self.insert_var_translation((new_info["var"], new_info["sentence"]))
            post = {
                "total_usage": 0,
                "usage_in_task": 0,
            }
            update_one(self.objective_content_col, {"_id": ObjectId(inserted_id)}, post)
        return inserted_id

    def update_search_engine(self, inserted_objective_content_id, objective_sentence):
        """
        Updates the token database using the input objective sentence.
        """
        tokens = self.tokenize_sentence(objective_sentence)
        self.insert_to_search_engine(tokens, inserted_objective_content_id)


class ObjectiveUpdate(ObjectiveManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        self.insert = ObjectiveInsert(client, test, demo)

    def update_objective_contents(self, user_id, old_info_list, new_info_list, content_index_ObjectId_dict):
        """
        Sort items according to events.
        Using the finalized ObjectIds and the previous ObjectIds,
        sort the items to increment in usage and decrement in usage.
        Update the usage counts.
        new_ids and new_info_list has the same order sequence.

        :param
        Order of step_details in old_info_list corresponds to new_info_list.
        Both old_info_list and new_info_list includes step ObjectId.
        If the event is insert, old_info_list[idx] == {} and new_info_list != {}.
        If the event is remove, new_info_list == {} and old_info_list != {}.
        :return: changed_id_list = [(old_ObjectId, new_ObjectId), ...] of all the finalized updated step items.
        """
        if old_info_list == new_info_list:
            # return index_inserted_id_dict
            index_order = [info["index"] for info in new_info_list]
            new_ids = [str(info["_id"]) for info in new_info_list]
        else:
            # sort items according to events
            new_info_list, new_count, index_order = self.sort_new_info(old_info_list, new_info_list)
            index_new_id_dict = self.insert.insert_objective_contents(
                user_id, new_info_list, content_index_ObjectId_dict, usage_count=False)
            new_ids = list(index_new_id_dict.values())
            old_ids, old_count = self.sort_old_id(old_info_list, new_info_list)
            increment_ids, decrement_ids = self.sort_id_usage_count(new_ids, old_ids, new_count, old_count)
            # record meta detail
            self.update_usage_count(user_id, increment_ids, +1)
            self.update_usage_count(user_id, decrement_ids, -1)
        index_inserted_id_dict = dict(zip(index_order, new_ids))    # for updating objective-content
        return index_inserted_id_dict

    def update_search_engine(self, old_inserted_id, new_inserted_id, old_sentence, new_sentence):
        """
        Updates the token database using the input sentence.
        """
        old_tokens = self.tokenize_sentence(old_sentence)
        new_tokens = self.tokenize_sentence(new_sentence)
        to_be_removed = [token for token in old_tokens if token not in new_tokens]     # tokens to be removed
        to_be_updated = [token for token in new_tokens if token not in old_tokens]     # tokens to be updated
        self.remove_from_search_engine(to_be_removed, old_inserted_id)
        self.insert_to_search_engine(to_be_updated, new_inserted_id)


class ObjectiveRemove(ObjectiveManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def remove_from_task(self, user_id, objective_list):
        for item in objective_list:
            item_id = str(item["_id"])
            self.update_usage_count(user_id, item_id, -1)

    def delete_objective_content(self, objective_sentence, objective_content_id):
        '''
        Delete inserted_id.
        Called by trash collector. Cannot be called manually.
        '''
        from pprint import pprint
        query = {
            '_id': ObjectId(objective_content_id)
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        self.objective_content_col.update_many(query, {"$set": new_info}, upsert=True)
        inserted_id = objective_content_id
        self.update_search_engine(inserted_id, objective_sentence)
        return

    def update_search_engine(self, inserted_objective_content_id, objective_sentence):
        """
        Updates the token database using the input objective sentence.
        """
        tokens = self.tokenize_sentence(objective_sentence)
        self.remove_from_search_engine(tokens, inserted_objective_content_id)


class StepManager(Manager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_to_search_engine(self, tokens, inserted_step_id):
        for token in tokens:
            query = {
                '_id': token
            }
            if self.step_token_col.count_documents(query) == 0:
                post = {
                    '_id': token,
                    'content': [inserted_step_id]
                }
                self.step_token_col.insert_one(post)
            else:
                new_info = {
                    'content': [inserted_step_id]
                }
                self.step_token_col.update_one(query, {'$addToSet': new_info}, upsert=False)

    def remove_from_search_engine(self, tokens, inserted_step_id):
        for token in tokens:
            query = {
                '_id': token
            }
            trash = {
                'content': inserted_step_id
            }
            self.step_token_col.update_one(query, {'$pull': trash})

    def replace_with_id_in_condition(
            self, user_id, state_index_ObjectId_dict, step_index_ObjectId_dict, condition_index_dict, new_info_list):
        condition_dict = dict()
        for c_name_index, c_index in condition_index_dict.items():  # for each condition
            if c_name_index != "index":
                suffix_to_be_skipped = len(c_name_index) - len("_index")
                c_name = c_name_index[:suffix_to_be_skipped]
                index_list = [c_set["index"] for c_set in new_info_list[c_name]]    # move index from c_set to list
                c_index_details_dict = dict(zip(index_list, new_info_list[c_name]))
                condition_dict[c_name] = [c_index_details_dict[index] for index in index_list]  # replace index with details
        condition_dict = self.replace_state_with_id(state_index_ObjectId_dict, condition_dict)
        condition_dict = self.replace_step_with_id(step_index_ObjectId_dict, condition_dict)
        condition_dict = self.replace_pre_state_set_with_details(condition_dict)
        condition_dict = self.replace_pre_state_set_with_id(user_id, condition_dict)
        return condition_dict

    def replace_state_with_id(self, index_ObjectId_dict, condition_dict):
        '''
        Replace state details with inserted state object id of that task.
        Assuming that the input has unique index.
        :param var_ObjectId_dict: Look up for state var and state object id
        '''
        for c_name, c in condition_dict.items():
            # if the condition has state as details
            state_detail_key_list = [
                detail_key for detail_key in condition_dict[c_name][0]  # from the first element of list
                if detail_key[0:4] == "State"[0:4]
            ]   # example: StateBlocker, StateCorrect, etc. ...
            for idx, c_set in enumerate(condition_dict[c_name]):    # for each set
                for state_detail_key in state_detail_key_list:
                    c_set[f"{state_detail_key}_ObjectId"] = [
                        index_ObjectId_dict[state_idx]      # state object id
                        if not ObjectId.is_valid(state_idx)  # if the element is not object id
                        else state_idx  # the element is an object id
                        for state_idx in c_set[state_detail_key]
                        ]
                    # remove original pre-state details list from condition dict
                    c_set.pop(state_detail_key)
        return condition_dict

    def replace_step_with_id(self, index_ObjectId_dict, condition_dict):
        '''
        Replace step details with inserted step object id of that task.
        Assuming that the input has unique index.
        :param var_ObjectId_dict: Look up for step var and step object id
        '''
        for c_name, c in condition_dict.items():
            # if the condition has state as details
            step_detail_key_list = [
                detail_key for detail_key in condition_dict[c_name][0]  # from the first element of list
                if detail_key[0:4] == "Step"[0:4]
            ]   # example: StepBlocker, StepPrerequisite, etc. ...
            for idx, c_set in enumerate(condition_dict[c_name]):    # for each set
                for step_detail_key in step_detail_key_list:
                    c_set[f"{step_detail_key}_ObjectId"] = [
                        index_ObjectId_dict[step_idx]      # state object id
                        if not ObjectId.is_valid(step_idx)  # if the element is not object id
                        else step_idx  # the element is an object id
                        for step_idx in c_set[step_detail_key]
                        ]
                    # remove original pre-state details list from condition dict
                    c_set.pop(step_detail_key)
        return condition_dict

    def replace_pre_state_set_with_details(self, condition_dict):
        '''
        The original condition dict has the "hasPrerequisiteState" condition in "details" format.
        Replace those "details" with the ObjectId that can be found from the database.
        The ObjectId can be found because the condition was inserted into the db separately earlier.
        '''
        for c_name, c in condition_dict.items():
            # if the condition needs pre-state set as details
            if any(True for c_set in c for var_key in c_set if var_key in ["hasPrerequisiteState"]):
                for idx, condition in enumerate(condition_dict[c_name]):
                    condition["hasPrerequisiteState"] = [
                        details
                        for details in condition_dict["hasPrerequisiteState"]
                        for index in condition["hasPrerequisiteState"]
                        if details["index"] == index
                    ]
        return condition_dict

    def replace_pre_state_set_with_id(self, user_id, condition_dict):
        '''
        The original condition dict has the "hasPrerequisiteState" condition in "details" format.
        Replace those "details" with the ObjectId that can be found from the database.
        The ObjectId can be found because the condition was inserted into the db separately earlier.
        '''
        for c_name, c in condition_dict.items():
            # if the condition needs pre-state set as details
            if any(True for c_set in c for var_key in c_set if var_key in ["hasPrerequisiteState"]):
                for idx, condition in enumerate(condition_dict[c_name]):
                    pre_state_dict_list = condition["hasPrerequisiteState"]
                    # insert the condition (without index) into the db separately
                    _ = self.insert_hasPrerequisiteState(user_id, pre_state_dict_list)
                    # get ObjectId; each pre_state_dict only points to one pre-state set
                    pre_state_list = [
                        get_item(self.pre_state_col, pre_state_dict)    # get list of pre-state docs from db col
                        if not ObjectId.is_valid(pre_state_dict)    # if the element is not object id
                        else [{"_id": pre_state_dict}]     # the element is an object id
                        for pre_state_dict in pre_state_dict_list
                    ]
                    condition["hasPrerequisiteState_ObjectId"] = [
                        str(pre_state[0]["_id"])    # extract only the object id of the first element in list
                        for pre_state in pre_state_list
                    ]
                    # remove original pre-state details list from condition dict
                    condition.pop("hasPrerequisiteState")
        return condition_dict

    def insert_hasPrerequisiteState(self, user_id, pre_state_dict_list):
        '''
        Insert this condition separately because this is used as part of definition of the other conditions.
        '''
        inserted_id_list = []
        for item in pre_state_dict_list:
            if item.get("index", None) is not None:
                item.pop("index")
            post = {
                "created_by": user_id,
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__()
            }
            post = {**item, **post}
            # pp.pprint(post)
            inserted_id, use_existing = self.insert_unique_post(self.pre_state_col, post)
            inserted_id_list.append(inserted_id)
        return inserted_id_list

    def insert_condition(self, user_id, condition_dict):
        '''
        Insert the rest of the conditions into the db.
        '''
        inserted_id_dict = {}
        for c_name, c_set in condition_dict.items():
            inserted_id_list = []
            for item in c_set:
                if item.get("index", None) is not None:
                    item.pop("index")
                post = {
                    "created_by": user_id,
                    "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__()
                }
                # combine condition details with these additional info
                post = {**item, **post}
                inserted_id, use_existing = self.insert_unique_post(self.condition_col_dict[c_name], post)
                inserted_id_list.append(inserted_id)
            inserted_id_dict[f"{c_name}_ObjectId"] = inserted_id_list
        return inserted_id_dict

    def get_step_details(self, step_ObjectIds):
        '''
        Access step collection to get ObjectIds of details within step.
        '''
        details = [
            get_item(self.step_col, {"_id": ObjectId(step_ObjectId)})[0]    # should have only one return
            for step_ObjectId in step_ObjectIds
        ]
        pprint(details)
        step_cond_ids = []
        step_param_ids = []
        state_exec_ids = []
        for detail in details:
            step_cond_ids.append(detail["step_cond_ObjectId"])
            step_param_ids = union(step_param_ids, detail["step_param_ObjectId"])
            state_exec_ids.append(detail["state_exec_ObjectId"])
        return step_cond_ids, step_param_ids, state_exec_ids

    def update_usage_count(self, user_id, item_ids, increment):
        db_col = self.step_col
        post = {
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # update usage count
        for item_id in item_ids:
            self.update_total_usage(db_col, item_id, increment)
        for item_id in unique(item_ids):
            self.update_usage_in_task(db_col, item_id, increment)
            query = {
                "_id": ObjectId(item_id)
            }
            update_one(db_col, query, post)  # update meta details

    def update_details_usage_count(self, user_id, old_ids, new_ids):
        old_condition_ids, old_param_ids, old_state_ids = self.get_step_details(old_ids)
        new_condition_ids, new_param_ids, new_state_ids = self.get_step_details(new_ids)
        self.update_one_detail_usage_count(self.step_cond_col, user_id, old_condition_ids, new_condition_ids)
        self.update_one_detail_usage_count(self.step_param_col, user_id, old_param_ids, new_param_ids)
        self.update_one_detail_usage_count(self.state_exec_col, user_id, old_state_ids, new_state_ids)

    def update_one_detail_usage_count(self, db_col, user_id, old_ids, new_ids):
        '''
        Update usage counts.
        One doc may be used more than once in a task. Thus, use unique to update usage_in_task.
        '''
        # record meta detail
        post = {
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # update usage counts
        for item_id in old_ids:
            self.update_total_usage(db_col, item_id, -1)
        for item_id in new_ids:

            self.update_total_usage(db_col, item_id, +1)
        for item_id in unique(old_ids):
            self.update_usage_in_task(db_col, item_id, -1)
            query = {
                "_id": ObjectId(item_id)
            }
            update_one(db_col, query, post)    # update meta details
        for item_id in unique(new_ids):
            self.update_usage_in_task(db_col, item_id, +1)
            query = {
                "_id": ObjectId(item_id)
            }
            update_one(db_col, query, post)    # update meta details


class StepInsert(StepManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_steps(self, user_id, new_info_list, state_index_ObjectId_dict, usage_count=True):
        '''
        Insert step without conditions to get step var - object id tuple dict.
        Then use the dict to insert step-cond.
        Update the inserted step-cond to the step docs.
        :param user_id:
        :param new_info_list:
        :param state_var_ObjectId_dict: Obtained after inserting/updating states.
        :param usage_count: True, if event: insert new task. False, if event: update task.
        :return:
        step_index_ObjectId_dict = dict of
        '''
        inserted_step_id_list = [
            self.insert_step_without_condition(user_id, step_info, new_info_list["parameter"], state_index_ObjectId_dict)
            for step_info in new_info_list["step"]
        ]
        index_order = [
            step_info["index"]
            for step_info in new_info_list["step"]
        ]
        index_ObjectId_dict = dict(zip(index_order, inserted_step_id_list))
        inserted_step_cond_id_list = [
            self.insert_step_cond(
                user_id, step_info["step_cond_index"], new_info_list, state_index_ObjectId_dict, index_ObjectId_dict)
            for step_info in new_info_list["step"]
        ]
        inserted_step_id_list = [
            self.add_inserted_step_cond(inserted_step_id, inserted_step_cond_id_list[idx])
            for idx, inserted_step_id in enumerate(inserted_step_id_list)
        ]   # exactly the same as previous list
        # update usage count
        if usage_count:
            self.update_usage_count(user_id, inserted_step_id_list, +1)
            self.update_details_usage_count(user_id, [], inserted_step_id_list)
        return index_ObjectId_dict

    def insert_step_without_condition(self, user_id, step_info, param_list, state_index_ObjectId_dict):
        '''
        Insert step into process db without condition described.
        Condition requires the newly inserted step ids and state ids.
        Hence, it will be added after new steps and states have been inserted into the db.
        '''
        # insert detail pairs
        inserted_step_param_id = self.insert_step_param(
            user_id, step_info["step_param_index"], param_list)
        inserted_state_exec_id = self.insert_state_exec(
            user_id, step_info["state_exec_index"], state_index_ObjectId_dict)

        # insert entry that ties condition, param and exec for that step as a single set
        post = {
            "var": step_info["var"],
            "location_id": step_info["location_id"],
            "step_param_ObjectId": inserted_step_param_id,
            "step_cond_ObjectId": "",
            "state_exec_ObjectId": inserted_state_exec_id,
            "created_by": user_id,
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        inserted_id, use_existing = self.insert_unique_post(self.step_col, post)
        if not use_existing:  # no previous entry
            post = {
                "total_usage": 0,
                "usage_in_task": 0,
            }
            update_one(self.step_col, {"_id": ObjectId(inserted_id)}, post)
            self.update_search_engine(inserted_id, step_info["sentence"])
            self.insert_var_translation((step_info["var"], step_info["sentence"]))
        return inserted_id

    def update_search_engine(self, inserted_step_id, step_sentence):
        """
        Updates the token database using the input objective sentence.
        """
        tokens = self.tokenize_sentence(step_sentence)
        self.insert_to_search_engine(tokens, inserted_step_id)

    def add_inserted_step_cond(self, inserted_step_id, inserted_step_cond_id):
        '''
        Add the inserted condition to describe the inserted step.
        '''
        # prepare post
        query = {
            "_id": ObjectId(inserted_step_id)
        }
        post = {
            'step_cond_ObjectId': inserted_step_cond_id,
        }
        # update entry that ties details for that step as a single set
        update_one(self.step_col, query, post)
        return inserted_step_id

    def insert_step_cond(
            self, user_id, step_cond_index, new_info_list, state_var_ObjectId_dict, step_var_ObjectId_dict):
        '''
        Replace all variables in condition dict with their respective object ids.
        Insert each condition.
        Insert step-cond and obtain object id.
        '''
        condition_index_dict = [
            condition
            for condition in new_info_list["condition"]
            if step_cond_index == condition["index"]
        ][0]    # should only have one
        condition_dict = self.replace_with_id_in_condition(
            user_id, state_var_ObjectId_dict, step_var_ObjectId_dict, condition_index_dict, new_info_list)
        # get condition ids
        condition_ids = self.insert_condition(user_id, condition_dict)
        # insert detail pairs
        post = {
            "isBlockedByStep_ObjectId": condition_ids["isBlockedByStep_ObjectId"],
            "isBlockedByState_ObjectId": condition_ids["isBlockedByState_ObjectId"],
            "hasPrerequisiteStep_ObjectId": condition_ids["hasPrerequisiteStep_ObjectId"],
            "hasPrerequisiteState_ObjectId": condition_ids["hasPrerequisiteState_ObjectId"],
            "isAchievedBy_ObjectId": condition_ids["isAchievedBy_ObjectId"],
            "isFailedByState_ObjectId": condition_ids["isFailedByState_ObjectId"],
            "created_by": user_id,
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # pp.pprint(post)
        inserted_id, use_existing = self.insert_unique_post(self.step_cond_col, post)
        if not use_existing:  # no previous entry
            post = {
                "total_usage": 0,
                "usage_in_task": 0,
            }
            update_one(self.step_cond_col, {"_id": ObjectId(inserted_id)}, post)
        return inserted_id

    def insert_step_param(self, user_id, param_list, param_info_list):
        # create param_index_details_dict
        param_index_list = [param["index"] for param in param_info_list]
        param_details_list = [{"var": param["var"], "type": param["type"]} for param in param_info_list]
        param_index_details_dict = dict(zip(param_index_list, param_details_list))
        # insert step-param
        inserted_id_list = []
        for param_index in param_list:
            post = {
                "param": param_index_details_dict[param_index],
                "created_by": user_id,
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            }
            # pp.pprint(post)
            inserted_id, use_existing = self.insert_unique_post(self.step_param_col, post)
            inserted_id_list.append(inserted_id)
            if not use_existing:  # no previous entry
                post = {
                    "total_usage": 0,
                    "usage_in_task": 0,
                }
                update_one(self.step_param_col, {"_id": ObjectId(inserted_id)}, post)
        return inserted_id_list

    def insert_state_exec(self, user_id, state_index, state_index_inserted_id_dict):
        """
        Adds a step-executor pair into the database.
        """
        inserted_id_list = []
        state_id = state_index_inserted_id_dict[state_index]
        post = {
            "state_ObjectId": state_id,
            "created_by": user_id,
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # pp.pprint(post)
        inserted_id, use_existing = self.insert_unique_post(self.state_exec_col, post)
        if not use_existing:  # no previous entry
            post = {
                "total_usage": 0,
                "usage_in_task": 0,
            }
            update_one(self.state_exec_col, {"_id": ObjectId(inserted_id)}, post)
        return inserted_id


class StepUpdate(StepManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        self.insert = StepInsert(client, test, demo)

    def update_steps(self, user_id, old_info_list, new_info_list, state_index_ObjectId_dict):
        '''
        Sort items according to events.
        Using the finalized ObjectIds and the previous ObjectIds,
        sort the items to increment in usage and decrement in usage.
        Update the usage counts.
        new_ids and new_info_list has the same order sequence.

        :param
        Order of step_details in old_info_list corresponds to new_info_list.
        Both old_info_list and new_info_list includes step ObjectId.
        If the event is insert, old_info_list[idx] == {} and new_info_list != {}.
        If the event is remove, new_info_list == {} and old_info_list != {}.
        :return: changed_id_list = [(old_ObjectId, new_ObjectId), ...] of all the finalized updated step items.
        '''
        if old_info_list == new_info_list:
            # return index_inserted_id_dict
            index_order = [info["index"] for info in new_info_list["step"]]
            new_ids = [str(info["_id"]) for info in new_info_list["step"]]
        else:
            # sort items according to events
            new_info_list, new_count, index_order = self.sort_new_info(old_info_list["step"], new_info_list["step"])
            index_new_id_dict = self.insert.insert_steps(user_id, new_info_list, state_index_ObjectId_dict, usage_count=False)
            new_ids = list(index_new_id_dict.values())
            old_ids, old_count = self.sort_old_id(old_info_list["step"], new_info_list["step"])
            increment_ids, decrement_ids = self.sort_id_usage_count(new_ids, old_ids, new_count, old_count)
            # record meta detail
            self.update_usage_count(user_id, increment_ids, +1)
            self.update_usage_count(user_id, decrement_ids, -1)
            # update step details
            self.update_details_usage_count(user_id, old_ids, new_ids)
        index_inserted_id_dict = dict(zip(index_order, new_ids))    # for updating objective-content
        return index_inserted_id_dict


class StepRemove(StepManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def remove_from_task(self, user_id, info):
        for item in info["step"]:
            item_id = str(item["_id"])
            self.update_usage_count(user_id, item_id, -1)
        for item in info["parameter"]:
            item_id = str(item["_id"])
            self.update_usage_count(user_id, item_id, -1)
        for item in info["condition"]:
            item_id = str(item["_id"])
            self.update_usage_count(user_id, item_id, -1)

    def delete_step(self, step_sentence, inserted_step_id):
        '''
        Delete inserted_id.
        Called by trash collector. Cannot be called manually.
        '''
        query = {
            "_id": inserted_step_id
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        self.step_col.update_many(query, {"$set": new_info}, upsert=True)
        inserted_id = inserted_step_id
        self.update_search_engine(inserted_id, step_sentence)

    def update_search_engine(self, inserted_step_id, step_sentence):
        """
        Updates the token database using the input objective sentence.
        """
        tokens = self.tokenize_sentence(step_sentence)
        self.remove_from_search_engine(tokens, inserted_step_id)

    def delete_step_cond(self, inserted_id):
        '''
        Delete inserted_id.
        Called by trash collector. Cannot be called manually.
        '''
        query = {
            "_id": inserted_id
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        self.step_cond_col.update_many(query, {"$set": new_info}, upsert=True)

    def delete_step_param(self, inserted_id):
        '''
        Delete inserted_id.
        Called by trash collector. Cannot be called manually.
        '''
        query = {
            "_id": inserted_id
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        self.step_param_col.update_many(query, {"$set": new_info}, upsert=True)

    def delete_condition(self, inserted_id, condition):
        '''
        Delete inserted_id.
        Called by trash collector. Cannot be called manually.
        '''
        query = {
            "_id": inserted_id
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        self.condition_col_dict[condition].update_many(query, {"$set": new_info}, upsert=True)


class StateManager(Manager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_exec(self, state_exec_id, inserted_exec_list):
        query = {
            "_id": ObjectId(state_exec_id),
        }
        new_info = {
            'exec': {'$each': inserted_exec_list}
        }
        self.state_exec_col.update_one(query, {'$push': new_info}, upsert=True)

    def remove_exec(self, state_exec_id, removed_exec_list):
        query = {
            "_id": ObjectId(state_exec_id),
        }
        new_info = {
            'exec': {'$in': removed_exec_list}
        }
        self.state_exec_col.update_one(query, {'$pull': new_info}, upsert=False)

    def update_usage_count(self, user_id, item_ids, increment):
        db_col = self.state_exec_col
        post = {
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        # update usage count
        for item_id in item_ids:
            self.update_total_usage(db_col, item_id, increment)
        for item_id in unique(item_ids):
            self.update_usage_in_task(db_col, item_id, increment)
            query = {
                "_id": ObjectId(item_id)
            }
            update_one(db_col, query, post)  # update meta details


class StateInsert(StateManager):
    def insert_state_execs(self, user_id, new_info_list, usage_count=True):
        '''
        Each new_info of state has an unique index attached to it.
        The unique index is used to indicate which step it's assigned to for what condition.
        '''
        inserted_id_list = [
            self.insert_state_exec(user_id, new_info)
            for new_info in new_info_list
        ]
        index_order = [
            new_info["index"]
            for new_info in new_info_list
        ]
        index_inserted_id_dict = dict(zip(index_order, inserted_id_list))    # for updating objective-content
        # update usage count
        if usage_count:
            self.update_usage_count(user_id, inserted_id_list, +1)
        return index_inserted_id_dict

    def insert_state_exec(self, user_id, new_info):
        """
        Adds a new state_exec pair.
        """
        post = {    # new_info["exec"] is inserted in self.update_exec
            "var": new_info["var"],
            "class": new_info["class"],
            "type": new_info["type"],
            "created_by": user_id,
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__()
        }
        # pp.pprint(post)
        inserted_id, use_existing = self.insert_unique_post(self.state_exec_col, post)
        self.update_exec(inserted_id, new_info, use_existing)
        if not use_existing:  # no previous entry
            post = {
                "total_usage": 0,
                "usage_in_task": 0,
            }
            update_one(self.state_exec_col, {"_id": ObjectId(inserted_id)}, post)
        return inserted_id

    def update_exec(self, inserted_id, new_info, use_existing):
        if use_existing:
            query = {
                "_id": ObjectId(inserted_id)
            }
            old_info = get_item(self.state_exec_col, query)[0] # todo: added [0]. Please handle empty list condition
        else:
            old_info = {"exec": []}
        # new_info["exec"] = [{"physical_resource_id": str(ObjectId), "cyber_resource_id": str(ObjectId)}, ...]
        # print(new_info["exec"])
        print("oldhere")
        print(old_info)
        inserted_exec = [item for item in new_info["exec"] if item not in old_info["exec"]]
        removed_exec = [item for item in old_info["exec"] if item not in new_info["exec"]]
        if len(inserted_exec) != 0:
            self.insert_exec(inserted_id, inserted_exec)
        if len(removed_exec) != 0:
            self.remove_exec(inserted_id, removed_exec)


class StateUpdate(StateManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        self.insert = StateInsert(client, test, demo)

    def update_state_execs(self, user_id, old_info_list, new_info_list):
        """
        Sort items according to events.
        Using the finalized ObjectIds and the previous ObjectIds,
        sort the items to increment in usage and decrement in usage.
        Update the usage counts.
        new_ids and new_info_list has the same order sequence.

        :param
        Order of step_details in old_info_list corresponds to new_info_list.
        Both old_info_list and new_info_list includes step ObjectId.
        If the event is insert, old_info_list[idx] == {} and new_info_list != {}.
        If the event is remove, new_info_list == {} and old_info_list != {}.
        :return: changed_id_list = [(old_ObjectId, new_ObjectId), ...] of all the finalized updated step items.
        """
        if old_info_list == new_info_list:
            # return index_inserted_id_dict
            index_order = [info["index"] for info in new_info_list]
            new_ids = [str(info["_id"]) for info in new_info_list]
        else:
            # sort items according to events
            new_info_list, new_count, index_order = self.sort_new_info(old_info_list, new_info_list)
            index_new_id_dict = self.insert.insert_state_execs(user_id, new_info_list, usage_count=False)
            new_ids = list(index_new_id_dict.values())
            old_ids, old_count = self.sort_old_id(old_info_list, new_info_list)
            increment_ids, decrement_ids = self.sort_id_usage_count(new_ids, old_ids, new_count, old_count)
            # record meta detail
            self.update_usage_count(user_id, increment_ids, +1)
            self.update_usage_count(user_id, decrement_ids, -1)
        index_inserted_id_dict = dict(zip(index_order, new_ids))    # for updating objective-content
        return index_inserted_id_dict


class StateRemove(StateManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def remove_from_task(self, user_id, state_list):
        for item in state_list:
            item_id = str(item["_id"])
            self.update_usage_count(user_id, item_id, -1)

    def delete_state_exec(self, state_exec_id):
        '''
        Delete inserted_id.
        Called by trash collector. Cannot be called manually.
        '''
        from pprint import pprint
        query = {
            '_id': ObjectId(state_exec_id)
        }
        new_info = {
            "is_deleted": True,
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        self.state_exec_col.update_many(query, {"$set": new_info}, upsert=True)


class ResourceManager(Manager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def get_post(self, resource_class, event, user_id, new_info):
        """
        Organizes kwargs into the appropriate arguments for the different resource type.
        """
        if resource_class in ["hardware", "robot", "human"]:
            post, post_id = self.physical_post(event, user_id, new_info)
        elif resource_class in ["software"]:
            post, post_id = self.cyber_post(event, user_id, new_info)
        elif resource_class in ["location"]:
            post, post_id = self.location_post(event, user_id, new_info)
        else:
            # todo: give warning
            post = None
            post_id = None
        return post, post_id

    def physical_post(self, event, user_id, new_info):
        """
        Standardizes the initial post for physical resources
        """
        post = {
            "name": new_info["name"],
            "type": new_info["type"],
            "class": new_info["class"],
            "available": new_info["available"],
            "active": new_info["active"],
            "online": new_info["online"],
            # "location_id": new_info["location_id"],
            "address": {
                "ip": None,
                "port": None
            },
            "settings": {},
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        if new_info["coordinate"]["position_sensor_tag"] is None:
            post["coordinate"] = {
                "x": new_info["coordinate"]["x"],
                "y": new_info["coordinate"]["y"],
                "z": new_info["coordinate"]["z"],
                "position_sensor_tag": None
            }
        else:
            post["coordinate"] = {
                "x": 0,
                "y": 0,
                "z": 0,
                "position_sensor_tag": new_info["coordinate"]["position_sensor_tag"]
            }

        if event == "insert":
            insert_post = {
                "created_by": user_id,
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            }
            post = {**post, **insert_post}
            post_id = self.get_new_id(new_info["class"])
        else:
            post_id = new_info["ID"]
        post["ID"] = post_id
        return post, post_id

    def cyber_post(self, event, user_id, new_info):
        """
        Standardizes the initial post for cyber resources
        """
        post = {
            "name": new_info["name"],
            "type": new_info["type"],
            "class": new_info["class"],
            "param_var": new_info["param_var"],
            "state_var": new_info["state_var"],
            "directory": new_info["directory"],
            "physical_resource_id": new_info["physical_resource_id"],
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        if event == "insert":
            insert_post = {
                "created_by": user_id,
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            }
            post = {**post, **insert_post}
            post_id = self.get_new_id(new_info["class"])
        else:
            post_id = new_info["ID"]
        post["ID"] = post_id
        return post, post_id

    def location_post(self, event, user_id, new_info):
        """
        Standardizes the initial post for location resources
        """
        post = {
            "name": new_info["name"],
            "type": new_info["type"],
            "class": new_info["class"],
            "available": new_info["available"],
            "active": new_info["active"],
            "position": {
                "x_min": float(new_info["position"]["x_min"]),  # min x
                "y_min": float(new_info["position"]["y_min"]),  # min y
                "z_min": float(new_info["position"]["z_min"]),  # min z
                "x_max": float(new_info["position"]["x_max"]),  # min x
                "y_max": float(new_info["position"]["y_max"]),  # min y
                "z_max": float(new_info["position"]["z_max"]),  # min z
            },
            "orientation": {
                "alpha": float(new_info["orientation"]["alpha"]),
                "beta": float(new_info["orientation"]["beta"]),
                "gamma": float(new_info["orientation"]["gamma"])
            },
            "content": new_info["content"],
            "content_info": new_info["content_info"],
            "last_updated_by": user_id,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        if event == "insert":
            insert_post = {
                "created_by": user_id,
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__()
            }
            post = {**post, **insert_post}
            post_id = self.get_new_id("location", workcell_id=new_info["type"])
        else:
            post_id = new_info["ID"]
        post["ID"] = post_id
        return post, post_id

    def get_new_id(self, resource_class, **kwargs):
        """
        get new resource ID, except for workcells/location details.
        """
        prefix = self.get_id_prefix(resource_class, **kwargs)
        if prefix:
            max_id = self.get_max_id(resource_class)
            suffix = self.get_id_suffix(resource_class, max_id)
            new_id = prefix + suffix
            return new_id
        else:
            # todo: change warning method
            print(f"no such resource type {resource_class}")

    def get_id_prefix(self, resource_class, **kwargs):
        """
        Retrieves the appropriate collection and initial according to the resource type
        """
        # todo: add type to prefix?
        if resource_class == "human":
            prefix = "P"
        elif resource_class == "robot":
            prefix = "E"
        elif resource_class == "hardware":
            prefix = "H"
        elif resource_class == "software":
            prefix = "S"
        elif resource_class == "location":
            prefix = "L" + "-" + kwargs["workcell_id"] + "-"
        else:
            prefix = False
        return prefix

    def get_id_suffix(self, resource_class, max_id):
        """
        Gets unique string of numbers as suffix for respective resource_class
        """
        if resource_class == "location":
            suffix = str(max_id + 1).rjust(2, "0")
        else:
            suffix = str(max_id + 1).rjust(5, "0")
        return suffix

    def get_max_id(self, resource_class):
        db = self.db_dict[resource_class]
        id_list = self.get_id_list(resource_class, db)
        if len(id_list) != 0:
            return max(id_list)
        else:
            return 0

    def get_id_list(self, resource_class, db):
        """
        Retrieves the maximum workcell ID based on existing workcell entries.
        """
        id_list = []
        for item in db.find():
            try:
                if resource_class == "location":
                    id_list.append(int(item["ID"][-2:]))
                else:
                    id_list.append(int(item["ID"][1:]))
            except:
                pass
        return id_list


class ResourceInsert(ResourceManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def insert_resource(self, resource_class, user_id, new_info):
        """
        Inserts into the db. \n
        Params: \n
        resource_class: Type of resource to be added.
        user_id: user_id that triggered the event.
        new_info: Arguments needed for the different resource types.
        """
        event = "insert"
        db_col = self.db_dict[resource_class]
        # set default variables
        new_info["available"] = True
        new_info["active"] = True
        new_info["online"] = False
        new_info["content"] = list()
        new_info["content_info"] = list()
        # get_post organizes the new_info into the appropriate arguments
        post, post_id = self.get_post(resource_class, event, user_id, new_info)
        inserted_id, use_existing = self.insert_unique_post(db_col, post)
        return inserted_id

    def insert_physical_resource_address(self, resource_class, resource_id, resource_address):
        db_col = self.db_dict[resource_class]
        query = {
            "ID": resource_id,
            "is_deleted": {"$ne": True}
        }
        new_info = {
            "address": resource_address,
            "online": True
        }
        update_one(db_col, query, new_info)


class ResourceUpdate(ResourceManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def update_resource(self, inserted_resource_id, resource_class, user_id, new_info):
        """
        Update into the db. \n
        Params: \n
        inserted_resource_id: string ObjectId of resource doc in db col.
        resource_class: Type of resource to be added.
        user_id: user_id that triggered the event.
        new_info: Arguments needed for the different resource types.
        """
        event = "update"
        db_col = self.db_dict[resource_class]
        # get_post organizes the **kwargs into the appropriate arguments
        post, post_id = self.get_post(resource_class, event, user_id, new_info)
        print(f"updating! {post}")
        old_inserted_id = inserted_resource_id
        inserted_id, use_existing = self.update_unique_post(db_col, post, old_inserted_id)
        return inserted_id, use_existing


class ResourceRemove(ResourceManager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def delete_resource(self, resource_ObjectId, resource_class):
        """
        Deletes the item in the database based on the chosen index. \n
        Resource type: "robot", "hardware", "software", "workcell"
        """
        db = self.db_dict[resource_class]
        query = {
            '_id': ObjectId(resource_ObjectId)
        }
        new_info = {
            "is_deleted": True
        }
        db.update_one(query, {"$set": new_info})
        logger.info(f"{resource_ObjectId} from {resource_class} has been deleted")
        return True


class DraftManager(Manager):
    """
        Contain utils for inheritance classes.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        if test:
            self.draft_db = client['test-draft']
        else:
            self.draft_db = client['draft']


class ProcessDraft(DraftManager):
    """
        Manage draft of process entry.
    """
    
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        self.draft_process = self.draft_db["process"]

    def insert_draft(self, user_id, info):
        """
        Saves newly created draft of process configuration.

        :param user_id: Draft is only accessible by the user that created it.
        :param info:
        info = {
            "var": task_var,
            "sentence": task_sentence,
            "draft": {
                page: page_info, ...
                }
            }        The var page is topic/title/address to each webpage on the front end.
        The var page_info contains all information of that topic in dict form.
        Example of page is "task", "objective_layer_1", ...
        """
        post = {
            "user_id": user_id,
            "var": info["var"],
            "sentence": info["sentence"],
            "draft": info["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        _id = self.draft_process.insert_one(post)
        inserted_id = str(_id.inserted_id)
        return inserted_id

    def duplicate_draft(self, draft_ObjectId):
        """"
        Saves as new a previously created draft of process configuration.

        :param draft_ObjectId: Draft object id in MongoDB.
        """
        original_post = get_item(self.draft_process, {"_id": ObjectId(draft_ObjectId)})[0]   # only one item
        post = {
            "user_id": original_post["user_id"],
            "var": original_post["var"],
            "sentence": original_post["sentence"],
            "draft": original_post["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        _id = self.draft_process.insert_one(post)
        inserted_id = str(_id.inserted_id)
        return inserted_id

    def update_draft(self, draft_ObjectId, info):
        """
        Saves previously created draft of process configuration.

        :param draft_ObjectId: Draft object id in MongoDB.
        :param info:
        info = {
            "var": task_var,
            "sentence": task_sentence,
            "draft": {
                page: page_info, ...
                }
            }
        The var page is topic/title/address to each webpage on the front end.
        The var page_info contains all information of that topic in dict form.
        Example of page is "task", "objective_layer_1", ...
        """
        query = {
            "_id": ObjectId(draft_ObjectId)
        }
        post = {
            "var": info["var"],
            "sentence": info["sentence"],
            "draft": info["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        update_one(self.draft_process, query, post)
        inserted_id = draft_ObjectId
        return inserted_id

    def archive_submitted_draft(self, draft_ObjectId, info):
        """
        Saves and submit draft of process configuration to be managed by process manager.

        If draft exists for the post that is submitted, the draft will be archived.
        If draft does not exist for post that is submitted, a draft will be newly created and archived.

        :param draft_ObjectId: Draft object id in MongoDB.
        :param info:
        info = {
            "var": task_var,
            "sentence": task_sentence,
            "draft": {
                page: page_info, ...
                }
            }
        The var page is topic/title/address to each webpage on the front end.
        The var page_info contains all information of that topic in dict form.
        Example of page is "task", "objective_layer_1", ...
        """
        post = {
            "var": info["var"],
            "sentence": info["sentence"],
            "draft": info["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "submission_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "is_deleted": True
        }
        if draft_ObjectId is not None:  # has been previously created
            query = {
                "_id": ObjectId(draft_ObjectId)
            }
            update_one(self.draft_process, query, post)
            inserted_id = draft_ObjectId
        else:   # is a newly created draft
            creation_info = {
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            }
            post = {**post, **creation_info}
            _id = self.draft_process.insert_one(post)
            inserted_id = str(_id.inserted_id)
        return inserted_id

    def discard_draft(self, draft_ObjectId, info):
        '''
        Discard draft of process configuration without saving.
        :param draft_ObjectId: Draft object id in MongoDB.
        '''
        query = {
            "_id": ObjectId(draft_ObjectId)
        }
        post = {
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "is_deleted": True
        }
        update_one(self.draft_process, query, post)
        inserted_id = draft_ObjectId
        return inserted_id


class ResourceDraft(DraftManager):
    """
        Manage draft of resource entry.
    """

    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)
        self.draft_resource = self.draft_db["resource"]

    def insert_draft(self, user_id, info):
        '''
        Saves newly created draft of resource configuration.

        :param user_id: String of draft is only accessible by the user that created it.
        :param info:
        info = {
            "class": resource_class,
            "type": resource_type,
            "name": resource_name,
            "draft": resource_info
        }
        '''
        post = {
            "user_id": user_id,
            "class": info["class"],
            "type": info["type"],
            "name": info["name"],
            "draft": info["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        _id = self.draft_resource.insert_one(post)
        inserted_id = str(_id.inserted_id)
        return inserted_id

    def update_draft(self, draft_ObjectId, info):
        '''
        Saves previously created draft of resource configuration.

        :param draft_ObjectId: String of draft object id in MongoDB.
        :param info:
        info = {
            "class": resource_class,
            "type": resource_type,
            "name": resource_name,
            "draft": resource_info
        }
        '''
        query = {
            "_id": ObjectId(draft_ObjectId)
        }
        post = {
            "class": info["class"],
            "type": info["type"],
            "name": info["name"],
            "draft": info["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
        }
        update_one(self.draft_resource, query, post)
        inserted_id = draft_ObjectId
        return inserted_id

    def archive_submitted_draft(self, draft_ObjectId, info):
        '''
        Saves and submit draft of resource configuration to be managed by resource manager.

        If draft exists for the post that is submitted, the draft will be archived.
        If draft does not exist for post that is submitted, a draft will be newly created and archived.

        :param draft_ObjectId: String of draft object id in MongoDB.
        :param info:
        info = {
            "class": resource_class,
            "type": resource_type,
            "name": resource_name,
            "draft": resource_info
        }
        '''
        post = {
            "class": info["class"],
            "type": info["type"],
            "name": info["name"],
            "draft": info["draft"],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "submission_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "is_deleted": True
        }
        if draft_ObjectId is not None:  # has been previously created
            query = {
                "_id": ObjectId(draft_ObjectId)
            }
            update_one(self.draft_resource, query, post)
            inserted_id = draft_ObjectId
        else:   # is a newly created draft
            creation_info = {
                "creation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            }
            post = {**post, **creation_info}
            _id = self.draft_resource.insert_one(post)
            inserted_id = str(_id.inserted_id)
        return inserted_id

    def discard_draft(self, draft_ObjectId):
        '''
        Discard draft of resource configuration without saving.

        :param draft_ObjectId: String of draft object id in MongoDB.
        :param session_id: The session that stored info before being sent to this method.
        '''
        query = {
            "_id": ObjectId(draft_ObjectId)
        }
        post = {
            "deletion_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            "is_deleted": True
        }
        update_one(self.draft_resource, query, post)
        inserted_id = draft_ObjectId
        return inserted_id


class ArchiveCollector(Manager):
    '''
    Archive collector runs in the background to check usage of each document in db collections.
    Checking processes are done in top-down manner.
    Collections in process db checked are objective-content, step, step-exec, step-param, step-condition, state-exec.
    All collections in condition db are checked.
    If doc is found to have 0 usage, this module will archive that doc (is_deleted = True).
    '''
    def __init__(self, client, test=False):
        super().__init__(client, test)
        # todo: incomplete. These are only drafts!!!

    def check_usage(self, objective_content_id):
        query = {
            "content_ObjectId": {
                "$all": [objective_content_id]
            }
        }
        usage_list = get_item(self.task_objective_col, query)
        if len(usage_list) == 0:  # if other superclass is using it
            used_by_others = True
        else:   # if no others is using it
            used_by_others = False
        return used_by_others


class FileManager():
    def __init__(self):
        super().__init__()


class ExcelFileManager(FileManager):
    def __init__(self, task_var, test=False, demo=False):
        super().__init__()
        if test:
            self.file_dir = "./CPSBuilder/modules/test/unit/fixture/"
        else:
            self.file_dir = config.excel_dir
        self.file_extension = ".xlsx"
        self.task_var = task_var

    def export_excel_workbook(self, onto_data):
        '''
        Write each item in the ontology data into excel workbook.
        :param onto_data: Obtained from OntologyBuilder module. (func build_ontology)
        :return:
        '''
        file_name = self.create_file_name()
        for sheet_name, post in onto_data:
            self.write_excel_sheet(post, sheet_name, file_name)

    def import_excel_workbook(self, file_name):
        '''
        Read each excel worksheet to get item of process data.
        '''
        onto_data = dict()
        dfs = pd.read_excel(file_name, sheet_name=None, dtype=str)
        for sheet_name, df in dfs.items():
            onto_data[sheet_name] = self.read_excel_sheet(df)
        return onto_data

    def create_file_name(self):
        '''
        Ensure the existence of file name for export.
        :return:
        '''
        file_name = f"{self.file_dir}{self.task_var}{self.file_extension}"
        file = Path(file_name)
        # check if file exist
        if file.exists():   # todo: improve this! Add something behind file name if exist
            file_name = file_name[:len(self.file_extension)] + "(1)" + self.file_extension
        return file_name

    def write_excel_sheet(self, post, sheet_name, file_name):
        '''
        This method convert dict of lists into dataframe and writes them into excel.
        post = {"column1": [list under column1], "column2": [list under column2], ...}
        '''
        df_content = list(zip(*post.values()))  # zip all values of post dict
        columns = list(post.keys())      # get column names
        # get dataframe and drop empty rows
        df = pd.DataFrame(df_content, columns=columns)
        df.to_excel(file_name, sheet_name=sheet_name)

    def read_excel_sheet(self, df):
        '''
        This method gets all details from worksheet to be used to build ontology.
        post = {"column1": [list under column1], "column2": [list under column2], ...}
        '''
        # get dataframe and drop empty rows
        df = df.dropna(axis=0, how="all")
        df = df.fillna(method="ffill")
        df = df.replace("nan", method="ffill")
        post = df.to_dict("list")
        return post


class ProfileManager(Manager):
    def __init__(self, client, test=False, demo=False):
        super().__init__(client, test, demo)

    def is_admin(self, position):
        """
            Determine whether newly added user has administration rights or not
        """
        if position in ["Lecturer", "Research Engineer", "PhD Student", "Master Student"]:
            return True
        else:
            return False

    def edit_profile(self, user_id, new_info):
        """
            Edits user profile details
        """
        query = {
            "user_id": user_id
        }

        post = {
            "user_id": user_id,
            "name": new_info["name"],
            "position": new_info["position"],
            "is_admin": self.is_admin(new_info["position"])
        }
        found_user = []
        for item in self.profile_col.find({"user_id": user_id}):
            found_user.append(item)
        if len(found_user) == 0:
            return False
        else:
            self.profile_col.update_one(query, {"$set": post})
            return user_id



