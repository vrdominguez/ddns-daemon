from urllib2 import urlopen
import json

class Publicip:
	'Public IP getters master class'
	def __init__(self, user, password):
		pass
	
	def getIp(self):
		raise NotImplementedError('Must be implemented for your own class');


class Jsonip:
	'Get ip from jsonip.org'
	def getIp(self):
		return json.load(urlopen('http://jsonip.com/'))['ip']
