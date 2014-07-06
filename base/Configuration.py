import os,sys,yaml

class Configuration:
	'Configuration utilities'
	def __init__(self):
		config_file_path = self.getBaseDir()+'/config.yml'	
		config_file = open(config_file_path)
		self.config_data = yaml.safe_load(config_file)
		
		
	def getBaseDir(self):
		return os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/..')
	
	def getConfigValue(self, config):
		return self.config_data[config]
