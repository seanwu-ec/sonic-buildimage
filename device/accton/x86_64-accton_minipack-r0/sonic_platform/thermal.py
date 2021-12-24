#############################################################################
# Edgecore
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################
import glob

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from .helper import APIHelper
    from collections import namedtuple
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

Threshold = namedtuple('Threshold', ['high_crit', 'high_err', 'high_warn',
                       'low_warn', 'low_err', 'low_crit'], defaults=[0]*6)

DEVICE_PATH ="/sys/bus/platform/devices/minipack_psensor/"

THERMAL_NAME_LIST = ["Temp sensor 1", "Temp sensor 2", 
                     "Temp sensor 3", "Temp sensor 4",
                     "Temp sensor 5", "Temp sensor 6",
                     "Temp sensor 7", "Temp sensor 8",] 
                     
PSU_THERMAL_NAME_LIST = ["PSU-1 temp sensor 1", "PSU-2 temp sensor 1",
                         "PSU-3 temp sensor 1", "PSU-4 temp sensor 1"]
CPU_THERMAL_NAME = "CPU Core temp"
THRESHOLDS = {
    0: Threshold(70.0, 66.5, 63.0),
    1: Threshold(70.0, 66.5, 63.0),
    2: Threshold(70.0, 66.5, 63.0),
    3: Threshold(70.0, 66.5, 63.0),
    4: Threshold(70.0, 66.5, 63.0),
    5: Threshold(53.0, 50.35, 47.7),
    6: Threshold(50.0, 47.5, 45.0),
    7: Threshold(70.0, 66.5, 63.0)
}


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    def __init__(self, thermal_index=0, is_psu=False, psu_index=0, is_cpu=False):
        self.index = thermal_index
        self.is_psu = is_psu
        self.psu_index = psu_index
        self.hwmon_path = DEVICE_PATH
        self._api_helper = APIHelper()

        self.ss_key = THERMAL_NAME_LIST[self.index]
        self.ss_index = 1

        self.is_cpu = is_cpu
        if self.is_cpu:
            self.cpu_paths = glob.glob('/sys/devices/platform/coretemp.0/hwmon/hwmon*/temp*_input')
            self.cpu_path_idx = 0

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
        
        raw_temp=self._api_helper.read_txt_file(temp_file)
        if raw_temp is not None:
            return float(raw_temp)/1000
        else:
            return 0        

    def __get_max_temp(self, paths):
        max_temp = -1.0
        max_idx = 0
        for i, path in enumerate(paths):
            read_temp = self.__get_temp(path)
            if(read_temp > max_temp):
                max_temp = read_temp
                max_idx = i
        return max_temp, max_idx

    def __get_cpu_threshold(self, type):
        path = self.cpu_paths[self.cpu_path_idx]
        high_warn = self.__get_temp(path.replace('_input', '_max'))
        if type == 'high_warn':
            return high_warn
        high_crit = self.__get_temp(path.replace('_input', '_crit'))
        if type == 'high_crit':
            return high_crit
        if type == 'high_err':
            return (high_crit + high_warn) / 2
        return 0 # for all low_* thresholds

    def __try_get_threshold(self, type):
        if self.is_cpu:
            return self.__get_cpu_threshold(type)

        if self.is_psu!=True and self.index in THRESHOLDS:
            return getattr(THRESHOLDS[self.index], type)
        else:
            return None

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        if self.is_cpu:
            cpu_temp, self.cpu_path_idx = self.__get_max_temp(self.cpu_paths)
            return cpu_temp

        if not self.is_psu:
            temp_path = "{}{}{}{}".format(self.hwmon_path, 'temp', self.index+1, '_input')
        else:
            temp_path = "{}{}{}{}".format(self.hwmon_path, 'psu', self.psu_index+1, '_temp_input')

        return self.__get_temp(temp_path)

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        if self.is_cpu:
            return CPU_THERMAL_NAME

        if self.is_psu:
            return PSU_THERMAL_NAME_LIST[self.psu_index]
        else:
            return THERMAL_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the Thermal
        Returns:
            bool: True if Thermal is present, False if not
        """
        return self.get_temperature()!=0

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_temperature()!=0

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """

        return "N/A"

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return "N/A"

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device. If the agent cannot determine the parent-relative position
        for some reason, or if the associated value of entPhysicalContainedIn is '0', then the value '-1' is returned
        Returns:
            integer: The 1-based relative physical position in parent device or -1 if cannot determine the position
        """
        return self.index+1

    def is_replaceable(self):
        """
        Retrieves whether thermal module is replaceable
        Returns:
            A boolean value, True if replaceable, False if not
        """
        return False

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
