from .rc import SEPERATOR, DIFFS
from .rc import VON_BASE_PATH, VON_INDEX_PATH, VON_CACHE_PATH
from . import view
import random
import functools

import os
import collections
import yaml
import pickle as pickle

from .strparse import demacro, toAOPS

def shortenPath(path):
	return os.path.relpath(path, VON_BASE_PATH)
def completePath(path):
	return os.path.join(VON_BASE_PATH, path)
def vonOpen(path, *args, **kwargs):
	return open(completePath(path), *args, **kwargs)

class pickleObj(collections.MutableMapping):
	def _initial(self):
		return None
	def __init__(self, path, mode='rb'):
		if not os.path.isfile(path) or os.path.getsize(path) == 0:
			self.store = self._initial()
		else:
			with vonOpen(path, 'rb') as f:
				self.store = pickle.load(f)
		self.path = path
		self.mode = mode
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		if self.mode == 'wb':
			with vonOpen(self.path, 'wb') as f:
				pickle.dump(self.store, f)
	def __getitem__(self, key):
		try:
			return self.store[key]
		except IndexError:
			raise IndexError("%s not a valid key" %key)
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
		for i in range(len(store)):
			store[i].i = i
		self.store = store

def VonIndex(mode = 'rb'):
	return pickleDict(VON_INDEX_PATH, mode)
def VonCache(mode = 'rb'):
	return pickleList(VON_CACHE_PATH, mode)

@functools.total_ordering
class GenericItem: # subclass to Problem, IndexEntry
	desc = ""           # e.g. "Fiendish inequality"
	source = ""         # used as problem ID, e.g. "USAMO 2000/6"
	tags = []           # tags for the problem
	path = ""           # path to problem TeX file
	i = None            # position in Cache, if any

	@property
	def n(self):
		return self.i + 1 if self.i is not None else None
	@property
	def diffvalue(self):
		for i, d in enumerate(DIFFS):
			if d in self.tags: return i
		return -1
	@property
	def diffstring(self):
		for i, d in enumerate(DIFFS):
			if d in self.tags: return d
		return "NONE"

	@property
	def sortkey(self):
		return (self.diffvalue, self.source)

	def __eq__(self, other):
		return self.sortkey == other.sortkey
	def __lt__(self, other):
		return self.sortkey < other.sortkey


class Problem(GenericItem):
	bodies = []         # statement, sol, comments, ...
	author = None       # default
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
	def entry(self):
		"""Returns an IndexEntry for storage in pickle"""
		return IndexEntry(source=self.source, desc=self.desc, author=self.author,
				tags=self.tags, path=self.path, i = self.i)
	@property
	def full(self):
		view.warn("sketchy af")
		return self

class IndexEntry(GenericItem):
	def __init__(self, **kwargs):
		for key in kwargs:
			if kwargs[key] is not None:
				setattr(self, key, kwargs[key])
	def hasTag(self, tag):
		return tag.lower() in [_.lower() for _ in self.tags]
	def hasTerm(self, term):
		blob = self.source + ' ' + self.desc
		if hasattr(self, 'author'): blob += ' ' + self.author
		return term.lower() in blob.lower() or term in self.tags
	def hasAuthor(self, name):
		if not hasattr(self, 'author'): return False
		haystacks = self.author.lower().strip().split(' ')
		return name.lower() in haystacks
	def hasSource(self, source):
		return source.lower() in self.source.lower()
	def __repr__(self):
		return self.source
	@property
	def secret(self):
		return 'SECRET' in self.source or 'secret' in self.tags
	@property
	def entry(self):
		view.warn("sketchy af")
		return self
	@property
	def full(self):
		p = makeProblemFromPath(self.path)
		p.i = self.i
		return p

def getcwd():
	true_dir = os.getcwd()
	if true_dir.startswith(VON_BASE_PATH):
		return os.path.relpath(true_dir, VON_BASE_PATH)
	else:
		return ''
def getCompleteCwd():
	return completePath(getcwd())

