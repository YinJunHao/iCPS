"""
Program title: iCPS
Project title: CPS Builder
This script instantiate components as object with its location in the modules as its attribute.
Written by Wong Pooi Mun.
"""

from collections import defaultdict
import weakref

import logging
logger = logging.getLogger(__name__)


class Component():
    """
        Update attribute of process components.
    """

    __refs__ = defaultdict(list)

    def __init__(self, test=False):
        self.__refs__[self.__class__].append(weakref.ref(self))

    @classmethod
    def get_instances(cls):
        for inst_ref in cls.__refs__[cls]:
            inst = inst_ref()
            if inst is not None:
                yield inst

    @classmethod
    def remove_instances(cls, component_id):
        for inst_ref in cls.__refs__[cls]:
            print(inst_ref)
            print(inst_ref())
            inst = inst_ref()
            if inst._id == component_id:
                cls.__refs__[cls].remove(inst_ref)

    def update_attribute(self, component_id, component_type, location):
        if component_type == "task":
            if component_id not in [item._id for item in Task.get_instances()]:
                component_instance = Task(str(component_id))
            else:
                component_instance = [item for item in Task.get_instances() if item._id == component_id][0]
        else:
            return None
        component_instance.location = location
        print(f"{component_instance._id} is in {component_instance.location}")
        return component_instance


class Task(Component):
    def __init__(self, component_id, test=False):
        super(Task, self).__init__(test)
        self._id = component_id
        self.location = None


class Objective(Component):
    def __init__(self, component_id, test=False):
        super(Objective, self).__init__(test)
        self._id = component_id
        self.location = None


class Step(Component):
    def __init__(self, component_id, test=False):
        super(Step, self).__init__(test)
        self._id = component_id
        self.location = None


class State(Component):
    def __init__(self, component_id, test=False):
        super(State, self).__init__(test)
        self._id = component_id
        self.location = None


"""
use this to get all instances
for item in demonstrator.Task.get_instances():
    print(item._id)
"""