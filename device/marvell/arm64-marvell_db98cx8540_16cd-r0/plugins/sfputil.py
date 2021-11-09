#!/usr/bin/env python

try:
    import os
    import time
    import sys
    import re
    import subprocess
    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

if sys.version_info[0] < 3:
        import commands as cmd
else:
        import subprocess as cmd

smbus_present = 1

try:
    import smbus
except ImportError as e:
    smbus_present = 0

profile_16x400G = {
  0:"0x70,4",   1:"0x70,4",   2:"0x70,4",   3:"0x70,4",   4:"0x70,4",   5:"0x70,4",   6:"0x70,4",   7:"0x70,4",
  8:"0x70,5",   9:"0x70,5",  10:"0x70,5",  11:"0x70,5",  12:"0x70,5",  13:"0x70,5",  14:"0x70,5",  15:"0x70,5",
 16:"0x70,6",  17:"0x70,6",  18:"0x70,6",  19:"0x70,6",  20:"0x70,6",  21:"0x70,6",  22:"0x70,6",  23:"0x70,6",
 24:"0x70,7",  25:"0x70,7",  26:"0x70,7",  27:"0x70,7",  28:"0x70,7",  29:"0x70,7",  30:"0x70,7",  31:"0x70,7",
 32:"0x70,0",  33:"0x70,0",  34:"0x70,0",  35:"0x70,0",  36:"0x70,0",  37:"0x70,0",  38:"0x70,0",  39:"0x70,0",
 40:"0x70,1",  41:"0x70,1",  42:"0x70,1",  43:"0x70,1",  44:"0x70,1",  45:"0x70,1",  46:"0x70,1",  47:"0x70,1",
 48:"0x70,2",  49:"0x70,2",  50:"0x70,2",  51:"0x70,2",  52:"0x70,2",  53:"0x70,2",  54:"0x70,2",  55:"0x70,2",
 56:"0x70,3",  57:"0x70,3",  58:"0x70,3",  59:"0x70,3",  60:"0x70,3",  61:"0x70,3",  62:"0x70,3",  63:"0x70,3",
 64:"0x71,4",  65:"0x71,4",  66:"0x71,4",  67:"0x71,4",  68:"0x71,4",  69:"0x71,4",  70:"0x71,4",  71:"0x71,4",
 72:"0x71,5",  73:"0x71,5",  74:"0x71,5",  75:"0x71,5",  76:"0x71,5",  77:"0x71,5",  78:"0x71,5",  79:"0x71,5",
 80:"0x71,6",  81:"0x71,6",  82:"0x71,6",  83:"0x71,6",  84:"0x71,6",  85:"0x71,6",  86:"0x71,6",  87:"0x71,6",
 88:"0x71,7",  89:"0x71,7",  90:"0x71,7",  91:"0x71,7",  92:"0x71,7",  93:"0x71,7",  94:"0x71,7",  95:"0x71,7",
 96:"0x71,0",  97:"0x71,0",  98:"0x71,0",  99:"0x71,0", 100:"0x71,0", 101:"0x71,0", 102:"0x71,0", 103:"0x71,0",
104:"0x71,1", 105:"0x71,1", 106:"0x71,1", 107:"0x71,1", 108:"0x71,1", 109:"0x71,1", 110:"0x71,1", 111:"0x71,1",
112:"0x71,2", 113:"0x71,2", 114:"0x71,2", 115:"0x71,2", 116:"0x71,2", 117:"0x71,2", 118:"0x71,2", 119:"0x71,2",
120:"0x71,3", 121:"0x71,3", 122:"0x71,3", 123:"0x71,3", 124:"0x71,3", 125:"0x71,3", 126:"0x71,3", 127:"0x71,3",
128:"0x74,4", 129:"0x74,5" }


