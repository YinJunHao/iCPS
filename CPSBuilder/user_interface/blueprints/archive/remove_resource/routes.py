from CPSBuilder.utils.db import *
from CPSBuilder.utils.archive.module_functions import *
from CPSBuilder.utils.route import *
from CPSBuilder.modules.archive.resource_delete_module import ResourceDeleteModule
from CPSBuilder.modules.archive.executor_mapping_module import ExecutorMappingModule
from CPSBuilder.user_interface.blueprints.remove_resource.forms import EquipmentDetailsOptionForm, EquipmentDetailsForm, WorkcellOptionForm, ResourceTypeForm, RobotOptionForm, HardwareOptionForm, SoftwareOptionForm


from pymongo import MongoClient
from flask import Blueprint, render_template, request, redirect, url_for, flash
import config

import logging
logger = logging.getLogger(__name__)

# initialize mongo client
client = MongoClient(config.mongo_ip, config.mongo_port)
remove_resource = Blueprint(
    'remove_resource', __name__, template_folder='templates')
resource_delete_module = ResourceDeleteModule(client)
executor_mapping_module = ExecutorMappingModule(client)

@remove_resource.route('/type_to_delete', methods=['GET', 'POST'])
def type_to_delete():
    resource_type = ResourceTypeForm(request.form)
    if resource_type.choose_robot.data:
        print('robot!')
        return redirect(url_for('remove_resource.remove_robot'))
    elif resource_type.choose_hardware.data:
        print('hardware!')
        return redirect(url_for('remove_resource.remove_hardware'))
    elif resource_type.choose_software.data:
        print('software!')
        return redirect(url_for('remove_resource.remove_software'))
    elif resource_type.choose_workcell.data:
        print('workcell!')
        return redirect(url_for('remove_resource.remove_workcell'))
    return render_template('type_to_delete.html', resource_type=resource_type)


