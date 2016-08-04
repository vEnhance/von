import os
from rc import SEPERATOR, VON_BASE_PATH, APPLY_COLOR, VON_INDEX_NAME
import yaml

INDEX_PATH = os.path.join(VON_BASE_PATH, VON_INDEX_NAME)

global CACHE # meow
if os.path.isfile(INDEX_PATH):
	with open(INDEX_PATH) as f:
		CACHE = yaml.load(f)
else:
	CACHE = {}

class Problem:
	bodies = []         # statement, sol, comments, ...
	desc = ""           # e.g. "Fiendish inequality"
	source = ""         # used as problem ID, e.g. "USAMO 2000/6"
	tags = []           # tags for the problem

	def __init__(self, **kwargs):
		for key in kwargs:
			setattr(self, key, kwargs[key])

	@property
	def state(self):
		return self.bodies[0]

	def __repr__(self):
		return "({p.source}) {p.state}".format(p=self)


def readProblem(text):
	x = text.split(SEPERATOR)
	data = yaml.load(x[0])
	data['bodies'] = x[1:]
	return Problem(**data)

def getAllProblems():
	# TODO: this is expensive
	ret = []

	for root, _, filenames in os.walk(VON_BASE_PATH):
		for fname in filenames:
			if not '.tex' in fname: continue
			with open(os.path.join(root, fname)) as f:
				ret.append(readProblem(''.join(f.readlines())))
	return ret

def addCache(problem):
	p = problem
	CACHE[p.source] = { 'desc' : p.desc, 'tags' : p.tags }

def writeCache():
	with open(INDEX_PATH, 'w') as f:
		print >>f, yaml.dump(CACHE)

def rebuildCache():
	CACHE.clear()
	for p in getAllProblems():
		if p.source in CACHE:
			print APPLY_COLOR("RED", "Duplicate problem ")+p.source+" is being skipped..."
		else:
			CACHE[p.source] = { 'desc' : p.desc, 'tags' : p.tags }
	writeCache()

if __name__ == "__main__":
	rebuildCache()
