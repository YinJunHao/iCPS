from CPSBuilder.utils.archive.module_functions import *

import requests

import logging
logger = logging.getLogger(__name__)


class DataValidationModule():
    def __init__(self, client):
        self.metadata_db = client['other-data']['metadata']
        self.connection_list_db = client['resources']['connection_list']
        self.resources_db = client['resources']
        self.broadcast = client['job-history']['broadcast']

    def add_data_type(self, data_type, resource, metadata_type):
        # add new datatype in the database
        return True

    def update_metadata(self, data_type, resource, metadata_input):
        # update existing metadata in the database with new input
        return True

    def check_data_validity(self, data_type, resource, metadata_type, metadata_input):
        # check metadata from sensor against data form database
        return True

    def check_connection(self):
        for item in self.connection_list_db.find():
            cyber_twin_id = item['name']
            cyber_twin_ip = item['ip']
            cyber_twin_port = item['port']
            cyber_twin_class = item['class']
            collection = {"hardware": "hardware_resources", "robot": "robot", "human": "human_resources"}
            sub_resources_db = self.resources_db[collection[cyber_twin_class]]
            # print(cyber_twin_id)
            try:
                requests.get(
                    f"http://{cyber_twin_ip}:{cyber_twin_port}/api/cyber-twin/test-connection")
                logger.info(
                    f"Detected connection for {cyber_twin_id} at {cyber_twin_ip}:{cyber_twin_port}")
                self.connection_list_db.update_one(
                    {'name': cyber_twin_id, 'ip': cyber_twin_ip, 'port': cyber_twin_port},
                    {'$set': {'status': 'online'}})
                sub_resources_db.update_one(
                    {'ID': cyber_twin_id},
                    {'$set': {'availability': '1'}}, upsert=True)
                # update broadcast item as given_up: False
                self.hold_onto_broadcast_item(cyber_twin_id)
                if cyber_twin_id == 'H87571':
                    print('online')
            except requests.exceptions.RequestException as e:
                self.connection_list_db.update_one(
                    {'name': cyber_twin_id, 'ip': cyber_twin_ip, 'port': cyber_twin_port}, {'$set': {'status': 'offline'}})
                sub_resources_db.update_one(
                    {'ID': cyber_twin_id},
                    {'$set': {'availability': '0'}}, upsert=True)
                # update broadcast item as given_up: True
                self.give_up_broadcast_item(cyber_twin_id)
                logger.error(
                    f"No connection for {cyber_twin_id} at {cyber_twin_ip}:{cyber_twin_port}")
                # print(
                #     f"No connection for {cyber_twin_id} at {cyber_twin_ip}:{cyber_twin_port}")
                # print(e)
                if cyber_twin_id == 'H87571':
                    print('offline')

    def give_up_broadcast_item(self, cyber_twin_id):
        # query preferred_exec: offline_CT from broadcast db
        query = {
            'preferred_exec': cyber_twin_id,
            'is_deleted': {'$ne': True}
        }
        # update broadcast item as given_up: True
        self.broadcast.update_many(query, {'$set': {'given_up': True}}, upsert=False)

    def hold_onto_broadcast_item(self, cyber_twin_id):
        # query preferred_exec: online_CT from broadcast db
        query = {
            'preferred_exec': cyber_twin_id,
            'is_deleted': {'$ne': True}
        }
        # update broadcast item as given_up: False
        self.broadcast.update_many(query, {'$set': {'given_up': False}}, upsert=False)