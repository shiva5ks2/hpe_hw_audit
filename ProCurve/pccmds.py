# This python file defines the list of PC Commands that we will parse.
# We will parse the golden configuration and also the current output of any PC "show config".

import re

ignore  = 1	# Ignore line parsing

golden_cfg = 1
input_cfg = 2

ip = '(?:NONE|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
ipv6 = '(?:NONE|\S+)'
temp=""
temp1=""

snmp_server_list = ["community", "contact", "enable", "host", "location", "mib", "response-source", "trap-source" ]

vlan_list = ["name", "untagged", "ip", "ip-recv-mac-address", "auto", "connection-rate-filter", "dhcp-snooping", "forbid", "igmp-proxy", "jumbo", "monitor", "protocol", "qos", "tagged", "voice", "vrrp" , "exit"]

interface_list = ["name", "broadcast-limit", "dhcp-snooping", "disable", "enable", "flow-control", "gvrp", "lacp", "mdix-mode", "monitor", "power", "qos", "speed-duplex", "type", "unknown-vlans", "bandwidth-min", "rate-limit", "link-keepalive", "exit" ]

mirror_list = ["endpoint", range(100), "name" ]

spanning_tree_list = [range(65535), "config-name", "force-version", "bpdu-protection-timeout", "force-version", "forward-delay", "hello-time", "instance", "legacy-mode", "legacy-path-cost", "max-hops", "maximum-age", "pending", "port-list", "priority", "trap" ]

lldp_list = ["admin-status", "config", "enable-notification", "fast-start-count", "holdtime-multiplier", "refresh-interval", "run", "top-change-notify", range(100)]

aaa_list = ["accounting", "authentication", "authorization", "port-access" ]

arp_protect_list = ["trust", "validate", "vlan"]

clock_list = ["set", "summer-time", "timezone" ]

connection_rate_filter_list = ["sensitivity", "unblock"]

console_list = ["baud-rate", "events", "flow-control", "inactivity-timer", "local-terminal", "screen-refresh", "terminal"]

copy_list = ["command-output", "config", "crash-data", "crash-log", "event-log", "flash", "running-config", "startup-config", "tftp", "xmodem", "usb"]

crypto_list = ["host-cert", "key"]

dhcp_relay_list = ["hop-count-increment", "option"]

dhcp_snooping_list = ["authorized-server", "database", "option", "trust", "verify", "vlan"]

filter_list = ["connection-rate", "multicast", "protocol", "source-port"]

link_test_list = ["mac", "repetitions", "timeout", "vlan"]

loop_protect_list = ["disable-timer", "port-list", "transmit-interval", "trap"]

port_security_list = ["action", "address-limit", "clear-intrusion-flag", "learn-mode", "mac-address"]

qos_list = ["apptype", "device-priority", "dscp-map", "protocol", "queue-config", "type-of-service"]

radius_server_list = ["dead-time", "host", "key", "retransmit", "timeout"]

router_list = ["ospf", "pim", "rip", "vrrp"]

snmpv3_list = ["community", "enable", "group", "notify", "only", "params", "restricted-access", "targetaddress", "user"]

tacacs_server_list = ["host", "key", "timeout"]


def parse(line_num, string, pattern, key_idx, val_idx, mydict):
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
def parse_cmd(line_num, string, pattern, key_idx, val_idx, mydict):
 
        m = re.match(pattern, string)
	if m:
		global temp, temp1
		temp = m.group(key_idx)
		temp1 = m.group(val_idx)
	#	mydict[ m.group(key_idx)] = (line_num, m.group(val_idx))
	return


def parse_sub(line_num, string, pattern, key_idx, val_idx, mydict):
	global temp, temp1
	m = re.match(pattern, string)
	if m:
		if temp and temp1 and m.group(key_idx) in eval(temp.replace('-','_')+ '_list') and m.group(key_idx)!="exit":
			mydict[(temp, temp1, m.group(key_idx))] = (line_num, m.group(val_idx))
		elif m.group(key_idx) == "exit":
			temp=""; temp1=""
	return


def parse_fw(line_num, string, pattern, key_idx, val_idx, mydict):
# Generic parse function. If this doesnt work, override with other functions that can do more.
        m = re.match(pattern, string)
	if m:
		mydict[m.group(key_idx)] = (line_num, m.group(val_idx))
	return


