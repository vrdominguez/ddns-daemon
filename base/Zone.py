class ZoneUpdater:
	'Base class for zone updates'
	def updateZone(self, params, config):
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
	
	def launchUpdate(self, params, config):
		# Run the zone updater
		try:
			return self.zone_object.updateZone(params, config)
		except Exception as e:
			return "ERROR: " +str(e)
