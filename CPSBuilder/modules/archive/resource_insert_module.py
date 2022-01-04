from flask import flash, Markup
from CPSBuilder.modules.archive.fault_detection_module import FaultDetectionModule
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class ResourceInsertModule():
    """
    Manages Insertion of resources into the collection.
    """

    def __init__(self, client):
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.software = client['resources']['software_resources']
        self.workcell_details = client['resources']['location-details']
        self.fault_detection_module = FaultDetectionModule(client)

    def robot_post(self, robot_type, robot_name, position_sensor_tag, location_id):
        """
        Standardizes the initial post for robot resources
        """
        # to resource_manager
        post = {
            'ID': self.get_new_id('robot'),
            'name': robot_name,
            'type': robot_type,
            'location_id': location_id,
            'assigned': '1',
            'availability': '1',
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            'coordinate':{
                'x': 0,
                'y': 0,
                'z': 0,
                'position_sensor_tag': position_sensor_tag
            }
        }
        return post

    def hardware_post(self, hardware_name, hardware_type, position_sensor_tag, location_id):
        """
        Standardizes the initial post for hardware resources
        """
        # to resource_manager
        post = {
            'ID': self.get_new_id('hardware'),
            'name': hardware_name,
            'type': hardware_type,
            'assigned': '1',
            'availability': '1',
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            'coordinate': {
                'x': 0,
                'y': 0,
                'z': 0,
                'position_sensor_tag': position_sensor_tag
            },
            'location_id': location_id,
        }
        return post

    def software_post(self, software_name, software_type):
        """
        Standardizes the initial post for software resources
        """
        # to resource_manager
        post_id = self.get_new_id('software')
        post = {
            'ID': post_id,
            'name': software_name,
            'software_type': software_type,
            # 'software_step': software_step,
            # 'software_step_id': software_step_id,
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__()
        }
        return post, post_id

    def workcell_post(self, workcell_id, location_name, x_min, x_max, y_min, y_max, z_min, z_max):
        """
        Standardizes the initial post for workcell resources
        """
        # to resource_manager as location_post
        post = {
            'workcell_id': workcell_id,
            'location_id': self.get_location_id(workcell_id),
            'location_name': location_name,
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S").__str__(),
            'coordinate': {
                'x_min': float(x_min),
                'x_max': float(x_max),
                'y_min': float(y_min),
                'y_max': float(y_max),
                'z_min': float(z_min),
                'z_max': float(z_max)
            }
        }
        return post

    def insert_to_db(self, resource_type, **kwargs):
        """
        Inserts into the db. \n
        Params: \n
        resource_type: Type of resource to be added. \n
        **kwargs: Arguments needed for the different resource types. \n
            **kwargs stores any arguments as a key-value pair. \n
            These values can be retrieved just as any dictionary \n
            See get_post for more information.
        """
        # to resource_manager as insert_resource
        db, _ = self.get_db(resource_type)
        # get_post organizes the **kwargs into the appropriate arguments
        post, post_id = self.get_post(resource_type, **kwargs)
        if self.fault_detection_module.detect_compatibility(None):
            mes = Markup(
                'No anomalies detected with cyber twin.<br/>Resource inserted into database.')
            flash(mes, 'success')
            #print('inserted to db')
        db.insert_one(post)
        if post_id is not None:
            return post_id
        else:
            return True

    def update_to_db(self, resource_type, **kwargs):
        """
        Update into the db. \n
        Params: \n
        resource_type: Type of resource to be added. \n
        **kwargs: Arguments needed for the different resource types. \n
            **kwargs stores any arguments as a key-value pair. \n
            These values can be retrieved just as any dictionary \n
            See get_post for more information.
        """
        # to resource_manager as update_resource
        db, _ = self.get_db(resource_type)
        # get_post organizes the **kwargs into the appropriate arguments
        post, post_id = self.get_post(resource_type, **kwargs)
        post['ID'] = kwargs['ID']
        # if post.get("location_id"):
        #     post.pop("location_id")
        query = self.get_query(resource_type, **kwargs)
        print(f"updating! {post}")

        if self.fault_detection_module.detect_compatibility(None):
            mes = Markup(
                'No anomalies detected with cyber twin.<br/>Resource inserted into database.')
            flash(mes, 'success')
            #print('inserted to db')
        db.update_one(query, {"$set": post}, upsert=True)
        if post_id is not None:
            return post_id
        else:
            return True

    def get_post(self, resource_type, **kwargs):
        """
        Organizes kwargs into the appropriate arguments for the different resource type.
        """
        # to resource_manager as get_post
        post_id = None
        if resource_type == "robot":
            post = self.robot_post(kwargs['robot_type'], kwargs['robot_name'], kwargs['position_sensor_tag'],
                                   kwargs['location_id'])
        elif resource_type == "hardware":
            post = self.hardware_post(
                kwargs['hardware_name'], kwargs['hardware_type'], kwargs['position_sensor_tag'],
                kwargs['location_id'])
        elif resource_type == "software":
            post, post_id = self.software_post(kwargs['software_name'], kwargs['software_type'])
        elif resource_type == "workcell":
            post = self.workcell_post(
                kwargs['workcell_id'], kwargs['location_name'], kwargs['x_min'], kwargs['x_max'],
                kwargs['y_min'], kwargs['y_max'], kwargs['z_min'], kwargs['z_max'])
        return post, post_id

    def get_query(self, resource_type, **kwargs):
        """
        Organizes kwargs into the appropriate arguments for the different resource type.
        """
        # deprecated
        if resource_type == "workcell":
            query = {"location_id": kwargs['location_id']}
        else:
            query = {"ID": kwargs['ID']}
        return query

    def get_db(self, resource_type):
        """
        Retrieves the appropriate collection and initial according to the resource type
        """
        # to resource_manager as get_id_prefix and use db_dict instead to find db
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
            db = self.workcell_details
        return db, initial

    def get_location_id(self, workcell_id):
        """
        Gets a new resource ID for workcell/location details
        """
        # deprecated, merged with get_new_id
        db = self.workcell_details
        max_id = self.get_max_workcell_id(db)
        new_id = workcell_id + '-' + str(max_id + 1).rjust(2, "0")
        return new_id

    def get_max_workcell_id(self, db):
        """
        Retrieves the maximum workcell ID based on existing workcell entries.
        """
        # deprecated, merged with get_max_id
        id_list = []
        for item in db.find():
            try:
                id_list.append(int(item['location_id'][-2:]))
            except:
                pass
        return max(id_list)

    def get_new_id(self, resource_type):
        """
        get new resource ID, except for workcells/location details.
        """
        # to resource_manager, changed at get prefix and suffix
        db, initial = self.get_db(resource_type)
        max_id = self.get_max_id(db)
        new_id = initial + str(max_id + 1).rjust(5, "0")
        return new_id

    def get_max_id(self, db):
        """
        Retrieves the maximum resource ID based on resource entries except workcells.
        """
        # to resource_manager
        id_list = self.get_id_list(db)
        return max(id_list)

    def get_id_list(self, db):
        """
        Retrieves the numerical component of resource IDs
        """
        # to resource_manager, merged with get_max_workcell_id
        id_list = []
        for item in db.find():
            try:
                id_list.append(int(item['ID'][1:]))
            except:
                pass
        return id_list
