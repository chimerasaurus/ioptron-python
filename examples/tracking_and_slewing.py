import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
# Get custom tracking rate
scope.get_custom_tracking_rate()
print("TRACKING: custom rate:: {}".format(scope.tracking.custom))

# Get custom tracking rate
print("SLEWING: max speed:: {}".format(scope.get_max_slewing_speed()))

# Get altitude limit
scope.get_altitude_limit()
print("ALTITUDE: max limit:: {}".format(scope.altitude_limit))

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
print("TRACKING: set siderial:: {}".format(scope.set_tracking_rate('siderial')))
scope.get_all_kinds_of_status()
print("TRACKING: current rate:: {}".format(scope.tracking.current_rate()))
