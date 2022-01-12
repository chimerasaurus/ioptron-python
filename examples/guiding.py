import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron()
# Refresh the status of the mount
scope.refresh_status()

# Get auto-guiding filter status
## Note - I cannot test this on my mount (JM)
ra_filter_status = scope.get_ra_guiding_filter_status()
print("RA FILTER: status: {}".format(ra_filter_status))

# PEC recording
print(">> STARTING test of :SPR1# >>")
print("Enable PEC recording:  {}".format(scope.start_recording_pec()))
print("<< ENDING test of :SPR1# <<")
print(">> STARTING test of :SPR0# >>")
print("Disable PEC recording:  {}".format(scope.stop_recording_pec()))
print("<< ENDING test of :SPR0# <<")

print(">> STARTING test of :SPP1# >>")
print("Enable PEC recording:  {}".format(scope.enable_pec_playback(True)))
print("<< ENDING test of :SPP1# <<")
print(">> STARTING test of :SPP0# >>")
print("Disable PEC recording:  {}".format(scope.enable_pec_playback(False)))
print("<< ENDING test of :SPP0# <<")