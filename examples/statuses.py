import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
print(">> Starting test of :GLS# >>")
scope.get_all_kinds_of_status()

# Lat and long
print("Latitude:  {}".format(scope.latitude))
print("Longitude:  {}".format(scope.longitude))

# GPS
print("GPS available:  {}".format(scope.gps.available))
print("GPS locked:  {}".format(scope.gps.locked))

# System status
print("System status code:  {}".format(scope.system_status.code))
print("System status description:  {}".format(scope.system_status.description))
print("System status is slewing:  {}".format(scope.is_slewing))
print("System status is tracking:  {}".format(scope.is_tracking))
print("System status is parked:  {}".format(scope.is_parked))
print("System status pec:  {}".format(scope.pec))
print("System status pec recorded:  {}".format(scope.pec_recorded))

# Tracking rate
print("Tracking rate - code:  {}".format(scope.tracking_rate.code))
print("Tracking rate - description:  {}".format(scope.tracking_rate.description))

# Moving speed
print("Moving speed - code:  {}".format(scope.moving_speed.code))
print("Moving speed - description:  {}".format(scope.moving_speed.description))

# Time source
print("Time source - code:  {}".format(scope.time_source.code))
print("Time source - description:  {}".format(scope.time_source.description))

# Hemisphere
print("Hemisphere - code:  {}".format(scope.hemisphere.code))
print("Hemisphere - location:  {}".format(scope.hemisphere.location))

print("<< Done with :GLS# <<")