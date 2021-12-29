# Imports
from datetime import datetime, timedelta
import time
import yaml

## A utility class to hold utility and common methods ##

# Convert arc seconds with 0.01 percision to degrees
def arc_seconds_to_degrees(seconds):
    return (seconds / 3600) * 0.01 # The value is 0.01 arc seconds

# Convert J2000 in ms to formatted UNIX in ms with offset if needed
def convert_j2k_to_unix_utc(ms, offset = 0):
    converted = datetime(2000,1,1,12,0) + timedelta(milliseconds=ms) + timedelta(minutes=offset)
    return time.mktime(converted.timetuple())

def convert_unix_to_formatted(unix_ms):
    return datetime.utcfromtimestamp(int(unix_ms)).strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

# Convert degrees to arc seconds
def degrees_to_arc_seconds(seconds):
    return (seconds * 3600) / 0.01 # The value is 0.01 arc seconds

# Get the current UTC offset
def get_utc_offset_min():
    offset = int(time.timezone/60)
    # TODO: Figure out why Python uses the oppposite sign I'd expect
    # I am in PST and the number is positive; it's negative ahead of UTC. /shrug
    return offset * -1

# Get the current UTC time in J2000
def get_utc_time_in_j2k():
    j2k_time = datetime(2000, 1, 1, 12, 00)
    utc = datetime.utcnow()
    difference = utc - j2k_time
    return(int(difference.total_seconds() * 1000))

# Convert a unix UTC time to an offset time
def offset_utc_time(unix, offset):
    offset_sec = timedelta(minutes=abs(offset)).seconds
    if (offset < 1):  
        return unix - offset_sec
    else:
        return unix + offset_sec

# Parse the mount config data in a JSON file
# this means it isn't needed to hard-code mount config
def parse_mount_config_file(file, model):
    with open(file) as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data[model]