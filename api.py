# For importing von externally
from . import model
from .puid import inferPUID

# For Pickle...
import sys

sys.modules["model"] = model

index = model.VonIndex().store  # get the underlying dict

source_to_puid_lookup = {inferPUID(source): source for source in index}


def has(source: str):
    """Checks whether a given source exists in database"""
    return source in index


def has_solution(source: str):
    """Checks whether a given source exists in database AND has a solution"""
    if not has(source):
        return False
    entry = index[source]
    return len(entry.full.bodies) > 1


def get_index(source: str, brave=False):
    """Returns the index entry for a given source"""
    entry = index[source]

    if not source in index:
        puid = source.upper()
        for indice in index:
            index_entry = index[indice]

            if puid == inferPUID(index_entry.source):
                entry = index_entry
                break

    assert brave or not entry.secret
    return entry


def get(source: str, brave=False):
    """Returns the full data for a given source"""
    entry = get_index(source, brave)
    return entry.full


def get_statement(source: str, brave=False):
    """Returns just the problem statement for a given source"""
    return get(source, brave).bodies[0]


def get_solution(source: str, brave=False):
    """Returns just the solution for a given source (asserts existence)"""
    bodies = get(source, brave).bodies
    assert len(bodies) > 1, f"{source} has no solution"
    return bodies[1]


def get_puid(source: str):
    return inferPUID(source)


def get_source(puid: str) -> str | None:
    return source_to_puid_lookup.get(puid)
