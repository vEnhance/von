import term
import sys
import controller

if __name__ == "__main__":
	cmd = term.VonTerminal()
	if len(sys.argv) == 1:
		cmd.run()
	else:
		cmd.onecmd(' '.join(sys.argv[1:]))
