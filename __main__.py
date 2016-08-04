import term
import sys
import controller


if __name__ == "__main__":
	if len(sys.argv) == 1:
		cmd = term.VonTerminal()
		cmd.run()
	else:
		command = sys.argv[1]
		args = sys.argv[2:]
		func = getattr(controller, command) # todo meh
		func(args)
