# imports
import math
import socket

from ftplib import FTP
from geoip import geolite2
 
# compare long lat for distance
def distance_on_unit_sphere(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    return arc

# germany
remoteip = '149.172.37.26'
# original ip
# sourceip = socket.gethostbyname(socket.gethostname())
# 
# bogus ip for testing
# china
sourceip = '58.51.177.92'
# sourceip = socket.gethostbyname(socket.gethostname())
ftptimeout = 1

# determine location
remotelookup = geolite2.lookup(remoteip)
sourcelookup = geolite2.lookup(sourceip)

# calculate timeout from location
if remotelookup is not None and sourcelookup is not None :
	remotelat = remotelookup.location[0]
	remotelong = remotelookup.location[1]
	sourcelat = sourcelookup.location[0]
	sourcelong = sourcelookup.location[1]
	distance = distance_on_unit_sphere(remotelat, remotelong, sourcelat, sourcelong)
	
	# multiplier for calculating timeout
	ftptimeout = distance*4

print "Ftp timeout: %s" % ftptimeout

# set timeout for fast processing
ftp = FTP(host=remoteip, timeout=ftptimeout)
ftp.login()
ftp.retrlines('LIST')
ftp.quit()