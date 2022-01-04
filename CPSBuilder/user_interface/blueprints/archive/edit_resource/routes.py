from flask import Blueprint, render_template, request, redirect, url_for, flash

from CPSBuilder.utils.archive.module_functions import *
from CPSBuilder.utils.route import *

from CPSBuilder.modules.archive.resource_insert_module import ResourceInsertModule
from CPSBuilder.modules.archive.resource_delete_module import ResourceDeleteModule
from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule

from CPSBuilder.user_interface.blueprints.edit_resource.forms import EditRobotForm
from CPSBuilder.user_interface.blueprints.edit_resource.forms import EditHardwareForm
from CPSBuilder.user_interface.blueprints.edit_resource.forms import EditSoftwareForm
from CPSBuilder.user_interface.blueprints.edit_resource.forms import EditWorkcellForm


from pprint import pprint

import config

import logging

logger = logging.getLogger(__name__)

client = MongoClient(config.mongo_ip, config.mongo_port)

edit_resource = Blueprint('edit_resource', __name__,
                          template_folder='templates')

resource_insert_module = ResourceInsertModule(client)
resource_delete_module = ResourceDeleteModule(client)
executor_mapping_module = ExecutorMappingModule(client)


@edit_resource.route('/manage_resources/edit-robot', methods=['GET', 'POST'])
def edit_robot():
    # todo: either add position_sensor_tag or add coordinates (XOR method html input)
    equipment_id = request.args.get('equipment_id')

    try:
        equipment_details = resource_delete_module.get_item_details('robot', {'ID': equipment_id})[0]
    except IndexError:
        flash(f"{equipment_id} not registered in the database")
        return redirect(url_for('remove_resource.remove_robot'))

    edit_robot_form = EditRobotForm(request.form, robot_type=equipment_details['item_type'])

    unique_types = executor_mapping_module.get_unique_resource_type("robot")
    form_choices = format_choice(unique_types)
    edit_robot_form.robot_type.choices += form_choices
    edit_robot_form.robot_type.choices.insert(0, ('', ''))

    form_choices = format_choice(executor_mapping_module.get_location_ids())
    pprint(form_choices)
    edit_robot_form.location_id.choices += form_choices

    for tup in form_choices[0]:
        print(tup)
        if tup[1] == equipment_details.get('location_id'):
            edit_robot_form.location_id.process_data(equipment_details.get('location_id'))
        else:
            logger.error(f"{equipment_details.get('location_id')} no longer exist!")

    if edit_robot_form.validate_on_submit():  # if triggered any event when validate on submit
        robot_name = edit_robot_form.robot_name.data
        position_sensor_tag = edit_robot_form.position_sensor_tag.data
        location_id = edit_robot_form.location_id.data
        print(f"HERE {location_id}")
        if edit_robot_form.robot_type_new.data == "":
            robot_type = edit_robot_form.robot_type.data
        else:
            robot_type = edit_robot_form.robot_type_new.data
        post = {
            "name": robot_name,
            "position_sensor_tag": position_sensor_tag,
            "robot_type": robot_type,
            "location_id": location_id
        }
        pprint(post)
        logger.info(f"{equipment_id} details is changed to {post}")
        resource_insert_module.update_to_db(
            'robot', ID=equipment_id, robot_name=robot_name, robot_type=robot_type,
            position_sensor_tag=position_sensor_tag, location_id=location_id)
        return redirect(url_for('remove_resource.remove_robot'))

    return render_template('edit_robot.html', equipment_details=equipment_details, edit_robot_form=edit_robot_form)


@edit_resource.route('/manage_resources/edit_hardware', methods=['GET', 'POST'])
def edit_hardware():
    '''
    Allows edit hardware details in the manage resources page. Edited info is updated to the DB.
    '''
    # todo: either add position_sensor_tag or add coordinates (XOR method html input)
    equipment_id = request.args.get('equipment_id')

    try:
        # get details from the database by using eq id as query
        equipment_details = resource_delete_module.get_item_details('hardware', {'ID': equipment_id})[0]
    except IndexError:
        flash(f"{equipment_id} not registered in the database")
        return redirect(url_for('remove_resource.remove_hardware'))

    edit_hardware_form = EditHardwareForm(request.form, hardware_type=equipment_details['item_type'])

    # fetch types that were once entered in db
    unique_types = executor_mapping_module.get_unique_resource_type("hardware")
    form_choices = format_choice(unique_types)
    # populate the form choices into the form (select field)
    edit_hardware_form.hardware_type.choices += form_choices
    edit_hardware_form.hardware_type.choices.insert(0, ('', ''))

    form_choices = format_choice(executor_mapping_module.get_location_ids())
    # pprint(form_choices)
    edit_hardware_form.location_id.choices += form_choices

    for tup in form_choices[0]:
        if tup[1] == equipment_details['location_id']:
            edit_hardware_form.location_id.process_data(equipment_details['location_id'])
        else:
            logger.error(f"{equipment_details['location_id']} no longer exist!")

    if edit_hardware_form.validate_on_submit():  # if triggered any event when validate on submit
        hardware_name = edit_hardware_form.hardware_name.data
        position_sensor_tag = edit_hardware_form.position_sensor_tag.data
        location_id = edit_hardware_form.location_id.data
        if edit_hardware_form.hardware_type_new.data == "":
            hardware_type = edit_hardware_form.hardware_type.data
        else:
            hardware_type = edit_hardware_form.hardware_type_new.data
        post = {
            "name": hardware_name,
            "position_sensor_tag": position_sensor_tag,
            "hardware_type": hardware_type,
            "location_id": location_id
        }
        pprint(post)
        logger.info(f"{equipment_id} details is changed to {post}")
        resource_insert_module.update_to_db(
            'hardware', ID=equipment_id, hardware_name=hardware_name, hardware_type=hardware_type,
            position_sensor_tag=position_sensor_tag, location_id=location_id)
        return redirect(url_for('remove_resource.remove_hardware'))

    return render_template('edit_hardware.html', equipment_details=equipment_details, edit_hardware_form=edit_hardware_form)


