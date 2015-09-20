ddns-daemon
===========

Dynamic DNS client daemon is a Dynamic DNS client written in Python

Current supported providers
------------
 - [Dinahosting S. L.](https://dinahosting.com/)

Instructions
------------

### Installation
 - Put the code in /opt/ddns-daemon (or any other place you like)
 - Copy config.yml-dist to config.yml and edit it as needed

### init.d script
 - Create an init.d script
 - Start the daemon with "service init.d_script_name start

#### autostart init.d script
 - As root, add the init.d script to rc with update-rc.d: update-rc.d init.d_script_name defaults 
