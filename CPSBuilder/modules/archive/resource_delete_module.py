from CPSBuilder.utils.db import *
from bson import ObjectId
import math

import logging
logger = logging.getLogger(__name__)


class ResourceDeleteModule():
    """
    Manages deletion of resources from the database
    """

    def __init__(self, client):
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.software = client['resources']['software_resources']
        self.human = client['resources']['human_resources']
        self.location_details = client['resources']['location-details']
        self.paged_robot = self.paginate_db(self.robot)
        self.paged_hardware = self.paginate_db(self.hardware)
        self.paged_software = self.paginate_db(self.software)

    def paginate_db(self, db, page_len=10):
        # deprecated
        db = self.robot
        length = db.count()
        page_num = math.ceil(length/page_len)
        db_curs = self.robot.find()
        page_list = []
        for i in range(page_num):
            page_content = []
            for j in range(page_len):
                try:
                    item = next(db_curs)
                    page_content.append(str(item['_id']))
                except:
                    pass
            page_list.append(page_content)
        return page_list

    def get_db(self, resource_type):
        """
        Get the appropriate db according to the different resource types
        """
        # deprecated
        if resource_type == "robot":
            initial = "E"
            db = self.robot
        elif resource_type == "hardware":
            initial = "H"
            db = self.hardware
        elif resource_type == "software":
            initial = "S"
            db = self.software
        elif resource_type == "workcell":
            initial = None
            db = self.location_details
        elif resource_type == "human":
            initial = "A"
            db = self.human
        return db, initial

    def get_db_list(self, resource_type, query={}):
        """
        Query the appropriate db according tot he resource type.
        """
        # deprecated, changed to one line db_list = get_item(db, {"update": ("is_deleted", {"$ne": True})})
        query.update([("is_deleted", {"$ne": True})])
        if resource_type == "robot":
            db = self.robot
        elif resource_type == "hardware":
            db = self.hardware
        elif resource_type == "software":
            db = self.software
        elif resource_type == "workcell":
            db = self.location_details
        elif resource_type == "human":
            db = self.human
        return get_item(db, query)

    def get_unique_item(self, resource_type, category_check):
        """
        Returns a list of unique items in the db. \n
        \n
        Parameters: \n
        resource_type: Resource type to be checked \n
        category_check: Category to be checked to ensure uniqueness of final list

        Returns: \n
        List of tuples (location_id, location_id) \n
        Note: The algorithm did not use "set" as set cannot be used to output a list of tuples. 
        """
        # to resource_manager, merged with get_unique_resource_type (from executor mapping)
        db_list = self.get_db_list(resource_type)
        unique_list = []
        out = []
        for item in db_list:
            if item[category_check] not in unique_list:
                unique_list.append(item[category_check])
                out.append((item[category_check], item[category_check]))
        return out

    def get_item_details(self, resource_type, query={}):
        # to resource_manager as get_resource_details
        out_list = []
        db_list = self.get_db_list(resource_type, query)
        for item in db_list:
            out = {}
            if item.get('_id'):
                out['_id'] = str(item['_id'])
            if item.get('ID'):
                out['ID'] = item['ID']
            if item.get('name'):
                out['name'] = item['name']
            if item.get('software_type'):
                out['software_type'] = item['software_type']
            if item.get('type'):
                out['item_type'] = item.get('type', 'user')
            if item.get('location_id'):
                out['location_id'] = item['location_id']
            if item.get('workcell_id'):
                out['workcell_id'] = item['workcell_id']
            if item.get('location_name'):
                out['location_name'] = item['location_name']
            if item.get('coordinate'):
                out['coordinate'] = item['coordinate']
            out_list.append(out)
        # pp.pprint(out_list)
        return out_list

    def get_choices(self, resource_type, query={}):
        # to resource_manager as get_resource_list
        out_list = []
        db_list = self.get_item_details(resource_type, query)
        for idx, item in enumerate(db_list):
            value = idx
            label = [item.get('ID'), item.get('_id')]
            out_list.append((str(value), label))
        # pp.pprint(out_list)
        return out_list

    def delete_indicated_resource(self, chosen_indexes, resource_type):
        """
        Deletes the item in the database based on the chosen index. \n
        Resource type: "robot", "hardware", "software", "workcell"
        """
        # to resource_manager as delete_resource
        db, _ = self.get_db(resource_type)
        db_list = self.get_db_list(resource_type)
        for idx in chosen_indexes:
            # print(idx, len(db_list))
            if db_list[idx].get('_id'):
                to_del_id = str(db_list[idx]['_id'])
            db.update_one({'_id': ObjectId(to_del_id)}, {"$set": {
                "is_deleted": True
            }}, upsert=True)
            logger.info(f"{get_item(db, {'_id': ObjectId(to_del_id)})[0]} has been deleted")
        return True

    def get_db_cursor(self, resource_type, query={}):
        # to resource_manager as get_resource_cursor
        db, _ = self.get_db(resource_type)
        query.update([("is_deleted", {"$ne": True})])
        # print(query)
        return db.find(query)

    def get_equipment_details(self):
        # todo: remove '/enter_workcell/enter_equipment', so this, is no longer needed
        equipment_id_list = []
        equipment_type_list = []
        equipment_class_list = []
        for item in self.robot.find({"is_deleted": {"$ne": True}}):
            equipment_id_list.append(item.get("ID") + " - " + item.get("name"))
            equipment_type_list.append(item.get("type"))
            equipment_class_list.append("robot")
        for item in self.hardware.find({"is_deleted": {"$ne": True}}):
            equipment_id_list.append(item.get("ID") + " - " + item.get("name"))
            equipment_type_list.append(item.get("type"))
            equipment_class_list.append("hardware")
        return equipment_id_list, equipment_class_list, equipment_type_list

    def register_equipment(self, location_id, equipment_id_name, equipment_class, equipment_type):
        """
        Registers an equipment into a location_id within a workcell. \n
        Params: \n
        location_id: ID of the location within workcell. \n
        equipment_id_name: A string of the form "<equipment_id> - <equipment_name>". This is split into id and name in the method.
        equipment_class: Class of the resource: "hardware", "robot", "workcell", etc.
        equipment_type: Type of resource: "camera", "actuator", etc.
        \n
        Returns \n
        None if insertion fails. \n
        True if insertion is successful.
        """
        # to resource_manager as insert_to_location
        equipment_id = equipment_id_name.split(" - ")[0]
        equipment_name = equipment_id_name.split(" - ")[-1]
        post = {
            "class": equipment_class,
            "type": equipment_type,
            "ID": equipment_id,
            "name": equipment_name
        }
        try:
            self.location_details.update_one({'location_id': location_id}, {
                                             '$addToSet': {'hardware_contents': post}}, upsert=True)
            db, _ = self.get_db(equipment_class)

            db.update_one({"ID": equipment_id}, {
                          '$set': {"location_id": location_id}}, upsert=True)
            return True
        except Exception as e:
            print(e)
            return None

    def delete_equipment(self, location_id, equipment_details):
        """
        Removes an equipment from a location_id within a workcell. \n
        Params: \n
        location_id: ID of the location within workcell. \n
        equipment_details: A dictionary containing the entry from the DB \n
        Returns None if removal fails.
        """
        # to resource_manager as remove_from_location
        equipment_id = equipment_details.get('ID', None)
        equipment_class = equipment_details.get('class', None)
        try:
            self.location_details.update_one({'location_id': location_id}, {
                                             '$pull': {"hardware_contents": {"ID": equipment_id}}})
            db, _ = self.get_db(equipment_class)
            db.update_one({"ID": equipment_id}, {
                          '$unset': {"location_id": None}})
        except Exception as e:
            print(e)
            return None
