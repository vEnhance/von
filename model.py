from rc import SEPERATOR
import yaml

class Problem:
	bodies = []         # statement, sol, comments, ...
	desc = ""           # e.g. "Fiendish inequality"
	source = ""         # used as problem ID, e.g. "USAMO 2000/6"
	tags = []           # tags for the problem
	date_added = None   # date for problem

	def __init__(self, **kwargs):
		for key in kwargs:
			setattr(self, key, kwargs[key])

	@property
	def state(self):
		return self.bodies[0]

	def __repr__(self):
		return "({p.source}) {p.state}".format(p=self)


def readProblem(text):
	x = text.split(SEPERATOR)
	data = x[0]
	data['bodies'] = x[1:]
	return Problem(**data)
