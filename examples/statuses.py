import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
print(">> Starting test of :GLS# >>")
scope.get_all_kinds_of_status()

# Lat and long
print("Latitude:  {}".format(scope.location.latitude))
print("Longitude:  {}".format(scope.location.longitude))

# GPS
print("GPS available:  {}".format(scope.location.gps_available))
print("GPS locked:  {}".format(scope.location.gps_locked))

# System status
print("System status code:  {}".format(scope.system_status.code))
print("System status description:  {}".format(scope.system_status.description))
print("System status is slewing:  {}".format(scope.is_slewing))
print("System status is tracking:  {}".format(scope.tracking.is_tracking))
print("System status is parked:  {}".format(scope.parking.is_parked))
print("System status pec:  {}".format(scope.pec))
print("System status pec recorded:  {}".format(scope.pec.integrity_complete))

# Tracking rate
print("Tracking rate - code:  {}".format(scope.tracking.code))
print("Tracking rate - description:  {}".format(scope.tracking.current_rate()))

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