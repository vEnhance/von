import collections
import collections.abc
import functools
import json
import os
import pickle as pickle
import random

import yaml

from . import view
from .puid import inferPUID
from .rc import OTIS_EVIL_JSON_PATH, SEPERATOR, SORT_TAGS, VON_BASE_PATH, VON_CACHE_PATH, VON_INDEX_PATH  # NOQA


def shortenPath(path):
	return os.path.relpath(path, VON_BASE_PATH)


def completePath(path):
	return os.path.join(VON_BASE_PATH, path)


def vonOpen(path, *args, **kwargs):
	return open(completePath(path), *args, **kwargs)


class pickleObj(collections.abc.MutableMapping):
	def _initial(self):
		return {}

	def __init__(self, path, mode='rb'):
		if not os.path.isfile(path) or os.path.getsize(path) == 0:
			self.store = self._initial()
		else:
			with vonOpen(path, 'rb') as f:
				self.store = pickle.load(f)  # type: ignore
		self.path = path
		self.mode = mode

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		if self.mode == 'wb':
			with vonOpen(self.path, 'wb') as f:
				pickle.dump(self.store, f)  # type: ignore

	def __getitem__(self, key):
		try:
			return self.store[key]
		except IndexError:
			raise IndexError(f"{key} not a valid key")

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


def VonIndex(mode='rb'):
	return pickleDict(VON_INDEX_PATH, mode)


def VonCache(mode='rb'):
	return pickleList(VON_CACHE_PATH, mode)


@functools.total_ordering
class GenericItem:  # superclass to Problem, IndexEntry
	desc = ""  # e.g. "Fiendish inequality"
	source = ""  # used as problem ID, e.g. "USAMO 2000/6"
	tags: list[str] = []  # tags for the problem
	path = ""  # path to problem TeX file
	i = None  # position in Cache, if any
	author = None  # default
	hardness = None  # default
	url = None

	@property
	def n(self):
		return self.i + 1 if self.i is not None else None

	@property
	def sortvalue(self):
		for i, d in enumerate(SORT_TAGS):
			if d in self.tags:
				return i
		return -1

	@property
	def sortstring(self):
		for i, d in enumerate(SORT_TAGS):
			if d in self.tags:
				return d
		return "NONE"

	@property
	def sortkey(self):
		if type(self.hardness) == int:
			return (self.sortvalue, self.hardness, self.source)
		else:
			return (self.sortvalue, -1, self.source)

	def __eq__(self, other):
		return self.sortkey == other.sortkey

	def __lt__(self, other):
		return self.sortkey < other.sortkey


class Problem(GenericItem):
	bodies: list[str] = []  # statement, sol, comments, ...

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
		return IndexEntry(
			source=self.source,
			desc=self.desc,
			author=self.author,
			url=self.url,
			hardness=self.hardness,
			tags=self.tags,
			path=self.path,
			i=self.i
		)

	@property
	def full(self):
		view.warn("sketchy af")
		return self


class IndexEntry(GenericItem):
	def __init__(self, **kwargs):
		for key in kwargs:
			if kwargs[key] is not None:
				setattr(self, key, kwargs[key])

	# search things
	def hasTag(self, tag):
		return tag.lower() in [_.lower() for _ in self.tags]

	def hasTerm(self, term):
		blob = self.source + ' ' + self.desc
		if self.author is not None:
			blob += ' ' + self.author
		return (
			term.lower() in blob.lower() or term in self.tags or
			term.upper() in inferPUID(self.source)
		)

	def hasAuthor(self, name):
		if self.author is None:
			return False
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
		if p is not None:
			p.i = self.i
		return p


def getcwd():
	true_dir = os.getcwd()
	if true_dir.startswith(VON_BASE_PATH) and true_dir != VON_BASE_PATH:
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
	data = yaml.safe_load(x[0])
	if data is None:
		view.warn(path + " gave None for data")
		return None
	data['bodies'] = [_.strip() for _ in x[1:]]
	return Problem(path, **data)


def getAllProblems():
	ret = []
	for root, _, filenames in os.walk(VON_BASE_PATH):
		for fname in filenames:
			if not fname.endswith('.tex'):
				continue
			path = shortenPath(os.path.join(root, fname))
			p = makeProblemFromPath(path)
			if p is not None:
				ret.append(p)
	return ret


def getEntryByCacheNum(n):
	with VonCache() as cache:
		return cache[n - 1]


def getEntryBySource(source):
	with VonIndex() as index:
		return index.get(source, None)


def getEntryByKey(key):
	# TODO this shouldn't actually be in model, but blah
	if key.isdigit():
		return getEntryByCacheNum(n=int(key))
	else:
		return getEntryBySource(source=key)


def addProblemByFileContents(path, text):
	with vonOpen(path, 'w') as f:
		print(text, file=f)
	view.log("Wrote to " + path)
	# Now update cache
	p = makeProblemFromPath(shortenPath(path))
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
			pass  # not TeX or directory
	dirs.sort()
	entries = [p.entry for p in problems]
	entries.sort()
	if len(entries) > 0:
		setCache(entries)
	return (entries, dirs)


def runSearch(
	terms=[],
	tags=[],
	sources=[],
	authors=[],
	path='',
	refine=False,
	alph_sort=False,
	in_otis=None
):
	if in_otis is not None and OTIS_EVIL_JSON_PATH is not None:
		with open(OTIS_EVIL_JSON_PATH) as f:
			evil_json = json.load(f)
			otis_used_sources = evil_json.values()
	else:
		otis_used_sources = None

	def _matches(entry):
		if otis_used_sources is not None:
			_used = entry.source in otis_used_sources or entry.hasTag('waltz')
			if _used and in_otis is False:
				return False
			elif not _used and in_otis is True:
				return False

		return (
			all([entry.hasTag(_) for _ in tags]) and all([entry.hasTerm(_) for _ in terms]) and
			all([entry.hasSource(_) for _ in sources]) and
			all([entry.hasAuthor(_) for _ in authors]) and entry.path.startswith(path)
		)

	if refine is False:
		with VonIndex() as index:
			result = [entry for entry in index.values() if _matches(entry)]
	else:
		with VonCache() as cache:
			result = [entry for entry in cache if _matches(entry)]
	if alph_sort:
		result.sort(key=lambda e: e.source)
	else:
		result.sort()
	if len(result) > 0:
		setCache(result)
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
			fake_source = f"DUPLICATE {random.randrange(10**6, 10**7)}"
			view.error(p.source + " is being repeated, replacing with " + fake_source)
			p.source = fake_source
		d[p.source] = p.entry
	setEntireIndex(d)
