# iOptron telescope Python interface
## Based on onstep-python

# Imports
from dataclasses import dataclass
from serial.serialutil import XOFF
import ioptron.iotty as iotty
import time
import ioptron.utils as utils

# Data classes
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

## Hemisphere
@dataclass
class Hemisphere:
    code: int = None
    location: str = None

class ioptron:
    def __init__(self, port = ''):
        if port != '':
            self.scope = iotty.iotty(port=port)
            self.utils = utils.utils()
            self.scope.open()
            self.get_mount_version()
        else:
            raise BadPortException
    
        # Assign default values
        self.longitude = None
        self.latitude = None
        self.gps = GpsState()
        self.system_status = SystemStatus()
        self.tracking_rate = TrackingRate()
        self.time_source = TimeSource()
        self.hemisphere = Hemisphere()
        self.moving_speed = MovingSpeed()
        self.is_slewing = False
        self.is_tracking = False
        self.is_parked = None
        self.type = None
        self.position = None
        self.is_home = None
        self.pier_side = None
        self.pec_recorded = False
        self.pec = None
        self.pps = False
        self.last_update = time.time()

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
        self.longitude = self.utils.arc_seconds_to_degrees(int(response_data[0:9]))
        self.latitude = self.utils.arc_seconds_to_degrees(int(response_data[9:17])) - 90 # Val is +90
        
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
        self.moving_speed.description = self.parse_moving_speed(moving_speed)

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

    def get_mount_version(self):
        self.scope.send(':MountInfo#')
        self.mount_version = self.scope.recv()

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
        if rate == '1':
            return '1x'
        elif rate == '2':
            return '2x'
        elif rate == '3':
            return '8x'
        elif rate == '4':
            return '16x'
        elif rate == '5':
            return '64x'
        elif rate == '6':
            return '128x'
        elif rate == '7':
            return '256x'
        elif rate == '8':
            return '512x'
        elif rate == '9':
            return 'max' # Depends on model
        else:
            return 'off'
        
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

    def send_str(self, string):
        # Send a string
        self.scope.send(string)
        return self.scope.recv()

    def stop(self):
        # Stop all movememnt
        self.scope.send(':Q#')
    
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