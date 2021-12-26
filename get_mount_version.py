import ioptron as iom
import ioptron.ioptron as iopt 

scope = iopt.ioptron('COM5')
print(scope.mount_version)