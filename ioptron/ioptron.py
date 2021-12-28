# iOptron telescope Python interface
## Based on onstep-python

# Imports
from dataclasses import dataclass
from serial.serialutil import XOFF, SerialException
from yaml.error import YAMLError
import ioptron.iotty as iotty
import time
import ioptron.utils as utils

# Data classes
## Firmwares
@dataclass
class Firmwares:
    mainboard: str = None
    hand_controller: str = None
    ra: str = None
    dec: str = None

## GPS state
@dataclass
class GpsState:
    available: bool = False
    locked: bool = False

## System status
@dataclass
class SystemStatus:
    code: int = None
    description: str = None

## Tracking rate
@dataclass
class TrackingRate:
    code: int = None
    description: str = "off"

## Moving speed
@dataclass
class MovingSpeed:
    code: int = None
    multiplier: int = None
    description: str = None

## Time source
@dataclass
class TimeSource:
    code: int = None
    description: str = "unset"

## Time information
@dataclass
class TimeInfo:
    utc_offset: int = None
    dst: bool = None
    jd: int = None
    unix: float = None
    formatted: str = None

## Hemisphere
@dataclass
class Hemisphere:
    code: int = None
    location: str = None

class ioptron:
    def __init__(self, port = ''):
        if port != '':
            self.scope = iotty.iotty(port=port)
            self.scope.open()
        else:
            raise SerialException
    
        # Assign default values
        self.longitude = None
        self.latitude = None
        main_fw_info = self.get_main_firmwares()
        motor_fw_info = self.get_motor_firmwares()
        self.firmware = Firmwares(mainboard=main_fw_info[0], hand_controller=main_fw_info[1], \
            ra=motor_fw_info[0], dec=motor_fw_info[1])
        self.gps = GpsState()
        self.hand_controller_attached = False if 'xx' in self.firmware.hand_controller else True
        self.system_status = SystemStatus()
        self.tracking_rate = TrackingRate()
        self.time_source = TimeSource()
        self.hemisphere = Hemisphere()
        self.moving_speed = MovingSpeed()
        self.is_slewing = False
        self.is_tracking = False
        self.is_parked = None
        self.mount_version = self.get_mount_version()
        self.type = None
        self.position = None
        self.is_home = None
        self.pier_side = None
        self.pec_recorded = False
        self.pec = None
        self.pps = False
        self.mount_config_data = utils.parse_mount_config_file('ioptron/mount_values.yaml', self.mount_version)
        self.last_update = time.time()
        # Time information
        self.time = TimeInfo()

    # Destructor that gets called when the object is destroyed
    def __del__(self):
        # Close the serial connection
        try:
            self.scope.close()
        except:
            print("CLEANUP: not needed or was unclean")

    # Get the current azimuth
    #def get_azimuth(self):

    # To get the joke here, read the official protocol docs
    def get_all_kinds_of_status(self):
        self.scope.send(":GLS#")
        response_data = self.scope.recv()
        print(response_data)

        # Parse latitude and longitude
        self.longitude = utils.arc_seconds_to_degrees(int(response_data[0:9]))
        self.latitude = utils.arc_seconds_to_degrees(int(response_data[9:17])) - 90 # Val is +90
        
        # Parse GPS state
        gps_state = response_data[17:18]
        if gps_state == '0':
            self.gps.available = False
        elif gps_state == '1':
            self.gps.available = True
            self.gps.locked = False
        elif gps_state == '2':
            self.gps.available = True
            self.gps.locked = True
        
        # Parse the system status
        status_code = response_data[18:19]
        self.system_status.code = status_code
        if status_code == '0':
            self.system_status.description = "stopped at non-zero position" 
            self.is_slewing = False
            self.is_tracking = False
        elif status_code == '1':
            self.system_status.description = "tracking with periodic error correction disabled"
            self.is_slewing = False
            self.is_tracking = True
            self.pec = False 
        elif status_code == '2':
            self.system_status.description = "slewing"
            self.is_slewing = True
            self.is_tracking = False 
        elif status_code == '3':
            self.system_status.description = "auto-guiding"
            self.is_slewing = False
            self.is_tracking = True 
        elif status_code == '4':
            self.system_status.description = "meridian flipping"
            self.is_slewing = True
        elif status_code == '5':
            self.system_status.description = "tracking with periodic error correction enabled"
            self.is_slewing = False
            self.is_tracking = True
            self.pec = True 
        elif status_code == '6':
            self.system_status.description = "parked"
            self.is_slewing = False
            self.is_tracking = False
            self.is_parked = True 
        elif status_code == '7':
            self.system_status.description = "stopped at zero position (home position)"
            self.is_slewing = False
            self.is_tracking = False

        # Parse tracking rate
        tracking_rate = response_data[19:20]
        self.tracking_rate.code = status_code
        self.tracking_rate.description = self.parse_tracking_rate(tracking_rate)

        # Parse moving speed
        moving_speed = response_data[20:21]
        self.moving_speed.code = moving_speed
        self.moving_speed.description = self.parse_moving_speed(int(moving_speed))

        # Parse the time source
        time_source = response_data[21:22]
        print(time_source)
        self.time_source.code = time_source
        if time_source == '1':
            self.time_source.description = "local port - RS232 or ethernet"
        elif time_source == '2':
            self.time_source.descriptio = "hand controller"
        elif time_source == '3':
            self.time_source.description == "gps"
        
        # Parse the hemisphere
        hemisphere = response_data[22:23]
        self.hemisphere.code = hemisphere
        if hemisphere == '0':
            self.hemisphere.location = 's'
        if hemisphere == '1':
            self.hemisphere.location = 'n'

    # Get the main firmwares (mount, hand controller)
    def get_main_firmwares(self):
        self.scope.send(':FW1#')
        returned_data = self.scope.recv()
        main_fw = returned_data[0:6]
        hc_fw = returned_data[6:12]
        return (main_fw, hc_fw)

    # Get the motor firmwares (ra, dec)
    def get_motor_firmwares(self):
        self.scope.send(':FW2#')
        returned_data = self.scope.recv()
        ra = returned_data[0:6]
        dec = returned_data[6:12]
        return (ra, dec)

    # Get the version of the mount (this is the model)
    def get_mount_version(self):
        self.scope.send(':MountInfo#')
        return self.scope.recv()

    # Get time-related information. This command returns a ton of data from the mount
    def get_time_information(self):
        response_data = self.scope.send(':GUT#')
        self.time.utc_offset = int(response_data[0:4])
        self.time.dst = False if response_data[4:5] == '0' else True
        self.time.jd = response_data[5:]
        self.time.unix = utils.convert_j2k_to_unix(self.time.jd)
        self.time.formatted = utils.convert_unix_to_formatted(self.time.unix)

    # Go to zero position
    def go_to_zero_position(self):
        self.scope.send(':MH#')
        self.is_slewing = True

    # Go to zero position
    def go_to_mechanical_zero_position(self):
        ## TODO: This is a good place to log a WARN
        if self.mount_version in ['0040', '0041', '0043', '0044', '0070', '0071','0120', '0121', '0122']:
            self.scope.send(':MSH#')
            self.is_slewing = True
        # Maybe worth throwing an exception

    # Park the moint (using pre-defined parking spot)
    def park(self):
        self.scope.send(':MP1#')
        response = self.scope.recv()
        if response == "1":
            # Mount parked OK
            self.is_parked = True
        else:
            # Mount was mot parked OK
            self.is_parked = False
        return self.is_parked
    
    # Parse moving speed
    ## In the future, we could use a YAML based dict to decide stuff like max/model
    def parse_moving_speed(self, rate):
        return str(self.mount_config_data['tracking_speeds'][rate]) + 'x'
        
    # Parse tracking rate
    ## In the future, we could use a YAML based dict to decide stuff like max/model
    def parse_tracking_rate(self, rate):
        if rate == '0':
            return 'sidereal'
        elif rate == '1':
            return 'lunar'
        elif rate == '2':
            return 'solar'
        elif rate == '3':
            return 'king'
        elif rate == '4':
            return 'custom'
        else:
            return 'off'
    
    # Reset all settings (time is unchanged)
    # Must pass a TRUE to indicate you _really_ want to do this
    def reset_settings(self, confirm: bool):
        if confirm == True:
            self.scope.send(':RAS#')
            self.get_all_kinds_of_status
            # TODO: Update other info once implemented

    def send_str(self, string):
        # Send a string
        self.scope.send(string)
        return self.scope.recv()
    
    # Set daylight savings time (on = True, off = False)
    def set_daylight_savings(self, dst: bool):
        if dst == True:
            self.scope.send(':SDS1#')
        else:
            self.scope.send(':SDS#0')
        
        # Update time information after setting
        self.get_time_information()

    # Stop all movement
    def stop_all_movement(self):
        self.scope.send(':Q#')
        self.is_slewing = False

    # Stop East or West movement (arrows or :me# or :mw#)
    def stop_e_or_w_movement(self):
        self.scope.send(':qR#')
        self.is_slewing = False
    
    # Stop North or South movement (arrows or :me# or :mw#)
    def stop_n_or_s_movement(self):
        self.scope.send(':qD#')
        self.is_slewing = False
    
    def unpark(self):
        self.scope.send(':MP0#')
        # Always returns a 1
        self.is_parked = False
        return self.is_parked
    
    def update_status(self):
        # Do this at max of every one second
        current_time = time.time()
        if current_time - self.last_update > 1:
            self.scope.send(':MP0#')