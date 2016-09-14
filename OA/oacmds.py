# This python file defines the list of OA Commands that we will parse.
# We will parse the golden configuration and also the current output of any OA "show config".

import re

ignore  = 1	# Ignore line parsing

golden_cfg = 1
input_cfg = 2

ip = '(?:NONE|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
ipv6 = '(?:NONE|\S+)'

rack_name = ''

def get_rack_name(line_num, string, pattern, key_idx, val_idx, mydict, config_type):
	global rack_name
	m = re.match(pattern, string)
	if m and len(m.groups()) >= 2:
		rack_name = m.group(2).strip('"')
	return

def parse(line_num, string, pattern, key_idx, val_idx, mydict, config_type):
# Generic parse function. If this doesnt work, override with other functions that can do more.
	m = re.match(pattern, string)
	if m:
		if isinstance(key_idx, tuple):
			t = ()
			for i in key_idx:
				t = t + (m.group(i),)
			mydict[t] = (line_num, m.group(val_idx))
		else:
			mydict[m.group(key_idx)] = (line_num, m.group(val_idx))
	return

def parse_fw(line_num, string, pattern, key_idx, val_idx, mydict, config_type):
# Generic parse function. If this doesnt work, override with other functions that can do more.
	m = re.match(pattern, string)
	if m:
		mydict['firmware_version' ,m.group(key_idx)] = (line_num, m.group(val_idx))
	return

def parse_set_ebipa_server(line_num, string, pattern, key_idx, val_idx, mydict, config_type):
	pattern = '(SET EBIPA SERVER) (%s %s|NETMASK %s|GATEWAY %s|DOMAIN \S+)( \S+)?' % (ip, ip, ip, ip)
	m = re.match(pattern, string)
	if m:
		if m.group(3) == None:
			bay = 'ALL'
		else:
			bay = m.group(3).strip(' "') or 'ALL'
		s1, s2 = m.group(2).split()

		if s1 in ['NETMASK', 'GATEWAY', 'DOMAIN']:
			mydict[(m.group(1), bay, s1)] = (line_num, s2)
		else:
			mydict[(m.group(1), bay, "IPADDR_N_MASK")] = (line_num, m.group(2))
	return

def parse_set_ebipa_interconnect(line_num, string, pattern, key_idx, val_idx, mydict, config_type):
	pattern = '(SET EBIPA INTERCONNECT) (%s %s|NETMASK %s|GATEWAY %s|NTP (?:PRIMARY|SECONDARY) %s|DOMAIN \S+)( \S+)?' % (ip, ip, ip, ip, ip)
	m = re.match(pattern, string)
	if m:
		if m.group(3) == None:
			bay = 'ALL'
		else:
			bay = m.group(3).strip(' "') or 'ALL'
		s1, s2 = m.group(2).rsplit(' ',1)

		if s1 in ['NETMASK', 'GATEWAY', 'DOMAIN', 'NTP PRIMARY', 'NTP SECONDARY']:
			mydict[(m.group(1), bay, s1)] = (line_num, s2)
		else:
			mydict[(m.group(1), bay, "IPADDR_N_MASK")] = (line_num, m.group(2))
	return

def parse_set_ebipav6(line_num, string, pattern, key_idx, val_idx, mydict, config_type):
	pattern = '(SET EBIPAV6 (?:SERVER|INTERCONNECT)) (GATEWAY %s|DOMAIN \S+|%s)( \S+)?' % (ipv6, ipv6)
	m = re.match(pattern, string)
	if m:
		if m.group(3) == None:
			bay = 'ALL'
		else:
			bay = m.group(3).strip(' "') or 'ALL'

		temp = m.group(2).rsplit(' ', 1)
		if len(temp) == 1:
			s1 = temp[0]
		else:
			s1, s2 = temp

		if s1 in ['GATEWAY', 'DOMAIN']:
			mydict[(m.group(1), bay, s1)] = (line_num, s2)
		else:
			mydict[(m.group(1), bay, "IPADDR")] = (line_num, m.group(2))
	return

