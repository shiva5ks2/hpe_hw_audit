# This python file defines the list of VC Commands that we will parse.

# We will parse the golden configuration and also the current output of any VC "show config".

import re
import bisect

ignore  = 1	# Ignore line parsing

# Context:
# no context  = 0
# qox context = 1
context_val = ''

golden_cfg = 1
input_cfg = 2

ip = '(?:NONE|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
ipv6 = '(?:NONE|\S+)'

ignore_key_list = [
'Address',
'Port',
'SecondaryPort',
'PortWWN',
'MacEnd', 
'SecondaryServerAddress', 
'iScsiMAC', 
'EthernetMAC', 
'MacStart', 
'WwnStart', 
'WwnEnd', 
'SubnetMask', 
'EthernetMac', 'NodeWWN', 'IpAddress', 'Gateway', 'ServerAddress']

domain_name = ''
drop_keys_list = [('set domain', 'Name'), ]

def parse_v(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
	global context_val
	m = re.match(pattern, string)
	if m and len(m.groups()) >= 2:
		context_val = m.group(2)
	return

def parse_fw(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
# Generic parse function. If this doesnt work, override with other functions that can do more.
        m = re.match(pattern, string)
	if m:
		mydict['firmware_version' ,m.group(key_idx)] = (line_num, m.group(val_idx))
	return

def parse_kv(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
# Generic parse function. If this doesnt work, override with other functions that can do more.
	global context_val
	m = re.match(pattern, string)
	if m:
		# For VC, I get attributes as key=value pairs. Lets first extract
		# all the attributes and then populate them in the dict.
		# For e.g. set parameter <name> attr1=val1 attr2 val2 - should be stored
		# in dict as:
		# dict ['set parameter <name>', attr1] = (line_no, val1)
		# dict ['set parameter <name>', attr2] = (line_no, val2)

		# For attrs, the below regex will match any attr=val, where val can contain:
		# -> \w, "." (ip address), ":" (mac address), "," comma-separated list of attrs. 
		attrs = re.findall("(\w+)\=([\w\.,-:\"]+)(?:\s)?", m.group(val_idx))

		# For opts, the below regex takes care of removing any attr of type:
		# ->    at-tr=val (attribute with one more more hyphens
		opts  = re.findall("(?<!\w)-(\w[\w-]+)", m.group(val_idx))
		if 'quiet' in opts:
			opts.remove('quiet')

		#print m.group(val_idx), "####", attrs, "####", opts

		t = ()
		if context:
			t = (context_val,)
		if isinstance(key_idx, tuple):
			for i in key_idx:
				t = t + (m.group(i),)
		else:
			t = t + (m.group(key_idx),)

		for (attr_k,attr_v) in attrs:
			if attr_k not in ignore_key_list:
				my_key = t + (attr_k,)
				mydict[my_key] = (line_num, attr_v)

		for opt_k in opts:
			my_key = t + (opt_k,)
			mydict[my_key] = (line_num, True)

		# Special case of "add profile" where I need to add context
		#if m.group(1) == 'add profile':
		#	context_val = m.group(2)

	return

def parse_ap(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
	# We create a profile and give it a name - "add profile PROFILE_NAME"
	# We then "add enet-connection PROFILE_NAME ..."
	# We then "assign profile PROFILE_NAME DEVICE_BAY"
	# Replace the PROFILE_NAME with DEVICE_BAY in "assign profile" dictionary.
	m = re.match(pattern, string)
	if m:
		profile_name, device_bay = m.groups()
		for key in mydict.keys():
			if len(key) == 2 and isinstance(key[0], tuple) and key[0][0] in ['add enet-connection', 'add fcoe-connection']:
				(my_conn, my_profile_name), my_value = key
				if profile_name == my_profile_name:
					new_key = ((my_conn, device_bay), my_value)
					mydict[new_key] = mydict.pop(key)
	return

def parse_kv_conn(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
# Generic parse function. If this doesnt work, override with other functions that can do more.
	global context_val
	m = re.match(pattern, string)
	if m:
		# For 'add enet-connection' and 'add fc-connection' , I get attributes as key=value pairs.
		# For e.g. add enet-connection ARTNTNBIVISP-A-VZ-C7000-2 Network=EDN PXE=UseBIOS SriovType=DEFAULT
		# in dict as:
		# dict[('add enet-connection', 'ARTNTNBIVISP-A-VZ-C7000-2', ('Network=EDN', 'PXE=UseBIOS', 'SriovType=DEFAULT'))] = (num_of_reps, [line_no, line_no, ... ])
		# The attrs have to be a tuple, not a list, since list cant be used as a key (not hashable)

		# For attrs, the below regex will match any attr=val, where val can contain:
		# -> \w, "." (ip address), ":" (mac address), "," comma-separated list of attrs. 
		# Here I consume attr=val together, instead of (key, value) tuple form
		attrs = re.findall("(\w+\=[\w\.,-:\"]+)(?:\s)?", m.group(val_idx))
		attrs.sort()

		t = ()
		if context:
			t = (context_val,)
		if isinstance(key_idx, tuple):
			for i in key_idx:
				t = t + (m.group(i),)
		else:
			t = t + (m.group(key_idx),)
		
		mykey = (t, tuple(attrs) )

		if mydict.has_key(mykey):
			(reps, line_no_list) = mydict[mykey]
			reps+=1
			line_no_list.append(line_num)
			mydict[mykey] = (reps, line_no_list)
		else:
			mydict[mykey] = (1, [line_num])
	return

vccmds = {
"set domain"			:(parse_kv,  0, '(set domain) (.+)', 1, 2),
"set stackinglink"		:(parse_kv,  0, '(set stackinglink) (.+)', 1, 2),
"set snmp"			:(parse_kv,  0, '(set snmp (?:enet|fc)) (.+)', 1, 2),
"set ssl"			:(parse_kv,  0, '(set ssl) (.+)', 1, 2),
"set user-security"		:(parse_kv,  0, '(set user-security) (.+)', 1, 2),
"set ldap"			:(parse_kv,  0, '(set ldap) (.+)', 1, 2),
"set tacacs"			:(parse_kv,  0, '(set tacacs) (.+)', 1, 2),
"set radius"			:(parse_kv,  0, '(set radius) (.+)', 1, 2),
"set role"			:(parse_kv,  0, '(set role (?:domain|network|server|storage)) (.+)', 1, 2),
"set serverid"			:(parse_kv,  0, '(set serverid) (.+)', 1, 2),
"add user"			:(parse_kv,  0, '(add user (?:\w+)) (.+)', 1, 2),
"set session"			:(parse_kv,  0, '(set session) (.+)', 1, 2),
"set qos"			:(parse_v,   0, '(set qos) (\w+)', 1, 2),
"set qos-class"			:(parse_kv,  1, '(set qos-class (?:\w+)) (.+)', 1, 2),		# In current qos context
"set qos-classifier"		:(parse_kv,  1, '(set qos-classifier (?:\w+)) (.+)', 1, 2),	# In current qos context
"set qos-map"			:(parse_kv,  1, '(set qos-map (?:\w+)) (.+)', 1, 2),		# In current qos context
"set mac-cache"			:(parse_kv,  0, '(set mac-cache) (.+)', 1, 2),
"set igmp"			:(parse_kv,  0, '(set igmp) (.+)', 1, 2),
"set enet-vlan"			:(parse_kv,  0, '(set enet-vlan) (.+)', 1, 2),
"set statistics-throughput"	:(parse_kv,  0, '(set statistics-throughput) (.+)', 1, 2),
"set port-protect"		:(parse_kv,  0, '(set port-protect) (.+)', 1, 2),
"set lacp-timer"		:(parse_kv,  0, '(set lacp-timer) (.+)', 1, 2),
"add network"			:(parse_kv,  0, '(add network (?:\w+)) (.+)', 1, 2),		# TBD - handle the -fcoe option
"add uplinkport"		:(parse_kv,  0, '(add uplinkport (?:[\w\.:]+)) (.+)', 1, 2),
"set link-dist-interval"	:(parse_kv,  0, '(set link-dist-interval) (.+)', 1, 2),
"set advanced-networking"	:(parse_kv,  0, '(set advanced-networking) (.+)', 1, 2),
"add profile"			:(parse_kv,  0, '(add profile) (\w+) (.+)', (1,2), 3),
"add enet-connection"		:(parse_kv_conn,  0, '(add enet-connection) (\w[\w-]+) (.+)', (1,2), 3),
"add fcoe-connection"		:(parse_kv_conn,  0, '(add fcoe-connection) (\w[\w-]+) (.+)', (1,2), 3),
"assign profile"		:(parse_ap,  0, 'assign profile\s+([\w\-\_]+)\s+([\w:]+)', 1, 2),
"add snmp-trap"			:(parse_kv,  0, '(add snmp-trap (?:[\w\-\_]+)) (.+)', 1, 2),
"add port-monitor AnalyzerPort"	:(parse_kv,  0, '(add port-monitor AnalyzerPort)=([\w\.:]+) (.+)', (1,2), 3),
"add port-monitor MonitorPort"	:(parse_kv,  0, '(add port-monitor MonitorPort)=([\w\.:]+) (.+)', (1,2), 3),
"set lldp"			:(parse_kv,  0, '(set lacp-timer) (.+)', 1, 2),
"add uplinkset"			:(parse_kv,  0, '(add uplinkset (?:\w+)) (.+)', 1, 2),
"set port-monitor"		:(parse_kv,  0, '(set port-monitor) (.+)', 1, 2),
"firmware"			:(parse_fw,  0, '(\w+\d+:\d{1,2})(?:\s+[\w\-]+){3}\s+(\w+\.\w+\s+[\w\-:]+)\s+\w+', 1, 2)
}

