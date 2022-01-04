from CPSBuilder.modules.manager import ResourceInsert
import config

from pymongo import MongoClient
from flask import Blueprint, Response, request


client = MongoClient(config.mongo_ip, config.mongo_port)

context = Blueprint("context", __name__)

resource_insert = ResourceInsert(client)


# todo: temp for test
@context.route('/cyber-twin/register-address', methods=['GET', 'POST'])
def add_cyber_twin():
    data = request.get_json()
    resource_class = data.get("class")
    resource_id = data.get("ID")
    resource_address = {
        "ip": data.get("ip"),
        "port": data.get("port"),
    }
    resource_insert.insert_physical_resource_address(resource_class, resource_id, resource_address)
    res = f'{resource_id} at {resource_address["ip"]}:{resource_address["port"]} is connected'
    status = 200
    return Response(res, status)
