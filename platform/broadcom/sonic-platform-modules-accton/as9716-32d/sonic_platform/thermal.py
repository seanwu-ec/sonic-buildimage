#!/usr/bin/env python


try:
    import sonic_platform
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


def is_fan_dir_F2B():
    fan = sonic_platform.platform.Platform().get_chassis().get_fan(0)
    return fan.get_direction() == fan.FAN_DIRECTION_EXHAUST


class Threshold():
    def __init__(self, high_crit, high_err, high_warn, low_warn=0, low_err=None, low_crit=None):
        self.__data = {
            'high_crit' : high_crit,
            'high_err' : high_err,
            'high_warn' : high_warn,
            'low_warn' : low_warn,
            'low_err' : low_err,
            'low_crit' : low_crit
        }

    def __getitem__(self, key):
        if key in self.__data:
            return self.__data[key]
        else:
            return None


class Thermal(PddfThermal):
    """PDDF Platform-Specific Thermal class"""

    __thresholds_F2B = {
        0: Threshold(77.0, 72.0, 68.0),
        1: Threshold(73.0, 68.0, 64.0),
        2: Threshold(74.0, 69.0, 65.0),
        3: Threshold(77.0, 72.0, 68.0),
        4: Threshold(70.0, 65.0, 61.0),
        5: Threshold(69.0, 64.0, 60.0),
        6: Threshold(73.0, 68.0, 64.0)
    }
    __thresholds_B2F = {
        0: Threshold(75.0, 70.0, 66.0),
        1: Threshold(65.0, 60.0, 56.0),
        2: Threshold(63.0, 58.0, 54.0),
        3: Threshold(52.0, 47.0, 43.0),
        4: Threshold(63.0, 58.0, 54.0),
        5: Threshold(58.0, 53.0, 49.0),
        6: Threshold(60.0, 55.0, 51.0)
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
            return self.__thresholds[self.__index][type]
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
