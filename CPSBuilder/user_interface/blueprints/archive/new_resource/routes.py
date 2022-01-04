from CPSBuilder.utils.route import *
from flask import Blueprint, render_template, request, redirect, url_for
from CPSBuilder.user_interface.blueprints.new_resource.form import NewEquipmentDetailsForm, NewWorkcellForm, ResourceTypeForm, NewHardwareForm, NewRobotForm, NewSoftwareForm

from pymongo import MongoClient

#import modules
from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule
from CPSBuilder.modules.archive.resource_insert_module import ResourceInsertModule
from CPSBuilder.modules.archive.resource_delete_module import ResourceDeleteModule
from CPSBuilder.modules.archive.action_management_module import ActionManagementModule
import config

import logging
logger = logging.getLogger(__name__)

# config mongodb
client = MongoClient(config.mongo_ip, config.mongo_port)

# initialize blueprint
new_resource = Blueprint('new_resource', __name__, template_folder='templates')

# initialize modules
executor_mapping_module = ExecutorMappingModule(client)
resource_insert_module = ResourceInsertModule(client)
resource_delete_module = ResourceDeleteModule(client)
action_management_module = ActionManagementModule(client)


@new_resource.route('/enter_type', methods=['GET', 'POST'])
def enter_type():
    resource_type = ResourceTypeForm(request.form)
    if resource_type.choose_robot.data:
        print('robot!')
        return redirect(url_for('new_resource.enter_robot'))
    elif resource_type.choose_hardware.data:
        print('hardware!')
        return redirect(url_for('new_resource.enter_hardware'))
    elif resource_type.choose_software.data:
        print('software!')
        return redirect(url_for('new_resource.enter_software'))
    return render_template('enter_type.html', resource_type=resource_type)


@new_resource.route('/enter_robot', methods=['GET', 'POST'])
def enter_robot():
    new_robot = NewRobotForm(request.form)
    unique_types = executor_mapping_module.get_unique_resource_type("robot")
    form_choices = format_choice(unique_types)
    new_robot.robot_type.choices += form_choices

    form_choices = format_choice(executor_mapping_module.get_location_ids())
    new_robot.location_id.choices += form_choices
    if new_robot.validate_on_submit():
        robot_name = new_robot.robot_name.data
        position_sensor_tag = new_robot.position_sensor_tag.data
        location_id = new_robot.location_id.data
        if new_robot.robot_type_new.data == "":
            robot_type = new_robot.robot_type.data
        else:
            robot_type = new_robot.robot_type_new.data
        resource_insert_module.insert_to_db(
            'robot', robot_name=robot_name, robot_type=robot_type, position_sensor_tag=position_sensor_tag, location_id=location_id)
        return redirect(url_for('remove_resource.remove_robot'))
    return render_template('enter_robot.html', new_robot=new_robot)


@new_resource.route('/enter_hardware', methods=['GET', 'POST'])
def enter_hardware():
    new_hardware = NewHardwareForm(request.form)
    unique_types = executor_mapping_module.get_unique_resource_type("hardware")
    form_choices = format_choice(unique_types)
    new_hardware.hardware_type.choices += form_choices

    form_choices = format_choice(executor_mapping_module.get_location_ids())
    new_hardware.location_id.choices += form_choices

    if new_hardware.validate_on_submit():
        hardware_name = new_hardware.hardware_name.data
        position_sensor_tag = new_hardware.position_sensor_tag.data
        location_id = new_hardware.location_id.data
        if new_hardware.hardware_type_new.data == "":
            hardware_type = new_hardware.hardware_type.data
        else:
            hardware_type = new_hardware.hardware_type_new.data
        resource_insert_module.insert_to_db(
            'hardware', hardware_name=hardware_name, hardware_type=hardware_type,
            position_sensor_tag=position_sensor_tag, location_id=location_id)
        return redirect(url_for('remove_resource.remove_hardware'))
    return render_template('enter_hardware.html', new_hardware=new_hardware)


@new_resource.route('/enter_software', methods=['GET', 'POST'])
def enter_software():
    new_software = NewSoftwareForm(request.form)
    unique_types = executor_mapping_module.get_software_types()
    form_choice = format_choice(unique_types)
    new_software.software_type.choices += form_choice
    if request.method == 'POST':
        software_name = new_software.software_name.data
        if new_software.software_type_new.data == "":
            software_type = new_software.software_type.data
        else:
            software_type = new_software.software_type_new.data
        software_id = resource_insert_module.insert_to_db(
            'software', software_name=software_name, software_type=software_type)
        return redirect(url_for('remove_resource.remove_software'))
    return render_template('enter_software.html', new_software=new_software)


@new_resource.route('/enter_workcell', methods=['GET', 'POST'])
def enter_workcell():
    new_workcell = NewWorkcellForm(request.form)
    new_workcell.workcell_id.choices = [('others', 'Not Listed')]
    new_workcell.workcell_id.choices += resource_delete_module.get_unique_item(
        'workcell', 'workcell_id')
    if new_workcell.validate_on_submit():
        if new_workcell.workcell_id.data == 'others':
            workcell_id = new_workcell.workcell_id_new.data
        else:
            workcell_id = new_workcell.workcell_id.data
        location_name = new_workcell.location_name.data
        x_min = new_workcell.x_min.data
        x_max = new_workcell.x_max.data
        y_min = new_workcell.y_min.data
        y_max = new_workcell.y_max.data
        z_min = new_workcell.z_min.data
        z_max = new_workcell.z_max.data
        resource_insert_module.insert_to_db(
            'workcell', workcell_id=workcell_id, location_name=location_name, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, z_min=z_min, z_max=z_max)
        return redirect(url_for('remove_resource.remove_workcell', location_name=location_name, workcell_id=workcell_id))
    return render_template('enter_workcell.html', new_workcell=new_workcell)


@new_resource.route('/enter_workcell/enter_equipment', methods=['GET', 'POST'])
def enter_equipment():
    location_id = request.args.get('location_id')
    equipment_id_list, equipment_class_list, equipment_type_list = resource_delete_module.get_equipment_details()
    new_equipment_form = NewEquipmentDetailsForm(request.form)
    new_equipment_form.equipment_id.choices = index_choice(equipment_id_list)
    if request.method == 'POST':
        chosen_idx = int(new_equipment_form.equipment_id.data)
        if resource_delete_module.register_equipment(location_id, equipment_id_list[chosen_idx], equipment_class_list[chosen_idx], equipment_type_list[chosen_idx]):
            return redirect(url_for('remove_resource.workcell_equipment_details', location_id=location_id))
    return render_template('enter_equipment.html', new_equipment_form=new_equipment_form, location_id=location_id)
