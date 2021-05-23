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

def get_index(source, brave = False):
	"""Returns the index entry for a given source"""
	entry = index[source]
	assert brave or not entry.secret
	return entry

def get(source, brave = False):
	"""Returns the full data for a given source"""
	entry = get_index(source, brave)
	return entry.full

def get_statement(source, brave = False):
	"""Returns just the problem statement for a given source"""
	return get(source, brave).bodies[0]

def get_solution(source, brave = False):
	"""Returns just the solution for a given source (asserts existence)"""
	bodies = get(source, brave).bodies
	assert len(bodies) > 1, f"{source} has no solution"
	return bodies[1]
