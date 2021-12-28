# Imports
import datetime
import time
import yaml

# A utility class to hold utility and common methods

# Convert arc seconds with 0.01 percision to degrees
def arc_seconds_to_degrees(seconds):
    return (seconds / 3600) * 0.01 # The value is 0.01 arc seconds

# Convert J2000 in ms to formatted UNIX in ms
def convert_j2k_to_unix(ms):
    converted = datetime.datetime(2000,1,1,12,0) + datetime.timedelta(milliseconds=ms)
    return time.mktime(converted.timetuple())

def convert_unix_to_formatted(unix_ms):
    return datetime.utcfromtimestamp(int(unix_ms)).strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

# Convert degrees to arc seconds
def degrees_to_arc_seconds(seconds):
    return (seconds * 3600) / 0.01 # The value is 0.01 arc seconds

# Get the current UTC time in J2000
def get_utc_time_in_j2k():
    j2k_time = datetime(2000, 1, 1, 12, 00)
    utc = datetime.utcnow()
    difference = utc - j2k_time
    return(int(difference.total_seconds() * 1000))

# Parse the mount config data in a JSON file
# this means it isn't needed to hard-code mount config
def parse_mount_config_file(file, model):
    with open(file) as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data[model]