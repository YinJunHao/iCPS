import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from pprint import pprint


def count_res(db, query):
    """
    Returns the number of results for a query
    """
    res = []
    for item in db.find(query):
        res.append(item)
    return len(res)


def print_collection(db, query=None, no_objectid=False, print_out=True):
    """
    Prints the collection. \n
    Params: \n
    db: Collection to be printed \n
    query: Query to be processed. Default = None \n
    no_objectid: Print/Append without MongoID. Default = False \n
    print_out: Allow printing of query result. Default = True \n
    \n
    Returns: \n
    List of query result from collection based on query.
    """
    out = []
    # print the contents of the collection
    for post in db.find(query):
        # print(post)
        if no_objectid:
            post.pop('_id', None)
        out.append(post)
        if print_out:
            pprint(post)
            print('\n')
    return out


def get_item(db, query, amount=None):
    """
    Returns results for a query on a collection. \n
    Params: \n
    db: Collection to be printed \n
    query: Query to be processed. Default = None \n
    amount: Number of result returned \n
    \n
    Results: \n
    List of query result from the input collectoin \n
    """
    if amount == None:
        res = []
        for item in db.find(query):
            res.append(item)
        return res
    else:
        res = []
        for item in db.find(query).limit(amount):
            res.append(item)
        return res


def query_db(db, query=None):
    out = []
    for post in db.find(query):
        out.append(post)
    return out


def get_rand_item(collection, query):
    """
    Returns a random item in a collection given a query
    """
    import random
    out = []
    for i in collection.find(query):
        out.append(i)
    try:
        idx = random.randint(0, len(out)-1)
        return out[idx]
    except:
        return -1


def update_one(db_col, query, new_info, method="$set", upsert=False):
    """
    Update an item in a collection
    Deprecated.
    """
    db_col.update_one(
        query, {method: new_info}, upsert=upsert)


def count_documents(db_col, query):
    '''
    Count number of items with query
    Deprecated.
    '''
    doc_number = db_col.count_documents(query)
    return doc_number

