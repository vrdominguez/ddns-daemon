import os,sys,yaml

class Command:
	'Base class for comands'
	def getBaseDir(self):
		return os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/..')
	
	def loadConfig(self, config):
		config_file_path = self.getBaseDir()+'/config.yml'	
		config_file = open(config_file_path)
		config_data = yaml.safe_load(config_file)
		return config_data[config]
	
	def runCommand(self):
		raise NotImplementedError('Must be implemented for your command')

class CommandRunner:
	'Command launcher'
	def __init__(self,command):
		self.command = command
	
	def instance(self):
		instance_command = self.command.lower().capitalize()
		
		# Instance the command	
		module = __import__(instance_command)
		class_ = getattr(module, instance_command)
		self.command_object = class_()
	
	def launchCommand(self):
		# Run the command
		return self.command_object.runCommand()