@remove_resource.route('/type_to_delete/remove_robot', methods=['GET', 'POST'])
def remove_robot():
    robot_list_form = RobotOptionForm(request.form)
    robot_list_form.robot_list.choices = resource_delete_module.get_choices(
        'robot')
    robot_db_curs = resource_delete_module.get_db_cursor('robot')
    #print(resource_delete_module.paginate_db(db = None))
    if request.method == 'POST':
        if request.form.get('del_resource', None) == 'activate':
            chosen_index = robot_list_form.robot_list.data
            executor_mapping_module.activate_resource(chosen_index, 'robot')
            return redirect(url_for('remove_resource.remove_robot'))

        elif request.form.get('del_resource', None) == 'deactivate':
            chosen_index = robot_list_form.robot_list.data
            executor_mapping_module.deactivate_resource(chosen_index, 'robot')
            return redirect(url_for('remove_resource.remove_robot'))

        elif request.form.get('del_resource', None) == 'clear_selection':
            robot_list_form.robot_list.data = []

        elif request.form.get('del_resource', None) == 'delete':
            chosen_index = robot_list_form.robot_list.data
            resource_delete_module.delete_indicated_resource(
                chosen_index, 'robot')
            return redirect(url_for('remove_resource.remove_robot'))

        elif request.form.get('edit_resource', None):
            chosen_id = request.form['edit_resource']
            logger.info(f"{chosen_id} chosen to be edited.')
            return redirect((url_for('edit_resource.edit_robot', equipment_id=chosen_id)))

    return render_template('robot_delete.html', robot_list_form=robot_list_form, robot_db_curs=robot_db_curs)


@remove_resource.route('/type_to_delete/remove_hardware', methods=['GET', 'POST'])
def remove_hardware():
    hardware_list_form = HardwareOptionForm(request.form)
    hardware_list_form.hardware_list.choices = resource_delete_module.get_choices(
        'hardware')
    hardware_db_curs = resource_delete_module.get_db_cursor('hardware')
    pprint(hardware_db_curs)
    #print(resource_delete_module.paginate_db(db = None))
    if request.method == 'POST':
        if request.form.get('del_resource', None) == 'activate':
            chosen_index = hardware_list_form.hardware_list.data
            # print(chosen_index)
            executor_mapping_module.activate_resource(chosen_index, 'hardware')
            return redirect(url_for('remove_resource.remove_hardware'))

        elif request.form.get('del_resource', None) == 'deactivate':
            chosen_index = hardware_list_form.hardware_list.data
            executor_mapping_module.deactivate_resource(
                chosen_index, 'hardware')
            return redirect(url_for('remove_resource.remove_hardware'))

        elif request.form.get('del_resource', None) == 'clear_selection':
            hardware_list_form.hardware_list.data = []

        elif request.form.get('del_resource', None) == 'delete':
            chosen_index = hardware_list_form.hardware_list.data
            resource_delete_module.delete_indicated_resource(
                chosen_index, 'hardware')
            return redirect(url_for('remove_resource.remove_hardware'))

        elif request.form.get('edit_resource', None):
            chosen_id = request.form['edit_resource']
            logger.info(f"{chosen_id} chosen to be edited.')
            return redirect((url_for('edit_resource.edit_hardware', equipment_id=chosen_id)))

    return render_template('hardware_delete.html', hardware_list_form=hardware_list_form, hardware_db_curs=hardware_db_curs)


@remove_resource.route('/type_to_delete/remove_software', methods=['GET', 'POST'])
def remove_software():
    software_list_form = SoftwareOptionForm(request.form)
    software_list_form.software_list.choices = resource_delete_module.get_choices(
        'software')
    software_db_curs = resource_delete_module.get_db_cursor('software')
    #print(resource_delete_module.paginate_db(db = None))
    if request.method == 'POST':
        if request.form.get('del_resource', None) == 'clear_selection':
            software_list_form.software_list.data = []
        elif request.form.get('del_resource', None) == 'delete':
            chosen_index = software_list_form.software_list.data
            resource_delete_module.delete_indicated_resource(
                chosen_index, 'software')
            return redirect(url_for('remove_resource.remove_software'))
        elif request.form.get('edit_resource', None):
            chosen_id = request.form['edit_resource']
            logger.info(f"{chosen_id} chosen to be edited.')
            return redirect((url_for('edit_resource.edit_software', equipment_id=chosen_id)))

    return render_template('software_delete.html', software_list_form=software_list_form, software_db_curs=software_db_curs)


@remove_resource.route('/type_to_delete/remove_workcell', methods=['GET', 'POST'])
def remove_workcell():
    workcell_list_form = WorkcellOptionForm(request.form)
    workcell_list_form.workcell_list.choices = resource_delete_module.get_choices(
        'workcell')
    workcell_db_curs = resource_delete_module.get_db_cursor('workcell')
    equipment_details_form = EquipmentDetailsForm(request.form)
    if request.method == 'POST':
        if request.form.get('equipment_details', False):
            location_id = request.form['equipment_details']
            return redirect(url_for('remove_resource.workcell_equipment_details', location_id=location_id))
        elif request.form.get('del_resource', False) == 'clear_selection':
            workcell_list_form.workcell_list.data = []
        elif request.form.get('del_resource', False) == 'delete':
            chosen_index = workcell_list_form.workcell_list.data
            resource_delete_module.delete_indicated_resource(
                chosen_index, "workcell")
            return redirect(url_for('remove_resource.remove_workcell'))
        elif request.form.get('edit_resource', None):
            chosen_id = request.form['edit_resource']
            logger.info(f"{chosen_id} chosen to be edited.')
            return redirect((url_for('edit_resource.edit_workcell', location_id=chosen_id)))
    return render_template('workcell_delete.html', equipment_details_form=equipment_details_form, workcell_list_form=workcell_list_form, workcell_db_curs=workcell_db_curs)


@remove_resource.route('/type_to_delete/remove_workcell/equipment_details', methods=['GET', 'POST'])
def workcell_equipment_details():
    location_id = request.args.get('location_id', None)
    if location_id is not None:
        equipment_details_option_form = EquipmentDetailsOptionForm(
            request.form)
        try:
            workcell_details = next(resource_delete_module.get_db_cursor(
                'workcell', {'location_id': location_id}))
            registered_equipment = workcell_details.get('hardware_contents')
            choices = []
            if registered_equipment is not None:
                for idx, equipment in enumerate(registered_equipment):
                    choices.append((idx, equipment))
            equipment_details_option_form.equipment_details.choices = choices
            if request.method == 'POST':
                if request.form.get('del_resource', False) == 'add_new':
                    return redirect(url_for('new_resource.enter_equipment', location_id=location_id))
                elif request.form.get('del_resource', False) == 'clear_selection':
                    equipment_details_option_form.equipment_details.data = []
                elif request.form.get('del_resource', False) == 'delete':
                    chosen_idx = equipment_details_option_form.equipment_details.data[0]
                    resource_delete_module.delete_equipment(
                        location_id, registered_equipment[chosen_idx])
                    return (redirect(url_for("remove_resource.workcell_equipment_details", location_id=location_id)))
                elif request.form.get('confirm_change', False) == 'submit':
                    return redirect(url_for('remove_resource.remove_workcell'))
            return render_template('workcell_equipment_details.html', equipment_details_option_form=equipment_details_option_form, location_id=location_id, registered_equipment=registered_equipment)
        except Exception as e:
            print(e)
            flash('Failed to retrieve details', 'danger')
            return redirect(url_for('remove_resource.remove_workcell'))
    else:
        flash('Failed to retrieve details', 'danger')
        return redirect(url_for('remove_resource.remove_workcell'))
