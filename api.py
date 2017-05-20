# For importing von externally
import model

# For Pickle...
import sys
sys.modules['model'] = model

index = model.VonIndex().store # get the underlying dict

def has(source):
	return source in index

def get(source):
	entry = index[source]
	return entry.full

def getStatement(source):
	entry = index[source]
	return entry.full.bodies[0]

def getSolution(source):
	entry = index[source]
	bodies = entry.full.bodies
	assert len(bodies) > 1, "%s has no solution" % source
	return bodies[1]
