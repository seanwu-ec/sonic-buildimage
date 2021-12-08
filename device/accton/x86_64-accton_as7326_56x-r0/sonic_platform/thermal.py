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

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from collections import namedtuple
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


Threshold = namedtuple('Threshold', ['high_crit', 'high_err', 'high_warn',
                       'low_warn', 'low_err', 'low_crit'], defaults=[0]*6)

PSU_I2C_PATH = "/sys/bus/i2c/devices/{}-00{}/"
PSU_HWMON_I2C_MAPPING = {
    0: {
        "bus": 17,
        "addr": "59"
    },
    1: {
        "bus": 13,
        "addr": "5b"
    },
}

PSU_CPLD_I2C_MAPPING = {
    0: {
        "bus": 17,
        "addr": "51"
    },
    1: {
        "bus": 13,
        "addr": "53"
    },
}

def is_fan_dir_F2B():
    from sonic_platform.platform import Platform
    fan = Platform().get_chassis().get_fan(0)
    return fan.get_direction().lower() == fan.FAN_DIRECTION_EXHAUST


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THERMAL_NAME_LIST = (
        "Main Board 0x48",
        "Main Board 0x49",
        "Main Board 0x4A",
        "CPU Board 0x4B"
    )
    PSU_THERMAL_NAME_LIST = (
        "PSU-1 temp sensor 1",
        "PSU-2 temp sensor 1"
    )
    CPU_THERMAL_NAME = "CPU Core temp"
    SYSFS_PATH = "/sys/bus/i2c/devices"

    THRESHOLDS_F2B = {
        0: Threshold(70.5, 68.0, 65.3),
        1: Threshold(68.0, 65.4, 62.8),
        2: Threshold(64.8, 62.1, 59.7),
        3: Threshold(64.3, 61.6, 59.2),
    }
    THRESHOLDS_B2F = {
        0: Threshold(71.0, 67.9, 65.2),
        1: Threshold(69.5, 66.4, 63.7),
        2: Threshold(66.5, 63.3, 60.8),
        3: Threshold(64.0, 60.8, 58.4),
    }
    THRESHOLDS = None

    def __init__(self, thermal_index=0, is_psu=False, psu_index=0, is_cpu=False):
        self.index = thermal_index
        self.is_psu = is_psu
        self.psu_index = psu_index
        self.is_cpu = is_cpu

        if self.is_cpu:
            self.cpu_paths = glob.glob('/sys/devices/platform/coretemp.0/hwmon/hwmon*/temp*_input')
            self.cpu_path_idx = 0

        if self.is_psu:
            psu_i2c_bus = PSU_HWMON_I2C_MAPPING[psu_index]["bus"]
            psu_i2c_addr = PSU_HWMON_I2C_MAPPING[psu_index]["addr"]
            self.psu_hwmon_path = PSU_I2C_PATH.format(psu_i2c_bus,
                                                      psu_i2c_addr)
            psu_i2c_bus = PSU_CPLD_I2C_MAPPING[psu_index]["bus"]
            psu_i2c_addr = PSU_CPLD_I2C_MAPPING[psu_index]["addr"]
            self.cpld_path = PSU_I2C_PATH.format(psu_i2c_bus, psu_i2c_addr)

        # Set hwmon path
        i2c_path = {
            0: "15-0048/hwmon/hwmon*/",
            1: "15-0049/hwmon/hwmon*/",
            2: "15-004a/hwmon/hwmon*/",
            3: "15-004b/hwmon/hwmon*/"
        }.get(self.index, None)

        self.hwmon_path = "{}/{}".format(self.SYSFS_PATH, i2c_path)
        self.ss_key = self.THERMAL_NAME_LIST[self.index]
        self.ss_index = 1

    def __read_txt_file(self, file_path):
        for filename in glob.glob(file_path):
            try:
                with open(filename, 'r') as fd:
                    return fd.readline().rstrip()
            except IOError as e:
                pass

    def __get_temp(self, temp_file):
        if not self.is_psu:
            temp_file_path = os.path.join(self.hwmon_path, temp_file)
        else:
            temp_file_path = temp_file

        raw_temp = self.__read_txt_file(temp_file_path)
        return float(raw_temp) / 1000

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
            temp_file = "temp{}_input".format(self.ss_index)
        else:
            temp_file = self.psu_hwmon_path + "psu_temp1_input"

        return self.__get_temp(temp_file)

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        if self.is_cpu:
            return self.CPU_THERMAL_NAME
        if self.is_psu:
            return self.PSU_THERMAL_NAME_LIST[self.psu_index]
        else:
            return self.THERMAL_NAME_LIST[self.index]

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        if self.is_cpu:
            return True
        if self.is_psu:
            val = self.__read_txt_file(self.cpld_path + "psu_present")
            return int(val, 10) == 1

        temp_file = "temp{}_input".format(self.ss_index)
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        raw_txt = self.__read_txt_file(temp_file_path)
        return raw_txt != None

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if self.is_cpu:
            return True
        if self.is_psu:
            temp_file = self.psu_hwmon_path + "psu_temp_fault"
            return self.get_presence() and (not int(
                self.__read_txt_file(temp_file)))

        file_str = "temp{}_input".format(self.ss_index)
        file_path = os.path.join(self.hwmon_path, file_str)

        raw_txt = self.__read_txt_file(file_path)
        if raw_txt is None:
            return False
        else:
            return int(raw_txt) != 0

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

    def _try_get_threshold(self, type):
        if self.THRESHOLDS is None:
            self.THRESHOLDS = self.THRESHOLDS_F2B if is_fan_dir_F2B() else self.THRESHOLDS_B2F

        if self.is_cpu:
            return self.__get_cpu_threshold(type)

        if self.is_psu==False and self.index in self.THRESHOLDS:
            return getattr(self.THRESHOLDS[self.index], type)
        else:
            return None

    def get_high_critical_threshold(self):
        return self._try_get_threshold('high_crit')

    def get_low_critical_threshold(self):
        return self._try_get_threshold('low_crit')

    def get_high_threshold(self):
        return self._try_get_threshold('high_err')

    def get_low_threshold(self):
        return self._try_get_threshold('low_err')

    def get_high_warning_threshold(self):
        return self._try_get_threshold('high_warn')

    def get_low_warning_threshold(self):
        return self._try_get_threshold('low_warn')
