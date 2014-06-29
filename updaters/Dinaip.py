from Zone import ZoneUpdater
from Configuration import Configuration 
from urllib2 import urlopen
import json

class Dinaip(ZoneUpdater):
	'Dinahosting zone updater'
	def updateZone(self, params):
		# Get srvice config
		self.config = (Configuration().loadConfig('services'))['dinaip']
		
		current_ip = self.zoneExists(params['domain'], params['zone'],params['type'])
		
		if current_ip:
			if current_ip == params['ip']:
				return "Zone already updated"
			else:
				return self.updateExistingZone(params['domain'], params['zone'], params['ip'], params['type'])
		else:
			return self.createZone(params['domain'], params['zone'], params['ip'], params['type'])
	
	def zoneExists(self, domain, zone, ztype):
		command = 'Domain_Zone_GetTypeA'
		if ztype == 'AAAA':
			command = 'Domain_Zone_GetTypeAAAA'
		
		domain_zones = json.load(urlopen('https://dinahosting.com/special/api.php?AUTH_USER='+self.config['user']+'&AUTH_PWD='\
						+ self.config['password'] + '&responseType=Json&domain='+domain+'&command='+command))
		
		for existing_zone in domain_zones['data']:
			if existing_zone['hostname'] == zone:
				return existing_zone['ip']
			
		return False 
	
	def createZone(self, domain, zone, ip, ztype):
		command = 'Domain_Zone_AddTypeA'
		if ztype == 'AAAA':
			command = 'Domain_Zone_AddTypeAAAA'
		
		create_zone_response = json.load(urlopen('https://dinahosting.com/special/api.php?AUTH_USER='+self.config['user']+'&AUTH_PWD='\
							 + self.config['password'] + '&responseType=Json&domain='+domain+ '&hostname='+ zone\
							 + '&ip=' + ip + '&command='+command))
		return json.dumps(create_zone_response) 
	
	def updateExistingZone(self, domain, zone, ip, ztype):
		command = 'Domain_Zone_UpdateTypeA'
		if ztype == 'AAAA':
			command = 'Domain_Zone_UpdateTypeAAAA'
		
		update_zone_response = json.load(urlopen('https://dinahosting.com/special/api.php?AUTH_USER='+self.config['user']+'&AUTH_PWD='\
							 + self.config['password'] + '&responseType=Json&domain='+domain+ '&hostname='+ zone\
							 + '&ip=' + ip + '&command='+command))
		return json.dumps(update_zone_response) 
	
