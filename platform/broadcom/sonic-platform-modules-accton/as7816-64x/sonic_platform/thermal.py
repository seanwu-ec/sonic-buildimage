#!/usr/bin/env python


try:
    import sonic_platform
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


def is_fan_dir_F2B():
    fan = sonic_platform.platform.Platform().get_chassis().get_fan(0)
    return fan.get_direction().lower() == fan.FAN_DIRECTION_EXHAUST


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
        0: Threshold(59.0, 56.0, 53.0),
        1: Threshold(60.0, 57.0, 54.0),
        2: Threshold(70.25, 68.625, 67.0),
        3: Threshold(70.49, 70.245, 70.0),
        4: Threshold(56.0, 55.5, 55.0),
        5: Threshold(55.75, 54.875, 54.0)
    }
    __thresholds_B2F = {
        0: Threshold(52.0, 49.5, 47.0),
        1: Threshold(51.0, 49.0, 47.0),
        2: Threshold(71.0, 68.5, 66.0),
        3: Threshold(57.5, 57.25, 57.0),
        4: Threshold(55.0, 53.0, 51.0),
        5: Threshold(50.5, 48.75, 47.0)
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
