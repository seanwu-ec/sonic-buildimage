#!/usr/bin/env python


try:
    from collections import namedtuple
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


Threshold = namedtuple('Threshold', ['high_crit', 'high_err', 'high_warn',
                       'low_warn', 'low_err', 'low_crit'], defaults=[0]*6)

def is_fan_dir_F2B():
    from sonic_platform.platform import Platform
    fan = Platform().get_chassis().get_fan(0)
    return fan.get_direction().lower() == fan.FAN_DIRECTION_EXHAUST


class Thermal(PddfThermal):
    """PDDF Platform-Specific Thermal class"""

    __thresholds_F2B = {
        0: Threshold(70.5, 68.0, 65.3),
        1: Threshold(68.0, 65.4, 62.8),
        2: Threshold(64.8, 62.1, 59.7),
        3: Threshold(64.3, 61.6, 59.2),
    }
    __thresholds_B2F = {
        0: Threshold(71.0, 67.9, 65.2),
        1: Threshold(69.5, 66.4, 63.7),
        2: Threshold(66.5, 63.3, 60.8),
        3: Threshold(64.0, 60.8, 58.4),
    }
    __thresholds = None

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfThermal.__init__(self, index, pddf_data, pddf_plugin_data)
        self.__index = index

    # Provide the functions/variables below for which implementation is to be overwritten

    def __try_get_threshold(self, type):
        if self.__thresholds is None:
            self.__thresholds = self.__thresholds_F2B if is_fan_dir_F2B() else self.__thresholds_B2F

        if self.__index in self.__thresholds:
            return getattr(self.__thresholds[self.__index], type)
        else:
            return None

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
