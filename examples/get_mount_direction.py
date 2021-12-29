import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
print("Version #:  {}".format(scope.mount_version))

# Get the mount's direction
scope.get_pointing_direction()

print("RA - ARCs:  {}".format(scope.ra.arcseconds))
print("RA - DMS:  {}".format(scope.ra.dms))
print("DEC - ARCs:  {}".format(scope.dec.arcseconds))
print("DEC - DMS:  {}".format(scope.dec.dms))
print("Pier side:  {}".format(scope.pier_side))
print("CW location:  {}".format(scope.counterweight_direction))
