import ioptron as iom
import ioptron.ioptron as iopt 
import time

scope = iopt.ioptron('COM5')
# Refresh the status of the mount
scope.refresh_status()
time.sleep(2)

# Get the hemisphere and set it
print("HEMISPHERE: location: {}".format(scope.hemisphere.location))
scope.set_hemisphere('n')
scope.refresh_status()
print("HEMISPHERE: location: {}".format(scope.hemisphere.location))