import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
# Refresh the status of the mount
scope.refresh_status()

# Get auto-guiding filter status
## Note - I cannot test this on my mount (JM)
ra_filter_status = scope.get_ra_guiding_filter_status()
print("RA FILTER: status: {}".format(ra_filter_status))

