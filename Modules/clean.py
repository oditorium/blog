#!/usr/local/bin/python3

import os
import sys
import string
import dirtools
import argparse


def remove(files, condition, invert=False, print_commands=True, ignorecase=False):
	""" remove the files that match a (regex) condition
	"""
	
	files = dirtools.filter(files, condition, invert=invert, ignorecase=ignorecase)
	
	if print_commands:
		for f in files:
			print ("rm '"+f[2] + "/" + f[0]+"'")
	

generated_files_regex = "(\.DS_Store|Thumbs.db)"

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="""clean up directories; this script removes a 
		number of generated files from the directory structure, notably .DS_Store and Thumbs.db""")
	parser.add_argument('-d', '--show-dirs', action='store_true', help='show directories and exit')
	parser.add_argument('-f', '--show-files', action='store_true', help='show files and exit (names only)')
	parser.add_argument('-ff', '--show-full-files', action='store_true', help='show files and exit (full path)')
	parser.add_argument('-y', '--dry-run', action='store_true', help='do not actually perform the action')
	parser.add_argument('-q', '--quiet', action='store_true', help='do not print actions')
	parser.add_argument('path', action='store', type=str, nargs='?', default='.', help='root of the directory structure to be clean')
	args = parser.parse_args()
	
	path = args.path
	quiet = args.quiet
	dry_run = args.dry_run
	
	dirs,files,tree = dirtools.read(path)
	
	if args.show_dirs:
		for d in dirs:
			print (d)
		exit()
		
	if args.show_files:
		for f in files:
			print (f[0])
		exit()

	if args.show_full_files:
		for f in files:
			print (f[2] + "/" + f[0])
		exit()
	
	remove (files, generated_files_regex)
	#remove (files, '(\.ds_store|thumbs.db)', ignorecase=True)
	
		

	