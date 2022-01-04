import logging
logger = logging.getLogger(__name__)


class BuildingModule():
    """
    Handles the management of softwares/scripts that is essential to the executing production steps
    """

    def __init__(self, client):
        self.software = client['resources']['software_resources']
        self.step_exec = client['action-step']['step-exec-pair']

    def get_software_list(self, step_var, exec_class):
        if exec_class == "human":
            return []
        query = {'step': step_var, "type": exec_class}
        out = []
        for res in self.step_exec.find(query):
            software_id = res.get('software_id')
            software_name = res.get('software_name')
            software_details_curs = self.software.find({'ID': software_id})
            try:
                item = {
                    'name': software_name,
                    'id': software_id,
                }
                # pp.pprint(item)
                out.append(item)
            except:
                print(software_name)
        return out
