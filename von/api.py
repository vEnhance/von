# For importing von externally
import sys

from . import model
from .puid import inferPUID

sys.modules["model"] = model

index = model.VonIndex().store  # get the underlying dict

source_to_puid_lookup = {inferPUID(source): source for source in index}


def has(source: str) -> bool:
    """Checks whether a given source exists in database"""
    return source in index


def has_solution(source: str) -> bool:
    """Checks whether a given source exists in database AND has a solution"""
    if not has(source):
        return False
    entry = index[source]
    return len(entry.full.bodies) > 1


def get_index(source: str, brave=False) -> model.PickleMappingEntry | None:
    """Returns the index entry for a given source, or None"""
    entry = index.get(source)

    if entry is None:
        puid = source.upper()
        for index_source, index_entry in index.items():
            if puid == inferPUID(index_source):
                entry = index_entry
                break

    if entry is not None and entry.secret:
        assert brave, f"{entry} requires security clearance"
    return entry


def get(source: str, brave=False) -> model.Problem:
    """Returns the full data for a given source"""
    entry = get_index(source, brave)
    assert entry is not None, f"{source} is None"
    return entry.full


def get_statement(source: str, brave=False) -> str:
    """Returns just the problem statement for a given source"""
    return get(source, brave).bodies[0]


def get_solution(source: str, brave=False) -> str:
    """Returns just the solution for a given source (asserts existence)"""
    bodies = get(source, brave).bodies
    assert len(bodies) > 1, f"{source} has no solution"
    return bodies[1]


def get_puid(source: str) -> str:
    return inferPUID(source)


def get_source(puid: str) -> str | None:
    return source_to_puid_lookup.get(puid)
