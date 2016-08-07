from rc import USE_COLOR, KEY_CHAR

# Color names {{{
TERM_COLOR = {}
TERM_COLOR["NORMAL"]          = ""
TERM_COLOR["RESET"]           = "\033[m"
TERM_COLOR["BOLD"]            = "\033[1m"
TERM_COLOR["RED"]             = "\033[31m"
TERM_COLOR["GREEN"]           = "\033[32m"
TERM_COLOR["YELLOW"]          = "\033[33m"
TERM_COLOR["BLUE"]            = "\033[34m"
TERM_COLOR["MAGENTA"]         = "\033[35m"
TERM_COLOR["CYAN"]            = "\033[36m"
TERM_COLOR["BOLD_RED"]        = "\033[1;31m"
TERM_COLOR["BOLD_GREEN"]      = "\033[1;32m"
TERM_COLOR["BOLD_YELLOW"]     = "\033[1;33m"
TERM_COLOR["BOLD_BLUE"]       = "\033[1;34m"
TERM_COLOR["BOLD_MAGENTA"]    = "\033[1;35m"
TERM_COLOR["BOLD_CYAN"]       = "\033[1;36m"
TERM_COLOR["BG_RED"]          = "\033[41m"
TERM_COLOR["BG_GREEN"]        = "\033[42m"
TERM_COLOR["BG_YELLOW"]       = "\033[43m"
TERM_COLOR["BG_BLUE"]         = "\033[44m"
TERM_COLOR["BG_MAGENTA"]      = "\033[45m"
TERM_COLOR["BG_CYAN"]         = "\033[46m"
if USE_COLOR is False:
	for key in TERM_COLOR.keys():
		TERM_COLOR[key] = ""
# }}}

def APPLY_COLOR(color_name, s):	
	return TERM_COLOR[color_name] + s + TERM_COLOR["RESET"]

ERROR_PRE = APPLY_COLOR("BOLD_RED", "Error:")
WARN_PRE  = APPLY_COLOR("BOLD_YELLOW", "Warn:")


def getProblemString(problem):
	s = getEntryString(problem.entry, tags = True)
	s += "\n"
	s += APPLY_COLOR("CYAN", problem.state.strip())
	return s
def getEntryString(entry, tags = False):
	s = ""
	if entry.i is not None:
		s += APPLY_COLOR("BOLD_RED", "[" + KEY_CHAR + str(entry.n) + "]")
		s += " \t"
	s +=  APPLY_COLOR("BOLD_BLUE", "(" + entry.source + ")")
	s += " "
	s += entry.desc
	s += " " 
	s += APPLY_COLOR("RED", "#"+ entry.diffstring)
	if tags:
		s +=  "\n\t" + APPLY_COLOR("MAGENTA", ' '.join(entry.tags))
	return s
def getDirString(path):
	return "Directory " + APPLY_COLOR("BOLD_BLUE", path)

def printProblem(*args, **kwargs):
	print getProblemString(*args, **kwargs)
def printEntry(*args, **kwargs):
	print getEntryString(*args, **kwargs)
def printDir(*args, **kwargs):
	print getDirString(*args, **kwargs)

def warn(message):
	print WARN_PRE, message
def error(message):
	print ERROR_PRE, message
def log(message):
	print message
def out(message):
	print message
