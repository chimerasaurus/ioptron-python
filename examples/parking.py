import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron()
# Park the mount
print("PARKING: mount: {}".format(scope.park()))
print("PARKING: is parked:: {}".format(scope.parking.is_parked))

# Unpark the mount
print("PARKING: unparking mount:: {}".format(scope.unpark()))
print("PARKING: is parked:: {}".format(scope.parking.is_parked))

# Get the parking position
scope.get_parking_position()
print("PARKING: Altitude:: {}".format(scope.parking.altitude))
print("PARKING: Azimuth:: {}".format(scope.parking.azimuth))
print("PARKING: is parked:: {}".format(scope.parking.is_parked))