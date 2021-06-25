#!/usr/bin/env python3

import json
import sonic_platform


def dump_thermal_thresholds():
    chassis = sonic_platform.platform.Platform().get_chassis()
    output = dict()
    for index, thermal in enumerate(chassis.get_all_thermals()):
        high_crit = thermal.get_high_critical_threshold()
        high_err = thermal.get_high_threshold()
        high_warn = thermal.get_high_warning_threshold()
        low_warn = thermal.get_low_warning_threshold()

        output[str(index + 1)] = {
            "error": int(high_err*1000),
            "shutdown": int(high_crit*1000),
            "warning_lower": int(low_warn*1000),
            "warning_upper": int(high_warn*1000),
        }
    print(json.dumps(output, indent=4))

if __name__ == '__main__':
    dump_thermal_thresholds()
