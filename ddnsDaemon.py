#!/usr/bin/env python
import logging, time, os, signal, sys, dns.resolver
from daemon import runner #pip install python-daemon

# add paths for base and command objects
app_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.append(app_dir + '/base')
sys.path.append(app_dir + '/updaters')

from Zone import ZoneUpdater, ZoneUpdateRunner
from Configuration import Configuration 

class DaemonDDNS:
	def __init__(self,config): 
		self.config = config
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/null'
		self.stderr_path = '/dev/null'
		self.pidfile_path =  '/var/run/ddnsDaemon.pid'
		self.pidfile_timeout = 5
		self.running = 0
	
	def reloadConfigFile(self, signum, frame):
		old_configuration = self.config
		try:
			# Instance new configuration object
			self.config = Configuration() 
			
			# Set new log level
			log_level = self.config.getConfigValue('log_level')
			if not (log_level.isdigit()):
				log_level = eval('logging.'+log_level)
			
			logger.setLevel(log_level)
			
			logger.info("Config reloaded correctly"); 
		except Exception as e:
			self.config = old_configuration
			logger.error("Error reloading configuration " + str(e))
			logger.info("Damemon keeps working with previous configuration")
	
	def run(self):
		logger.info("ddnsDaemon started!")
		self.running = 1
		
		# Signal control for config reload
		signal.signal(signal.SIGHUP, self.reloadConfigFile)
		
		# Instance public ip getter
		try:
			module = __import__('Publicip')
			class_ = getattr(module, self.config.getConfigValue('ip_service'))
			self.public_ip = class_()
		except Exception as e:
			self.running = 0
			logger.error("Error loading ip getter for " 
			     + self.config.getConfigValue('ip_service')
			     + ". ddnsDaemon finished!")
			sys.exit(1)
	
		while True:
			current_ip = self.public_ip.getIp()
			
			for zone_data in self.config.getConfigValue('zones'):
				for zone in zone_data['zones']:
					ips = self.getZone(zone_data['domain'], zone['zone'], zone['type'])
					
					if len(ips):
						logger.debug(zone['zone']
							+'.'+zone_data['domain']
							+ ' has ips: ' + ','.join(ips))
					else:
						logger.warning(zone['zone']+'.'+zone_data['domain']
							+ ' is not defined on your dns client.') 
					
					if current_ip in ips:
						logger.debug('No updates needed')
					else:
						logger.debug('Updating zone '+ zone['zone']
							+'.'+zone_data['domain'] + '...')
						zone_update_data= { 'zone': zone['zone'], 'domain': zone_data['domain'],
							'type': zone['type'], 'ip': current_ip}
						try:
							zone_updater = ZoneUpdateRunner(zone_data['service'])
							zone_updater.instance()
							response = zone_updater.launchUpdate(zone_update_data,
								(self.config.getConfigValue('services'))[zone_data['service']])
							logger.debug("Response from " + zone_data['service'] + " updater: " + response)
						except Exception as e:
							logger.error("Error updating '"+ zone_update_data['zone'] +'.'+zone_update_data['domain']
								+"' using " + zone_data['service']  + " service: " + str(e))
						
			
			sleep_time = self.config.getConfigValue('time_sleep')
			logger.debug('Sleeping for ' + str(sleep_time) + ' seconds...')
			for x in range(1, int(sleep_time)):
				time.sleep(1)

	def getZone(self,domain,zone,ztype):
		zone_resolution = []
		query_zone = zone +'.'+domain
		answers = []
		
		try:
			answers = dns.resolver.query(query_zone, ztype)
		except Exception as e:
			if not len(str(e)):
				logger.debug("Zone not defined in your conection's dns server")
			else:
				logger.error("Error getting zones: " + str(e)) 
				
		
		for rdata in answers:
			zone_resolution.append(str(rdata))
		
		return zone_resolution
	
	def __del__(self):
		if self.running:
			self.running = 0
			logger.info('Daemon finished')

# Get log_level configuration
config = Configuration()
log_level = config.getConfigValue('log_level')
if not (log_level.isdigit()):
	log_level = eval('logging.'+log_level)

# Logs configuration
logger = logging.getLogger("ddnsDaemon")
logger.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler = logging.FileHandler('/var/log/ddnsDaemon.log')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Daemon launch
ddns_daemon_app = DaemonDDNS(config)
ddns_daemon_runner = runner.DaemonRunner(ddns_daemon_app)
ddns_daemon_runner.daemon_context.files_preserve=[handler.stream] # Keep log file opened
ddns_daemon_runner.do_action()
