# -*- coding: utf-8 -*-
from pyscada import log

try:
    # import something
    #from ConfigParser import ConfigParser # we don't need this we use the django settings
    #from bacpypes.core import run
    #from bacpypes.object import LocalDeviceObject

    driver_ok = True
except ImportError:
    driver_ok = False

from time import time

class Device:
    """
    BAnet device
    """
    def __init__(self,device):
        self._device_inst           = device
        
        self.data = []


    def request_data(self):
        """
    
        """
        if not driver_ok:
            return None
            
        
        output = None
        return output
    
    def write_data(self,variable_id, value):
        """
        write value to single modbus register or coil
        """
        if not self.variables[variable_id].writeable:
            return False

        
        return False

