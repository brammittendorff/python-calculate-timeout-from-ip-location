# imports
import math, socket, pprint, json, urllib

from ftplib import FTP
from ftplib import FTP_TLS
from geoip import geolite2

# original ip (make sure it is a ip near your location)
data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
sourceip = data["ip"]
print("Sourceip: %s" % sourceip)

# config
remoteftpip = '216.216.32.20'
print("Remoteip: %s" % remoteftpip)
ftptimeout = 1

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

# determine location
remotelookup = geolite2.lookup(remoteftpip)
sourcelookup = geolite2.lookup(sourceip)

# calculate timeout from location
if remotelookup is not None and sourcelookup is not None :
	distance = distance_on_unit_sphere(remotelookup.location[0], remotelookup.location[1], sourcelookup.location[0], sourcelookup.location[1])
	# multiplier for calculating timeout
	ftptimeout = distance*4

print("Generated timeout: %s" % ftptimeout)

# set timeout for fast processing
try:
    ftp = FTP(host=remoteftpip, timeout=ftptimeout)
    ftp.login()
    ftp.retrlines('LIST')
    ftp.quit()
except Exception as e:
    print("The remote ftp is unreachable with error: \n%s" % e)

    try:
        print("\nTrying to connect with TLS/SSL")
        ftps = FTP_TLS(host=remoteftpip, timeout=ftptimeout)
        ftps.login()
        ftps.prot_p()
        ftps.retrlines('LIST')
    except Exception as e:
        print("The remote ftp is unreachable with TLS error: \n%s" % e)
