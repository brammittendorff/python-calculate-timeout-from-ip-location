# imports
import math
import socket
import pprint
import shodan
import sys

from ftplib import FTP
from geoip import geolite2

from ftplib import FTP

# Configuration
apikey = "<APIKEY>"
ftptimeout = 1
timeoutmultiplier = 2

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

# Input validation
if len(sys.argv) == 1:
    print 'Usage: %s <search query>' % sys.argv[0]
    sys.exit(1)

try:
    # Setup the api
    api = shodan.Shodan(apikey)

    # Perform the search
    query = ' '.join(sys.argv[1:])
    result = api.search(query)

    # Loop through the matches and print each IP
    for service in result['matches']:

		# config
		remoteip = service['ip_str']

		# original ip (make sure it is a ip near your location)
		# sourceip = socket.gethostbyname(socket.gethostname())
		sourceip = '62.197.131.200'

		# determine location
		remotelookup = geolite2.lookup(remoteip)
		sourcelookup = geolite2.lookup(sourceip)

		# calculate timeout from location
		if remotelookup is not None and sourcelookup is not None :
			distance = distance_on_unit_sphere(remotelookup.location[0], remotelookup.location[1], sourcelookup.location[0], sourcelookup.location[1])
			# multiplier for calculating timeout
			ftptimeout = distance*timeoutmultiplier

		print "Ftp timeout: %s" % ftptimeout

		# set timeout for fast processing
		try:
			ftp = FTP(host=remoteip, timeout=ftptimeout)
			ftp.login()
			ftp.retrlines('LIST')
			ftp.quit()
		except Exception, e:
   			print str(e)

except Exception, e:
    print 'Error: %s' % e
    sys.exit(1)