profile_64x25G = {
  0:"0x70,4",   1:"0x70,4",   2:"0x70,4",   3:"0x70,4",   4:"0x70,5",   5:"0x70,5",   6:"0x70,5",   7:"0x70,5",
  8:"0x70,6",   9:"0x70,6",  10:"0x70,6",  11:"0x70,6",  12:"0x70,7",  13:"0x70,7",  14:"0x70,7",  15:"0x70,7",
 16:"0x70,0",  17:"0x70,0",  18:"0x70,0",  19:"0x70,0",  20:"0x70,1",  21:"0x70,1",  22:"0x70,1",  23:"0x70,1",
 24:"0x70,2",  25:"0x70,2",  26:"0x70,2",  27:"0x70,2",  28:"0x70,3",  29:"0x70,3",  30:"0x70,3",  31:"0x70,3",
 32:"0x71,4",  33:"0x71,4",  34:"0x71,4",  35:"0x71,4",  36:"0x71,5",  37:"0x71,5",  38:"0x71,5",  39:"0x71,5",
 40:"0x71,6",  41:"0x71,6",  42:"0x71,6",  43:"0x71,6",  44:"0x71,7",  45:"0x71,7",  46:"0x71,7",  47:"0x71,7",
 48:"0x71,0",  49:"0x71,0",  50:"0x71,0",  51:"0x71,0",  52:"0x71,1",  53:"0x71,1",  54:"0x71,1",  55:"0x71,1",
 56:"0x71,2",  57:"0x71,2",  58:"0x71,2",  59:"0x71,2",  60:"0x71,3",  61:"0x71,3",  62:"0x71,3",  63:"0x71,3",
 64:"0x74,4",  65:"0x74,5" }

profile_32x25G = {
  0:"0x70,4",   1:"0x70,4",   2:"0x70,5",   3:"0x70,5",   4:"0x70,6",   5:"0x70,6",   6:"0x70,7",   7:"0x70,7",
  8:"0x70,0",   9:"0x70,0",  10:"0x70,1",  11:"0x70,1",  12:"0x70,2",  13:"0x70,2",  14:"0x70,3",  15:"0x70,3",
 16:"0x71,4",  17:"0x71,4",  18:"0x71,5",  19:"0x71,5",  20:"0x71,6",  21:"0x71,6",  22:"0x71,7",  23:"0x71,7",
 24:"0x71,0",  25:"0x71,0",  26:"0x71,1",  27:"0x71,1",  28:"0x71,2",  29:"0x71,2",  30:"0x71,3",  31:"0x71,3",
 32:"0x74,4",  33:"0x74,5" }

profile_16x25G = {
 0:"0x70,4",   1:"0x70,5",   2:"0x70,6",   3:"0x70,7",   4:"0x70,0",   5:"0x70,1",   6:"0x70,2",   7:"0x70,3",
 8:"0x71,4",   9:"0x71,5",  10:"0x71,6",  11:"0x71,7",  12:"0x71,0",  13:"0x71,1",  14:"0x71,2",  15:"0x71,3",
16:"0x74,4",  17:"0x74,5" }

profile_16x25G_ixia = {
 0:"0x70,4",   1:"0x70,4",   2:"0x70,4",   3:"0x70,4",   4:"0x70,5",   5:"0x70,5",   6:"0x70,5",   7:"0x70,5",
 8:"0x70,6",   9:"0x70,6",  10:"0x70,6",  11:"0x70,6",  12:"0x70,7",  13:"0x70,7",  14:"0x70,7",  15:"0x70,7",
16:"0x74,4",  17:"0x74,5" }

profile_24x25G_4x200G = {
  0:"0x70,4",   1:"0x70,4",   2:"0x70,5",   3:"0x70,5",   4:"0x70,6",   5:"0x70,6",   6:"0x70,7",   7:"0x70,7",
  8:"0x70,0",   9:"0x70,0",  10:"0x70,1",  11:"0x70,1",  12:"0x70,2",  13:"0x70,2",  14:"0x70,3",  15:"0x70,3",
 16:"0x71,4",  17:"0x71,4",  18:"0x71,5",  19:"0x71,5",  20:"0x71,6",  21:"0x71,6",  22:"0x71,7",  23:"0x71,7",
 24:"0x71,0",  25:"0x71,0",  26:"0x71,0",  27:"0x71,0",  28:"0x71,1",  29:"0x71,1",  30:"0x71,1",  31:"0x71,1",
 32:"0x71,2",  33:"0x71,2",  34:"0x71,2",  35:"0x71,2",  36:"0x71,3",  37:"0x71,3",  38:"0x71,3",  39:"0x71,3",
 40:"0x74,4",  41:"0x74,5" }

