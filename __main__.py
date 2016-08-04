import term
import sys

if __name__ == "__main__":
	cmd = term.VonTerminal()
	if len(sys.argv) == 1:
		cmd.run() # No argument, so start interactive mode
	else:
		cmd.onecmd(' '.join(sys.argv[1:]))
