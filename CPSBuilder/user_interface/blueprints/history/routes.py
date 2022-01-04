from pymongo import MongoClient
from flask import Blueprint, render_template, request, redirect, url_for

from CPSBuilder.utils.route import *

from CPSBuilder.modules.archive.execution_module import ExecutionModule
from CPSBuilder.user_interface.blueprints.history.forms import SeeDetailForm, CloseDetailForm
from CPSBuilder.modules import visualizer
import config

import logging
logger = logging.getLogger(__name__)

client = MongoClient(config.mongo_ip, config.mongo_port)
process_display = visualizer.ProcessDisplay(client)
execution_module = ExecutionModule(client)

history = Blueprint("history", __name__, static_folder="static", template_folder="templates")


@history.route("/job_history", methods=["GET", "POST"])
def job_history():
    see_detail_form = SeeDetailForm(request.form)
    job_list = execution_module.get_job_status(session["user_id"])
    if request.method == "POST":
        job_idx = int(see_detail_form.request_id.data)
        job_id = str(job_list[job_idx]["job_id"])
        if see_detail_form.see_detail.data:
            return redirect(url_for("history.job_details", job_id=job_id))
        elif see_detail_form.see_progress.data:
            return redirect(url_for("job_monitoring.progress_monitor", job_id=job_id, user_id=session["user_id"]))
    return render_template("job_history.html", see_detail_form=see_detail_form, job_list=job_list)


@history.route("/job_details", methods=["GET", "POST"])
def job_details():
    job_id = request.args.get("job_id")
    close_detail_form = CloseDetailForm(request.form)
    job_detail = execution_module.get_job_detail(
        job_id, session.get("user_id"))
    task_sentence =process_display.get_task_sentence(
        job_detail["task"])
    if request.method == "POST":
        return redirect(url_for("history.job_history"))
    return render_template("job_details.html", job_detail=job_detail, task_sentence=task_sentence, close_detail_form=close_detail_form)