profile_24x25G_8x200G = {
  0:"0x70,4",   1:"0x70,4",   2:"0x70,5",   3:"0x70,5",   4:"0x70,6",   5:"0x70,6",   6:"0x70,7",   7:"0x70,7",
  8:"0x70,0",   9:"0x70,0",  10:"0x70,1",  11:"0x70,1",  12:"0x70,2",  13:"0x70,2",  14:"0x70,3",  15:"0x70,3",
 16:"0x71,4",  17:"0x71,4",  18:"0x71,5",  19:"0x71,5",  20:"0x71,6",  21:"0x71,6",  22:"0x71,7",  23:"0x71,7",
 24:"0x71,0",  25:"0x71,0",  26:"0x71,0",  27:"0x71,0",  28:"0x71,0",  29:"0x71,0",  30:"0x71,0",  31:"0x71,0",
 32:"0x71,1",  33:"0x71,1",  34:"0x71,1",  35:"0x71,1",  36:"0x71,1",  37:"0x71,1",  38:"0x71,1",  39:"0x71,1",
 40:"0x71,2",  41:"0x71,2",  42:"0x71,2",  43:"0x71,2",  44:"0x71,2",  45:"0x71,2",  46:"0x71,2",  47:"0x71,2",
 48:"0x71,3",  49:"0x71,3",  50:"0x71,3",  51:"0x71,3",  52:"0x71,3",  53:"0x71,3",  54:"0x71,3",  55:"0x71,3",
 56:"0x74,4",  57:"0x74,5" }

profile_48x25G_8x100G = {
  0:"0x70,4",   1:"0x70,4",   2:"0x70,4",   3:"0x70,4",   4:"0x70,5",   5:"0x70,5",   6:"0x70,5",   7:"0x70,5",
  8:"0x70,6",   9:"0x70,6",  10:"0x70,6",  11:"0x70,6",  12:"0x70,7",  13:"0x70,7",  14:"0x70,7",  15:"0x70,7",
 16:"0x70,0",  17:"0x70,0",  18:"0x70,0",  19:"0x70,0",  20:"0x70,1",  21:"0x70,1",  22:"0x70,1",  23:"0x70,1",
 24:"0x70,2",  25:"0x70,2",  26:"0x70,2",  27:"0x70,2",  28:"0x70,3",  29:"0x70,3",  30:"0x70,3",  31:"0x70,3",
 32:"0x71,4",  33:"0x71,4",  34:"0x71,4",  35:"0x71,4",  36:"0x71,5",  37:"0x71,5",  38:"0x71,5",  39:"0x71,5",
 40:"0x71,6",  41:"0x71,6",  42:"0x71,6",  43:"0x71,6",  44:"0x71,7",  45:"0x71,7",  46:"0x71,7",  47:"0x71,7",
 48:"0x71,0",  49:"0x71,0",  50:"0x71,0",  51:"0x71,0",  52:"0x71,0",  53:"0x71,0",  54:"0x71,0",  55:"0x71,0",
 56:"0x71,1",  57:"0x71,1",  58:"0x71,1",  59:"0x71,1",  60:"0x71,1",  61:"0x71,1",  62:"0x71,1",  63:"0x71,1",
 64:"0x71,2",  65:"0x71,2",  66:"0x71,2",  67:"0x71,2",  68:"0x71,2",  69:"0x71,2",  70:"0x71,2",  71:"0x71,2",
 72:"0x71,3",  73:"0x71,3",  74:"0x71,3",  75:"0x71,3",  76:"0x71,3",  77:"0x71,3",  78:"0x71,3",  79:"0x71,3",
 80:"0x74,4",  81:"0x74,5" }