pccmds = {
# General commands

# show running-config
"aaa_key"							:(parse_cmd, '(aaa)\s+([\w\-]+)\s+.*$', 1, 2),
"aaa_sub"							:(parse_sub, 'aaa\s+([\w\-]+)\s+(.*$)', 1, 2),
"arp-protect_key"						:(parse_cmd, '(arp-protect)\s+(\w+)\s+.*$', 1, 2),
"arp-protect_sub"                                               :(parse_sub, 'arp-protect\s+(\w+)\s+(.*$)', 1, 2),
"auto-tftp"							:(parse_fw, '(auto-tftp)\s+(.*$)', 1, 2),
"clock_key"							:(parse_cmd, '(clock)\s+([\w\-]+)\s+.*$', 1, 2),
"clock_sub"                                                     :(parse_sub, 'clock\s+([\w\-]+)\s+(.*$)', 1, 2),
"copy_key"                                                      :(parse_cmd, '(copy)\s+([\w\-]+)\s+.*$', 1, 2),
"copy_sub"                                                      :(parse_sub, 'copy\s+([\w\-]+)\s+(.*$)', 1, 2),
"crypto_key"                                                    :(parse_cmd, '(crypto)\s+([\w\-]+)\s+.*$', 1, 2),
"crypto_sub"                                                    :(parse_sub, 'crypto\s+([\w\-]+)\s+(.*$)', 1, 2),
"dhcp-snooping_key"                                             :(parse_cmd, '(dhcp-snooping)\s+([\w\-]+)\s+.*$', 1, 2),
"dhcp-snooping_sub"                                             :(parse_sub, 'dhcp-snooping\s+([\w\-]+)\s+(.*$)', 1, 2),
"dhcp-relay_key"                                                :(parse_cmd, '(dhcp-relay)\s+([\w\-]+)\s+.*$', 1, 2),
"dhcp-relay_sub"                                                :(parse_sub, 'dhcp-relay\s+([\w\-]+)\s+(.*$)', 1, 2),
"fault-finder"							:(parse_fw, '(fault-finder)\s+(.*$)', 1, 2),
"fault-finder sensitivity"					:(parse_fw, '(fault-finder sensitivity)\s+(.*$)', 1, 2),
"connection-rate-filter_key"					:(parse_cmd, '(connection-rate-filter)\s+(\w+)\s+.*$', 1, 2),
"connection-rate-filter_key"                                    :(parse_sub, 'connection-rate-filter\s+(\w+)\s+(.*$)', 1, 2),
"console_key"							:(parse_cmd, '(console)\s+([\w\-]+)\s+.*$', 1, 2),
"console_sub"                                                   :(parse_sub, 'console\s+([\w\-]+)\s+(.*$)', 1, 2),
"filter_key"                                                    :(parse_cmd, '(filter)\s+([\w\-]+)\s+.*$', 1, 2),
"filter_sub"                                                    :(parse_sub, 'filter\s+([\w\-]+)\s+(.*$)', 1, 2),
"igmp"								:(parse_fw, '(igmp delayed-flush)\s+(\d+)', 1, 2),
"igmp-proxy-domain"						:(parse_fw, '(igmp-proxy-domain domain-name)\s+(.*$)', 1, 2),
"link-keepalive-interval"					:(parse_fw, '(link-keepalive interval)\s+(\d+)', 1, 2),
"link-keepalive-retries"                                        :(parse_fw, '(link-keepalive retries)\s+(\d+)', 1, 2),
#"version"							:(parse_fw, ';\s\w+\-.*\#(.*)', 1, 2),
"hostname"							:(parse_fw, '(hostname)\s+\"(.*)', 1, 2),
"timezone"							:(parse_fw, 'time (timezone) (.*)', 1, 2),
"dalite-rule"							:(parse_fw, 'time (daylight-time-rule) (.*)', 1, 2),
"IP access-list"						:(parse_fw, '(ip access-list extended) (.*)', 1, 2),
"link-test_key"                                                 :(parse_cmd, '(link-test)\s+(\w+)\s+.*$', 1, 2),
"link-test_sub"                                                 :(parse_sub, 'link-test\s+(\w+)\s+(.*$)', 1, 2),
"loop-protect_key"						:(parse_cmd, '(loop-protect)\s+([\w\-]+)\s+.*$', 1, 2),
"loop-protect_sub"                                              :(parse_sub, 'loop-protect\s+([\w\-]+)\s+(.*$)', 1, 2),
"snmp"								:(parse_fw, 'snmp-server community "(\w+)"\s(.*)', 1, 2),
"spanning-tree"							:(parse_fw, '(spanning-tree\s+\d)\s+(.*)', 1, 2),
"telnet"							:(parse, '(no)?\s*(telnet (?:server|client))', 2, 1),
"vlan"								:(parse_fw, '(vlan\s+\d+)\s+(.+$)', 1, 2),
"vlan_key"                                                      :(parse_cmd, '(vlan)\s+(\d+)', 1, 2),
"vlan_sub"							:(parse_sub, '\s+(\w+)\s+(.*$)', 1, 2),
"interface"							:(parse_cmd, '(interface\s+\d+)\s+(.+$)', 1, 2),
"interface_key"							:(parse_cmd, '(interface)\s+(\d+)', 1, 2),
"interface_sub"							:(parse_sub, '\s+(\w+)\s+(.*$)', 1, 2),
"snmp-server_key"						:(parse_cmd, '(snmp-server)\s+(\w+)\s+.*$', 1, 2),
"snmp-server_sub"						:(parse_sub, 'snmp-server\s+(\w+)\s+(.*$)', 1, 2),
"mirror_key"							:(parse_cmd, '(mirror)\s+(\d|\w+)\s+.*$', 1, 2),
"mirror_sub"							:(parse_sub, 'mirror\s+(\d|\w+)\s+(.*$)', 1, 2),
"spanning-tree_key"						:(parse_cmd, '(spanning-tree)\s+(\d|\w+)\s+.*$', 1, 2),
"spanning-tree_sub"						:(parse_sub, 'spanning-tree\s+(\d|\w+)\s+(.*$)', 1, 2),
"lldp_key"							:(parse_cmd, '(lldp)\s+([\w\-]+)\s+.*$', 1, 2),
"lldp_sub"							:(parse_sub, 'lldp\s+([\w\-]+)\s+(.*$)', 1, 2),
"timesync"							:(parse_fw,  '(timesync)\s+(\w+)', 1, 2),
"mac-age-time"							:(parse_fw,  '(mac-age-time)\s+(\d+)', 1, 2),
"max-vlans"							:(parse_fw,  '(max-vlans)\s+(\d+)', 1, 2),
"mirror-port"							:(parse_fw,  '(mirror-port)\s+(.*$)', 1, 2),
"module"							:(parse_fw,  '(module \d+ type)\s+(.*$)', 1, 2),
"port-security_key"						:(parse_cmd, '(port-security\s+[\w\d]+)\s+([\w\-]+)\s+.*$', 1, 2),
"port-security_sub"						:(parse_sub, 'port-security\s+[\w\d]+\s+([\w\-]+)\s+(.*$)', 1, 2),
"qos_key"                          	                        :(parse_cmd, '(qos)\s+([\w\-]+)\s+.*$', 1, 2),
"qos_sub"                               	                :(parse_sub, 'qos\s+([\w\-]+)\s+(.*$)', 1, 2),
"radius-server_key"                                             :(parse_cmd, '(radius-server)\s+([\w\-]+)\s+.*$', 1, 2),
"radius-server_sub"                                             :(parse_sub, 'radius-server\s+([\w\-]+)\s+(.*$)', 1, 2),
"repeat"							:(parse_fw,  '(repeat \w+)\s+(.*$)', 1, 2),
"router_key"                                                    :(parse_cmd, '(router)\s+(\w+)\s+.*$', 1, 2),
"router_sub"                                                    :(parse_sub, 'router\s+(\w+)\s+(.*$)', 1, 2),
"snmpv3_key"                                                    :(parse_cmd, '(snmpv3)\s+([\w\-]+)\s+.*$', 1, 2),
"snmpv3_sub"                                                    :(parse_sub, 'snmpv3\s+([\w\-]+)\s+(.*$)', 1, 2),
"sntp"								:(parse_fw,  '(sntp \w+)\s+(.+$)', 1, 2),
"stack"								:(parse_fw,  '(stack [\w\-]+)\s+(.*$)', 1, 2),
"static-mac_vlan"						:(parse_fw,  '(static-mac [\w\d]+ vlan)\s+(.*$)', 1, 2),
"static-mac_interface"                                          :(parse_fw,  '(static-mac [\w\d]+ interface)\s+(.*$)', 1, 2),
"tacacs-server_key"						:(parse_cmd, '(tacacs-server)\s+(\w+)\s+.*$', 1, 2),
"tacacs-server_sub"                                             :(parse_sub, 'tacacs-server\s+(\w+)\s+(.*$)', 1, 2),
"trunk"								:(parse_fw,  '(trunk\s+[\w\d]+)\s+(.*$)', 1, 2),

}

