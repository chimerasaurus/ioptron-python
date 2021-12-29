import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
# Park the mount
print("Parking mount: {}".format(scope.park()))
print("Mount reports parked position: {}".format(scope.is_parked))

# Unpark the mount
print("Parking mount: {}".format(scope.unpark()))
print("Mount reports unparked position: {}".format(scope.is_parked))

# Park the mount
print("Parking mount: {}".format(scope.park()))
print("Mount reports parked position: {}".format(scope.is_parked))