def makeProblemFromPath(path):
	# Creates a problem instance from a source, without looking at Index
	with vonOpen(path, 'r') as f:
		text = ''.join(f.readlines())
	x = text.split(SEPERATOR)
	data = yaml.load(x[0])
	if data is None:
		view.warn(path + " gave None for data")
		return None
	data['bodies'] = [_.strip() for _ in x[1:]]
	return Problem(path, **data)

def getAllProblems():
	ret = []
	for root, _, filenames in os.walk(VON_BASE_PATH):
		for fname in filenames:
			if not fname.endswith('.tex'): continue
			path = shortenPath(os.path.join(root, fname))
			p = makeProblemFromPath(path)
			if p is not None:
				ret.append(p)
	return ret

def getEntryByCacheNum(n):
	with VonCache() as cache:
		return cache[n-1]

def getEntryBySource(source):
	with VonIndex() as index:
		return index.get(source, None)

def getEntryByKey(key):
	# TODO this shouldn't actually be in model, but blah
	if key.isdigit():
		return getEntryByCacheNum(n = int(key))
	else:
		return getEntryBySource(source = key)

def addProblemByFileContents(path, text):
	with vonOpen(path, 'w') as f:
		print(text, file=f)
	view.log("Wrote to " + path)
	# Now update cache
	p = makeProblemFromPath(path)
	addProblemToIndex(p)
	return p

def viewDirectory(path):
	problems = []
	dirs = []
	for item_path in os.listdir(getCompleteCwd()):
		abs_item_path = os.path.join(getCompleteCwd(), item_path)
		if os.path.isfile(abs_item_path) and abs_item_path.endswith('.tex'):
			problems.append(makeProblemFromPath(abs_item_path))
		elif os.path.isdir(abs_item_path):
			dirs.append(item_path)
		else:
			pass # not TeX or directory
	dirs.sort()
	entries = [p.entry for p in problems]
	entries.sort()
	if len(entries) > 0:
		setCache(entries)
	return (entries, dirs)

def runSearch(terms = [], tags = [], sources = [], authors = [], \
		path = '', refine = False, alph_sort = False):
	def _matches(entry):
		return all([entry.hasTag(_) for _ in tags]) \
				and all([entry.hasTerm(_) for _ in terms]) \
				and all([entry.hasSource(_) for _ in sources]) \
				and all([entry.hasAuthor(_) for _ in authors]) \
				and entry.path.startswith(path)
	if refine is False:
		with VonIndex() as index:
			result = [entry for source, entry in index.items() if _matches(entry)]
	else:
		with VonCache() as cache:
			result = [entry for entry in cache if _matches(entry)]
	if alph_sort:
		result.sort(key = lambda e: e.source)
	else:
		result.sort()
	if len(result) > 0: setCache(result)
	return result

def augmentCache(*entries):
	with VonCache('wb') as cache:
		cache.set(cache.store + list(entries))
def setCache(entries):
	with VonCache('wb') as cache:
		cache.set(entries)
def clearCache():
	with VonCache('wb') as cache:
		cache.set([])
def readCache():
	with VonCache() as cache:
		return cache

# A certain magical Index~ <3

def addEntryToIndex(entry):
	with VonIndex('wb') as index:
		index[entry.source] = entry

def updateEntryByProblem(old_entry, new_problem):
	new_problem.i = old_entry.i
	new_entry = new_problem.entry
	
	with VonIndex('wb') as index:
		if old_entry.source != new_entry.source:
			del index[old_entry.source]
		index[new_entry.source] = new_entry
	with VonCache('wb') as cache:
		for i, entry in enumerate(cache):
			if entry.source == old_entry.source:
				new_entry.i = i
				cache[i] = new_entry
				break
		else:
			cache.set(cache.store + [new_entry])
	return index[new_entry.source]

def addProblemToIndex(problem):
	with VonIndex('wb') as index:
		p = problem
		index[p.source] = p.entry
		return index[p.source]

def setEntireIndex(d):
	with VonIndex('wb') as index:
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
