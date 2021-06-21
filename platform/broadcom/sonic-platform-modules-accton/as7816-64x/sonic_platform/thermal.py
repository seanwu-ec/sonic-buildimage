#!/usr/bin/env python


try:
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


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

    __thresholds = {
        0: Threshold(59.0, 56.0, 53.0),
        1: Threshold(60.0, 57.0, 54.0),
        2: Threshold(70.25, 68.625, 67.0),
        3: Threshold(70.49, 70.245, 70.0),
        4: Threshold(56.0, 55.5, 55.0),
        5: Threshold(55.75, 54.875, 54.0)
    }

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfThermal.__init__(self, index, pddf_data, pddf_plugin_data)
        self.__index = index

    # Provide the functions/variables below for which implementation is to be overwritten

    def __try_get_threshold(self, type):
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


# import sonic_platform
# def dump():
#     chassis = sonic_platform.platform.Platform().get_chassis()
#     print('Dump thermal thresholds:')
#     for index, thermal in enumerate(chassis.get_all_thermals()):
#         high_crit = thermal.get_high_critical_threshold()
#         high_err = thermal.get_high_threshold()
#         high_warn = thermal.get_high_warning_threshold()
#         low_warn = thermal.get_low_warning_threshold()
#         low_err = thermal.get_low_threshold()
#         low_crit = thermal.get_low_critical_threshold()
#         print(f'{index}:{{h_c={high_crit}, h_e={high_err}, h_w={high_warn}, l_w={low_warn}, l_e={low_err}, l_c={low_crit} }}')

# if __name__ == '__main__':
#     dump()
