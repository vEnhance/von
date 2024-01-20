import collections
import collections.abc
import functools
import json
import logging
import os
import pickle as pickle
import random
from typing import Any, Callable, TextIO

import yaml

from .puid import inferPUID
from .rc import (  # NOQA
    OTIS_EVIL_JSON_PATH,
    SEPARATOR,
    SORT_TAGS,
    VON_BASE_PATH,
    VON_CACHE_PATH,
    VON_INDEX_PATH,
)

OTIS_USED_SOURCES_LIST: list[str] | None
if OTIS_EVIL_JSON_PATH is not None:  # type: ignore
    with open(OTIS_EVIL_JSON_PATH) as f:
        evil_json = json.load(f)
        OTIS_HANDOUT_USED_SOURCES = evil_json.values()
else:
    OTIS_HANDOUT_USED_SOURCES = None


def shortenPath(path: str):
    return os.path.relpath(path, VON_BASE_PATH)


def completePath(path: str):
    return os.path.join(VON_BASE_PATH, path)


def vonOpen(path: str, *args: Any, **kwargs: Any) -> TextIO:
    return open(completePath(path), *args, **kwargs)


class pickleObj(collections.abc.MutableMapping):
    def _initial(self) -> Any:
        return {}

    def __init__(self, path: str, mode="rb"):
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            self.store = self._initial()
        else:
            with vonOpen(path, "rb") as f:
                self.store = pickle.load(f)  # type: ignore
        self.path = path
        self.mode = mode

    def __enter__(self):
        return self

    def __exit__(self, *_: Any):
        if self.mode == "wb":
            with vonOpen(self.path, "wb") as f:
                pickle.dump(self.store, f)  # type: ignore

    def __getitem__(self, key: Any):
        try:
            return self.store[key]
        except IndexError:
            raise IndexError(f"{key} not a valid key")

    def __setitem__(self, key: int | str, value: Any):
        if isinstance(self.store, list):
            assert isinstance(key, int)
            self.store[key] = value
        else:
            assert isinstance(key, str)
            self.store[key] = value

    def __delitem__(self, key: str):
        if isinstance(self.store, list):
            assert isinstance(key, int)
            del self.store[key]
        else:
            assert isinstance(key, str)
            del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def set(self, store: Any):
        self.store = store


class pickleDictVonIndex(pickleObj):
    store: dict[str, "PickleMappingEntry"]
    __getitem__: Callable[..., "PickleMappingEntry"]

    def _initial(self) -> dict[str, "PickleMappingEntry"]:
        return {}


class pickleListVonCache(pickleObj):
    store: list["PickleMappingEntry"]

    def __getitem__(self, idx: int) -> "PickleMappingEntry":
        return super().__getitem__(idx)

    def _initial(self) -> list["PickleMappingEntry"]:
        return []

    def set(self, store: list["PickleMappingEntry"]):
        for i in range(len(store)):
            store[i].i = i
        self.store = store


def VonIndex(mode="rb"):
    return pickleDictVonIndex(VON_INDEX_PATH, mode)


def VonCache(mode="rb"):
    return pickleListVonCache(VON_CACHE_PATH, mode)


@functools.total_ordering
class GenericItem:  # superclass to Problem, PickleMappingEntry
    desc = ""  # e.g. "Fiendish inequality"
    source = ""  # used as problem ID, e.g. "USAMO 2000/6"
    tags: list[str] = []  # tags for the problem
    path = ""  # path to problem TeX file
    i: int | None = None  # position in Cache, if any
    author: str | None = None  # default
    hardness: int | None = None  # default
    url: str | None = None

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
        for d in SORT_TAGS:
            if d in self.tags:
                return d
        return "NONE"

    @property
    def sortkey(self):
        if isinstance(self.hardness, int):
            return (self.sortvalue, self.hardness, self.source)
        else:
            return (self.sortvalue, -1, self.source)

    @property
    def used_by_otis(self):
        if OTIS_HANDOUT_USED_SOURCES is not None:
            if "waltz" in self.tags:
                if self.source in OTIS_HANDOUT_USED_SOURCES:
                    logging.critical(f"{self.source} in both OTIS handout and exam")
                return True
            return self.source in OTIS_HANDOUT_USED_SOURCES
        else:
            return False

    def __eq__(self, other: "GenericItem") -> bool:
        return self.sortkey == other.sortkey

    def __lt__(self, other: "GenericItem") -> bool:
        return self.sortkey < other.sortkey


