# iOptron telescope Python interface
# This is intended to understand how the mount works
# If I am going to trash their software (it IS crap) I need to understand it
# James Malone, 2021

# Imports
from dataclasses import dataclass
import time
from serial.serialutil import SerialException
from ioptron import iotty
from ioptron import utils


# Data classes
## Altitude data
@dataclass
class Altitude:
    arcseconds: float = None
    dms: float = None

## Azimuth data
@dataclass
class Azimuth:
    arcseconds: float = None
    dms: float = None

## DEC data
@dataclass
class DEC:
    arcseconds: float = None
    dms: float = None

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

## RA data
@dataclass
class RA:
    arcseconds: float = None
    dms: float = None

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
    custom: float = 1.0000

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
    unix_utc: float = None
    unix_offset: float = None
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
        self.pec_recorded = False
        self.pec = None
        self.pps = False
        self.mount_config_data = \
            utils.parse_mount_config_file('ioptron/mount_values.yaml', self.mount_version)
        self.last_update = time.time()

        # Time information
        self.time = TimeInfo()

        # Direction information
        self.ra = RA()
        self.dec = DEC()
        self.pier_side = None
        self.counterweight_direction = None
        self.altitude - Altitude()
        self.azimuth = Azimuth()

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
        # TODO: Refactor using YAML config
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
        self.time_source.code = time_source
        if time_source == '1':
            self.time_source.description = "local port - RS232 or ethernet"
        elif time_source == '2':
            self.time_source.description = "hand controller"
        elif time_source == '3':
            self.time_source.description = "gps"

        # Parse the hemisphere
        hemisphere = response_data[22:23]
        self.hemisphere.code = hemisphere
        if hemisphere == '0':
            self.hemisphere.location = 's'
        if hemisphere == '1':
            self.hemisphere.location = 'n'

    def get_alt_and_az(self):
        """Get the altitude and azimuth of the mount's current direction."""
        self.scope.send(':GAC#')
        returned_data = self.scope.recv()

        # Alt
        right_asc = returned_data[0:9]
        self.ra.arcseconds = float(right_asc)
        self.ra.dms = utils.arc_seconds_to_degrees(self.ra.arcseconds)

        # Az
        dec = returned_data[9:18]
        self.dec.arcseconds = float(dec)
        self.dec.dms = utils.arc_seconds_to_degrees(self.dec.arcseconds)

    def get_custom_tracking_rate(self):
        """Get the custom tracking rate, if it is set. Otherwise will be 1.000."""
        self.scope.send(':GTR#')
        returned_data = self.scope.recv()
        # Set the value and strip the control '#' at the end (response is d{5})
        self.tracking_rate.custom = bool(returned_data[:5])

    def get_main_firmwares(self):
        """Get the firmware(s) of the mount and hand controller, if it is attached, otherwise
        a null value (xxxxxx) is used for the HC firmware."""
        self.scope.send(':FW1#')
        returned_data = self.scope.recv()
        main_fw = returned_data[0:6]
        hc_fw = returned_data[6:12]
        return (main_fw, hc_fw)

    def get_motor_firmwares(self):
        """Get the firmware of the motors (ra and dec)."""
        self.scope.send(':FW2#')
        returned_data = self.scope.recv()
        right_asc = returned_data[0:6]
        dec = returned_data[6:12]
        return (right_asc, dec)

    def get_mount_version(self):
        """Get the model / version of the mount. Returns the model number."""
        self.scope.send(':MountInfo#')
        return self.scope.recv()

    def get_ra_and_dec(self):
        """Get the RA and DEC of the telescope's current pointing position."""
        self.scope.send(':GEP#')
        returned_data = self.scope.recv()

        # RA
        right_asc = returned_data[0:9]
        self.ra.arcseconds = float(right_asc)
        self.ra.dms = utils.arc_seconds_to_degrees(self.ra.arcseconds)

        # DEC
        dec = returned_data[9:18]
        self.dec.arcseconds = float(dec)
        self.dec.dms = utils.arc_seconds_to_degrees(self.dec.arcseconds)

        # The following only works for eq mounts
        if self.mount_config_data['type'] == "equatorial":
            # Pier side
            pier_side = returned_data[18:19]
            self.pier_side = self.mount_config_data['pier_sides'][int(pier_side)]

            # Counterweight direction
            counterweight_direction = returned_data[19:20]
            self.counterweight_direction = \
                self.mount_config_data['counterweight_direction'][int(counterweight_direction)]

    def get_time_information(self):
        """Get all time information from the mount, including it's time,
        timezone, and DST setting."""
        self.scope.send(':GUT#')
        response_data = self.scope.recv()
        # Sometimes the response includes a leading 1; I assume it means update OK or new data?
        if response_data[0] == '1':
            self.scope.send(':GUT#')
            response_data = self.scope.recv()
        self.time.utc_offset = int(response_data[0:4])
        self.time.dst = False if response_data[4:5] == '0' else True
        self.time.jd = int(response_data[5:18].lstrip("0"))
        self.time.unix_utc = utils.convert_j2k_to_unix_utc(self.time.jd, self.time.utc_offset)
        self.time.unix_offset = utils.offset_utc_time(self.time.unix_utc, self.time.utc_offset)
        self.time.formatted = utils.convert_unix_to_formatted(self.time.unix_offset)

    def go_to_zero_position(self):
        """Go to the mount's zero position."""
        self.scope.send(':MH#')
        self.is_slewing = True
        # Get the response; do nothing with it
        self.scope.recv()

    def go_to_mechanical_zero_position(self):
        """Search and go to the *mechanical* zero position.
        Only supported by some mounts."""
        ## TODO: This is a good place to log a WARN
        # ['0040', '0041', '0043', '0044', '0070', '0071','0120', '0121', '0122']
        if self.mount_config_data['mechanical_zero'] is True:
            self.scope.send(':MSH#')
            self.is_slewing = True
            # Get the response; do nothing with it
            self.scope.recv()
        # Maybe worth throwing an exception

    def park(self):
        """Park the mount at the most recently defined parking position.
        Returns a true if successful or false if parking failed."""
        self.scope.send(':MP1#')
        response = self.scope.recv()
        if response == "1":
            # Mount parked OK
            self.is_parked = True
        else:
            # Mount was mot parked OK
            self.is_parked = False
        return self.is_parked

    def parse_moving_speed(self, rate):
        """Return the mount's current tracking speed in factors of sidarial rate."""
        return str(self.mount_config_data['tracking_speeds'][rate]) + 'x'

    def parse_tracking_rate(self, rate):
        """Return the human readable tracking rate (i.e. 'siderial') of the mount."""
        return str(self.mount_config_data['tracking_rates'][rate])

    def reset_settings(self, confirm: bool):
        """Reset all settings to default. Only applies if True is specified to indicate
        the reset is really wanted. Does not reset any time-based information."""
        if confirm is True:
            self.scope.send(':RAS#')
            self.get_all_kinds_of_status()
            # TODO: Update other info once implemented

    def set_custom_tracking_rate(self, rate):
        """Set a custom tracking rate to n.nnnn of the siderial rate. Only used
        when 'custom' tracking rate is being used."""
        formatted_rate = (f"{float(rate):.6f}")
        send_command = ":RR" + formatted_rate + "#"
        self.scope.send(send_command)
        # Get the response; do nothing with it
        self.scope.recv()

    def set_daylight_savings(self, dst: bool):
        """Enables daylight savings time when true, disables it when false."""
        if dst is True:
            self.scope.send(':SDS1#')
        else:
            self.scope.send(':SDS0#')
        # Get the response; do nothing with it
        self.scope.recv()

        # Update time information after setting
        #self.get_time_information()

    def set_time(self):
        """Set the current time on the moint to the current computer's time. Sets to UTC."""
        j2k_time = str(utils.get_utc_time_in_j2k()).zfill(13)
        time_command = ":SUT" + j2k_time + "#"
        self.scope.send(time_command)

    def set_timezone_offset(self, offset = utils.get_utc_offset_min()):
        """Sets the time zone offset on the mount to the computer's TZ offset."""
        tz_offset = str(offset).zfill(3)
        tz_command = ":SG" + tz_offset + "#" if offset < 0 else ":SG+" + tz_offset + "#"
        self.scope.send(tz_command)
        # Get the response; do nothing with it
        self.scope.recv()

    def _toggle_pec_recording(self, turn_on: bool):
        """PRIVATE method for toggling PEC recording on and off."""
        if self.mount_config_data['type'] == 'equatorial' and \
            self.mount_config_data['capabilities']['pec'] is True and \
            self.mount_config_data['capabilities']['encoders'] is False:
            # Default is off
            pec_command = ":SPR1#" if turn_on is True else ":SPR0#"
            self.scope.send(pec_command)
        else:
            print("PEC recording not usable with this mount")

    def start_recording_pec(self):
        """Start recording the periodic error. Only used in eq mounts without encoders."""
        self._toggle_pec_recording(True)

    def stop_recording_pec(self):
        """Stop recording the periodic error. Only used in eq mounts without encoders."""
        self._toggle_pec_recording(False)

    def stop_all_movement(self):
        """Stop all slewing no matter the source of slewing or the direction(s)."""
        self.scope.send(':Q#')
        self.is_slewing = False

    def stop_e_or_w_movement(self):
        """Stop movement in the east or west directions. Useful when using the
        commands to slew in the specfic directions. Mimics the arrow buttons on
        the hand controller."""
        self.scope.send(':qR#')
        self.is_slewing = False

    def stop_n_or_s_movement(self):
        """Stop movement in the north or south directions. Useful when using the
        commands to slew in the specfic directions. Mimics the arrow buttons on
        the hand controller."""
        self.scope.send(':qD#')
        self.is_slewing = False

    def unpark(self):
        """Unpark the moint. If the mount is unparked already, this does nothing. """
        self.scope.send(':MP0#')
        # Always returns a 1
        self.is_parked = False
        return self.is_parked

    def update_status(self):
        """Call all of the (4) update commands to get the latest status of the mount."""
        current_time = time.time()
        if current_time - self.last_update > 1:
            self.get_all_kinds_of_status()
            self.get_time_information()
            self.get_ra_and_dec()