@edit_resource.route('/manage_resources/edit_software', methods=['GET', 'POST'])
def edit_software():
    '''
    Allows edit software details in the manage resources page. Edited info is updated to the DB.
    '''
    equipment_id = request.args.get('equipment_id')


    try:
        # get details from the database by using eq id as query
        equipment_details = resource_delete_module.get_item_details('software', {'ID': equipment_id})[0]
    except IndexError:
        flash(f"{equipment_id} not registered in the database")
        return redirect(url_for('remove_resource.remove_software'))

    software_type = equipment_details['software_type']

    edit_software_form = EditSoftwareForm(request.form, software_type=software_type)

    unique_types = executor_mapping_module.get_software_types()
    form_choice = format_choice(unique_types)
    edit_software_form.software_type.choices += form_choice
    print(equipment_details)

    if edit_software_form.validate_on_submit():  # if triggered any event when validate on submit
        software_name = edit_software_form.software_name.data
        software_type = edit_software_form.software_type.data
        post = {
            "name": software_name,
            "software_type": software_type,
        }
        pprint(post)
        logger.info(f"{equipment_id} details is changed to {post}")
        # todo: find a way to update all related stuff (manage processes) on the edited software details
        resource_insert_module.update_to_db(
            'software', ID=equipment_id, software_name=software_name, software_type=software_type)
        return redirect(url_for('remove_resource.remove_software'))

    return render_template('edit_software_resource.html', equipment_details=equipment_details,
                           edit_software_form=edit_software_form)


@edit_resource.route('/manage_resources/edit_workcell', methods=['GET', 'POST'])
def edit_workcell():
    '''
    Allows edit workcell details in the manage resources page. Edited info is updated to the DB.
    '''
    location_id = request.args.get('location_id')

    try:
        # get details from the database by using eq id as query
        equipment_details = resource_delete_module.get_item_details('workcell', {'location_id': location_id})[0]
    except IndexError:
        flash(f"{location_id} not registered in the database")
        return redirect(url_for('remove_resource.remove_workcell'))

    edit_workcell_form = EditWorkcellForm(request.form, workcell_id=equipment_details['workcell_id'])

    edit_workcell_form.workcell_id.choices += resource_delete_module.get_unique_item(
        'workcell', 'workcell_id')
    # edit_workcell_form.workcell_id.process_data(equipment_details['workcell_id'])
    edit_workcell_form.workcell_id.choices.insert(0, ('', ''))

    if edit_workcell_form.validate_on_submit():  # if triggered any event when validate on submit
        if edit_workcell_form.workcell_id_new.data == "":
            workcell_id = edit_workcell_form.workcell_id.data
        else:
            workcell_id = edit_workcell_form.workcell_id_new.data
        location_name = edit_workcell_form.location_name.data
        x_min = edit_workcell_form.x_min.data
        x_max = edit_workcell_form.x_max.data
        y_min = edit_workcell_form.y_min.data
        y_max = edit_workcell_form.y_max.data
        z_min = edit_workcell_form.z_min.data
        z_max = edit_workcell_form.z_max.data
        post = {
            "workcell_id": workcell_id,
            "location_name": location_name,
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "z_min": z_min,
            "z_max": z_max
        }
        pprint(post)
        logger.info(f"{location_id} details is changed to {post}")
        resource_insert_module.update_to_db(
            'workcell', workcell_id=workcell_id, location_id=location_id, location_name=location_name, x_min=x_min, x_max=x_max, y_min=y_min,
            y_max=y_max, z_min=z_min, z_max=z_max)
        return redirect(url_for('remove_resource.remove_workcell'))

    return render_template('edit_workcell.html', equipment_details=equipment_details,
                           edit_workcell_form=edit_workcell_form)

@edit_resource.route('/edit_human', methods=['GET', 'POST'])
def edit_human():
    '''
    Allows edit human details in the manage resources page. Edited info is updated to the DB.
    '''
    # todo: edit for human (create whole new category button for that)
    pass
