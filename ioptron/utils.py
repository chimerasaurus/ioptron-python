# Imports
import yaml

# A utility class to hold utility and common methods

# Convert arc seconds with 0.01 percision to degrees
def arc_seconds_to_degrees(seconds):
    return (seconds / 3600) * 0.01 # The value is 0.01 arc seconds

# Convert degrees to arc seconds
def degrees_to_arc_seconds(seconds):
    return (seconds * 3600) / 0.01 # The value is 0.01 arc seconds

# Parse the mount config data in a JSON file
# this means it isn't needed to hard-code mount config
def parse_mount_config_file(file, model):
    with open(file) as f:
        yaml_data = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_data[model]