from flask import session

from CPSBuilder.modules.archive.data_validation_module import DataValidationModule

from pymongo import MongoClient
import config

import time

import logging
logger = logging.getLogger(__name__)

"""
Miscellaneous
Functions in this file are written to help with formatting lists/inputs into a format more suitable for Flask-WTForms templating
"""
client = MongoClient(config.mongo_ip, config.mongo_port)
data_validation_module = DataValidationModule(client)


def check_connection():
    while True:
        data_validation_module.check_connection()
        time.sleep(.1)


def format_choice(input_list, sentence_db=None):
    """
    Formats the inputted list into a list of tuples in the form (item, item)
    """
    out = []
    if sentence_db is None:
        for item in input_list:
            out.append((item, item))
    #  todo: add functionality to translate and package

    return out


def index_choice(input_list, from_n=0):
    """
    Formats the inputted list into a list of tuple in the form (index, item). "from_n" adjusts the first element of the index, default is 0.
    """
    out = []
    for i, item in enumerate(input_list):
        out.append((i + from_n, item))
    return out


def clear_session(is_log_out=False):
    if is_log_out:
        user_id = session['user_id']
        session.clear()
        session['user_id'] = user_id
    else:
        session.clear()


def get_var_and_sentence(var_sentence_list):
    """
    Splits a list of tuples in the form (variable, sentence) into separate lists.
    """
    var = []
    sentence = []
    for item in var_sentence_list:
        var.append(item[0])
        sentence.append(item[1])
    return var, sentence


def pack_var_sentence(var_list, sentence_list):
    """
    Combines the list of variables and sentences into a list of tuples in the form (variable, sentence)
    """
    out = []
    for item in zip(var_list, sentence_list):
        out.append(item)
    return out


def dict2table(item_dict):
    """
    Converts a dictionary into a list of tuples in the form (key, value)
    """
    return item_dict.items()
