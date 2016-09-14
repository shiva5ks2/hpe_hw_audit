#!/usr/bin/env python

import os, sys, types
import argparse, re
import vccmds

import pprint

import xlsxwriter, pprint

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
			if len(o) == 2 and isinstance(o[0], tuple) and o[0][0] in ['add enet-connection', 'add fcoe-connection']:
				past_reps, past_line_no_list = self.past_dict[o]
				cur_reps, cur_line_no_list = self.current_dict[o]
				# Here, the key itself has the value.
				# So, we only check if the reps are different.
				if past_reps != cur_reps:
					l_o.append(o)
			else:
				past_line_num, past_line_val = self.past_dict[o]
				cur_line_num, cur_line_val = self.current_dict[o]
				if past_line_val != cur_line_val:
					l_o.append(o)
		return set(l_o)

	def unchanged(self):
		return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

def drop_keys(dict, list_of_keys):
	for i in list_of_keys:
		if dict.has_key(i):
			del dict[i]

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
			if not line.startswith('#') and line.strip():
				in_dict[line_num] = line.strip()
				line_num = line_num + 1
	return

def populate_dict_by_key_val(in_dict_by_line, in_dict, config_type):
	for line_num, line_str in in_dict_by_line.iteritems():
		for key, (parse_option, context, parse_str, parse_key, parse_val) in vccmds.vccmds.iteritems():
			if callable(parse_option):
				parse_option(line_num, line_str, parse_str, parse_key, parse_val, in_dict, config_type, context)
	return

def writeOutput(added, removed, changed, workbook, input_file_name):
	# added - in infile_dict only
	# removed - in golden_dict only
	# changed - exists in boths dicts but with different values
	global output_xls

	output_list = []
	#print added, removed, changed

	for o in added:
		if len(o) == 2 and isinstance(o[0], tuple) and o[0][0] in ['add enet-connection', 'add fcoe-connection']:
			reps, line_num_list = infile_dict[o]
			for line_num in line_num_list:
				output_list.append( (line_num, 'Added enet/fcoe connection', '', infile_dict_by_line[line_num]) )
			continue

		line_num, line_val = infile_dict[o]
		if (line_num, '', infile_dict_by_line[line_num]) not in output_list:
			output_list.append( (line_num, 'Added ' + o[-1], '', infile_dict_by_line[line_num]) )
	for o in removed:
		if len(o) == 2 and isinstance(o[0], tuple) and o[0][0] in ['add enet-connection', 'add fcoe-connection']:
			reps, line_num_list = golden_dict[o]
			for line_num in line_num_list:
				output_list.append( (line_num, 'Removed enet/fcoe connection', golden_dict_by_line[line_num], '') )
			continue

		line_num, line_val = golden_dict[o]
		if (line_num, golden_dict_by_line[line_num], '') not in output_list:
			output_list.append( (line_num, 'Removed ' + o[-1], golden_dict_by_line[line_num], '') )
	for o in changed:
		if len(o) == 2 and isinstance(o[0], tuple) and o[0][0] in ['add enet-connection', 'add fcoe-connection']:
			i_reps, i_line_num_list = infile_dict[o]
			g_reps, g_line_num_list = golden_dict[o]

			# There is a difference in reps only
			reps = i_reps - g_reps
			if reps > 0:
				# Added
				for line_num in i_line_num_list[-reps:]:
					output_list.append( (line_num, 'Added enet/fcoe connection', '', infile_dict_by_line[line_num]) )
			else: # Has to be less than 0.
				# Removed
				for line_num in g_line_num_list[reps:]:
					output_list.append( (line_num, 'Removed enet/fcoe connection', golden_dict_by_line[line_num], '') )

			continue

		i_line_num, i_line_val = infile_dict[o]
		g_line_num, g_line_val = golden_dict[o]
		if (i_line_num, golden_dict_by_line[g_line_num], infile_dict_by_line[i_line_num]) not in output_list:
			output_list.append( (i_line_num, 'Changed ' + o[-1], golden_dict_by_line[g_line_num], infile_dict_by_line[i_line_num]) )

	base_fname = os.path.basename(input_file_name)
	if not output_list:
		# No change from golden configuration
		print "VC configuration file %s is compliant." % base_fname
		return 0 # No worksheet added

	sorted_output = sorted(output_list, key=lambda x: x[0])
	if output_xls:
		# Check if worksheet with domain_name is already added?
		# If yes, then just give base_fname as worksheet name
		m=re.match('(.+)\.txt', base_fname)
		if m:
			base_fname = m.group(1)

		if vccmds.domain_name:
			for ws in workbook.worksheets():
				if ws.get_name() == vccmds.domain_name:
					# Change the domain name to file name
					vccmds.domain_name = base_fname
					break
			worksheet = workbook.add_worksheet(vccmds.domain_name)
		else:
			worksheet = workbook.add_worksheet(base_fname)

		bold = workbook.add_format({'bold': True})

		worksheet.write('B1', 'Golden Configuration', bold)
		worksheet.write('C1', 'Current Configuration', bold)
		worksheet.write('A2', 'Attribute change', bold)

		row = 2
		col = 0
		for (l_num, change, g_line, i_line) in sorted_output:
			worksheet.write(row, col, change)
			worksheet.write(row, col+1, g_line)
			worksheet.write(row, col+2, i_line)
			row += 1
	else:
		pp.pprint( sorted_output )
	return 1 # 1 worksheet added

def get_args():
	# Assign description to the help doc
	parser = argparse.ArgumentParser(
		description='Script compares two VC files')
	# Add arguments
	parser.add_argument('-g', '--golden', type=str, help='VC file from golden configuration', required=True)

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-i', '--infile'  , type=str, help='VC file to compare with')
	group.add_argument('-f', '--filelist', type=str, help='File that contains list of VC config file paths')

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
	populate_dict_by_key_val(golden_dict_by_line, golden_dict, vccmds.golden_cfg)

	# Drop the domain name from the golden dict
	if golden_dict.has_key( ('set domain', 'Name') ):
		drop_keys(golden_dict, vccmds.drop_keys_list)

	if output_xls:
		workbook = xlsxwriter.Workbook(output_xls)

	total_cnt = 0 # If XLSX, no. of worksheets added
	for i in input_files:
		infile_dict_by_line.clear()
		infile_dict.clear()
		vccmds.domain_name = ''

		populate_dict_by_line(i, infile_dict_by_line)
		populate_dict_by_key_val(infile_dict_by_line, infile_dict, vccmds.input_cfg)
		if infile_dict.has_key( ('set domain', 'Name') ):
			(unused, vccmds.domain_name) = infile_dict[('set domain', 'Name')]

		drop_keys(infile_dict, vccmds.drop_keys_list)

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
			print "All VC configurations compliant. Removing empty XLSX file."
			os.remove(output_xls)
