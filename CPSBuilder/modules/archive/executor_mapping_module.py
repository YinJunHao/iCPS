from CPSBuilder.utils.db import *
from CPSBuilder.modules.archive.resource_management_module import ResourceManagementModule

import logging
logger = logging.getLogger(__name__)


class ExecutorMappingModule():
    def __init__(self, client):
        self.step_exec = client['action-step']['step-exec-pair']
        self.human = client['resources']['human_resources']
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.software = client['resources']['software_resources']
        self.workcell_location = client['resources']['location-details']
        self.translate_step = client['action-step']['step-sentence']
        self.resource_management_module = ResourceManagementModule(client)
        # self._reset_system()

    def activate_resource(self, chosen_indexes, resource_type):
        # todo: add another function in cyber twin to do it automatically
        """
        Sets resource status and availability to 1 (activated) from front end (UI) "Manage Robot"
        """
        db, _ = self.get_db(resource_type)
        db_list = self.get_db_list(resource_type)
        for idx in chosen_indexes:
            if db_list[idx].get('_id'):
                resource_id = str(db_list[idx]['_id'])
            db.update_one({'_id': ObjectId(resource_id)}, {"$set": {
                "assigned": "1",
                "availability": "1"
            }}, upsert=False)
        return

    def deactivate_resource(self, chosen_indexes, resource_type):
        """
        Sets resource status and availability to 0 (deactivated) from front end (UI) "Manage Robot"
        """
        db, _ = self.get_db(resource_type)
        db_list = self.get_db_list(resource_type)
        for idx in chosen_indexes:
            if db_list[idx].get('_id'):
                resource_id = str(db_list[idx]['_id'])
            db.update_one({'_id': ObjectId(resource_id)}, {"$set": {
                "assigned": "0",
                "availability": "0"
            }}, upsert=False)
        return

    def get_db_list(self, resource_type):
        if resource_type == "robot":
            db = self.robot
        elif resource_type == "hardware":
            db = self.hardware
        elif resource_type == "software":
            db = self.software
        return get_item(db, None)

    def get_all_matched_exec(self, step_list, user_id, location_id=None):
        """
        Get all valid executors for the given step list. \n
        The result will be returned as a 2D list with the row indicating all valid executors in a certain step
        """
        exec_list = []
        for step_var in step_list:
            step_exec_list = self.resource_management_module.get_all_step_exec_pair(    # grab from step-exec-pair db
                step_var, location_id)      # the avail_score has to be greater than or equal 1
            tmp_exec_list = []
            # print(step_exec_list)
            for step_exec_pair in step_exec_list:
                # print(step_exec_pair)
                if step_exec_pair is None:
                    tmp_exec_list.append(
                        self.get_human_exec(step_var, user_id))
                    # todo: ^ change this, this is done so that the system won't break if there is no exec is avail for that pairing
                    print(f"There is no available executor for that step!")
                    logger.error(f"There is no available executor for that step!")
                else:
                    #
                    if (step_exec_pair['dependency'] != 'None') and (step_exec_pair['dependency'] != None) and (step_exec_pair['dependency'] != ''):
                        matched_exec = []
                        for exec_list_per_step in exec_list:    # exec_list is an embedded list for the defined step-exec pair
                            for executor in exec_list_per_step:
                                if executor.get('step_var') == step_exec_pair['dependency']:
                                    matched_exec.append(executor)
                                    print(f"the dependency name is {step_exec_pair['dependency']}")
                                    print(f"for step {step_exec_pair['step']}")
                                    print(f'depended exec is {executor}')
                                else:
                                    print(f"not depended exec is {executor}")
                        to_append = {
                            "step_var": step_var,
                            "ID": matched_exec[0].get('ID'),
                            "name": matched_exec[0].get('name'),
                            "software_id": step_exec_pair.get('software_id'),
                            "type": matched_exec[0].get('type'),
                            "software_name": self.resource_management_module.get_software_name(step_exec_pair.get('software_id')),
                            "class": step_exec_pair.get('type'),
                            "allow_alternative_exec": True,
                            "alternative_exec": self.get_alternative_exec_list(step_var, user_id, step_exec_pair.get('type'), matched_exec[0].get('ID'))
                        }
                        logger.info(
                            f"For {step_var}, exec config is {to_append}")
                        tmp_exec_list.append(to_append)
                        # print(tmp_exec_list)
                    else:   # if no dependency
                        exec_details = self._get_exec(
                            step_var, step_exec_pair, user_id, step_exec_pair.get('software_id'), location_id)
                        print(f'step without dependency is {exec_details}')
                        if exec_details:
                            tmp_exec_list.append(exec_details)
                        else:
                            logger.error('No unassigned resource available!')
                            tmp_exec_list.append(False)
                            # return False
                        # print(tmp_exec_list)
            exec_list.append(tmp_exec_list)
            # pprint(exec_list)
        self.reset_system()
        return exec_list

    def get_top_exec_list(self, step_list, user_id, location_id=None):
        """
        Get the list of best executors for a given step list
        """
        exec_list = []
        for step in step_list:
            # print(step)
            item = self.resource_management_module.get_valid_step_exec_pair(
                step, location_id)
            # pprint(item)
            if item is None:
                exec_list.append(self.get_human_exec(step, user_id))
            else:
                if (item['dependency'] != 'None') and (item['dependency'] != None) and (item['dependency'] != ''):
                    # print(item)
                    matches = []       # initialize for all match exec from the previous defined step
                    for executor in exec_list:
                        if executor.get('step_var') == item['dependency']:
                            matches.append(executor)
                    # print("matches")
                    # print(matches)
                    to_append = self.get_post(
                        step=step,
                        user_id=user_id,
                        ID=matches[0].get('ID'),
                        name=matches[0].get('name'),
                        type=matches[0].get('type'),
                        software_id=item.get('software_id'),
                        exec_class=item.get('type')
                    )
                    # print(matches)
                    exec_list.append(to_append)
                else:
                    exec_list.append(self._get_exec(
                        step, item, user_id, item.get('software_id'), location_id))
        # pprint(exec_list)
        return exec_list

    def get_alternative_exec_list(self, step, user_id, exec_class, exec_id):
        """
        Get all valid executors for a specific step for the same type and class as the chosen executor
        """
        if exec_class != "human":
            logger.info(
                f"Search alternative executors for class {exec_class}.")
            resource_db, _ = self.get_db(exec_class)
        else:
            logger.error(
                f"Search alternative executors for class {exec_class}.")
            return None
        try:
            exec_type = next(resource_db.find({'ID': exec_id})).get('type')
        except Exception as e:
            print(e)
            return None
        out = []
        for item in resource_db.find({'type': exec_type, 'availability': '1'}, {'_id': 0, 'ID': 1, 'name': 1, 'type': 1}):
            if item['ID'] != exec_id:
                item['class'] = exec_class
                out.append(item)
        logger.info(
            f'Alternative executors for {exec_id} - {exec_type} are {out}')
        return out

    def get_human(self, user_id):
        try:
            return next(self.human.find({'ID': user_id}))
        except Exception as e:
            print(e)
            return None

    def translate_compound_exec_list(self, compound_exec_list):
        """
        Converts the compound executor list that contains variables to a list that contains translated sentences. \n
        Changes are mainly in the step variable and formatting.
        """
        out = []
        # pprint(exec_list)
        for exec_list in compound_exec_list:
            tmp = []
            for executor in exec_list:
                step = executor.get('step_var')
                exec_id = executor.get('ID')
                exec_name = executor.get('name')
                software_id = executor.get('software_id')
                software_name = executor.get('software_name')
                exec_class = executor.get('class')
                allow_alternative_exec = executor.get('allow_alternative_exec')
                sentence = self._get_sentence(step)
                post = {
                    "step_sentence": sentence,
                    "ID": exec_id,
                    "name": exec_name,
                    "software_id": software_id,
                    "software_name": software_name,
                    "allow_alternative_exec" : allow_alternative_exec,
                    "class": exec_class
                }
                tmp.append(post)
            out.append(tmp)
        return out

    def translate_exec_list(self, exec_list):
        """
        Converts the executor list that contains variables to a list that contains translated sentences. \n
        Changes are mainly in the step variable and formatting.
        """
        out = []
        # pprint(exec_list)
        for executor in exec_list:
            step = executor.get('step_var')
            exec_id = executor.get('ID')
            exec_name = executor.get('name')
            software_id = executor.get('software_id')
            software_name = executor.get('software_name')
            exec_class = executor.get('class')
            allow_alternative_exec = executor.get('allow_alternative_exec')
            sentence = self._get_sentence(step)
            post = {
                "step_sentence": sentence,
                "ID": exec_id,
                "name": exec_name,
                "software_id": software_id,
                "software_name": software_name,
                "allow_alternative_exec" : allow_alternative_exec,
                "class": exec_class
            }
            out.append(post)
        return out

    def get_location_ids(self):
        """
        Retrieves all unique location_ids
        """
        out = []
        for item in self.workcell_location.find():
            try:
                out.append(item['location_id'])
            except KeyError:
                logger.error(f"No location_id found in item id: {item['_id']}")
        return set(out)

    def get_unique_exec_name(self, col_name=None):
        """
        Retrieves all unique executor names from a single resource type
        """
        out = [('user', 'user')]
        if col_name == 'robot':
            out = self._get_unique_exec_name(self.robot)
        if col_name == 'hardware':
            out = self._get_unique_exec_name(self.hardware)
        elif col_name is None:
            out += self._get_unique_exec_name(self.robot)
            out += self._get_unique_exec_name(self.hardware)
        return out

    def _get_unique_exec_name(self, col):
        out = []
        for item in col.find({}):
            if ('type' in item):
                test_item = (item['type'], item['type'])
                if (test_item not in out):
                    #print(item['type'] not in out)
                    # print(out)
                    out.append(test_item)
        return out

    def get_human_exec(self, step, user_id):
        """
        Retrieves details for a user based on the user_id and step. \n
        Result is packaged using get_post method to standardize the output with the various similar methods in this class
        """
        query = {
            'ID': user_id
        }
        tmp = get_rand_item(self.human, query)
        out = self.get_post(
            step=step,
            user_id=user_id,
            ID=tmp.get('ID'),
            name=tmp.get('name'),
            type=tmp.get('type'),
            software_id='',
            exec_class='human'
        )
        return out

    def _get_exec(self, step, item, user_id, software_id, location_id=None):
        """
        Get a valid executor given a step detail and resource type. \n
        Executor is chosen based on its location and type required by the step. \n
        Result is packaged using get_post method to standardize the output with \n
        the various similar methods in this class
        :param item is the step-exec-pair
        """
        print(f"at _get_exec {step}")
        if item.get('type') == 'human':
            print("INHUMAN")
            query = {'ID': user_id}     #don't care about location
            tmp = get_rand_item(self.human, query)
            if tmp != -1:
                out = self.get_post(
                    step=step,
                    user_id=user_id,
                    ID=tmp.get('ID'),
                    name=tmp.get('name'),
                    type=tmp.get('type'),
                    software_id='',
                    exec_class=item.get('type')     # from the step-exec-pair
                )
            else:
                return False

        elif item.get('type') == 'robot':
            print("INROBOT")
            query = {
                "type": item.get('executor'),      #executor in step-exec-pair == type in resources db
                "location_id": location_id
            }
            tmp = self.get_active_item(self.robot, query)   # returns everything that's available and not assigned
            idx = self._assign_action(tmp)  #pick one from the list ^
            if idx != -1:
                out = self.get_post(
                    step=step,
                    user_id=user_id,
                    ID=tmp[idx].get('ID'),
                    name=tmp[idx].get('name'),
                    type=tmp[idx].get('type'),
                    software_id=software_id,
                    exec_class=item.get('type'),
                    location_id=location_id
                )
                # self.robot.update_one({'ID': tmp[idx]['ID']}, {
                #                       '$set': {'assigned': '0'}}, upsert=False)
            else:
                return False
        elif item.get('type') == 'hardware':
            print(item.get('type'))
            query = {
                "type": item.get('executor'),
                "location_id": location_id
            }
            tmp = self.get_active_item(self.hardware, query)
            idx = self._assign_action(tmp)
            if idx != -1:
                out = self.get_post(
                    step=step,
                    user_id=user_id,
                    ID=tmp[idx].get('ID'),
                    name=tmp[idx].get('name'),
                    type=tmp[idx].get('type'),
                    software_id=software_id,
                    exec_class=item.get('type'),
                    location_id=location_id
                )
                # self.hardware.update_one({'ID': tmp[idx]['ID']}, {
                #                          '$set': {'assigned': '0'}}, upsert=False)
            else:
                print("All hardware assigned!")
                return False
        return out

    def get_post(self, step, user_id, ID, name, type, software_id, exec_class, location_id=None):
        """
        Method to standardize the output of an executor
        """
        if location_id is not None:
            alternative_exec = self.get_alternative_exec_list(      # from resources db
                step, user_id, exec_class, ID)
        else:
            alternative_exec = None
        software_name = self.resource_management_module.get_software_name(      #from software resource db
            software_id)
        out = {
            "step_var": step,
            "ID": ID,
            "name": name,
            "type": type,
            "software_id": software_id,
            "software_name": software_name,
            "class": exec_class,
            "allow_alternative_exec": True,
            "alternative_exec": alternative_exec
        }
        return out

    def edit_exec(self, old_exec, new_exec, user_id, location_id):
        """
        Inserts the contents of the new input and formats it into a post following the format in get_post
        """
        out = {
            "step_var": old_exec['step_var'],
            "class": old_exec['class'],
            "ID": new_exec.get('ID'),
            "name": new_exec.get('name'),
            "type": new_exec.get('type'),
            "software_id": old_exec['software_id'],
            "software_name": old_exec['software_name'],
            "allow_alternative_exec": old_exec['allow_alternative_exec'],
            "alternative_exec": self.get_alternative_exec_list(step=old_exec['step_var'],
                                                               user_id=user_id,
                                                               exec_class=old_exec['class'],
                                                               exec_id=new_exec.get(
                                                                   'ID'))
        }
        return out

    def get_active_item(self, collection, query):
        """
        Retrieves the list of all active items in the input collection according to the query.
        """
        query['assigned'] = '1'
        query['availability'] = '1'
        query['is_deleted'] = {"$ne": True}
        out = []
        # print(query)
        for i in collection.find(query):
            out.append(i)
        # for i in collection.find({'$and':[query, {'assigned':'1'}, {'availability':'1'}, {"is_deleted": {"$ne": True}}]}):
        #     out.append(i)
        # pprint(out)
        return out

    def _assign_action(self, exec_list):
        """
        Returns an random index based on the length of the exec_list input
        """
        import random
        # pprint(exec_list)
        try:
            out = random.randint(0, len(exec_list)-1)
            # print(len(exec_list))
            return out
        except:
            return -1   # there's no match

    def _get_sentence(self, step):
        """
        Retrieves the translated sentence of the input step variable
        """
        sentence_cursor = self.translate_step.find({'var': step})
        res_list = []
        for item in sentence_cursor:
            res_list.append(item)
        return res_list[0]['sentence']

    def get_software_types(self):
        """
        Retrieves all software types
        """
        out = []
        for item in self.software.find():
            try:
                if item.get('software_type', None) is None:
                    pass
                else:
                    out.append(item.get('software_type', None))
            except Exception as e:
                logger.error(f"{e} - There is an error when retrieving software type")
                pass
        return set(out)

    def get_unique_resource_type(self, resource):
        """
        Retrieves all unique resource type (camera, actuator) according to the resource class input
        """
        out = []
        if resource == "robot":
            db = self.robot
        elif resource == "hardware":
            db = self.hardware
        else:
            return False

        for item in db.find():
            try:
                out.append(item['type'])
            except:
                pass
        return set(out)

    def get_db(self, resource_type):
        """
        Retrieves the appriate DB along with the appropriate resource initial for the database.
        """
        if resource_type == "robot":
            initial = "E"
            db = self.robot
        elif resource_type == "hardware":
            initial = "H"
            db = self.hardware
        elif resource_type == "software":
            initial = "S"
            db = self.software
        elif resource_type == "human":
            initial = "A"
            db = self.human
        return db, initial

    def get_exec_list(self, resource_type, user_id=None, query=None):
        """
        Get the list of executors on a certain resource type according to the query.
        """
        out = []
        if resource_type != "human":
            db_curs = self.get_db_cursor(resource_type, query)
            for item in db_curs:
                item['resource_type'] = resource_type
                out.append(item)
        else:
            for item in self.human.find({'ID': user_id}):
                item['resource_type'] = resource_type
                out.append(item)
        return out

    def get_db_cursor(self, resource_type, query=None):
        """
        Returns a cursor to the query result for the inputted query and resource type
        """
        db, _ = self.get_db(resource_type)
        return db.find(query)

    def reset_system(self):
        """
        Resets certain var (assigned and availability) per action
        Returns assigned back to '1' (active) for all resource with availability value '1' (resource available for use)
        """
        self.robot.update_many({'availability': '1'}, {
                               '$set': {'assigned': '1'}})
        self.hardware.update_many({'availability': '1'}, {
                                  '$set': {'assigned': '1'}})
