#############################################################################
# Edgecore
#
# Module contains an implementation of SONiC Platform Base API and
# provides the fan status which are available in the platform
#
#############################################################################



try:
    from sonic_platform_base.fan_base import FanBase
    from sonic_platform_base.fan_drawer_base import FanDrawerBase
    from .helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

PSU_FAN_MAX_RPM = 26688
FAN_MAX_RPM = 13000

CPLD_I2C_PATH = "/sys/bus/i2c/devices/3-0060/fan_"
PSU_HWMON_I2C_PATH ="/sys/bus/i2c/devices/{}-00{}/"
PSU_I2C_MAPPING = {
    0: {
        "num": 10,
        "addr": "58"
    },
    1: {
        "num": 11,
        "addr": "59"
    },
}
FANLED_FNODE = "/sys/class/leds/fan/brightness"
FANLED_MODES = {
    "0": FanBase.STATUS_LED_COLOR_OFF,
    "1": FanBase.STATUS_LED_COLOR_GREEN,
    "2": FanBase.STATUS_LED_COLOR_AMBER
}


class Fan(FanBase):
    """Platform-specific Fan class"""

    def __init__(self, fan_tray_index, fan_index=0, is_psu_fan=False, psu_index=0):
        self._api_helper=APIHelper()
        self.fan_index = fan_index
        self.fan_tray_index = fan_tray_index
        self.is_psu_fan = is_psu_fan

        if self.is_psu_fan:
            self.psu_index = psu_index
            self.psu_i2c_num = PSU_I2C_MAPPING[self.psu_index]['num']
            self.psu_i2c_addr = PSU_I2C_MAPPING[self.psu_index]['addr']
            self.psu_hwmon_path = PSU_HWMON_I2C_PATH.format(
                self.psu_i2c_num, self.psu_i2c_addr)

        FanBase.__init__(self)  


    def get_direction(self):
        """
        Retrieves the direction of fan
        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction
        """
        if not self.is_psu_fan:
            dir_str = "{}{}{}".format(CPLD_I2C_PATH, 'direction_', self.fan_tray_index+1)
            val=self._api_helper.read_txt_file(dir_str)
            if val is not None:
                if int(val, 10)==0:#F2B
                    direction=self.FAN_DIRECTION_EXHAUST
                else:
                    direction=self.FAN_DIRECTION_INTAKE
            else:
                direction=self.FAN_DIRECTION_EXHAUST
                
        else: #For PSU
            dir_str = "{}{}".format(self.psu_hwmon_path,'psu_fan_dir')
            val=self._api_helper.read_txt_file(dir_str)
            if val is not None:
                if val=='F2B':
                    direction=self.FAN_DIRECTION_EXHAUST
                else:
                    direction=self.FAN_DIRECTION_INTAKE
            else:
                direction=self.FAN_DIRECTION_EXHAUST
                
        return direction

    def get_speed(self):
        """
        Retrieves the speed of fan as a percentage of full speed
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
                         
        """
        speed = 0
        if self.is_psu_fan:
            psu_fan_path= "{}{}".format(self.psu_hwmon_path, 'psu_fan1_speed_rpm')
            fan_speed_rpm = self._api_helper.read_txt_file(psu_fan_path)
            if fan_speed_rpm is not None:
                speed = (int(fan_speed_rpm,10))*100/PSU_FAN_MAX_RPM
                if speed > 100:
                    speed=100
            else:
                return 0
        elif self.get_presence():            
            speed_path = "{}{}{}".format(CPLD_I2C_PATH, 'speed_rpm_', self.fan_tray_index+1)
            speed_rpm=self._api_helper.read_txt_file(speed_path)
            if speed_rpm is None:
                return 0
            else:
                speed_rpm = int(speed_rpm)
                speed = speed_rpm*100/FAN_MAX_RPM if speed_rpm < FAN_MAX_RPM else 100
        return int(speed)
            
    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan
        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)

        Note:
            speed_pc = pwm_target/255*100

            0   : when PWM mode is use
            pwm : when pwm mode is not use
        """
        if self.is_psu_fan:
            raise NotImplementedError
        if not self.get_presence():
            return 0

        speed_path = "{}{}".format(CPLD_I2C_PATH, 'duty_cycle_percentage')
        speed = self._api_helper.read_txt_file(speed_path)
        return int(speed) if speed is not None else 0

    def get_speed_tolerance(self):
        """
        Retrieves the speed tolerance of the fan
        Returns:
            An integer, the percentage of variance from target speed which is
                 considered tolerable
        """
        return 80

    def set_speed(self, speed):
        """
        Sets the fan speed
        Args:
            speed: An integer, the percentage of full fan speed to set fan to,
                   in the range 0 (off) to 100 (full speed)
        Returns:
            A boolean, True if speed is set successfully, False if not

        """
        
        if not self.is_psu_fan and self.get_presence():            
            speed_path = "{}{}".format(CPLD_I2C_PATH, 'duty_cycle_percentage')
            return self._api_helper.write_txt_file(speed_path, int(speed))

        return False

    def set_status_led(self, color):
        """
        Sets the state of the fan module status LED
        Args:
            color: A string representing the color with which to set the
                   fan module status LED
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        return False #Not supported
   
    def get_status_led(self):
        """
        Gets the state of the fan status LED
        Returns:
            A string, one of the predefined STATUS_LED_COLOR_* strings above
        """
        if self.is_psu_fan:
            raise NotImplementedError
        read_val=self._api_helper.read_txt_file(FANLED_FNODE)
        return FANLED_MODES[read_val] if read_val in FANLED_MODES else "unknown"

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        if not self.is_psu_fan:
            fan_name = "FAN-{}".format(self.fan_tray_index+1)
        else:
            fan_name = "PSU-{} FAN-{}".format(self.psu_index+1, self.fan_index+1)
        return fan_name
            
    def get_presence(self):
        """
        Retrieves the presence of the FAN
        Returns:
            bool: True if FAN is present, False if not
        """
        present_path = "{}{}{}".format(CPLD_I2C_PATH, 'present_', self.fan_tray_index+1)
        val=self._api_helper.read_txt_file(present_path)
        if not self.is_psu_fan:
            if val is not None:
                return int(val, 10)==1
            else:
                return False
        else:
            return True

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if self.is_psu_fan:
            psu_fan_path= "{}{}".format(self.psu_hwmon_path, 'psu_fan1_fault')
            val=self._api_helper.read_txt_file(psu_fan_path)
            if val is not None:
                return int(val, 10)==0
            else:
                return False
        else:    
            path = "{}{}{}".format(CPLD_I2C_PATH, 'fault_', self.fan_tray_index+1)
            val=self._api_helper.read_txt_file(path)
            if val is not None:
                return int(val, 10)==0
            else:
                return False

    
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


class FanDrawer(FanDrawerBase):
    pass
