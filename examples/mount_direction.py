import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron()
print("Version #:  {}".format(scope.mount_version))

# Get the mount's direction
print(">> STARTING test of :GLS# >>")
scope.get_ra_and_dec()
## RA
print("RA - ARCs:  {}".format(scope.right_ascension.arcseconds))
hms = [scope.right_ascension.hours, scope.right_ascension.minutes, scope.right_ascension.seconds]
print("RA - HMS:  {}".format((hms)))
## DEC
print("DEC - ARCs:  {}".format(scope.declination.arcseconds))
hms = [scope.declination.degrees, scope.declination.minutes, scope.declination.seconds]
print("DEC - DMS:  {}".format(hms))
## PIER
print("Pier side:  {}".format(scope.pier_side))
print("CW location:  {}".format(scope.counterweight_direction))
print("<< ENDING test of :GLS# <<")

# Get the altitude and azimuth
print(">> STARTING test of :GAC# >>")
scope.get_alt_and_az()
## Alt
print("Alt - ARCs:  {}".format(scope.altitude.arcseconds))
hms = [scope.altitude.degrees, scope.altitude.minues, scope.altitude.seconds]
print("Alt - DMS:  {}".format((hms)))

## Az
print("Az - ARCs:  {}".format(scope.azimuth.arcseconds))
hms = [scope.azimuth.degrees, scope.azimuth.minues, scope.azimuth.seconds]
print("Az - DMS:  {}".format(hms))
print("<< ENDING test of :GAC# <<")

# Get and set positions
print(">> STARTING test of :QAP# >>")
print("Memory positions:  {}".format(scope.get_coordinate_memory()))
print("<< ENDING test of :QAP# <<")

# Get and set button movement speed
print(">> STARTING test of :SRn# >>")
print("Setting movement rate to 128x:  {}".format(scope.set_arrow_button_movement_speed(6)))
print("<< ENDING test of :SRn# <<")

# Test auto guiding of RA
# NOTE: I cannot really test these; do not have an EC mount
print(">> STARTING test of :SGF1# >>")
print("Enable filter:  {}".format(scope.set_ra_guiding_filter_status(True)))
print("<< ENDING test of :SGF1# <<")
print(">> STARTING test of :SGF0# >>")
print("Disable filter:  {}".format(scope.set_ra_guiding_filter_status(False)))
print("<< ENDING test of :SGF0# <<")