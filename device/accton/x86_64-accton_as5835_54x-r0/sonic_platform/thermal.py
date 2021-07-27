#############################################################################
# Edgecore
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################

import os
import os.path
import glob
from collections import namedtuple

try:
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

Threshold = namedtuple('Threshold', ['high_crit', 'high_err', 'high_warn',
                       'low_warn', 'low_err', 'low_crit'], defaults=[0]*6)

def is_fan_dir_F2B():
    from sonic_platform.platform import Platform
    fan = Platform().get_chassis().get_fan(0)
    return fan.get_direction().lower() == fan.FAN_DIRECTION_EXHAUST


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THERMAL_NAME_LIST = (
        'CPU Board 0x4B',
        'Main Board 0x4C',
        'Main Board 0x49',
        'Main Board 0x4A'
    )
    SYSFS_PATH = "/sys/bus/i2c/devices"

    THRESHOLDS_F2B = {
        0: Threshold(78.0, 73.0, 73.0),
        1: Threshold(72.0, 67.0, 67.0),
        2: Threshold(66.0, 61.0, 61.0),
        3: Threshold(71.0, 66.0, 66.0),
    }
    THRESHOLDS_B2F = {
        0: Threshold(67.0, 62.0, 62.0),
        1: Threshold(75.0, 70.0, 70.0),
        2: Threshold(68.0, 63.0, 63.0),
        3: Threshold(68.0, 63.0, 63.0),
    }
    THRESHOLDS = None

    def __init__(self, thermal_index=0):
        self.index = thermal_index

        # Set hwmon path
        i2c_path = {
            0: "18-004b/hwmon/hwmon*/", 
            1: "19-004c/hwmon/hwmon*/", 
            2: "20-0049/hwmon/hwmon*/",
            3: "21-004a/hwmon/hwmon*/"
        }.get(self.index, None)
          
        self.hwmon_path = "{}/{}".format(self.SYSFS_PATH, i2c_path)
        self.ss_key = self.THERMAL_NAME_LIST[self.index]
        self.ss_index = 1

    def __read_txt_file(self, file_path):
        for filename in glob.glob(file_path):           
            try:
                with open(filename, 'r') as fd:
                    data =fd.readline().rstrip()
                    return data
            except IOError as e:
                pass
        
        return None
        
            
    def __get_temp(self, temp_file):
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        raw_temp = self.__read_txt_file(temp_file_path)
        if raw_temp is not None:
            return float(raw_temp)/1000
        else:
            return 0

    def __try_get_threshold(self, type):
        if self.THRESHOLDS is None:
            self.THRESHOLDS = self.THRESHOLDS_F2B if is_fan_dir_F2B() else self.THRESHOLDS_B2F

        if self.index in self.THRESHOLDS:
            return getattr(self.THRESHOLDS[self.index], type)
        else:
            return None

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        temp_file = "temp{}_input".format(self.ss_index)
        return self.__get_temp(temp_file)

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        return self.THERMAL_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the Thermal
        Returns:
            bool: True if Thermal is present, False if not
        """
        temp_file = "temp{}_input".format(self.ss_index)
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        raw_txt = self.__read_txt_file(temp_file_path)
        if raw_txt is not None:
            return True
        else:
            return False

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """

        file_str = "temp{}_input".format(self.ss_index)
        file_path = os.path.join(self.hwmon_path, file_str)
        raw_txt = self.__read_txt_file(file_path)
        if raw_txt is None:
            return False
        else:     
            return int(raw_txt) != 0

    def get_high_critical_threshold(self):
        return self.__try_get_threshold('high_crit')

    def get_low_critical_threshold(self):
        return self.__try_get_threshold('low_crit')

    def get_high_threshold(self):
        return self.__try_get_threshold('high_err')

    def get_low_threshold(self):
        return self.__try_get_threshold('low_err')

    def get_high_warning_threshold(self):
        return self.__try_get_threshold('high_warn')

    def get_low_warning_threshold(self):
        return self.__try_get_threshold('low_warn')
