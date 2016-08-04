from rc import USE_COLOR
import cmd
import traceback
import shlex

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

PROMPT_TEXT = TERM_COLOR["BOLD_CYAN"] + "von" \
		+ TERM_COLOR["GREEN"] + ":) " + TERM_COLOR["RESET"]

def apply_color(color_name, s):	
	return TERM_COLOR[color_name] + s + TERM_COLOR["RESET"]

WELCOME_STRING = apply_color("BOLD_YELLOW", "Welcome to VON!")
GOODBYE_STRING = apply_color("BOLD_YELLOW", "OK, goodbye! :D")


class VonTerminal(cmd.Cmd):
	prompt = PROMPT_TEXT
	def emptyline(self):
		pass

	def run(self):
		print WELCOME_STRING
		while 1:
			try:
				self.cmdloop()
				break
			except KeyboardInterrupt:
				print "^C"
			except SystemExit:
				pass
			except:
				traceback.print_exc()
		print "\n" + GOODBYE_STRING 


	def do_EOF(self, arg):
		return 1

	def do_help(self, arg):
		if arg:
			try:
				func = getattr(self, 'do_' + arg)
			except AttributeError:
				print 'Command {} not found'.format(arg)
			else:
				print apply_color("MAGENTA", "Running `{} --help`...".format(arg))
				func('--help')
		else:
			print "Here is a list of available commands:"
			for name in sorted(self.get_names()):
				if name[:3] == 'do_' and name != 'do_help' and name != 'do_EOF':
					print name[3:]

if __name__ == "__main__":
	VonTerminal().run()

	
# vim: fdm=marker
