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
    from collections import namedtuple
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

Threshold = namedtuple('Threshold', ['high_crit', 'high_err', 'high_warn',
                       'low_warn', 'low_err', 'low_crit'], defaults=[0]*6)

PSU_I2C_PATH = "/sys/bus/i2c/devices/{}-00{}/"

PSU_HWMON_I2C_MAPPING = {
    0: {
        "num": 10,
        "addr": "5b"
    },
    1: {
        "num": 9,
        "addr": "58"
    },
}

PSU_CPLD_I2C_MAPPING = {
    0: {
        "num": 10,
        "addr": "53"
    },
    1: {
        "num": 9,
        "addr": "50"
    },
}

THERMAL_NAME_LIST = (
    "Main Board 0x48",
    "Main Board 0x49",
    "Main Board 0x4A",
    "CPU Board 0x4B",
    "Fan Board 0x4D",
    "Fan Board 0x4E"
)
PSU_THERMAL_NAME_LIST = ["PSU-1 temp sensor 1", "PSU-2 temp sensor 2"]

SYSFS_PATH = "/sys/bus/i2c/devices"

def is_fan_dir_F2B():
    from sonic_platform.platform import Platform
    fan = Platform().get_chassis().get_fan(0)
    return fan.get_direction().lower() == fan.FAN_DIRECTION_EXHAUST


class Thermal(ThermalBase):
    """Platform-specific Thermal class"""

    THRESHOLDS_F2B = {
        0: Threshold(59.0, 56.0, 53.0),
        1: Threshold(60.0, 57.0, 54.0),
        2: Threshold(70.25, 68.625, 67.0),
        3: Threshold(70.49, 70.245, 70.0),
        4: Threshold(56.0, 55.5, 55.0),
        5: Threshold(55.75, 54.875, 54.0)
    }
    THRESHOLDS_B2F = {
        0: Threshold(52.0, 49.5, 47.0),
        1: Threshold(51.0, 49.0, 47.0),
        2: Threshold(71.0, 68.5, 66.0),
        3: Threshold(57.5, 57.25, 57.0),
        4: Threshold(55.0, 53.0, 51.0),
        5: Threshold(50.5, 48.75, 47.0)
    }
    THRESHOLDS = None

    def __init__(self, thermal_index=0, is_psu=False, psu_index=0):
        self.index = thermal_index
        self.is_psu = is_psu
        self.psu_index = psu_index

        if self.is_psu:
            psu_i2c_bus = PSU_HWMON_I2C_MAPPING[psu_index]["num"]
            psu_i2c_addr = PSU_HWMON_I2C_MAPPING[psu_index]["addr"]
            self.psu_hwmon_path = PSU_I2C_PATH.format(psu_i2c_bus,
                                                      psu_i2c_addr)
            psu_i2c_bus = PSU_CPLD_I2C_MAPPING[psu_index]["num"]
            psu_i2c_addr = PSU_CPLD_I2C_MAPPING[psu_index]["addr"]
            self.cpld_path = PSU_I2C_PATH.format(psu_i2c_bus, psu_i2c_addr)

        # Set hwmon path
        i2c_path = {
            0: "18-0048/hwmon/hwmon*/", 
            1: "18-0049/hwmon/hwmon*/", 
            2: "18-004a/hwmon/hwmon*/",
            3: "18-004b/hwmon/hwmon*/",
            4: "17-004d/hwmon/hwmon*/",
            5: "17-004e/hwmon/hwmon*/"
        }.get(self.index, None)

        self.hwmon_path = "{}/{}".format(SYSFS_PATH, i2c_path)
        self.ss_key = THERMAL_NAME_LIST[self.index]
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
        if not self.is_psu:
            temp_file_path = os.path.join(self.hwmon_path, temp_file)
        else:
            temp_file_path = temp_file
        raw_temp = self.__read_txt_file(temp_file_path)
        if raw_temp is not None:
            return float(raw_temp)/1000
        else:
            return 0        

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
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
        if self.is_psu:
            val = self.__read_txt_file(self.cpld_path + "psu_present")
            return int(val, 10) == 1
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
