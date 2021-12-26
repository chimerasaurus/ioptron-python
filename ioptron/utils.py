# Imports
import yaml

class utils:
    def __init__(self, port = ''):
        with open('mount_values.yaml') as f:
            self.mount_values = yaml.load(f, Loader=yaml.FullLoader)
            print(self.mount_values)

    # Convert arc seconds with 0.01 percision to degrees
    def arc_seconds_to_degrees(self, seconds):
        return (seconds / 3600) * 0.01 # The value is 0.01 arc seconds

    # Convert degrees to arc seconds
    def degrees_to_arc_seconds(self, seconds):
        return (seconds * 3600) / 0.01 # The value is 0.01 arc seconds

    def get_mount_values(self, mount, value):
        return self.mount_values[mount][value]