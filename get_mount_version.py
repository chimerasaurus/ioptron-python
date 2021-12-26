import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
print("Version #:  {}".format(scope.mount_version))
print("FW_MAIN:  {}".format(scope.firmware.mainboard))
print("FW_HC:  {}".format(scope.firmware.hand_controller))
print("FW_RA:  {}".format(scope.firmware.ra))
print("FW_DEC:  {}".format(scope.firmware.dec))