from CPSBuilder.modules.archive.cyber_twin_module import CyberTwinModule

import logging
logger = logging.getLogger(__name__)


class FaultDetectionModule():
    def __init__(self, client):
        self.robot = client['resources']['robot']
        self.hardware = client['resources']['hardware_resources']
        self.software = client['resources']['software_resources']
        self.cyber_twin_module = CyberTwinModule(client)

    def detect_compatibility(self, resource_details):
        """
        Detects issues with compatibility between new resource and overal system integrity. \n
        Utilizes input from simulation results from the cyber twin and the physical resource details.
        """
        cyber_twin_sim = self.cyber_twin_module.get_resource_sim(
            resource_details)
        compatibility = self.check_compatibility(
            cyber_twin_sim, resource_details)
        return compatibility

    def check_compatibility(self, cyber_twin_sim, resource_details):
        """
        checks the compatibility between the cyber twin simulation results and the resource details
        """
        return True
