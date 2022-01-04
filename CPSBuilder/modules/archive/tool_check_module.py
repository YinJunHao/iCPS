from pymongo import MongoClient
from CPSBuilder.utils.db import *

import logging
logger = logging.getLogger(__name__)


class ToolCheckModule():
    def __init__(self, client):
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']

    def diagnose_tool(self, tool_id):
        # current implementation always returns true.
        # future implementation will include tool specific diagnosis
        mes = tool_id + " is faulty"
        # print(mes)
        return True

    def down_faulty_tool(self, tool_id):
        faulty = self.diagnose_tool(tool_id)
        if faulty and (tool_id[0] == 'H'):
            self.hardware.update_one({'ID': tool_id}, {'$set': {
                'availability': '0'
            }}, upsert=False)
        elif faulty and (tool_id[0] == 'E'):
            self.robot.update_one({'ID': tool_id}, {'$set': {
                'availability': '0'
            }}, upsert=False)
        mes = tool_id + " is down"
        # print(mes)

    def reinit_sys(self):
        self.robot.update_many({}, {'$set': {
            'availability': '1'
        }}, upsert=False)
        self.hardware.update_many({}, {'$set': {
            'availability': '1'
        }})

    def list_availability(self, toolID=None):
        self._print_availability(toolID)

    def _get_availability(self, toolID):
        if toolID[0] == 'H':
            item = query_db(self.hardware, {'ID': toolID})[0]
        elif toolID[0] == 'E':
            item = query_db(self.robot, {'ID': toolID})[0]
        return item['availability']

    def _print_availability(self, toolID):
        if self._get_availability(toolID) == 1:
            print(toolID + " is available")
        else:
            print(toolID + " is not available")