oacmds = {
# General commands
# CLEAR SCREEN
# EXIT
# HELP
# LOGOUT
# QUIT

# Rack commands
"SET RACK NAME"							:(get_rack_name, '(SET RACK NAME) (\S.+)', 0, 0),	# Get rack name to be used later.
# SHOW RACK INFO
# SHOW RACK NAME
# SHOW TOPOLOGY

# User account commands
"ADD USER"							:(ignore, "", 0, 0),
"ASSIGN"							:(ignore, '(ASSIGN (?:INTERCONNECT|SERVER)) (.+)', 0, 0),
"ASSIGN OA"							:(ignore, "", 0, 0),
"DISABLE USER"							:(ignore, "", 0, 0),
"DISABLE STRONG PASSWORDS"					:(parse, '(DISABLE) (STRONG PASSWORDS)', 2, 1),
"ENABLE STRONG PASSWORDS"					:(parse, '(ENABLE) (STRONG PASSWORDS)', 2, 1),
"ENABLE USER"							:(parse, '(ENABLE USER) (\S+)', 1, 2),
# HISTORY
"REMOVE USER"							:(ignore, "", 0, 0),
"SET MINIMUM PASSWORD LENGTH"					:(parse, '(SET MINIMUM PASSWORD LENGTH) (\S+)', 1, 2),
"SET PASSWORD"							:(ignore, "", 0, 0),
"SET SESSION TIMEOUT"						:(parse, '(SET SESSION TIMEOUT) (\S+)', 1, 2),
"SET USER ACCESS"						:(parse, '(SET USER ACCESS) (\S+) (\S+)', (1, 2), 3),
"SET USER CONTACT"						:(parse, '(SET USER CONTACT) (\S+) (\S+)', (1, 2), 3),
"SET USER FULLNAME"						:(parse, '(SET USER FULLNAME) (\S+) (\S+)', (1, 2), 3),
"SET USER PASSWORD"						:(parse, '(SET USER PASSWORD) (\S+) (\S.+)', (1, 2), 3),
# SHOW PASSWORD SETTINGS
# SHOW SESSION TIMEOUT
# SHOW USER
# SLEEP
"UNASSIGN"							:(ignore, '(ASSIGN (?:INTERCONNECT|SERVER)) (.+)', 0, 0),
"UNASSIGN OA"							:(ignore, "", 0, 0),

# Two-Factor Authentication commands
"ADD CA CERTIFICATE"						:(ignore, "", 0, 0),
"DISABLE CRL"							:(ignore, "", 0, 0),
"DISABLE TWOFACTOR"						:(ignore, "", 0, 0),
"DOWNLOAD CA CERTIFICATE"					:(ignore, "", 0, 0),
"DOWNLOAD USER CERTIFICATE"					:(ignore, "", 0, 0),
"REMOVE CA CERTIFICATE"						:(ignore, "", 0, 0),
"REMOVE USER CERTIFICATE"					:(ignore, "", 0, 0),
"SET USER CERTIFICATE"						:(ignore, "", 0, 0),
# SHOW CA CERTIFICATES
# SHOW TWOFACTOR INFO

# Directory commands
"ADD LDAP CERTIFICATE"						:(ignore, "", 0, 0),
"ADD LDAP GROUP"						:(ignore, "", 0, 0),
"ASSIGN for LDAP"						:(ignore, "", 0, 0),
"ASSIGN OA LDAP GROUP"						:(ignore, "", 0, 0),
"DISABLE LDAP"							:(parse, '(DISABLE) (LDAP)', 2, 1),
"DOWNLOAD LDAP CERTIFICATE"					:(ignore, "", 0, 0),
"ENABLE LDAP"							:(parse, '(ENABLE) (LDAP)', 2, 1),
"REMOVE LDAP CERTIFICATE"					:(ignore, "", 0, 0),
"REMOVE LDAP GROUP"						:(ignore, "", 0, 0),
"SET LDAP GROUP ACCESS"						:(ignore, "", 0, 0),
"SET LDAP GROUP DESCRIPTION"					:(ignore, "", 0, 0),
"SET LDAP NAME MAP"						:(ignore, "", 0, 0),
"SET LDAP GCPORT"						:(ignore, "", 0, 0),
"SET LDAP PORT"							:(ignore, "", 0, 0),
"SET LDAP SEARCH"						:(ignore, "", 0, 0),
"SET LDAP SERVER"						:(ignore, "", 0, 0),
# SHOW LDAP CERTIFICATE
# SHOW LDAP GROUP
# SHOW LDAP INFO
# TEST LDAP
"UNASSIGN for LDAP"						:(ignore, "", 0, 0),
"UNASSIGN OA LDAP GROUP"					:(ignore, "", 0, 0),

# HP SIM commands
"ADD HPSIM CERTIFICATE"						:(ignore, "", 0, 0),
"DOWNLOAD HPSIM CERTIFICATE"					:(ignore, "", 0, 0),
"REMOVE HPSIM CERTIFICATE"					:(ignore, "", 0, 0),
"SET HPSIM TRUST MODE"						:(ignore, "", 0, 0),
# SHOW HPSIM INFO

# General management commands
"DISABLE URB"							:(parse, '(DISABLE) (URB)', 2, 1),
"DOWNLOAD OA CERTIFICATE"					:(ignore, "", 0, 0),
"ENABLE URB"							:(parse, '(ENABLE) (URB)', 2, 1),
"FORCE TAKEOVER"						:(ignore, "", 0, 0),
"GENERATE CERTIFICATE"						:(ignore, "", 0, 0),
"GENERATE CERTIFICATE prompts"					:(ignore, "", 0, 0),
"GENERATE KEY"							:(ignore, "", 0, 0),
# PING
"SET DEVICE SERIAL_NUMBER BLADE"				:(ignore, "", 0, 0),
"SET FACTORY"							:(ignore, "", 0, 0),
"SET SCRIPT MODE"						:(ignore, "", 0, 0),
"SET URB"							:(ignore, "", 0, 0),
# SHOW ALL
# SHOW DEVICE SERIAL_NUMBER BLADE
# SHOW URB
# TEST URB

# Enclosure Bay IP Addressing commands
"ADD EBIPA"							:(ignore, "", 0, 0),
"ADD EBIPAV6"							:(ignore, "", 0, 0),
"DISABLE EBIPA"							:(parse, '(DISABLE EBIPA (?:INTERCONNECT|SERVER)) (\S.+)', 1, 2),
"DISABLE EBIPAV6"						:(parse, '(DISABLE EBIPAV6 (?:INTERCONNECT|SERVER)) (\S.+)', 1, 2),
"ENABLE EBIPA"							:(parse, '(ENABLE EBIPA (?:INTERCONNECT|SERVER)) (\S.+)', 1, 2),
"ENABLE EBIPAV6"						:(parse, '(ENABLE EBIPAV6 (?:INTERCONNECT|SERVER)) (\S.+)', 1, 2),
"REMOVE EBIPA"							:(ignore, "", 0, 0),
"REMOVE EBIPAV6"						:(ignore, "", 0, 0),
"SAVE EBIPA"							:(ignore, "", 0, 0),
"SAVE EBIPAV6"							:(ignore, "", 0, 0),
"SET EBIPA INTERCONNECT"					:(parse_set_ebipa_interconnect, "", 0, 0),
"SET EBIPA SERVER"						:(parse_set_ebipa_server, "", 0, 0),
"SET EBIPAV6 INTERCONNECT"					:(parse_set_ebipav6, "", 0, 0),
"SET EBIPAV6 SERVER"						:(parse_set_ebipav6, "", 0, 0),
# SHOW EBIPA
# SHOW EBIPAV6

# Enclosure network configuration commands
"ADD OA ADDRESS IPV6"						:(ignore, "", 0, 0),
"ADD OA DNS"							:(ignore, "", 0, 0),
"ADD OA DNS IPV6"						:(ignore, "", 0, 0),
"ADD OA ROUTE IPV6"						:(ignore, "", 0, 0),
"ADD SSHKEY"							:(ignore, "", 0, 0),
# pattern = '(ADD SNMP TRAPRECEIVER(?! v3)) (\S+)( \S+)?'
"ADD SNMP TRAPRECEIVER"						:(parse, '(ADD SNMP TRAPRECEIVER(?: v3)?) (.+)', 1, 2),
# "ADD SNMP TRAPRECEIVER V3"					:(ignore, "", 0, 0),		# covered by above parse
"ADD SNMP USER"							:(ignore, "", 0, 0),
"ADD TRUSTED HOST"						:(ignore, "", 0, 0),
"CLEAR LOGIN_BANNER_TEXT"					:(ignore, "", 0, 0),
"CLEAR NTP"							:(ignore, "", 0, 0),
"CLEAR SSHKEY"							:(ignore, "", 0, 0),
"CLEAR VCMODE"							:(ignore, "", 0, 0),
"DISABLE ALERTMAIL"						:(parse, '(DISABLE) (ALERTMAIL)', 2, 1),
"DISABLE DHCPV6"						:(parse, '(DISABLE) (DHCPV6)', 2, 1),
"DISABLE ENCLOSURE_ILO_FEDERATION_SUPPORT"			:(parse, '(DISABLE) (ENCLOSURE_ILO_FEDERATION_SUPPORT)', 2, 1),
"DISABLE ENCLOSURE_IP_MODE"					:(parse, '(DISABLE) (ENCLOSURE_IP_MODE)', 2, 1),
"DISABLE HTTPS"							:(parse, '(DISABLE) (HTTPS)', 2, 1),
"DISABLE FQDN_LINK_SUPPORT"					:(parse, '(DISABLE) (FQDN_LINK_SUPPORT)', 2, 1),
"DISABLE IPV6"							:(parse, '(DISABLE) (IPV6)', 2, 1),
"DISABLE IPV6DYNDNS"						:(parse, '(DISABLE IPV6DYNDNS)(?: (\S+))?', 1, 2),
"DISABLE LOGIN_BANNER"						:(parse, '(DISABLE) (LOGIN_BANNER)', 2, 1),
"DISABLE NTP"							:(parse, '(DISABLE) (NTP)', 2, 1),
"DISABLE ROUTER ADVERTISEMENTS"					:(parse, '(DISABLE) (ROUTER ADVERTISEMENTS)', 2, 1),
"DISABLE SECURESH"						:(parse, '(DISABLE) (SECURESH)', 2, 1),
"DISABLE SLAAC"							:(parse, '(DISABLE) (SLAAC)', 2, 1),
"DISABLE SNMP"							:(parse, '(DISABLE) (SNMP)', 2, 1),
"DISABLE SSL CIPHER"						:(ignore, "", 0, 0),
"DISABLE SSL PROTOCOL"						:(ignore, "", 0, 0),
"DISABLE TELNET"						:(parse, '(DISABLE) (TELNET)', 2, 1),
"DISABLE WEB"							:(parse, '(DISABLE) (WEB)', 2, 1),
"DISABLE TRUSTED HOST"						:(parse, '(DISABLE) (TRUSTED HOST)', 2, 1),
"DISABLE XMLREPLY"						:(parse, '(DISABLE) (XMLREPLY)', 2, 1),
"DOWNLOAD CONFIG"						:(ignore, "", 0, 0),
"DOWNLOAD SSHKEY"						:(ignore, "", 0, 0),
"ENABLE ALERTMAIL"						:(parse, '(ENABLE) (ALERTMAIL)', 2, 1),
"ENABLE DHCPV6"							:(parse, '(ENABLE) (DHCPV6)', 2, 1),
"ENABLE ENCLOSURE_ILO_FEDERATION_SUPPORT"			:(parse, '(ENABLE) (ENCLOSURE_ILO_FEDERATION_SUPPORT)', 2, 1),
"ENABLE ENCLOSURE_IP_MODE"					:(parse, '(ENABLE) (ENCLOSURE_IP_MODE)', 2, 1),
"ENABLE FQDN_LINK_SUPPORT"					:(parse, '(ENABLE) (FQDN_LINK_SUPPORT)', 2, 1),
"ENABLE HTTPS"							:(parse, '(ENABLE) (HTTPS)', 2, 1),
"ENABLE IPV6"							:(parse, '(ENABLE) (IPV6)', 2, 1),
"ENABLE IPV6DYNDNS"						:(parse, '(ENABLE IPV6DYNDNS)(?: (\S+))?', 1, 2),
"ENABLE LOGIN_BANNER"						:(parse, '(ENABLE) (LOGIN_BANNER)', 2, 1),
"ENABLE NTP"							:(parse, '(ENABLE) (NTP)', 2, 1),
"ENABLE ROUTER ADVERTISEMENTS"					:(parse, '(ENABLE) (ROUTER ADVERTISEMENTS)', 2, 1),
"ENABLE SECURESH"						:(parse, '(ENABLE) (SECURESH)', 2, 1),
"ENABLE SLAAC"							:(parse, '(ENABLE) (SLAAC)', 2, 1),
"ENABLE SNMP"							:(parse, '(ENABLE) (SNMP)', 2, 1),
"ENABLE SSL CIPHER"						:(ignore, "", 0, 0),
"ENABLE SSL PROTOCOL"						:(ignore, "", 0, 0),
"ENABLE TELNET"							:(parse, '(ENABLE) (TELNET)', 2, 1),
"ENABLE WEB"							:(parse, '(ENABLE) (WEB)', 2, 1),
"ENABLE TRUSTED HOST"						:(parse, '(ENABLE) (TRUSTED HOST)', 2, 1),
"ENABLE XMLREPLY"						:(parse, '(ENABLE) (XMLREPLY)', 2, 1),
"REMOVE OA ADDRESS IPV6"					:(ignore, "", 0, 0),
"REMOVE OA DNS"							:(ignore, "", 0, 0),
"REMOVE OA DNS IPV6"						:(ignore, "", 0, 0),
"REMOVE OA ROUTE IPV6"						:(ignore, "", 0, 0),
"REMOVE SNMP TRAPRECEIVER"					:(ignore, "", 0, 0),
"REMOVE SNMP TRAPRECEIVER V3"					:(ignore, "", 0, 0),
"REMOVE SNMP USER"						:(ignore, "", 0, 0),
"REMOVE TRUSTED HOST"						:(ignore, "", 0, 0),
"SET ALERTMAIL MAILBOX"						:(parse, '(SET ALERTMAIL MAILBOX) (\S+)', 1, 2),
"SET ALERTMAIL SENDERDOMAIN"					:(parse, '(SET ALERTMAIL SENDERDOMAIN) (\S+)', 1, 2),
"SET ALERTMAIL SENDERNAME"					:(parse, '(SET ALERTMAIL SENDERNAME) (\S+)', 1, 2),
"SET ALERTMAIL SMTPSERVER"					:(parse, '(SET ALERTMAIL SMTPSERVER)(?: (\S+))?', 1, 2),
"SET FIPS MODE"							:(ignore, "", 0, 0),
"SET HTTP REQUESTREADTIMEOUT"					:(parse, '(SET HTTP REQUESTREADTIMEOUT) (\S.+)', 1, 2),
"SET IPCONFIG"							:(ignore, "", 0, 0),
"SET LOGIN_BANNER_TEXT"						:(ignore, "", 0, 0),
"SET NTP POLL"							:(parse, '(SET NTP POLL) (\S.+)', 1, 2),
"SET NTP PRIMARY"						:(parse, '(SET NTP PRIMARY) (\S.+)', 1, 2),
"SET NTP SECONDARY"						:(parse, '(SET NTP SECONDARY) (\S.+)', 1, 2),
"SET OA GATEWAY"						:(ignore, "", 0, 0),
"SET OA GATEWAY"						:(ignore, "", 0, 0),
"SET OA NAME"							:(ignore, "", 0, 0),
"SET OA UID"							:(ignore, "", 0, 0),
"SET SECURESH SERVER KEX DHG1"					:(parse, '(SET SECURESH SERVER KEX DHG1) (\S.+)', 1, 2),
"SET SERIAL BAUD"						:(parse, '(SET SERIAL BAUD)(?: (\S+))?', 1, 2),
"SET SNMP COMMUNITY"						:(parse, '(SET SNMP COMMUNITY (?:READ|WRITE)) (\S.+)', 1, 2),
"SET SNMP ENGINEID"						:(parse, '(SET SNMP ENGINEID) (\S.+)', 1, 2),
"SET SNMP CONTACT"						:(parse, '(SET SNMP CONTACT) (\S.+)', 1, 2),
"SET SNMP LOCATION"						:(parse, '(SET SNMP LOCATION) (\S.+)', 1, 2),
# SHOW FIPS MODE
# SHOW HEALTH
# SHOW LOGIN_BANNER
# SHOW NETWORK
# SHOW SNMP
# SHOW SNMP USER
# SHOW SSHFINGERPRINT
# SHOW SSHKEY
# SHOW SSL CIPHER
# SHOW SSL PROTOCOL
# SHOW VCMODE
# TEST ALERTMAIL
# TEST SNMP

# Enclosure management commands
"ADD LANGUAGE"							:(ignore, "", 0, 0),
"CLEAR SYSLOG"							:(ignore, "", 0, 0),
"CONNECT ENCLOSURE"						:(ignore, "", 0, 0),
"DISABLE DHCP_DOMAIN_NAME"					:(ignore, "", 0, 0),
"DISABLE GUI_LOGIN_DETAIL"					:(ignore, "", 0, 0),
"DISABLE LLF"							:(parse, '(DISABLE) (LLF)', 2, 1),
"ENABLE DHCP_DOMAIN_NAME"					:(ignore, "", 0, 0),
"ENABLE GUI_LOGIN_DETAIL"					:(ignore, "", 0, 0),
"ENABLE LLF"							:(parse, '(ENABLE) (LLF)', 2, 1),
"REMOVE LANGUAGE"						:(ignore, "", 0, 0),
"RESET ILO"							:(ignore, "", 0, 0),
"RESTART OA"							:(ignore, "", 0, 0),
"SET DATE"							:(ignore, "", 0, 0),
"SET DISPLAY EVENTS"						:(ignore, "", 0, 0),
"SET ENCLOSURE ASSET"						:(ignore, "", 0, 0),
"SET ENCLOSURE NAME"						:(ignore, "", 0, 0),
"SET ENCLOSURE PART_ NUMBER"					:(ignore, "", 0, 0),
"SET ENCLOSURE PDU_TYPE"					:(ignore, "", 0, 0),
"SET ENCLOSURE SERIAL_NUMBER"					:(ignore, "", 0, 0),
"SET ENCLOSURE UID"						:(ignore, "", 0, 0),
"SET LLF INTERVAL"						:(parse, '(SET LLF INTERVAL) (\S.+)', 1, 2),
"SET OA DOMAIN_NAME"						:(ignore, "", 0, 0),
"SET OA USB"							:(ignore, "", 0, 0),
"SET POWER MODE"						:(parse, '(SET POWER MODE) (\S.+)', 1, 2),
"SET POWER LIMIT"						:(parse, '(SET POWER LIMIT) (\S.+)', 1, 2),
"SET POWER SAVINGS"						:(parse, '(SET POWER SAVINGS) (\S.+)', 1, 2),
"SET TIMEZONE"							:(parse, '(SET TIMEZONE) (\S.+)', 1, 2),
# SHOW CONFIG
# SHOW DATE
# SHOW DISPLAY EVENTS
# SHOW ENCLOSURE FAN
# SHOW ENCLOSURE INFO
# SHOW ENCLOSURE LCD
# SHOW ENCLOSURE POWER_SUMMARY
# SHOW ENCLOSURE POWERSUPPLY
# SHOW ENCLOSURE STATUS
# SHOW ENCLOSURE TEMP
# SHOW FRU
# SHOW LANGUAGES
# SHOW OA
# SHOW OA CERTIFICATE
# SHOW OA INFO
# SHOW OA NETWORK
# SHOW OA STATUS
# SHOW OA UPTIME
# SHOW OA USB
# SHOW POWER
# SHOW SYSLOG
# SHOW SYSLOG OA
# SHOW SYSLOG HISTORY
"UPDATE"							:(ignore, "", 0, 0),
"UPDATE ILO"							:(ignore, "", 0, 0),
"UPDATE IMAGE FW_ISO"						:(ignore, "", 0, 0),
"UPLOAD CONFIG"							:(ignore, "", 0, 0),
"UPLOAD SUPPORTDUMP"						:(ignore, "", 0, 0),
"UPLOAD SYSLOG"							:(ignore, "", 0, 0),

# Enclosure Firmware Management commands
"CLEAR FIRMWARE MANAGEMENT ALL_LOGS"				:(ignore, "", 0, 0),
"DISCOVER FIRMWARE SERVER"					:(ignore, "", 0, 0),
"DISABLE FIRMWARE MANAGEMENT"					:(parse, '(DISABLE) (FIRMWARE MANAGEMENT)', 2, 1),
"ENABLE FIRMWARE MANAGEMENT"					:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT"					:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT URL"					:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT POLICY"				:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT POWER"					:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT SCHEDULE"				:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT BAYS_TO_INCLUDE SERVER"		:(ignore, "", 0, 0),
"SET FIRMWARE MANAGEMENT FORCE DOWNGRADE"			:(ignore, "", 0, 0),
# SHOW FIRMWARE
# SHOW FIRMWARE MANAGEMENT
# SHOW FIRMWARE MANAGEMENT LOG
# SHOW FIRMWARE SUMMARY
# SHOW FIRMWARE SUMMARY CSV
# SHOW FIRMWARE LOG SERVER
# SHOW FIRMWARE LOG SESSION
# SHOW SERVER FIRMWARE
"UPDATE FIRMWARE SERVER"					:(ignore, "", 0, 0),

# Blade management commands
"ASSIGN SERVER"							:(ignore, "", 0, 0),
"CONNECT SERVER"						:(ignore, "", 0, 0),
"HPONCFG"							:(ignore, "", 0, 0),
"POWEROFF SERVER"						:(ignore, "", 0, 0),
"POWERON SERVER"						:(ignore, "", 0, 0),
"REBOOT SERVER"							:(ignore, "", 0, 0),
"SET NIC"							:(ignore, "", 0, 0),
"SET SERVER BOOT"						:(ignore, "", 0, 0),
"SET SERVER BOOT FIRST"						:(ignore, "", 0, 0),
"SET SERVER BOOT ONCE"						:(ignore, "", 0, 0),
"SET SERVER POWERDELAY"						:(parse, '(SET SERVER POWERDELAY) (\S+) (\S+)', (1, 2), 3),
"SET SERVER UID"						:(ignore, "", 0, 0),
# SHOW SERVER BOOT
# SHOW SERVER INFO
# SHOW SERVER LIST
# SHOW SERVER NAMES
# SHOW SERVER PORT MAP
# SHOW SERVER POWERDELAY
# SHOW SERVER STATUS
# SHOW SERVER TEMP
# SHOW SYSLOG SERVER
"UNASSIGN SERVER"						:(ignore, "", 0, 0),

# Interconnect management commands
"ASSIGN INTERCONNECT"						:(ignore, "", 0, 0),
"CLEAR INTERCONNECT SESSION"					:(ignore, "", 0, 0),
"CONNECT INTERCONNECT"						:(ignore, "", 0, 0),
"POWEROFF INTERCONNECT"						:(ignore, "", 0, 0),
"POWERON INTERCONNECT"						:(ignore, "", 0, 0),
"RESTART INTERCONNECT"						:(ignore, "", 0, 0),
"SET INTERCONNECT ADMIN_PASSWORD FACTORY"			:(ignore, "", 0, 0),
"SET INTERCONNECT FACTORY"					:(ignore, "", 0, 0),
"SET INTERCONNECT POWERDELAY"					:(parse, '(SET INTERCONNECT POWERDELAY) (\S+) (\S+)', (1, 2), 3),
"SET INTERCONNECT UID"						:(ignore, "", 0, 0),
# SHOW INTERCONNECT
# SHOW INTERCONNECT INFO
# SHOW INTERCONNECT LIST
# SHOW INTERCONNECT PORT MAP
# SHOW INTERCONNECT POWERDELAY
# SHOW INTERCONNECT SESSIONS
# SHOW INTERCONNECT STATUS

# Active Health System commands
"ENABLE ACTIVE_HEALTH_SYSTEM"					:(parse, '(ENABLE) (ACTIVE_HEALTH_SYSTEM)', 2, 1),
"DISABLE ACTIVE_HEALTH_SYSTEM"					:(parse, '(DISABLE) (ACTIVE_HEALTH_SYSTEM)', 2, 1),
"SET SERVER DVD"						:(ignore, "", 0, 0),
# SHOW SERVER DVD

# Remote syslog commands
"DISABLE SYSLOG REMOTE"						:(parse, '(DISABLE) (SYSLOG REMOTE)', 2, 1),
"ENABLE SYSLOG REMOTE"						:(parse, '(ENABLE) (SYSLOG REMOTE)', 2, 1),
"SET REMOTE SYSLOG PORT"					:(parse, '(SET REMOTE SYSLOG PORT) (\S.+)', 1, 2),
"SET REMOTE SYSLOG SERVER"					:(parse, '(SET REMOTE SYSLOG SERVER) (\S.+)', 1, 2),
# SHOW SYSLOG SETTINGS
# TEST SYSLOG

# USB support commands
"DOWNLOAD CONFIG using USB key"					:(ignore, "", 0, 0),
"SET SERVER DVD for USB key"					:(ignore, "", 0, 0),
# SHOW USBKEY
"UPDATE IMAGE using USB key"					:(ignore, "", 0, 0),
"UPLOAD CONFIG using USB key"					:(ignore, "", 0, 0),

# VLAN commands
"ADD VLAN"							:(ignore, "", 0, 0),
"DISABLE VLAN"							:(ignore, "", 0, 0),
"EDIT VLAN"							:(ignore, "", 0, 0),
"ENABLE VLAN"							:(ignore, "", 0, 0),
"REMOVE VLAN"							:(ignore, "", 0, 0),
"SAVE VLAN"							:(ignore, "", 0, 0),
"SET VLAN DEFAULT"						:(parse, '(SET VLAN DEFAULT) (\S+)', 1, 2),
"SET VLAN FACTORY"						:(ignore, "", 0, 0),
"SET VLAN INTERCONNECT"						:(parse, '(SET VLAN INTERCONNECT) (\S+) (\S+)', (1, 3), 2),
"SET VLAN IPCONFIG"						:(ignore, "", 0, 0),
"SET VLAN IPCONFIG DHCP"					:(ignore, "", 0, 0),
"SET VLAN IPCONFIG SAVE"					:(ignore, "", 0, 0),
"SET VLAN IPCONFIG STATIC"					:(ignore, "", 0, 0),
"SET VLAN OA"							:(parse, '(SET VLAN OA) (\S+)', 1, 2),
"SET VLAN REVERT"						:(parse, '(SET VLAN REVERT) (\S+)', 1, 2),
"SET VLAN SERVER"						:(parse, '(SET VLAN SERVER) (\S+) (\S+)', (1, 3), 2),
# SHOW VLAN

# HP Insight Remote Support commands
"ADD REMOTE_SUPPORT CERTIFICATE"				:(ignore, "", 0, 0),
"DOWNLOAD REMOTE_SUPPORT CERTIFICATE"				:(ignore, "", 0, 0),
"ENABLE REMOTE_SUPPORT DIRECT"					:(ignore, "", 0, 0),
"ENABLE REMOTE_SUPPORT IRS"					:(ignore, "", 0, 0),
"ENABLE REMOTE_SUPPORT MAINTENANCE"				:(ignore, "", 0, 0),
"DISABLE REMOTE_SUPPORT"					:(parse, '(DISABLE) (REMOTE_SUPPORT)', 2, 1),
"DISABLE REMOTE_SUPPORT MAINTENANCE"				:(parse, '(DISABLE) (REMOTE_SUPPORT MAINTENANCE)', 2, 1),
"REMOVE REMOTE_SUPPORT CERTIFICATE"				:(ignore, "", 0, 0),
"SEND REMOTE_SUPPORT DATACOLLECTION"				:(ignore, "", 0, 0),
"SET REMOTE_SUPPORT DIRECT ONLINE_REGISTRATION_COMPLETE"	:(ignore, "", 0, 0),
"SET REMOTE_SUPPORT DIRECT PROXY"				:(ignore, "", 0, 0),
# SHOW REMOTE_SUPPORT
# SHOW REMOTE_SUPPORT CERTIFICATE
# SHOW REMOTE_SUPPORT EVENTS
# TEST REMOTE_SUPPORT

# Enclosure Dynamic Power Cap commands
"SET ENCLOSURE POWER_CAP"					:(parse, '(SET ENCLOSURE POWER_CAP) (\S.+)', 1, 2),
"SET ENCLOSURE POWER_CAP_BAYS_TO_EXCLUDE"			:(parse, '(SET ENCLOSURE POWER_CAP_BAYS_TO_EXCLUDE) (\S.+)', 1, 2),
"firmware"							:(parse_fw,'^([0-9]{1,2}),[\w ]+,[\w ]+,.+(?:iLO4), ([^,]+),.+', 1, 2)
# SHOW ENCLOSURE POWER_CAP
# SHOW ENCLOSURE POWER_CAP_BAYS_TO_EXCLUDE
}

