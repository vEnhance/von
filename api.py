# For importing von externally
import model

# For Pickle...
import sys
sys.modules['model'] = model

def get(source):
	entry = model.getEntryBySource(source)
	return None if entry is None else entry.full