class Problem(GenericItem):
    bodies: list[str] = []  # statement, sol, comments, ...

    def __init__(self, path: str, **kwargs: Any):
        self.path = path
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def state(self) -> str:
        return self.bodies[0]

    def __repr__(self):
        return self.source

    @property
    def entry(self) -> "PickleMappingEntry":
        """Returns an PickleMappingEntry for storage in pickle"""
        return PickleMappingEntry(
            source=self.source,
            desc=self.desc,
            author=self.author,
            url=self.url,
            hardness=self.hardness,
            tags=self.tags,
            path=self.path,
            i=self.i,
        )

    @property
    def full(self) -> "Problem":
        logging.warn("Sketchy af")
        return self


class PickleMappingEntry(GenericItem):
    def __init__(self, **kwargs: Any):
        for key in kwargs:
            if kwargs[key] is not None:
                setattr(self, key, kwargs[key])

    # search things
    def hasTag(self, tag: str):
        return tag.lower() in [_.lower() for _ in self.tags]

    def hasTerm(self, term: str):
        blob = self.source + " " + self.desc
        if self.author is not None:
            blob += " " + self.author
        return (
            term.lower() in blob.lower()
            or term in self.tags
            or term.upper() in inferPUID(self.source)
        )

    def hasAuthor(self, name: str):
        if self.author is None:
            return False
        haystacks = self.author.lower().strip().split(" ")
        return name.lower() in haystacks

    def hasSource(self, source: str):
        return source.lower() in self.source.lower()

    def __repr__(self):
        return self.source

    @property
    def secret(self):
        return "SECRET" in self.source or "secret" in self.tags

    @property
    def entry(self):
        logging.warn("sketchy af")
        return self

    @property
    def full(self) -> Problem:
        p = makeProblemFromPath(self.path)
        assert p is not None
        return p


def getcwd():
    true_dir = os.getcwd()
    if true_dir.startswith(VON_BASE_PATH) and true_dir != VON_BASE_PATH:
        return os.path.relpath(true_dir, VON_BASE_PATH)
    else:
        return ""


def getCompleteCwd():
    return completePath(getcwd())


def makeProblemFromPath(path: str) -> Problem:
    # Creates a problem instance from a source, without looking at Index
    with vonOpen(path, "r") as f:
        text = "".join(f.readlines())
    x = text.split(SEPARATOR)
    data = yaml.safe_load(x[0])
    assert data is not None, f"No data in {path}"
    data["bodies"] = [_.strip() for _ in x[1:]]
    assert data["source"], f"No source in {path}"
    assert data["desc"], f"No description in {path}"
    return Problem(path, **data)


def getAllProblems() -> list[Problem]:
    ret: list[Problem] = []
    for root, _, filenames in os.walk(VON_BASE_PATH):
        for fname in filenames:
            if not fname.endswith(".tex"):
                continue
            path = shortenPath(os.path.join(root, fname))
            p = makeProblemFromPath(path)
            ret.append(p)
    return ret


def getEntryByCacheNum(n: int) -> PickleMappingEntry:
    with VonCache() as cache:
        entry = cache[n - 1]
        return entry


def getEntryByTerm(term: str) -> PickleMappingEntry | None:
    with VonIndex() as index:
        entry = None
        if term in index:
            entry = index[term]

        if entry is None:
            puid = term.upper()
            for index_source, index_entry in index.store.items():
                if puid == inferPUID(index_source):
                    entry = index_entry
                    break

    if entry is not None:
        with VonCache() as cache:
            for cache_entry in cache:
                if cache_entry.source == entry.source:
                    return cache_entry

    return entry


