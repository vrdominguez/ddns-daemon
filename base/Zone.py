import os,sys,yaml

class ZoneUpdater:
	'Base class for zone updates'
	def getBaseDir(self):
		return os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/..')
	
	def loadConfig(self, config):
		config_file_path = self.getBaseDir()+'/config.yml'	
		config_file = open(config_file_path)
		config_data = yaml.safe_load(config_file)
		return config_data[config]
	
	def updateZone(self, params):
		raise NotImplementedError('Must be implemented for your zone')

class ZoneUpdateRunner:
	'Zone update launcher'
	def __init__(self,zone):
		self.zone = zone
	
	def instance(self):
		instance_zone = self.zone.lower().capitalize()
		
		# Instance the zone	
		module = __import__(instance_zone)
		class_ = getattr(module, instance_zone)
		self.zone_object = class_()
	
	def launchUpdate(self, params):
		# Run the zone updater
		return self.zone_object.updateZone(params)
