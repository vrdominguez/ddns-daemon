from Zone import ZoneUpdater
from urllib2 import urlopen
import md5
import socket
import json

class Cdmon(ZoneUpdater):
	'Cdmon zone updater'
	def updateZone(self, params, config):
		# Service config
		self.config = config 
		
		current_ips = self.zoneExists(params['domain'], params['zone'],params['type'])
		
		if current_ips:
			if params['ip'] in current_ips:
				return "Zone already updated"
			else:
				return self.updateExistingZone(params['domain'], params['zone'], params['ip'], params['type'])
		else:
			return self.createZone(params['domain'], params['zone'], params['ip'], params['type'])
	
        def zoneExists(self, domain, zone, ztype):

                family = socket.AF_INET6 if ztype == 'AAAA' else socket.AF_INET

                addr_info = ()

                try: 
                        addr_info = socket.getaddrinfo(zone+'.'+domain, None, family, socket.SOCK_STREAM)
                except Exception as e:
                        if not len(str(e)):
				print ("Zone not defined in your conection's dns server")
			else:
				print("Error getting zones: " + str(e)) 


                current_ips = []
                
                for addr in addr_info:
                        current_ips.append(addr[4][0])
		
                return current_ips

        def createZone(self, domain, zone, ip, ztype):
                raise Exception('Action "createZone" not supported in driver')

	def updateExistingZone(self, domain, zone, ip, ztype):

                md5pass = md5.new(self.config['password'])

                response = urlopen('https://dinamico.cdmon.org/onlineService.php?enctype=MD5&'\
                                                + 'n=' + self.config['user']+'&p='+ str(md5pass.hexdigest()))
		return response.read()