def getEntryByKey(key: str):
    # TODO this shouldn't actually be in model, but blah
    if key.isdigit():
        return getEntryByCacheNum(int(key))
    else:
        return getEntryByTerm(key)


def addProblemByFileContents(path: str, text: str):
    with vonOpen(path, "w") as f:
        print(text, file=f)
    logging.info("Wrote to " + path)
    # Now update cache
    p = makeProblemFromPath(shortenPath(path))
    addProblemToIndex(p)
    return p


def viewDirectory(path: str):
    problems: list["Problem"] = []
    dirs: list[str] = []
    for item_path in os.listdir(path):
        abs_item_path = os.path.join(path, item_path)
        if os.path.isfile(abs_item_path) and abs_item_path.endswith(".tex"):
            problem = makeProblemFromPath(abs_item_path)
            assert problem is not None
            problems.append(problem)
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
    terms: list[str] | None = None,
    tags: list[str] | None = None,
    sources: list[str] | None = None,
    authors: list[str] | None = None,
    path="",
    refine=False,
    alph_sort=False,
    in_otis: bool | None = None,
    has_url: bool | None = None,
) -> list[PickleMappingEntry]:
    def _lambda_is_matching(entry: PickleMappingEntry):
        if OTIS_HANDOUT_USED_SOURCES is not None:
            if entry.used_by_otis and in_otis is False:
                return False
            elif not entry.used_by_otis and in_otis is True:
                return False

        if has_url is not None:
            if entry.url is None and has_url is True:
                return False
            if entry.url is not None and has_url is False:
                return False

        return all(
            (
                entry.path.startswith(path),
                (not tags or all([entry.hasTag(_) for _ in tags])),
                (not terms or all([entry.hasTerm(_) for _ in terms])),
                (not sources or all([entry.hasSource(_) for _ in sources])),
                (not authors or all([entry.hasAuthor(_) for _ in authors])),
            )
        )

    if refine is False:
        with VonIndex() as index:
            result: list[PickleMappingEntry] = [
                entry for entry in index.values() if _lambda_is_matching(entry)
            ]
    else:
        with VonCache() as cache:
            result = [entry for entry in cache.values() if _lambda_is_matching(entry)]
    if alph_sort:
        result.sort(key=lambda e: e.source)
    else:
        result.sort()
    if len(result) > 0:
        setCache(result)
    return result


def augmentCache(*entries: PickleMappingEntry):
    with VonCache("wb") as cache:
        cache.set(cache.store + list(entries))


def setCache(entries: list[PickleMappingEntry]):
    with VonCache("wb") as cache:
        cache.set(entries)


def clearCache():
    with VonCache("wb") as cache:
        cache.set([])


def readCache():
    with VonCache() as cache:
        return cache


# A certain magical Index~ <3


def addEntryToIndex(entry: PickleMappingEntry):
    with VonIndex("wb") as index:
        index[entry.source] = entry


def updateEntryByProblem(old_entry: PickleMappingEntry, new_problem: Problem):
    new_problem.i = old_entry.i
    new_entry = new_problem.entry

    with VonIndex("wb") as index:
        if old_entry.source != new_entry.source:
            del index[old_entry.source]
        index[new_entry.source] = new_entry
    with VonCache("wb") as cache:
        for i, entry in enumerate(cache):
            if entry.source == old_entry.source:
                new_entry.i = i
                cache[i] = new_entry
                break
        else:
            cache.set(cache.store + [new_entry])
    return index[new_entry.source]


def addProblemToIndex(problem: Problem):
    with VonIndex("wb") as index:
        p = problem
        index[p.source] = p.entry
        return index[p.source]


def setEntireIndex(von_index_dict: dict[str, PickleMappingEntry]):
    with VonIndex("wb") as index:
        index.set(von_index_dict)


def rebuildIndex():
    d: dict[str, PickleMappingEntry] = {}
    for p in getAllProblems():
        if p.source in d:
            fake_source = f"DUPLICATE {random.randrange(10**6, 10**7)}"
            logging.error(
                p.source + " is being repeated, replacing with " + fake_source
            )
            p.source = fake_source
        d[p.source] = p.entry
    setEntireIndex(d)
