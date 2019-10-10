import smbus
import time

# Get I2C bus
bus = smbus.SMBus(1)

# I2C Address of the device
TCA9548A_DEFAULT_ADDRESS = 0x70

class TCA9548A():
    def __init__(self,address=TCA9548A_DEFAULT_ADDRESS):
        self.i2caddress = address
    def tcaselect(self,portnum):
        """tells the multiplexer to select a port"""
        bus.write_byte_data(self.i2caddress,1,1<<portnum)
    def scan(self):
        """scans through all multiplexer channels and all i2c addresses.
        If the data send doesn't fail, it means there's a device there."""
        devices = []
        for mult_ind in range(8):
            #this part scans across all possible multiplexers
            self.tcaselect(mult_ind)
            for i in range(127):
                if(i==self.i2caddress):
                    continue
                else:
                    try:
                        bus.write_byte_data(i,0,0)
                        devices+=[[mult_ind,i]]
                    except OSError:
                        #this happens if we don't find a device
                        pass
        return devices
