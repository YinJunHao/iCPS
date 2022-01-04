from flask import session

import logging
logger = logging.getLogger(__name__)


def session_pop(item_list):
    for item in item_list:
        session.pop(item, None)
