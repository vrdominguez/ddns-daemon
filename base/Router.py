import re,sys,telnetlib

class Router:
	'Router base class'
	def __init__(self, user, password, host='192.168.0.1'):
		self.user = user
		self.password= password
		self.host = host
	
	def execute(self, command):
		raise NotImplementedError('Must be implemented for your router')
	
	
	def getConnectionStatus(self):
		raise NotImplementedError('Must be implemented for your router')
	
	def getPublicIp(self):
		raise NotImplementedError('Must be implemented for your router')
	
	

class VodafoneHG556a(Router):
	'Vodafone router HG556a'
	def __init__(self, user, password, host='192.168.0.1', prompt='VFMN0001222915> '):
		self.user = user
		self.password= password
		self.prompt = prompt
		self.host = host
	
	def execute(self, command):
		# Router connection
		conection = telnetlib.Telnet(self.host)
		
		# telnet login
		conection.read_until("Login: ")
		conection.write(self.user+"\n")
		conection.read_until("Password: ")
		conection.write(self.password+"\n")
		
		# wait for prompt
		conection.read_until(self.prompt)
		
		# execute command
		conection.write(command+"\n")
		conection.read_until(command)
		
		# get command output
		command_output= conection.read_until(self.prompt)
		# Logout from router
		conection.write("logout\n")
		
		#split command output by new line and delete \r chars
		output = [line.strip() for line in command_output.split('\n') if line.strip()]
		
		# delete prompt line
		del output[-1]
		
		return output
	
	def getConnectionStatus(self):
		command_output = self.execute('adsl info')
		output = [] 
		
		regexp_status = re.compile('.*Status:\s+Showtime.+', re.IGNORECASE)
		if ( regexp_status.match(command_output[1]) ):
			output.append('active')
			
			regexp_speed = re.compile('.*upstream\s+rate\s+\=\s+(.+)\,\s+downstream\s+rate\s+\=\s+(.+)$', re.IGNORECASE)
			data = regexp_speed.match(command_output[2])
			if ( data ):
				output.append(data.group(1))
				output.append(data.group(2))
			else:
				output.append('unknown')
				output.append('unknown')
		else:
			output = ['inactive', '0 kbps', '0 kbps']
		
		return output 
	
	def getPublicIp(self):
		#ip line: inet addr:77.230.59.78
		command_output = self.execute('ifconfig nas_0_44')
		
		regexp_ip = re.compile('^inet\s+addr:((\d{1,3}\.){3}\d{1,3}).+',re.IGNORECASE)
		for line in command_output:
			data = regexp_ip.match(line)
			if (data):
				return data.group(1)
		return 'unknown'
	
	def getArpTable(self):
		command_output = self.execute('arp show')
		del(command_output[0])
		return command_output

#Add your router here to get the router commands running
class AnotherCompanyRouter(Router):
	'Diferent Router'
	def execute(self, command):
		pass
