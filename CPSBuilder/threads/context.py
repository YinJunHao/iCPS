from CPSBuilder.modules import context_aware
from CPSBuilder.modules import executor_mapper
import config

from pymongo import MongoClient
import time

import logging
logger = logging.getLogger(__name__)

client = MongoClient(config.mongo_ip, config.mongo_port)
external_context_aware = context_aware.ExternalContextAware(client)
executor_mapper = executor_mapper.ExecutorMapper(client)


def check_online_resource():
    while True:
        executor_mapper.check_online_resource()
        time.sleep(1)


def generate_avail_p():
    while True:
        location_content_dict = executor_mapper.record_location_content()
        total_resource_dict = executor_mapper.count_total_available_resource()
        external_context_aware.generate_avail_p(location_content_dict, total_resource_dict)
        time.sleep(1)

