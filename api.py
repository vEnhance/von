# For importing von externally
from . import model

# For Pickle...
import sys
sys.modules['model'] = model

index = model.VonIndex().store # get the underlying dict

def has(source):
	"""Checks whether a given source exists in database"""
	return source in index

def has_solution(source):
	"""Checks whether a given source exists in database AND has a solution"""
	if not has(source): return False
	entry = index[source]
	return len(entry.full.bodies) > 1

def get(source):
	"""Returns the full data for a given source"""
	entry = index[source]
	return entry.full

def get_statement(source):
	"""Returns just the problem statement for a given source"""
	return get(source).bodies[0]

def get_solution(source):
	"""Returns just the solution for a given source (asserts existence)"""
	bodies = get(source).bodies
	assert len(bodies) > 1, "%s has no solution" % source
	return bodies[1]
