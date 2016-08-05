from rc import SEPERATOR, KEY_CHAR
from rc import VON_BASE_PATH, VON_INDEX_PATH, VON_CACHE_PATH
import view
import random

import os
import collections
import yaml
import cPickle as pickle

class pickleObj(collections.MutableMapping):
	def _initial(self):
		return None
	def __init__(self, path, mode='r'):
		if not os.path.isfile(path):
			self.store = self._initial()
		else:
			with open(path) as f:
				try:
					self.store = pickle.load(f)
				except:
					view.warn("Index corrupted, reading fresh...")
					self.store = self._initial()
		self.path = path
		self.mode = mode
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		if self.mode == 'w':
			with open(self.path, 'w') as f:
				pickle.dump(self.store, f)
	def __getitem__(self, key):
		return self.store[key]
	def __setitem__(self, key, value):
		self.store[key] = value
	def __delitem__(self, key):
		del self.store[key]
	def __iter__(self):
		return iter(self.store)
	def __len__(self):
		return len(self.store)
	def set(self, store):
		self.store = store

class pickleDict(pickleObj):
	def _initial(self):
		return {}
class pickleList(pickleObj):
	def _initial(self):
		return []
	def set(self, store):
		for i in xrange(len(store)):
			store[i].i = i
		self.store = store

def VonIndex(mode = 'r'):
	return pickleDict(VON_INDEX_PATH, mode)
def VonCache(mode = 'r'):
	return pickleList(VON_CACHE_PATH, mode)


class Problem:
	bodies = []         # statement, sol, comments, ...
	desc = ""           # e.g. "Fiendish inequality"
	source = ""         # used as problem ID, e.g. "USAMO 2000/6"
	tags = []           # tags for the problem
	path = ""           # path to problem TeX file
	i = None            # position in Cache, if any

	def __init__(self, path, **kwargs):
		self.path = path
		for key in kwargs:
			setattr(self, key, kwargs[key])

	@property
	def state(self):
		return self.bodies[0]
	def __repr__(self):
		return self.source

	@property
	def n(self):
		return self.i + 1 if self.i is not None else None
	@property
	def entry(self):
		"""Returns an IndexEntry for storage in pickle"""
		return IndexEntry(source=self.source, desc=self.desc, tags=self.tags, path=self.path)

class IndexEntry:
	desc = ""           # e.g. "Fiendish inequality"
	i = None            # position in Cache, if any
	def __init__(self, **kwargs):
		for key in kwargs:
			if kwargs[key] is not None:
				setattr(self, key, kwargs[key])
	def hasTag(self, tag):
		return tag in self.tags
	def hasTerm(self, term):
		return term.lower() in (self.source + ' ' + self.desc).lower()
	def __repr__(self):
		return self.source
	@property
	def entry(self):
		view.warn("sketchy af")
		return self
	@property
	def n(self):
		return self.i + 1 if self.i is not None else None
	@property
	def full(self):
		p = makeProblemFromPath(self.path)
		p.i = self.i
		return p

def makeProblemFromPath(path):
	# Creates a problem instance from a source, without looking at Index
	with open(path) as f:
		text = ''.join(f.readlines())
	x = text.split(SEPERATOR)
	data = yaml.load(x[0])
	data['bodies'] = [_.strip() for _ in x[1:]]
	return Problem(path, **data)

def getAllProblems():
	ret = []
	for root, _, filenames in os.walk(VON_BASE_PATH):
		for fname in filenames:
			if not '.tex' in fname: continue
			path = os.path.join(root, fname)
			with open(path) as f:
				ret.append(makeProblemFromPath(path))
	return ret

def getEntryByCacheNum(n):
	with VonCache() as cache:
		return cache[n-1]

def getEntryBySource(source):
	with VonIndex() as index:
		if not source in index:
			return None
		path = index.get(source).path
	return makeProblemFromPath(path)

def getEntryByKey(key):
	# TODO this shouldn't actually be in mode, but blah
	if key.startswith(KEY_CHAR):
		return getEntryByCacheNum(n = int(key[1:]))
	else:
		return getEntryBySource(source = key)

def addProblemByFileContents(path, text):
	with open(path, 'w') as f:
		print >>f, out_text
	view.log("Wrote to " + path)
	# Now update cache
	p = model.makeProblemFromPath(path)
	model.addProblemToIndex(p)

def viewDirectory(path):
	problems = []
	dirs = []
	for item_path in os.listdir(path):
		if os.path.isfile(item_path) and item_path.endswith('.tex'):
			problems.append(makeProblemFromPath(item_path))
		elif os.path.isdir(item_path):
			dirs.append(item_path)
		else:
			pass # not TeX or directory
	entries = [p.entry for p in problems]
	if len(problems) > 0:
		with VonCache('w') as cache:
			setCache(entries)
	return (entries, dirs)

def runSearch(tags, terms, path = VON_BASE_PATH, refine = False):
	def _matches(entry):
		return all([entry.hasTag(t) for t in tags]) \
				and all([entry.hasTerm(t) for t in terms]) \
				and entry.path.startswith(path)
	if refine is False:
		with VonIndex() as index:
			result = [entry for source, entry in index.iteritems() if _matches(entry)]
			augmentCache(result)
	else:
		with VonCache() as cache:
			result = [entry for entry in cache if _matches(entry)]
	return result

def augmentCache(entries):
	with VonCache('w') as cache:
		cache.set(cache.store + entries)
def setCache(entries):
	with VonCache('w') as cache:
		cache.set(entries)
def clearCache():
	with VonCache('w') as cache:
		cache.set([])
def readCache():
	with VonCache() as cache:
		return cache

# A certain magical Index~ <3

def addEntryToIndex(entry):
	with VonIndex('w') as index:
		index[entry.source] = entry

def updateEntryByProblem(old, new):
	with VonIndex('w') as index:
		if old.source != new.source:
			del index[old.source]
		index[new.source] = new.entry
		index[new.source].i = old.i
	return index[new.source]

def addProblemToIndex(problem):
	with VonIndex('w') as index:
		p = problem
		index[p.source] = p.entry
		return index[p.source]

def setEntireIndex(d):
	with VonIndex('w') as index:
		index.set(d)

def rebuildIndex():
	d = {}
	for p in getAllProblems():
		if p.source in d:
			fake_source = "DUPLICATE " + str(random.randrange(1e6, 1e7))
			view.error(p.source + " is being repeated, replacing with " + fake_source)
			p.source = fake_source
		d[p.source] = p.entry
	setEntireIndex(d)
