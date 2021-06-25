#!/usr/bin/env python


try:
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")



class Thermal(PddfThermal):
    """PDDF Platform-Specific Thermal class"""

    __thresholds = {
        0: {'crit_high': 80.0, 'high':  60.0, 'low': 0.0, 'crit_low': -20.0},
        1: {'crit_high': 81.0, 'high':  61.0, 'low': 1.0, 'crit_low': -21.0},
        2: {'crit_high': 82.0, 'high':  62.0, 'low': 2.0, 'crit_low': -22.0},
        3: {'crit_high': 83.0, 'high':  63.0, 'low': 3.0, 'crit_low': -23.0},
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

    def get_high_threshold(self):
        return self.__try_get_threshold('high')

    def get_low_threshold(self):
        return self.__try_get_threshold('low')

    def get_high_critical_threshold(self):
        return self.__try_get_threshold('crit_high')

    def get_low_critical_threshold(self):
        return self.__try_get_threshold('crit_low')
