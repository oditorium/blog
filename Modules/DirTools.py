"""directory tools


read - read a directory tree and return directories, files, tree as tuples
filter - filter a list based on a regex
decorate - decorate a list based on a regex
counter - a counter object for use in list comprehensions

DEPENDENCIES
	os
	string
	re

COPYRIGHT AND LICENSE

	copyright (c) Stefan LOESCH / oditorium 2014
	Licensed under AGPL


"""
import os
import string
import re

__version__ = "0.1a"
def read (path=None, decorated=True):
	""" read out directory structure of `path` and return it as a tuple
	
	PARAMETERS

		path - the path where to start the walk (default: `.`)
		decorated - if True, the dir names are returned as well as the index

	RETURNS
		(dirs, files, tree)

		dirs - tuple of dirs, in order traversed by walk
		files - tuple of tuples (filename, dir_ix) where dir_ix is index in dirs
		tree - tuple of tuples (dir_ix1, dir_ix2, ...) where dir_ix1... are subdirs
	"""

	if path == None: path = "."
	path = path.rstrip("/")


	dirs_and_files = list(os.walk(path))
	dirs = []
	files = []
	for df in dirs_and_files:
		dir_ix = len(dirs)
		dirs.append( df[0] )
		for f in df[2]:
			files.append( (f, dir_ix) )
	
	tree = []
	#for df in dirs_and_files:
	for df in []:
		parent_dir = df[0]
		parent_dir_ix = dirs.index(parent_dir)
		tree.append(tuple((dirs.index(parent_dir+"/"+dir)) for dir in df[1]))

	if decorated:
		files = ( (x[0], x[1], dirs[x[1]]) for x in files)

	return tuple(( 
		tuple(dirs),
		tuple(files),
		tuple(tree)))

		
def filter (list0, regex, position=0, invert=False, ignorecase=False):
	"""filters an array-like tuple according to a regex 
	
	PARAMETERS
		list0 - the list to be filtered (any iterable)
		regex - the regular expression
		position - to which `column` the regex should be applied
		invert - if True, retain iff regex does _not_ match
		nocase - if True, case insensitive matching (regex must be all lowercase)
	
	RETURNS
		the filtered list (as a generator expression)
	"""
	
	if ignorecase:
		lc = lambda x: str(x).lower()
	else:	
		lc = lambda x: x
	
	if invert == False:
		return ( item for item in list0 if re.match(regex, lc(item[position])) )
	else:
		return ( item for item in list0 if not re.match(regex, lc(item[position])) )


def decorate (list0, regex, position=0, no_match_val=None, filter=False):
	"""decorates an array-list list (ie adds columns) based on regex
	
	for each of the rows, applies the regex to the list (at `position`)
	and adds the resulting groups() array as _one_ additional column
	(that in itself can be a list if capturing groups are present).
	If there is no match, `no_match_val` is used instead
	
	PARAMETERS
	
		list0 - the list to be filtered (any iterable)
		regex - the regular expression
		position - to which `column` the regex should be applied
		no_match_val - what value should be returned in case of no match
		filter - if True, only matching rows are returned
	
	RETURNS
		the decorated list (as a generator expression)	
	"""
	
	def regx(regex, s, no_match_val=None):
		m = re.match(regex, s)
		if m == None: return no_match_val
		return m.groups()
	
	if filter == False:
		return (  tuple(item) + ( regx(regex, item[position], no_match_val) , )   for item in list0  )

	else:	
		list1 = (  tuple(item) + ( regx(regex, item[position], None) , )   for item in list0  )
		return ( item for item in list1 if item[-1] != None )

	
class counter()	:
	"""counter to be used eg in list comprehensions to detect changes and make items unique
	
	EXAMPLE
		c = dirtools.counter()	
		l0 = (x for x in range(10) for y in range(3))
		l1 = list( (x, c.n(x)) for x in l0)
		print (l1)
		
		--> 
		l0 == [0, 0, 0, 1, 1, 1, 2,...]
		l1 == [(0,0), (0,1), (0,2), (1,0), ...]
		
	"""
	def __init__(self, start=None):
		self.last = start
		self.nval = 0
	
	def n(self, current=None):
		"""execute a counter tick event
	
		if `current` equals the last call's `current` then increment the counter,
		otherwise set the counter to zero; return the counter
		"""
		if current != self.last:
			self.last = current
			self.nval = 0
		else:
			self.nval += 1
		
		return self.nval
		