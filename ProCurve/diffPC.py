#!/usr/bin/env python

import os, sys, types
import argparse, re
import pccmds

import xlsxwriter, pprint
from operator import itemgetter, attrgetter

golden_dict_by_line = {} # This list is ordered by line number. Key = line number. Value = Line contents
infile_dict_by_line = {} # This list is ordered by line number. Key = line number. Value = Line contents

golden_dict = {}
infile_dict = {}

class DictDiffer(object):
	"""
	Calculate the difference between two dictionaries as:
	(1) items only in current config
	(2) items only in golden/past config
	(3) keys same in both but changed values
	(4) keys same in both and unchanged values
	"""
	def __init__(self, current_dict, past_dict):
		self.current_dict, self.past_dict = current_dict, past_dict
		self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
		self.intersect = self.set_current.intersection(self.set_past)

	def added(self):
		return self.set_current - self.intersect

	def removed(self):
		return self.set_past - self.intersect

	def changed(self):
		l_o = []
		for o in self.intersect:
			past_line_num, past_line_val = self.past_dict[o]
			cur_line_num, cur_line_val = self.current_dict[o]
			if past_line_val != cur_line_val:
				l_o.append(o)
		return set(l_o)

	def unchanged(self):
		return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

def populate_list_of_files(in_file):
	list_of_files = []
	with open(in_file) as f:
		for line in f:
			if not line.startswith('#') and line.strip():
				filename = line.strip()
				if os.path.isfile(filename) == False:
					print filename + ": File does not exist"
				else:
					list_of_files.append(filename)
	return list_of_files

def populate_dict_by_line(in_file, in_dict):
	line_num = 1
	with open(in_file) as f:
		for line in f:
			#if not line.startswith('#') and line.strip():
			if not line.startswith('#') and line.rstrip():
				in_dict[line_num] = line
				line_num = line_num + 1
	return
import pdb
def populate_dict_by_key_val(in_dict_by_line, in_dict, config_type):
	for line_num, line_str in in_dict_by_line.iteritems():
		for key, (parse_option, parse_str, parse_key, parse_val) in pccmds.pccmds.iteritems():
			if callable(parse_option):
				parse_option(line_num, line_str, parse_str, parse_key, parse_val, in_dict)
	return

def writeOutput(added, removed, changed, workbook, input_file_name):
	# added - in infile_dict only
	# removed - in golden_dict only
	# changed - exists in boths dicts but with different values
	global output_xls

	output_list = []
	#print added, removed, changed

	for o in added:
		cmd_s = ''
		line_num, line_val = infile_dict[o]
		if isinstance(o, tuple) and len(o) >= 2:
			if re.search('\S', infile_dict_by_line[line_num]).start():
				cmd_l = list(o)
				cmd_s = " ".join(cmd_l[:2])
		output_list.append( ('Added', cmd_s, '', infile_dict_by_line[line_num]) )
	for o in removed:
		cmd_s = ''
		line_num, line_val = golden_dict[o]
		if isinstance(o, tuple) and len(o) >= 2:
			if re.search('\S', golden_dict_by_line[line_num]).start():
				cmd_l = list(o)
				cmd_s = " ".join(cmd_l[:2])
		output_list.append( ('Removed', cmd_s, golden_dict_by_line[line_num], '') )
	for o in changed:
		cmd_s = ''
		i_line_num, i_line_val = infile_dict[o]
		g_line_num, g_line_val = golden_dict[o]
		if isinstance(o, tuple) and len(o) >= 2:
			if re.search('\S', golden_dict_by_line[g_line_num]).start():
				cmd_l = list(o)
				cmd_s = " ".join(cmd_l[:2])
		output_list.append( ('Changed', cmd_s, golden_dict_by_line[g_line_num], infile_dict_by_line[i_line_num]) )

	base_fname = os.path.basename(input_file_name)
	if not output_list:
		# No change from golden configuration
		print "ProCurve configuration file %s is compliant." % base_fname
		return 0 # No worksheet added

	sorted_output = sorted(output_list, key=itemgetter(1))
	if output_xls:
		m=re.match('(.+)\.txt', base_fname)
		if m:
			base_fname = m.group(1)
		worksheet = workbook.add_worksheet(base_fname)

		bold = workbook.add_format({'bold': True})

		worksheet.write('B1', 'Sub-command for', bold)
		worksheet.write('C1', 'Value (Golden)', bold)
		worksheet.write('D1', 'Value (Current)', bold)

		row = 2
		col = 0
		for (change, subcmd_for, g_line, i_line) in sorted_output:
			worksheet.write(row, col, change)
			worksheet.write(row, col+1, subcmd_for)
			worksheet.write(row, col+2, g_line)
			worksheet.write(row, col+3, i_line)
			row += 1
	else:
		pp.pprint( sorted_output )
	return 1 # 1 worksheet added

def get_args():
	# Assign description to the help doc
	parser = argparse.ArgumentParser(
		description='Script compares two ProCurve files')
	# Add arguments
	parser.add_argument('-g', '--golden', type=str, help='ProCurve file from golden configuration', required=True)

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-i', '--infile'  , type=str, help='ProCurve file to compare with')
	group.add_argument('-f', '--filelist', type=str, help='File that contains list of ProCurve config file paths')

	parser.add_argument('-o', '--output', type=str, help='Output XLSX file in which the configuration differences are dumped', required=False)

	# Array for all arguments passed to script
	args = parser.parse_args()

	# Assign args to variables
	golden   = args.golden
	infile   = args.infile
	filelist = args.filelist
	output   = args.output

	# Return all variable values
	return golden, infile, filelist, output

if __name__ == "__main__":
	golden, infile, filelist, output_xls = get_args()

	# Pretty print for debug reasons
	pp = pprint.PrettyPrinter(indent=4)

	if os.path.isfile(golden) == False:
		print golden + ": File does not exist"
		sys.exit(1)

	input_files = []
	if infile:
		if os.path.isfile(infile) == False:
			print infile + ": File does not exist"
			sys.exit(1)
		else:
			input_files.append(infile)

	if filelist:
		if os.path.isfile(filelist) == False:
			print filelist + ": File does not exist"
			sys.exit(1)
		else:
			input_files = populate_list_of_files(filelist)

	populate_dict_by_line(golden, golden_dict_by_line)
	populate_dict_by_key_val(golden_dict_by_line, golden_dict, pccmds.golden_cfg)

	#pprint.pprint(golden_dict.keys())
	#sys.exit(1)

	if output_xls:
		workbook = xlsxwriter.Workbook(output_xls)

	total_cnt = 0 # If XLSX, no. of worksheets added
	for i in input_files:
		infile_dict_by_line.clear()
		infile_dict.clear()
		pccmds.rack_name = ''

		populate_dict_by_line(i, infile_dict_by_line)
		populate_dict_by_key_val(infile_dict_by_line, infile_dict, pccmds.input_cfg)

		d = DictDiffer(infile_dict, golden_dict)
		if output_xls:
			output_cnt = writeOutput(list(d.added() ), list(d.removed() ), list(d.changed() ), workbook, i)
			total_cnt += output_cnt
			
		else:
			output_cnt = writeOutput(list(d.added() ), list(d.removed() ), list(d.changed() ), None, i)

	if output_xls:
		workbook.close()
		if not total_cnt:
			# Remove empty XLSX
			print "All ProCurve configurations compliant. Removing empty XLSX file."
			os.remove(output_xls)
