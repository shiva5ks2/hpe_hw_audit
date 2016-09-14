# This python file defines the list of P2000 Commands that we will parse.

# We will parse the golden configuration and also the current output of any P2000 config commands.

import re
import bisect

ignore  = 1	# Ignore line parsing

# Context:
parent_context_val = 0
parent_context_key = ()
myTempList = []

iAdvancedSettingsTable	= 1
iAutoWriteThroughTrigger= 2
iCertificateStatus	= 3	# MULTIPLE - one for each controller - IGNORED
iDriveParameters	= 4
iEmailParameters	= 5
iIscsiParameters	= 6
iJobParameters		= 7
iNetworkParameters	= 8	# MULTIPLE - one for each controller
iSecurityCommunicationsProtocols= 9
iRedundancy		= 10
iSnmpParameters		= 11
iSystemParametersTable	= 12
iUsers			= 13	# MULTIPLE - one for each user
iVersions		= 14	# MULTIPLE - one for each controller

settings_mult_key = {
iNetworkParameters	: 'durable-id',
iUsers			: 'username',
iVersions		: 'name'	# Provided with -> basetype:"versions",name:CONTROLLER_NAME ...
}

golden_cfg = 1
input_cfg = 2

ignore_key_list = [
'email-notify-address-1',
'email-notify-address-2',
'email-notify-address-3',
'email-notify-address-4',
'email-server',
'email-domain',
'email-sender',
'ip-address',
'gateway',
'subnet-mask',
'mac-address',
'snmp-trap-host-1',
'snmp-trap-host-2',
'snmp-trap-host-3',
'health-reason',
'health-recommendation',
'controller-a-serial-number',
'controller-b-serial-number',
'serial-number'
]

def parse_v(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
	global parent_context_val
	global parent_context_key
	m = re.match(pattern, string)
	if m and not context:
		parent_context_val = 0
		parent_context_key = ()
	elif m:		# And context is to be parsed
		parent_context_val = context
		parent_context_key = (m.group(key_idx),)
	return

def parse_base(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
	global parent_context_val
	global parent_context_key
	global myTempList
	m = re.match(pattern, string)
	if m:
		# Must be in the context of version
		# I should have seen all version attributes before this
		parent_context_key = parent_context_key + (m.group(1),)
		for (k,v) in myTempList:
			my_key = parent_context_key + (k,)
			mydict[my_key] = v
		myTempList = []
	return

def parse_nv(line_num, string, pattern, key_idx, val_idx, mydict, config_type, context):
	global parent_context_val
	global parent_context_key
	global myTempList
	m = re.match(pattern, string)
	if parent_context_val and m and len(m.groups()) == 2 and m.group(1) not in ignore_key_list and not re.match('\w[\w-]+-numeric$', m.group(1)):
		# Ignore variables ending with "-numeric"
		# Ignore variables in ignore_key_list
		if parent_context_val not in settings_mult_key.keys():
			# This table does not have multiple entries (like multiple users etc.)
			my_key = parent_context_key + (m.group(1),)
			mydict[my_key] = m.group(2)
		else:
			# This table can have multiple entries - one for each user or each controller
			# Populate in temp list till you get the unique key
			if m.group(1) in settings_mult_key.values():
				# I have just got the unique key
				# Pop the previous entries from myTempList and push into mydict
				parent_context_key = parent_context_key + (m.group(2),)
				for (k,v) in myTempList:
					my_key = parent_context_key + (k,)
					mydict[my_key] = v
				myTempList = []
			else:
				if len(parent_context_key) == 2:
					# I have the unique key. Add to mydict directly
					my_key = parent_context_key + (m.group(1),)
					mydict[my_key] = m.group(2)
				else:
					myTempList.append( (m.group(1), m.group(2)) )



p2kcmds = {
"APIAdvancedSettingsTable"		:(parse_v,  iAdvancedSettingsTable,		'\s*new API(AdvancedSettingsTable).+', 1, 0),
"APIAutoWriteThroughTrigger"		:(parse_v,  iAutoWriteThroughTrigger,		'\s*new API(AutoWriteThroughTrigger).+', 1, 0),
"APIDriveParameters"			:(parse_v,  iDriveParameters,			'\s*new API(DriveParameters).+', 1, 0),
"APIEmailParameters"			:(parse_v,  iEmailParameters,			'\s*new API(EmailParameters).+', 1, 0),
"APIIscsiParameters"			:(parse_v,  iIscsiParameters,			'\s*new API(IscsiParameters).+', 1, 0),
"APIJobParameters"			:(parse_v,  iJobParameters,			'\s*new API(JobParameters).+', 1, 0),
"APINetworkParameters"			:(parse_v,  iNetworkParameters,			'\s*new API(NetworkParameters).+', 1, 0),
"APISecurityCommunicationsProtocols"	:(parse_v,  iSecurityCommunicationsProtocols,	'\s*new API(SecurityCommunicationsProtocols).+', 1, 0),
"APIRedundancy"				:(parse_v,  iRedundancy,			'\s*new API(Redundancy).+', 1, 0),
"APISnmpParameters"			:(parse_v,  iSnmpParameters,			'\s*new API(SnmpParameters).+', 1, 0),
"APISystemParametersTable"		:(parse_v,  iSystemParametersTable,		'\s*new API(SystemParametersTable).+', 1, 0),
"APIUsers"				:(parse_v,  iUsers,				'\s*new API(Users).+', 1, 0),
"APIVersions"				:(parse_v,  iVersions,				'\s*new API(Versions).+', 1, 0),
"APIData"				:(parse_v,  0,					'\s*new API(Data).+', 1, 0),
"APIStatus"				:(parse_v,  0,					'\s*new API(Status).+', 1, 0),
"APIProp"				:(parse_nv, 0,		'\s*new APIProp\(\{name\:\"([^\"]+)\",value\:\"([^\"]+)\".+', 1, 2),
"basetype"				:(parse_base, 0,	'\s*\{basetype\:\"versions\",name\:\"([^\"]+)\".+', 1, 2)
}

