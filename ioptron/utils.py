"""
This is a utility module to do common methods, conversions, etc.
@author - James Malone
"""

# Imports
from datetime import datetime, timedelta
from decimal import Decimal
import math
import time
import yaml

def convert_arc_seconds_to_degrees(seconds):
    """Convert arc seconds with 0.01 percision to degrees"""
    return (seconds / 3600) * 0.01

def convert_arc_seconds_to_dms(seconds):
    """Convert arc seconds to degrees, minutes, seconds. Returns
    a touple with the integer dms values."""
    degrees = convert_arc_seconds_to_degrees(seconds)
    d = int(degrees)
    m = int((degrees - d) * 60)
    s = int((degrees - d - m/60) * 3600)
    return (d, m, s)

def convert_arc_seconds_to_hms(seconds):
    """Converts arc seconds at 0.01 precision to arc HH:MM:SS"""
    hours = float(seconds) / (15.0 * 60.0 * 60.0 * 100.0) #Thank you INDI.
    print(hours)
    minutes = (Decimal(hours) % 1) * 60
    print(minutes)
    seconds = (Decimal(minutes) % 1) * 60
    print(seconds)
    return (int(hours), int(minutes), int(seconds))

def convert_j2k_to_unix_utc(sec, offset = 0):
    """Convert J2000 in 0.01 seconds to formatted UNIX in ms with offset if needed."""
    converted = datetime(2000,1,1,12,0) + timedelta(milliseconds=sec) + timedelta(minutes=offset)
    return time.mktime(converted.timetuple())

def convert_unix_to_formatted(unix_ms):
    """Convert a unix timestamp to HH:MM:SS.ss."""
    return datetime.utcfromtimestamp(int(unix_ms)).strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

def degrees_to_arc_seconds(seconds):
    """Convert degrees into arcseconds."""
    return (seconds * 3600) / 0.01 # The value is 0.01 arc seconds

def get_utc_offset_min():
    """Get the UTC offset of this computer in minutes."""
    offset = int(time.timezone/60)
    # TODO: Figure out why Python uses the oppposite sign I'd expect
    # I am in PST and the number is positive; it's negative ahead of UTC. /shrug
    return offset * -1

def get_utc_time_in_j2k():
    """Get the UTC time expressed in J2000 format (seconds since 12 on 1/1/2000.)"""
    j2k_time = datetime(2000, 1, 1, 12, 00)
    utc = datetime.utcnow()
    difference = utc - j2k_time
    return(int(difference.total_seconds() * 1000))

def offset_utc_time(unix, offset):
    """Convert utc time into a time with the supplied timezone offset."""
    offset_sec = timedelta(minutes=abs(offset)).seconds
    if offset < 1:  
        return unix - offset_sec
    else:
        return unix + offset_sec

def parse_mount_config_file(file, model):
    """Parse the given YAML config and return the sub-branch with the given
    key - used to store and parse mount-specific information."""
    with open(file) as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data[model]