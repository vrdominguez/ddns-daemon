#!/usr/bin/env python
import logging, time, os, sys, dns.resolver
from daemon import runner #pip install python-daemon

# add paths for base and command objects
app_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.append(app_dir + '/base')
sys.path.append(app_dir + '/commands')

from Command import Command, CommandRunner

class DaemonDDNS:
	def __init__(self): 
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/null'
		self.stderr_path = '/dev/null'
		self.pidfile_path =  '/var/run/ddnsDaemon.pid'
		self.pidfile_timeout = 5
		self.running = 0
	
	def run(self):
		logger.info("ddnsDaemon started!")
		self.running = 1
		
		# Instance public ip getter
		ip_service = Command().loadConfig('ip_service')
		sleep_time = Command().loadConfig('time_sleep')
		
		try:
			module = __import__('Publicip')
			class_ = getattr(module, ip_service)
			self.public_ip = class_()
		except Exception as e:
			self.running = 0
			logger.error("Error loading ip getter for " + ip_service  + ". ddnsDaemon finished!")
			sys.exit(1)
	
		while True:
			# Read zone list on each pass in order to get new zones added to the config file
			zone_list= Command().loadConfig('zones')
			logger.debug(zone_list)
			
			current_ip = self.public_ip.getIp()
			logger.debug("Public IP is: " + str(current_ip))
			
			for zone_data in zone_list:
				for zone in zone_data['zones']:
					ips = self.getZone(zone_data['domain'], zone['zone'], zone['type'])
					logger.debug(zone['zone']+'.'+zone_data['domain'] + ' has ips: ' + ','.join(ips))
					
					if current_ip in ips:
						logger.debug('No updates needed')
					else:
						logger.debug('Updating zone ' + zone['zone']+'.'+zone_data['domain'] + '...')
						#TODO: Update zones
						
			
			logger.debug('Sleeping for ' + str(sleep_time) + ' seconds...')
			time.sleep(int(sleep_time))

	def getZone(self,domain,zone,ztype):
		zone_resolution = []
		
		query_zone = zone +'.'+domain
		answers = dns.resolver.query(query_zone, ztype)
		for rdata in answers:
			zone_resolution.append(str(rdata))
		
		return zone_resolution
	
	def __del__(self):
		if self.running:
			self.running = 0
			logger.info('Daemon finished')

# Get log_level configuration
log_level = Command().loadConfig('log_level')
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
ddns_daemon_app = DaemonDDNS()
ddns_daemon_runner = runner.DaemonRunner(ddns_daemon_app)
ddns_daemon_runner.daemon_context.files_preserve=[handler.stream] # Keep log file opened
ddns_daemon_runner.do_action()
