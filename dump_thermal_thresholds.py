#!/usr/bin/env python3

import json
import sys

class PlatformModuleLoader():
    """ module loader for API1.0 """

    @classmethod
    def load_module_from_source(cls, module_name, file_path):
        """
        This function will load the Python source file specified by <file_path>
        as a module named <module_name> and return an instance of the module
        """
        module = None

        # TODO: Remove this check once we no longer support Python 2
        if sys.version_info.major == 3:
            import importlib.machinery
            import importlib.util
            loader = importlib.machinery.SourceFileLoader(module_name, file_path)
            spec = importlib.util.spec_from_loader(loader.name, loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
        else:
            import imp
            module = imp.load_source(module_name, file_path)

        sys.modules[module_name] = module

        return module

    @classmethod
    def __get_platform(cls):
        '''
        return Accton platform string, likes "as7816_64x", NOT very generic.
        '''
        import re
        from sonic_py_common import device_info
        platform = device_info.get_platform()
        match = re.search('as\d\d\d\d[\d\w]+', platform)
        if match:
            return match.group()
        else:
            raise Exception(f'{platform} is NOT a leagal plaform string')

    @classmethod
    def __get_module_filepath(cls, module):
        PKG_DIR = '/usr/lib/python2.7/dist-packages/'
        return PKG_DIR + cls.__get_platform() + '/' + module + '.py'

    @classmethod
    def load_platform_util(cls, module_name, class_name):
        filepath = cls.__get_module_filepath(module_name)
        module =  cls.load_module_from_source(module_name, filepath)
        util_class = getattr(module, class_name)
        return util_class()


def dump_thermal_thresholds_api2():
    import sonic_platform
    chassis = sonic_platform.platform.Platform().get_chassis()
    output = dict()
    for index, thermal in enumerate(chassis.get_all_thermals()):
        high_crit = thermal.get_high_critical_threshold()
        high_err = thermal.get_high_threshold()
        high_warn = thermal.get_high_warning_threshold()
        low_warn = thermal.get_low_warning_threshold()

        if high_crit==None and high_err==None and high_warn==None and low_warn==None:
            continue

        output[str(index + 1)] = {
            "error": int(high_err*1000),
            "shutdown": int(high_crit*1000),
            "warning_lower": int(low_warn*1000),
            "warning_upper": int(high_warn*1000),
        }
    print(json.dumps(output, indent=4))

def dump_thermal_thresholds_api1():
    thermalutil = PlatformModuleLoader.load_platform_util('thermalutil', 'ThermalUtil')
    output = dict()
    for i in range(1, thermalutil.get_num_thermals()):
        high_crit = thermalutil.get_high_critical_threshold(i)
        high_err = thermalutil.get_high_threshold(i)
        high_warn = thermalutil.get_high_warning_threshold(i)
        low_warn = thermalutil.get_low_warning_threshold(i)

        if high_crit==None and high_err==None and high_warn==None and low_warn==None:
            continue

        output[str(i)] = {
            "error": int(high_err*1000),
            "shutdown": int(high_crit*1000),
            "warning_lower": int(low_warn*1000),
            "warning_upper": int(high_warn*1000),
        }
    print(json.dumps(output, indent=4))


def dump_thermal_thresholds():
    try:
        dump_thermal_thresholds_api2()
    except:
        dump_thermal_thresholds_api1()


if __name__ == '__main__':
    dump_thermal_thresholds()
