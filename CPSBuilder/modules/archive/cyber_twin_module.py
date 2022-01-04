from CPSBuilder.utils.db import *

import logging
logger = logging.getLogger(__name__)


class CyberTwinModule():
    """
    Checks the availability of each resource.
    Simulates the compability check of new components.
    """

    def __init__(self, client):
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.software = client['resources']['software_resources']

    def get_resource_sim(self, resource):
        resource_sim = self.sim_resource(resource)
        return resource_sim

    def sim_resource(self, resource):
        return resource

    def get_avail_robot(self, exec_type, location_id):
        query = {
            'type': exec_type,
            'location_id': location_id,
            'assigned': '1',
            'availability': '1',
            'is_deleted': {'$ne': True}
        }
        return get_item(self.robot, query)

    def get_avail_hardware(self, exec_type, location_id):
        # print(exec_type, location_id)
        query = {
            'type': exec_type,
            'location_id': location_id,
            'assigned': "1",
            'availability': '1',
            'is_deleted': {'$ne': True}
        }
        return get_item(self.hardware, query)
