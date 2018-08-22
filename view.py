from .rc import USE_COLOR
import sys
import argparse
import string

def file_escape(s):
	s = s.replace("/", "-")
	s = s.replace(" ", "")
	s = ''.join([_ for _ in s if _ in string.ascii_letters+string.digits+'-'])
	if s == '':
		s += 'emptyname'
	return s

# Arguments hacking whee
# We have _OPTS here which will pick up any parse_args()
_view_parser = argparse.ArgumentParser(add_help=False)
_view_parser.add_argument('-q', '--quiet', action = "store_const",\
		default = False, const = True,\
		help = "Suppress some output (only with ls now).") # TODO generalize
_view_parser.add_argument('--nocolor', action = "store_const",\
		dest = 'color', default = True, const = False,\
		help = "Suppress color output.")
_view_parser.add_argument('--tabs', action = "store_const",\
		dest = 'tabs', default = False, const = True,\
		help = "Uses tabs as separator for data in list-type commands.")
_view_parser.add_argument('--brave', action = "store_const",\
		dest = 'brave', default = False, const = True,\
		help = "Show problems marked as SECRET.")
_view_parser.add_argument('-v', '--verbose', action = "store_const",\
		default = False, const = True,\
		help = "More verbose displays (e.g. include problem tags).")

_OPTS = _view_parser.parse_args([])
class Parser(argparse.ArgumentParser):
	def __init__(self, *args, **kwargs):
		super(Parser, self).__init__(parents=[_view_parser], *args, **kwargs)
	def process(self, *args, **kwargs):
		opts = self.parse_args(*args, namespace = _OPTS, **kwargs)
		return _OPTS

# Color names {{{
_TERM_COLOR = {}
_TERM_COLOR["NORMAL"]          = ""
_TERM_COLOR["RESET"]           = "\033[m"
_TERM_COLOR["BOLD"]            = "\033[1m"
_TERM_COLOR["RED"]             = "\033[31m"
_TERM_COLOR["GREEN"]           = "\033[32m"
_TERM_COLOR["YELLOW"]          = "\033[33m"
_TERM_COLOR["BLUE"]            = "\033[34m"
_TERM_COLOR["MAGENTA"]         = "\033[35m"
_TERM_COLOR["CYAN"]            = "\033[36m"
_TERM_COLOR["BOLD_RED"]        = "\033[1;31m"
_TERM_COLOR["BOLD_GREEN"]      = "\033[1;32m"
_TERM_COLOR["BOLD_YELLOW"]     = "\033[1;33m"
_TERM_COLOR["BOLD_BLUE"]       = "\033[1;34m"
_TERM_COLOR["BOLD_MAGENTA"]    = "\033[1;35m"
_TERM_COLOR["BOLD_CYAN"]       = "\033[1;36m"
_TERM_COLOR["BG_RED"]          = "\033[41m"
_TERM_COLOR["BG_GREEN"]        = "\033[42m"
_TERM_COLOR["BG_YELLOW"]       = "\033[43m"
_TERM_COLOR["BG_BLUE"]         = "\033[44m"
_TERM_COLOR["BG_MAGENTA"]      = "\033[45m"
_TERM_COLOR["BG_CYAN"]         = "\033[46m"
if USE_COLOR is False:
	for key in list(_TERM_COLOR.keys()):
		_TERM_COLOR[key] = ""
# }}}

def APPLY_COLOR(color_name, s):	
	if _OPTS.color is False:
		return s
	return _TERM_COLOR[color_name] + s + _TERM_COLOR["RESET"]

ERROR_PRE = APPLY_COLOR("BOLD_RED", "Error:")
WARN_PRE  = APPLY_COLOR("BOLD_YELLOW", "Warn:")

def getProblemString(problem):
	s = getEntryString(problem.entry)
	s += "\n"
	s += APPLY_COLOR("CYAN", problem.state.strip())
	return s
def getEntryString(entry):
	# SPECIAL hide brave
	if entry.secret and not _OPTS.brave:
		return APPLY_COLOR("BOLD_YELLOW", "Problem not shown")

	if _OPTS.tabs is True:
		s = '\t'.join([entry.source, entry.desc, entry.diffstring])
		if _OPTS.verbose:
			s += '\t' + ' '.join(entry.tags)
		return s
	s = ""

	# SPECIAL GLOW
	if entry.i is not None:
		if "final" in entry.tags:
			s += APPLY_COLOR("BOLD_YELLOW", "[" + "#" + str(entry.n) + "]")
		elif "waltz" in entry.tags:
			s += APPLY_COLOR("BOLD_GREEN", "[" + "#" + str(entry.n) + "]")
		else:
			s += APPLY_COLOR("BOLD_RED", "[" + "#" + str(entry.n) + "]")
		s += " \t"
	# "nice" / "favorite" glow
	if 'favorite' in entry.tags or 'nice' in entry.tags:
		s += APPLY_COLOR("BOLD_CYAN", "(" + entry.source + ")")
	else:
		s += APPLY_COLOR("BOLD_BLUE", "(" + entry.source + ")")
	s += " "
	s += entry.desc
	if hasattr(entry, 'author'):
		s += ", " + APPLY_COLOR("CYAN", entry.author)
	s += " "
	s += APPLY_COLOR("RED", "#"+ entry.diffstring)
	if _OPTS.verbose:
		s += "\n\t"
		s += APPLY_COLOR("MAGENTA", ' '.join(entry.tags))
	return s
def formatPath(path):
	return 'VON/' + path
def getDirString(path):
	return "Directory " + APPLY_COLOR("BOLD_BLUE", path)

def printProblem(*args, **kwargs):
	print(getProblemString(*args, **kwargs))
def printEntry(*args, **kwargs):
	print(getEntryString(*args, **kwargs))
def printDir(*args, **kwargs):
	print(getDirString(*args, **kwargs))

def warn(message):
	print(WARN_PRE, message, file=sys.stderr)
def error(message):
	print(ERROR_PRE, message)
def log(message):
	print(message)
def out(message):
	print(message)