sfputil_profiles = {
 "FALCON16X25G":profile_16x25G,
 "FC16x25GIXIA":profile_16x25G_ixia,
 "FALCON16x400G":profile_16x400G,
 "FALCON128x50G":profile_16x400G,
 "FALCON64x100G":profile_16x400G,
 "FC16x100G8x400G":profile_16x400G,
 "FC24x100G4x400G":profile_16x400G,
 "FC32x100G8x400G":profile_16x400G,
 "FALCON64x25G":profile_64x25G,
 "FALCON32x25G64":profile_32x25G,
 "FC24x254x200G64":profile_24x25G_4x200G,
 "FC24x258x100G64":profile_24x25G_8x200G,
 "FC48x10G8x100G":profile_48x25G_8x100G,
 "FC48x25G8x100G":profile_48x25G_8x100G
}

class SfpUtil(SfpUtilBase):
    """Platform specific sfputil class"""
    _port_profile = "FALCON16X25G"
    _port_start = 1
    _port_end = 132
    ports_in_block = 132

    _port_to_eeprom_mapping = {}

    _qsfp_ports = range(_port_start, ports_in_block + 1)

    def __init__(self):
        #os.system("modprobe i2c-dev")
        if not os.path.exists("/sys/bus/i2c/devices/0-0050") :
            os.system("echo optoe2 0x50 > /sys/bus/i2c/devices/i2c-0/new_device")

        eeprom_path = '/sys/bus/i2c/devices/0-0050/eeprom'
        #for x in range(self.port _start, self.port_end +1):
        x = self.port_start
        while(x<self.port_end+1):
            self.port_to_eeprom_mapping[x] = eeprom_path
            x = x + 1

        from sonic_py_common import device_info
        hwsku = device_info.get_hwsku()
        platform = device_info.get_platform()
        if platform is not None:
            cmd = "cat /usr/share/sonic/device/" + platform + "/" + hwsku + "/sai.profile | grep hwId | cut -f2 -d="
        else:
            cmd = "cat /usr/share/sonic/platform/" + hwsku + "/sai.profile | grep hwId | cut -f2 -d="

        port_profile = os.popen(cmd).read()
        self._port_profile = port_profile.split("\n")[0]
        SfpUtilBase.__init__(self)

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        port_ps = "/sys/bus/i2c/devices/0-0050/sfp_port_reset"
          
        try:
            reg_file = open(port_ps, 'w')
        except IOError as e:
            print(e)
            #print "Error: unable to open file: %s" % str(e)
            return False

        #toggle reset
        reg_file.seek(0)
        reg_file.write('1')
        time.sleep(1)
        reg_file.seek(0)
        reg_file.write('0')
        reg_file.close()
        return True

    def set_low_power_mode(self, port_nuM, lpmode):
        raise NotImplementedError

    def get_low_power_mode(self, port_num):
        raise NotImplementedError

    def i2c_get(self, device_addr, offset):
        status = 0
        if smbus_present == 0:
            x = "i2cget -y 0 " + hex(device_addr) + " " + hex(offset)
            cmdstatus, status = cmd.getstatusoutput(x)
            if cmdstatus != 0:
                return cmdstatus
            status = int(status, 16)
        else:
            bus = smbus.SMBus(0)
            status = bus.read_byte_data(device_addr, offset)
        return status

    def i2c_set(self, device_addr, offset, value):
        if smbus_present == 0:
            cmd = "i2cset -y 0 " + hex(device_addr) + " " + hex(offset) + " " + hex(value)
            os.system(cmd)
        else:
            bus = smbus.SMBus(0)
            bus.write_byte_data(device_addr, offset, value)
      
    def get_presence(self, port_num):
        # Check for invalid port_num
        port_index = port_num-1
        #print self._port_profile
        profile = sfputil_profiles[self._port_profile]
        if  port_index not in profile:
            return False
        else:
            offset = int(profile[port_index].split(",")[1])
            bin_offset = 1<<offset
            device_reg = int(profile[port_index].split(",")[0],16)

            #print "i2c %d %x %x" % (port_num, device_reg, bin_offset)
            self.i2c_set(device_reg, 0, bin_offset)
            path = "/sys/bus/i2c/devices/0-0050/eeprom"
            try:
                reg_file = open(path,'rb')
                reg_file.seek(1)
                reg_file.read(2)
            except IOError as e:
                return False

            return True

    def read_porttab_mappings(self, porttabfile, var):
        logical = []
        logical_to_bcm = {}
        logical_to_physical = {}
        physical_to_logical = {}
        last_fp_port_index = 0
        last_portname = ""
        first = 1
        port_pos_in_file = 0
        parse_fmt_port_config_ini = False

        try:
            f = open(porttabfile)
        except:
            raise

        parse_fmt_port_config_ini = (os.path.basename(porttabfile) == "port_config.ini")
        # Read the porttab file and generate dicts
        # with mapping for future reference.
        #
        # TODO: Refactor this to use the portconfig.py module that now
        # exists as part of the sonic-config-engine package.
        title = []
        for line in f:
            line.strip()
            if re.search("^#", line) is not None:
                # The current format is: # name lanes alias index speed
                # Where the ordering of the columns can vary
                title = line.split()[1:]
                continue
            #print title

            # Parsing logic for 'port_config.ini' file
            if (parse_fmt_port_config_ini):
                # bcm_port is not explicitly listed in port_config.ini format
                # Currently we assume ports are listed in numerical order according to bcm_port
                # so we use the port's position in the file (zero-based) as bcm_port
                portname = line.split()[0]

                bcm_port = str(port_pos_in_file)


                if "index" in title:
                    fp_port_index = int(line.split()[title.index("index")])
                # Leave the old code for backward compatibility
                #if len(line.split()) >= 4:
                #    fp_port_index = (line.split()[3])
                #    print(fp_port_index)     
                else:
                    fp_port_index = portname.split("Ethernet").pop()
                    fp_port_index = int(fp_port_index.split("s").pop(0))+1
            else:  # Parsing logic for older 'portmap.ini' file
                (portname, bcm_port) = line.split("=")[1].split(",")[:2]

                fp_port_index = portname.split("Ethernet").pop()
                fp_port_index = int(fp_port_index.split("s").pop(0))+1

            if ((len(self.sfp_ports) > 0) and (fp_port_index not in self.sfp_ports)):
                continue

            if first == 1:
                # Initialize last_[physical|logical]_port
                # to the first valid port
                last_fp_port_index = fp_port_index
                last_portname = portname
                first = 0

            logical.append(portname)

            logical_to_bcm[portname] = "xe" + bcm_port
            logical_to_physical[portname] = [fp_port_index]
            if physical_to_logical.get(fp_port_index) is None:
                physical_to_logical[fp_port_index] = [portname]
            else:
                physical_to_logical[fp_port_index].append(
                    portname)

            if (fp_port_index - last_fp_port_index) > 1:
                # last port was a gang port
                for p in range(last_fp_port_index+1, fp_port_index):
                    logical_to_physical[last_portname].append(p)
                    if physical_to_logical.get(p) is None:
                        physical_to_logical[p] = [last_portname]
                    else:
                        physical_to_logical[p].append(last_portname)

            last_fp_port_index = fp_port_index
            last_portname = portname

            port_pos_in_file += 1

        self.logical = logical
        self.logical_to_bcm = logical_to_bcm
        self.logical_to_physical = logical_to_physical
        self.physical_to_logical = physical_to_logical

       
        #print(self.logical_to_physical)
        '''print("logical: " + self.logical)
        print("logical to bcm: " + self.logical_to_bcm)
        print("logical to physical: " + self.logical_to_physical)
        print("physical to logical: " + self.physical_to_logical)'''
        #print("exiting port_tab_mappings")

    def get_logical_to_physical(self, logical_port):
        # Return only first lane num for multi lane ports.
        return {self.logical_to_physical[logical_port][0]}

    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end

    @property
    def qsfp_ports(self):
        return self._qsfp_ports

    @property 
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping

    @property
    def get_transceiver_change_event(self):
        raise NotImplementedError 
