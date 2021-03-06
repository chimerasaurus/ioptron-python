import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron()
# Get custom tracking rate
scope.get_custom_tracking_rate()
print("TRACKING: custom rate:: {}".format(scope.tracking.custom))

# Get custom tracking rate
print("SLEWING: max speed:: {}".format(scope.get_max_slewing_speed()))

# Get altitude limit
print("ALTITUDE: max limit:: {}".format(scope.get_altitude_limit()))

# Get ra and dec guiding rates
scope.get_guiding_rate()
print("GUIDING RATE: RA:: {}".format(scope.guiding.right_ascention_rate))
print("GUIDING RATE: DEC:: {}".format(scope.guiding.declination_rate))

# Get the meredian treatment
scope.get_meredian_treatment()
print("MEREDIAN: code:: {}".format(scope.meredian.code))
print("MEREDIAN: description:: {}".format(scope.meredian.description))
print("MEREDIAN: degree limit:: {}".format(scope.meredian.degree_limit))

# PEC tests
scope.get_pec_integrity()
print("PEC: integrity:: {}".format(scope.pec.integrity_complete))
scope.get_pec_recording_status()
print("PEC: recording:: {}".format(scope.pec.recording))

# Tracking rates
scope.get_all_kinds_of_status()
print("TRACKING: current rate:: {}".format(scope.tracking.current_rate()))
print("TRACKING: available rates:: {}".format(scope.tracking.available_rates))
print("TRACKING: set siderial:: {}".format(scope.set_tracking_rate('sidereal')))
scope.get_all_kinds_of_status()
print("TRACKING: current rate:: {}".format(scope.tracking.current_rate()))

# Movement speed
print("TRACKING: get max slew rate:: {}".format(str(scope.get_max_slewing_speed())))
print("TRACKING: set max slew rate at 512x:: {}".format(scope.set_max_slewing_speed('512x')))
print("TRACKING: get max slew rate:: {}".format(str(scope.get_max_slewing_speed())))
