import os
import collections
from rc import SEPERATOR, APPLY_COLOR, WARN_PRE, KEY_CHAR
from rc import VON_BASE_PATH, VON_INDEX_PATH, VON_CACHE_PATH
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
					print WARN_PRE, "Index corrupted, reading fresh..."
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

class Problem:
	bodies = []         # statement, sol, comments, ...
	desc = ""           # e.g. "Fiendish inequality"
	source = ""         # used as problem ID, e.g. "USAMO 2000/6"
	tags = []           # tags for the problem
	path = ""           # path to problem TeX file
	def __init__(self, path, **kwargs):
		self.path = path
		for key in kwargs:
			setattr(self, key, kwargs[key])

	@property
	def state(self):
		return self.bodies[0]
	def __repr__(self):
		return "({p.source}) {p.state}".format(p=self)

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
		s = ""
		if self.i is not None:
			s += APPLY_COLOR("BOLD_RED", "[" + KEY_CHAR + str(self.i) + "]")
			s += " \t"
		s +=  APPLY_COLOR("BOLD_BLUE", "(" + self.source + ")")
		s += " "
		s +=  self.desc
		return s
	@property
	def entry(self):
		print WARN_PRE, "sketchy af"
		return self

def makeProblemFromPath(path):
	# Creates a problem instance from a source, without looking at Index
	with open(path) as f:
		text = ''.join(f.readlines())
	x = text.split(SEPERATOR)
	data = yaml.load(x[0])
	data['bodies'] = x[1:]
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

def getEntryByCacheNum(i):
	with pickleDict(VON_CACHE_PATH) as cache:
		return cache[i]

def getEntryBySource(source):
	with pickleDict(VON_INDEX_PATH) as index:
		if not source in index:
			return None
		path = index.get(source).path
	return makeProblemFromPath(path)

def getEntryByKey(key):
	# TODO this shouldn't actually be in mode, but blah
	if key[0] == KEY_CHAR:
		return getEntryByCacheNum(i = int(key[1:]))
	else:
		return getEntryBySource(source = key)

def addProblemByFileContents(path, text):
	with open(path, 'w') as f:
		print >>f, out_text
	print "Wrote to", path
	# Now update cache
	p = model.makeProblemFromPath(path)
	model.addProblemToIndex(p)

def runSearch(tags, terms, set_cache = True):
	def _matches(entry):
		return all([entry.hasTag(t) for t in tags]) \
				and all([entry.hasTerm(t) for t in terms])
	with pickleDict(VON_INDEX_PATH) as index:
		result = [entry for source, entry in index.iteritems() if _matches(entry)]
	if set_cache:
		with pickleList(VON_CACHE_PATH, 'w') as cache:
			cache.set(result)
	return result

# A certain magical Index~ <3

def addEntryToIndex(entry):
	with pickleDict(VON_INDEX_PATH, 'w') as index:
		index[entry.source] = entry

def updateEntryByProblem(old, new):
	with pickleDict(VON_INDEX_PATH, 'w') as index:
		if old.source != new.source:
			del index[old.source]
		index[new.source] = new.entry
		index[new.source].i = old.i
	return index[new.source]

def addProblemToIndex(problem):
	with pickleDict(VON_INDEX_PATH, 'w') as index:
		p = problem
		index[p.source] = p.entry

def setEntireIndex(d):
	with pickleDict(VON_INDEX_PATH, 'w') as index:
		index.set(d)

def rebuildIndex():
	d = {}
	for p in getAllProblems():
		if p.source in d:
			print APPLY_COLOR("RED", "Duplicate problem ")+p.source+" is being skipped..."
		else:
			d[p.source] = p.entry
	setEntireIndex(d)
