from rc import TERM_COLOR, APPLY_COLOR
import cmd
import traceback
import shlex
import controller


PROMPT_TEXT = TERM_COLOR["BOLD_CYAN"] + "von" \
		+ TERM_COLOR["GREEN"] + ":) " + TERM_COLOR["RESET"]
WELCOME_STRING = APPLY_COLOR("BOLD_YELLOW", "Welcome to VON!")
GOODBYE_STRING = APPLY_COLOR("BOLD_YELLOW", "OK, goodbye! :D")


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
				print APPLY_COLOR("MAGENTA", "Running `{} --help`...".format(arg))
				func('--help')
		else:
			print "Here is a list of available commands:"
			for name in sorted(self.get_names()):
				if name[:3] == 'do_' and name != 'do_help' and name != 'do_EOF':
					print name[3:]
	
	def do_add(self, arg):
		controller.do_add(shlex.split(arg))

if __name__ == "__main__":
	VonTerminal().run()

	
# vim: fdm=marker
