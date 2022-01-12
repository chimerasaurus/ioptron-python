import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron()
print("Version #:  {}".format(scope.mount_version))
print("FW_MAIN:  {}".format(scope.firmware.mainboard))
print("FW_HC:  {}".format(scope.firmware.hand_controller))
print("FW_RA:  {}".format(scope.firmware.right_ascention))
print("FW_DEC:  {}".format(scope.firmware.declination))
print("HC plugged in:   {}".format(scope.hand_controller_attached))