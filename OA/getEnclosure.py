#!/usr/bin/env python
'''
Function of the code is Connect to enclosure parallel and run the passing argument command
How to Run:
	python -W ignore get_enclosure.py <input file>
For example:
	python -W ignore get_enclosure.py input.csv
'''

import time
import argparse
import sys,csv,os
import paramiko,threading,datetime
from threading import Thread

command = '''show config
show firmware summary csv
'''

DIR_PATH=os.path.dirname(os.path.realpath(__file__))

def connect_enclosure (hostname,username,password,command, outdir):
	port = 22

	if not os.path.exists(outdir):
		os.makedirs(outdir)
	try:
		client = paramiko.SSHClient()
		client.load_system_host_keys()
		client.set_missing_host_key_policy(paramiko.WarningPolicy())

		print " Connecting to the host %r "%(hostname )

		client.connect(hostname, port=port, username=username, password=password)

		stdin, stdout, stderr = client.exec_command(command)
		cmd=command.replace('"','').replace(' ','')

		out_file = open (outdir + time.strftime("%Y-%m-%d") + '_OA_' + hostname + '.txt','w')
		out_file.write(stdout.read())
		out_file.close()

	finally:
		client.close()

def get_args():
	# Assign description to the help doc
	parser = argparse.ArgumentParser(
				description='Script to get OA enclosure information')
	# Add arguments
	parser.add_argument('-i', '--inputcsv', type=str, help='Input CSV that contains the OA login credentials. Format : <IP address>,<UserID>,<Password>', required=True)
	parser.add_argument('-o', '--outdir', type=str, help='Output Directory in which the output files are generated', default='', required=False)
	
	args = parser.parse_args()

	# Assign args to variables
	inputcsv = args.inputcsv

	if os.path.isabs(args.outdir):
		outdir = args.outdir + '/'
	else:
		outdir = DIR_PATH + '/' + args.outdir + '/'

	return inputcsv, outdir

if __name__ == '__main__':

	inputcsv, outdir = get_args()

	f = open(inputcsv, 'rt')
	try:
		reader = csv.reader(f)
		threads = []
		for row in reader:
			t = Thread(target = connect_enclosure, args=(row[0], row[1], row[2], command, outdir))
			t.start()
	finally:
		f.close()
