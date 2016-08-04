from rc import TERM_COLOR, APPLY_COLOR, ERROR_PRE
import os
import cmd
import traceback
import shlex
import controller
import glob

import readline
readline.set_completer_delims(' \t\n')

PROMPT_TEXT = TERM_COLOR["BOLD_CYAN"] + "von" \
		+ TERM_COLOR["GREEN"] + ":) " + TERM_COLOR["RESET"]
WELCOME_STRING = APPLY_COLOR("BOLD_YELLOW", "Welcome to VON!")
GOODBYE_STRING = APPLY_COLOR("BOLD_YELLOW", "OK, goodbye! :D")

def _complete_path(path):
	if os.path.isdir(path):
		return glob.glob(os.path.join(path, '*'))
	else:
		return glob.glob(path+'*')

class VonTerminal(cmd.Cmd, controller.VonController):
	prompt = PROMPT_TEXT
	def emptyline(self):
		pass

	def completedefault(self, text, line, start_idx, end_idx):
		return _complete_path(text)

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

	def onecmd(self, line):
		"""Interpret the argument as though it had been typed in response
		to the prompt."""
		if line.strip() == "":
			return self.emptyline()
		_ = shlex.split(line)
		cmd = _[0]
		argv = _[1:]
		self.lastcmd = line
		if line == 'EOF' :
			self.lastcmd = ''
			return 1
		else:
			try:
				func = getattr(self, 'do_' + cmd)
			except AttributeError:
				return self.default(line)
			return func(argv)

	def direct(self, cargs):
		# cargs = sys.argv ostensibly
		if len(cargs) == 0:
			print "No command given"
		cmd = cargs[0]
		if hasattr(self, 'do_' + cmd):
			func = getattr(self, 'do_' + cmd)
			func(cargs[1:])
		else:
			print ERROR_PRE, "Command {} not recognized".format(cmd)

	def do_help(self, arg):
		if arg:
			try:
				func = getattr(self, 'do_' + arg)
			except AttributeError:
				print 'Command {} not found'.format(arg)
			else:
				print APPLY_COLOR("MAGENTA", "Running `{} --help`...".format(arg))
				func('--help')
		else:
			print "Here is a list of available commands:"
			for name in sorted(self.get_names()):
				if name[:3] == 'do_' and name != 'do_help' and name != 'do_EOF':
					print name[3:]
	
# vim: fdm=marker
