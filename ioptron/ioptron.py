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
    """An altitude position. Contains the arcseconds and DMS."""
    arcseconds: float = None
    degrees: float = None
    minues: int = None
    seconds: int = None

## Azimuth data
@dataclass
class Azimuth:
    """An azimuth position. Contains the arcseconds and DMS."""
    arcseconds: float = None
    degrees: float = None
    minues: int = None
    seconds: int = None

@dataclass
class DEC:
    """Information about a declination value."""
    arcseconds: float = None
    degrees: int = None
    minutes: int = None
    seconds: int = None

@dataclass
class Firmwares:
    """Information on the firmware istalled on the mount and components."""
    mainboard: str = None
    hand_controller: str = None
    ra: str = None
    dec: str = None

@dataclass
class Location:
    """Holds location information along with GPS data."""
    gps_available: bool = False
    gps_locked: bool = False
    longitude: float = None
    latitude: float = None

@dataclass
class Guiding:
    """Informationa bout the RA and dec guiding rate. Can be 0.01 - 0.99.
    Represents the rate * siderial rate."""
    right_ascention_rate: float = None
    declination_rate: float = None
    ra_filter_enabled: bool = None
    has_ra_filter: bool = False

## RA data
@dataclass
class RA:
    arcseconds: float = None
    hours: int = None
    minutes: int = None
    seconds: int = None
    degrees: float = None

## System status
@dataclass
class SystemStatus:
    code: int = None
    description: str = None

@dataclass
class Tracking:
    """Holds tracking and rate information for the mount."""
    code: int = None
    custom: float = 1.0000
    available_rates: dict = None
    is_tracking: bool = False

    def current_rate(self):
        """Return a string description of the current rate."""
        if self.code is not None:
            return self.available_rates[self.code]
        # Not set, return none
        return None

@dataclass
class Meredian:
    """Holds meredian-related information."""
    code: int = None
    degree_limit: int = None

    def description(self):
        """Get the text description of the meredian treatment."""
        if self.code == 0:
            return "Stop at meredian"
        if self.code == 1:
            return "Flip at meredian with custom limit"
        else:
            return "Unknown or not set."

@dataclass
class MovingSpeed:
    """Information about the moving speed of the mount."""
    code: int = None
    multiplier: int = None
    description: str = None
    button_rate: int = None
    available_rates: dict = None

@dataclass
class Parking:
    """Contains information and location of parking."""
    is_parked: bool = None
    altitude: Altitude = Altitude()
    azimuth: Azimuth = Azimuth()

@dataclass
class Pec:
    """Holds information related to the periodic error correction (PEC.)"""
    integrity_complete: bool = None
    enabled: bool = None
    recording: bool = None

