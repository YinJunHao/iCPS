from flask import Blueprint
from flask import render_template, request, flash, redirect, url_for, session, logging, jsonify

from CPSBuilder.modules.auth_module import AuthModule
from CPSBuilder.modules import visualizer, manager

import logging
logger = logging.getLogger(__name__)

#initialize MongoDB client
from pymongo import MongoClient
import config
import sys
client = MongoClient(config.mongo_ip, config.mongo_port)

#initialize user
ar = Blueprint("ar", __name__, static_folder="static", template_folder="templates")

#initialize modules

#login user
auth_module = AuthModule(client)
profile_display = visualizer.ProfileVisualizer(client)
profile_manager = manager.ProfileManager(client)


@ar.route("/ar/login/<user_id>/<password>/", methods=["GET", "POST"])
def ar_login(user_id, password):
    print("test")
    if request.method == "POST":
        print("post request")
        data = request.get_json()
        print(data)
    if request.method == "GET":
        print("get request")
        print(user_id)
        print(password)
        if auth_module.login_user(user_id, password):
            profile_details = profile_display.get_profile(user_id)
            print(profile_details)
            return jsonify(profile_details)
        else:
            return "Login Error"
    sys.stdout.flush()
    return "Login"


#to get job list for the user
@ar.route("/ar/get_job/<user_id>/", methods=["GET", "POST"])
def get_job(user_id):
    # Get job list submitted/assigned to user
    one_job = {"sentence": "Rick Roll", "var": "Rick Roll",
                          "video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO"}
    job_list = {"jobs": [{"sentence": "Rick Roll", "var": "Rick Roll",
                          "video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO"},
                         {"sentence": "Nyan Cat", "var": "Nyan Cat",
                          "video": "https://www.youtube.com/watch?v=QH2-TGUlwu4&ab_channel=NyanCat"}]}
    if request.method == "GET":
        print("get request")
        # return jsonify(one_job)
        return jsonify(job_list)
    return "Job List"
