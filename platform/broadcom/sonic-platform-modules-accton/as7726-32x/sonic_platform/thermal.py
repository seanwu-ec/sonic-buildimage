#!/usr/bin/env python


try:
    from collections import namedtuple
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


Threshold = namedtuple('Threshold', ['high_crit', 'high_err', 'high_warn',
                       'low_warn', 'low_err', 'low_crit'], defaults=[0]*6)


class Thermal(PddfThermal):
    """PDDF Platform-Specific Thermal class"""

    _thresholds = {
        0: Threshold(80.0, 70.0, 60.0, 0.0, -10.0, -20.0),
        1: Threshold(81.0, 71.0, 61.0, 1.0, -11.0, -21.0),
        2: Threshold(82.0, 72.0, 62.0, 2.0, -12.0, -22.0),
        3: Threshold(83.0, 73.0, 63.0, 3.0, -13.0, -23.0),
        4: Threshold(84.0, 74.0, 64.0, 4.0, -14.0, -24.0)
    }

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfThermal.__init__(self, index, pddf_data, pddf_plugin_data)
        self._index = index

    # Provide the functions/variables below for which implementation is to be overwritten

    def _try_get_threshold(self, type):
        if self._index in self._thresholds:
            return getattr(self._thresholds[self._index], type)
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
