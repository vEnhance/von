import os
import collections
from rc import SEPERATOR, VON_BASE_PATH, APPLY_COLOR, VON_INDEX_NAME
import yaml

VON_INDEX_PATH = os.path.join(VON_BASE_PATH, VON_INDEX_NAME)

class yamlOpen(collections.MutableMapping):
	def __init__(self, path, mode = 'r'):
		self.path = path
		self.mode = mode
		with open(self.path) as f:
			self.store = yaml.load(''.join(f.readlines()))
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		if self.mode == 'w':
			with open(self.path, 'w') as f:
				print >>f, yaml.dump(self.store)
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


def makeProblemFromText(path, text):
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
				ret.append(makeProblemFromText(path, ''.join(f.readlines())))
	return ret

def addToCache(path, problem):
	with yamlOpen(VON_INDEX_NAME, 'w') as index:
		p = problem
		index[p.source] = { 'desc' : p.desc, 'tags': p.tags, 'path' : path }

def writeCache(d):
	with yamlOpen(VON_INDEX_PATH, 'w') as index:
		index.set(d)

def rebuildCache():
	d = {}
	for p in getAllProblems():
		if p.source in d:
			print APPLY_COLOR("RED", "Duplicate problem ")+p.source+" is being skipped..."
		else:
			d[p.source] = { 'desc' : p.desc, 'tags' : p.tags, 'path' : p.path}
	writeCache(d)

if __name__ == "__main__":
	rebuildCache()