@dataclass
class TimeSource:
    """Keeps track of the source of time. May be removed in the future."""
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
        self.location = Location()
        main_fw_info = self.get_main_firmwares()
        motor_fw_info = self.get_motor_firmwares()
        self.mount_version = self.get_mount_version()
        self.firmware = Firmwares(mainboard=main_fw_info[0], hand_controller=main_fw_info[1], \
            ra=motor_fw_info[0], dec=motor_fw_info[1])
        self.hand_controller_attached = False if 'xx' in self.firmware.hand_controller else True
        self.system_status = SystemStatus()
        self.tracking = Tracking()
        self.time_source = TimeSource()
        self.hemisphere = Hemisphere()
        self.moving_speed = MovingSpeed()
        self.guiding = Guiding()
        self.is_slewing = False
        self.altitude_limit = None
        self.is_home = None
        self.pec = Pec()
        self.pps = False
        self.mount_config_data = \
            utils.parse_mount_config_file('ioptron/mount_values.yaml', self.mount_version)

        # Time information
        self.time = TimeInfo()

        # Direction information
        self.right_ascension = RA()
        self.declination = DEC()
        self.pier_side = None
        self.counterweight_direction = None
        self.altitude = Altitude()
        self.azimuth = Azimuth()
        self.meredian = Meredian()

        # Parking
        self.parking = Parking()

        # Apply the latest update time
        self.last_update = time.time()

    # Destructor that gets called when the object is destroyed
    def __del__(self):
        # Close the serial connection
        try:
            self.scope.close()
        except:
            print("CLEANUP: not needed or was unclean")

    # To get the joke here, read the official protocol docs
    def get_all_kinds_of_status(self):
        self.scope.send(":GLS#")
        response_data = self.scope.recv()

        # Parse latitude and longitude
        self.location.longitude = utils.convert_arc_seconds_to_degrees(int(response_data[0:9]))
        self.location.latitude = utils.convert_arc_seconds_to_degrees(\
            int(response_data[9:17])) - 90 # Val is +90

        # Parse GPS state
        gps_state = response_data[17:18]
        if gps_state == '0':
            self.location.gps_available = False
        elif gps_state == '1':
            self.location.gps_available = True
            self.location.gps_locked = False
        elif gps_state == '2':
            self.location.gps_available = True
            self.location.gps_locked = True

        # Parse the system status
        # TODO: Refactor using YAML config
        status_code = response_data[18:19]
        self.system_status.code = status_code
        if status_code == '0':
            self.system_status.description = "stopped at non-zero position"
            self.is_slewing = False
            self.tracking.is_tracking = False
        elif status_code == '1':
            self.system_status.description = "tracking with periodic error correction disabled"
            self.is_slewing = False
            self.tracking.is_tracking = True
            self.pec.enabled = False
        elif status_code == '2':
            self.system_status.description = "slewing"
            self.is_slewing = True
            self.tracking.is_tracking = False
        elif status_code == '3':
            self.system_status.description = "auto-guiding"
            self.is_slewing = False
            self.tracking.is_tracking = True
        elif status_code == '4':
            self.system_status.description = "meridian flipping"
            self.is_slewing = True
        elif status_code == '5':
            self.system_status.description = "tracking with periodic error correction enabled"
            self.is_slewing = False
            self.tracking.is_tracking = True
            self.pec.enabled = True
        elif status_code == '6':
            self.system_status.description = "parked"
            self.is_slewing = False
            self.tracking.is_tracking = False
            self.parking.is_parked = True
        elif status_code == '7':
            self.system_status.description = "stopped at zero position (home position)"
            self.is_slewing = False
            self.tracking.is_tracking = False

        # Parse tracking rate
        tracking_rate = response_data[19:20]
        self.tracking.code = tracking_rate
        self.tracking.available_rates = self.mount_config_data['tracking_rates']

        # Parse moving speed
        moving_speed = response_data[20:21]
        self.moving_speed.code = moving_speed
        self.tracking.available_rates = self.mount_config_data['tracking_speeds']
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

        # Altitude
        altitude = returned_data[0:9]
        self.altitude.arcseconds = float(altitude)
        self._set_dataclass_dms_from_arcseconds(self.altitude)

        # Azimuth
        azimuth = returned_data[9:18]
        self.azimuth.arcseconds = float(azimuth)
        self._set_dataclass_dms_from_arcseconds(self.azimuth)

    def get_altitude_limit(self):
        """Get the altitude limt currently set. Applies to tracking and slewing. Motion will
        stop if it exceeds this value."""
        self.scope.send(':GAL#')
        returned_data = self.scope.recv()
        self.altitude_limit = returned_data[0:3]

    def get_custom_tracking_rate(self):
        """Get the custom tracking rate, if it is set. Otherwise will be 1.000."""
        self.scope.send(':GTR#')
        returned_data = self.scope.recv()
        # Set the value and strip the control '#' at the end (response is d{5})
        self.tracking.custom = format((float(returned_data[:5]) * 0.0001), '.4f')

    def get_guiding_rate(self):
        """Get the current RA and DEC guiding rates. They are 0.01 - 0.99 * siderial."""
        self.scope.send(':AG#')
        returned_data = self.scope.recv()
        # Convert values to 0.01 - 0.9
        self.guiding.right_ascention_rate = float(returned_data[0:2]) * 0.01
        self.guiding.declination_rate = float(returned_data[2:4])*  0.01

    def get_pec_integrity(self):
        """Get the integrity of the PEC. Returns (and sets) if it is complete or incomplete.
        Only available with eq mounts without encoders"""
        if self.mount_config_data['type'] != "equatorial" or \
            self.mount_config_data['capabilities']['encoders'] == True:
            return
        # Continue - is an EQ mount without encoders
        self.scope.send(':GPE#')
        returned_data = self.scope.recv()
        if returned_data == "0":
            self.pec.integrity_complete = False
        if returned_data == "1":
            self.pec.integrity_complete = True

    def get_pec_recording_status(self):
        """Get the status of the PEC recording. Returns (and sets) if it is stopped or recording.
        Only available with eq mounts without encoders"""
        if self.mount_config_data['type'] != "equatorial" or \
            self.mount_config_data['capabilities']['encoders'] is True:
            return
        # Continue - is an EQ mount without encoders
        self.scope.send(':GPR#')
        returned_data = self.scope.recv()
        if returned_data == "0":
            self.pec.recording = False
        if returned_data == "1":
            self.pec.recording = True

    def get_max_slewing_speed(self):
        """Get the maximum slewing speed for this mount and returns a factor of siderial (eg 8x)."""
        self.scope.send(':GSR#')
        returned_data = self.scope.recv()

        # Response depends on mount model
        if returned_data == "7#":
            return 256
        if returned_data == "8#":
            return 512
        if returned_data == "9#":
            return self.mount_config_data['tracking_speeds'][9]

    def get_meredian_treatment(self):
        """Get the treatment of the meredian - stop below limit or flip at limit along
        with the position limit in degrees past meredian. Only used for equitorial mounts."""
        # This works for eq mounts only
        if self.mount_config_data['type'] != 'equatorial':
            return
        # This is an eq mount
        self.scope.send(':GMT#')
        returned_data = self.scope.recv()
        code = returned_data[0:1]
        degrees = returned_data[1:3]
        self.meredian.code = int(code)
        self.meredian.degree_limit = int(degrees)

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

    def get_parking_position(self):
        """Get the current parking position of the mount. """
        self.scope.send(':GPC#')
        returned_data = self.scope.recv()

        # Altitude
        altitude = returned_data[0:8]
        self.parking.altitude.arcseconds = float(altitude)
        self._set_dataclass_dms_from_arcseconds(self.parking.altitude)

        # Azimuth
        azimuth = returned_data[8:17]
        self.parking.azimuth.arcseconds = float(azimuth)
        self._set_dataclass_dms_from_arcseconds(self.parking.azimuth)

    def get_ra_and_dec(self):
        """Get the RA and DEC of the telescope's current pointing position."""
        self.scope.send(':GEP#')
        returned_data = self.scope.recv()

        # RA
        right_asc = returned_data[9:18]
        self.right_ascension.arcseconds = float(right_asc)
        self.right_ascension.degrees = utils.convert_arc_seconds_to_degrees(self.right_ascension.arcseconds)
        hms = utils.convert_arc_seconds_to_hms(right_asc)
        self.right_ascension.hours = hms[0]
        self.right_ascension.minutes = hms[1]
        self.right_ascension.seconds = hms[2]

        # Declination
        declination = returned_data[0:9]
        self.declination.arcseconds = float(declination)
        dms = utils.convert_arc_seconds_to_dms(self.declination.arcseconds)
        self.declination.degrees = dms[0]
        self.declination.minutes = dms[1]
        self.declination.seconds = dms[2]

        # The following only works for eq mounts
        if self.mount_config_data['type'] == "equatorial":
            # Pier side
            pier_side = returned_data[18:19]
            self.pier_side = self.mount_config_data['pier_sides'][int(pier_side)]

            # Counterweight direction
            counterweight_direction = returned_data[19:20]
            self.counterweight_direction = \
                self.mount_config_data['counterweight_direction'][int(counterweight_direction)]

    def get_ra_guiding_filter_status(self):
        """Get the status of the RA guiding filter for mounts with encoders."""
        # Only available for eq mounts with encoders
        if self.mount_config_data['type'] != "equatorial" or \
            self.mount_config_data['capabilities']['encoders'] is False:
            return None
        self.guiding.has_ra_filter = True
        self.scope.send(':GGF#')
        returned_data = self.scope.recv()
        if returned_data == "0":
            self.guiding.ra_filter_enabled = False
        if returned_data == "1":
            self.guiding.ra_filter_enabled = True
        return self.guiding.ra_filter_enabled

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
            self.parking.is_parked = True
        else:
            # Mount was mot parked OK
            self.parking.is_parked = False
        return self.parking.is_parked

    def parse_moving_speed(self, rate):
        """Return the mount's current tracking speed in factors of sidarial rate."""
        return str(self.mount_config_data['tracking_speeds'][rate]) + 'x'

    def reset_settings(self, confirm: bool):
        """Reset all settings to default. Only applies if True is specified to indicate
        the reset is really wanted. Does not reset any time-based information."""
        if confirm is True:
            self.scope.send(':RAS#')
            self.get_all_kinds_of_status()
            self.get_time_information()
            self.get_ra_and_dec()
            self.get_alt_and_az()

    def set_altitude_limit(self, limit: int):
        """Set the maximum altitude limt, in degrees. Applies to tracking and slewing. Motion will
        stop if it exceeds this value. Limit is +/- 89 degrees. Returns True after command sent."""
        self.altitude_limit = str(limit).zfill(3)
        set_command = ":SAL" + self.altitude_limit + "#" # Pad with zeros when single digit
        self.scope.send(set_command)
        # Get the response; do nothing with it
        self.scope.recv()
        return True

    def set_arrow_button_movement_speed(self, rate):
        """Set the movement speed when the N-S-E-W buttons are used. Rate must be
        given as a multiplier of siderial (e.g. 2 for 2x or 64 for 64x.) The value
        supplied must be supported by the mount. This value is wiped and replaced
        by the default (64x) on the next powerup. Returns True after command is sent."""
        assert rate in self.moving_speed.available_rates
        self.moving_speed.button_rate = rate
        movement_command = ":SR" + rate + "#"
        self.scope.send(movement_command)
        # Get the response; do nothing with it
        self.scope.recv()
        return True

    def set_guiding_rate(self, right_ascention: float, declination: float):
        """Set the current RA and DEC guiding rates. The valid range for both is 0.01 - 0.90.
        These values will be used to set the guiding rate * siderial. For example 0.50 will be
        0.50 * siderial guiding. First argument is the RA, second argument is DEC
        Only works for equitorial mounts. Returns true once command is sent
        and a response received."""
        assert self.mount_config_data['type'] is 'equatorial' # only works on EQ mounts
        assert right_ascention >= 0.01 and right_ascention <= 0.90 \
            and declination >= 0.01 and declination <= 0.90
        self.guiding.right_ascention_rate = round(right_ascention, 2)
        self.guiding.declination_rate = round(declination, 2)
        guiding_rate_command = ":RG" + f'{self.guiding.right_ascention_rate:<04n}' \
            + f'{self.guiding.declination_rate:<04n}' + "#"
        self.scope.send(guiding_rate_command)
        returned_data = self.scope.recv()
        assert returned_data == '1'
        return True

    def set_ra_guiding_filter_status(self, enabled: bool):
        """Set the status of the RA guiding filter for eq mounts with encoders.
        This command may or may not be saved on mount restart - the docs are unclear.
        Returns True after the command is sent."""
        # Only available for eq mounts with encoders
        if self.mount_config_data['type'] != "equatorial" or \
            self.mount_config_data['capabilities']['encoders'] is False:
            return None
        if enabled is True:
            self.guiding.ra_filter_enabled = True
            self.scope.send(":SGF1#")
        if enabled is False:
            self.guiding.ra_filter_enabled = False
            self.scope.send(":SGF0#")
        # Get the response; do nothing with it
        self.scope.recv()
        return True

    def set_custom_tracking_rate(self, rate):
        """Set a custom tracking rate to n.nnnn of the siderial rate. Only used
        when 'custom' tracking rate is being used. Returns True after command
        is sent."""
        formatted_rate = (f"{float(rate):.6f}")
        send_command = ":RR" + formatted_rate + "#"
        self.scope.send(send_command)
        # Get the response; do nothing with it
        self.scope.recv()
        return True

    def _set_dataclass_dms_from_arcseconds(self, data_class):
        """PRIVATE: Set DMS for a given dataclass like Altitude and Azimuth given
        their pre-set arcseconds value. Intended to keep code DRY."""
        dms = utils.convert_arc_seconds_to_dms(data_class.arcseconds)
        data_class.degrees = dms[0]
        data_class.minues = dms[1]
        data_class.seconds = dms[2]

    def set_daylight_savings(self, dst: bool):
        """Enables daylight savings time when true, disables it when false."""
        if dst is True:
            self.scope.send(':SDS1#')
        else:
            self.scope.send(':SDS0#')
        # Get the response; do nothing with it
        self.scope.recv()

        # Update time information after setting
        self.get_time_information()

    def set_hemisphere(self, direction: str):
        """Set the mount's hemisphere. Supplied argument must be 'north', 'south', or
        'n' or 's'. Returns True after command is sent."""
        assert direction.lower() in ['north', 'south', 'n', 's']
        hemisphere = 0 if direction[0:1] is 's' else 1
        command = ":SHE" + hemisphere + "#"
        self.scope.send(command)
        self.scope.recv()
        return True

    def set_max_slewing_speed(self, speed: str):
        """Set the maximum slewing speed. Input is the maximum siderial
        rate desired. Must be '256x', '512x', or 'max'. The max rate
        will depend on the mount. Returns True once command is sent."""
        assert speed in ['256x', '512x', 'max']
        # Set to max by default
        speed_bit = '9'
        if speed == '256x':
            speed_bit = '7'
        if speed == '512x':
            speed_bit = '8'
        speed_command = ":MSR" + speed_bit + "#"
        self.scope.send(speed_command)
        # Get the response; do nothing with it
        self.scope.recv()
        return True

    def set_meredian_treatment(self, treatment: str, limit: int):
        """Set the treatment of the meredian. First argument is whether to
        'stop' or 'flip'. Second argument is the limit, in degrees (nn) to apply
        the behavior to. Will return True once command is sent and response received.
        Only works for equitorial mounts; will return False otherwise."""
        # This works for eq mounts only
        if self.mount_config_data['type'] != 'equatorial':
            return False # only works on EQ mounts
        # Validate arguments
        assert treatment.lower() in ['stop', 'flip']
        assert 0 <= limit <= 90
        # This is an eq mount
        self.meredian.code = 1 if treatment.lower() == 'flip' else 0
        self.meredian.degree_limit = f'{limit:<02n}'
        treatment_cmd = ":SMT" + self.meredian.code + self.meredian.degree_limit + "#"
        self.scope.send(treatment_cmd)
        if self.scope.recv() == '1':
            return True
        return False

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

    def set_tracking_rate(self, rate):
        """Set the tracking rate of the mount. 
        Rate must be one supported by the mount (tracking.available_rates)
        Returns True once command is sent."""
        assert rate in (self.tracking.available_rates)
        reverse = dict((v,k) for k,v in self.tracking.available_rates.items())
        rate_command = ":RT" + reverse[rate] + "#"
        self.scope.send(rate_command)
        self.scope.recv()
        return True

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
        self.parking.is_parked = False
        return self.parking.is_parked

    def update_status(self):
        """Call all of the (4) update commands to get the latest status of the mount."""
        current_time = time.time()
        if current_time - self.last_update > 1:
            self.get_all_kinds_of_status()
            self.get_time_information()
            self.get_ra_and_dec()
