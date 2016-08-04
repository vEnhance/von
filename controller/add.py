from rc import EDITOR, VON_BASE_PATH, SEPERATOR, NSEPERATOR, TAG_HINT_TEXT

import clipboard
import datetime
import tempfile
import subprocess
import yaml
import string
import os
import traceback
import argparse

def user_file_input(initial = "", extension = ".tmp"):
	"""Opens in $EDITOR a file with content 'initial'
	and 'extension', and returns edited file."""

	with tempfile.NamedTemporaryFile(suffix=extension) as tf:
		tf.write(initial)
		tf.flush()
		subprocess.call([EDITOR, tf.name])

		# do the parsing with `tf` using regular File operations.
		# for instance:
		tf.seek(0)
		edited_message = ''.join(tf.readlines())
	return edited_message

def alert_error_tryagain(message = ''):
	"""Prints an error message and waits for user to confirm."""
	return raw_input(message + ' ')

PS_INSTRUCT = """% Input your problem and solution below.
% Three dashes on a newline indicate the breaking points.
% vim: tw=72"""

def get_bodies(raw_text):
	initial = PS_INSTRUCT + NSEPERATOR + raw_text
	while True:
		# TODO maybe give user instructions
		raw_ps = user_file_input(initial = initial, extension = ".tex")
		if raw_ps.count(SEPERATOR) >= 1:
			bodies = [_.strip() for _ in raw_ps.split(SEPERATOR)[1:]]
			if bodies[0] == '': return None
			return bodies
		elif raw_ps.strip() == "":
			return None
		else:
			alert_error_tryagain("Bad format: can't find separator. Try again.")
			initial = raw_ps
	return bodies

YAML_DATA_FILE = """# Input your problem metadata here

source: <++>     # e.g. USAMO 2000/6. This must be unique
desc:   <++>     # e.g. Fiendish inequality
path:   {path}<++>
tags:   [{now.year}-{now.month:02d}, <++>] # don't forget difficulty and shape!

{hint}
""".format(path = VON_BASE_PATH, now=datetime.datetime.now(), hint = TAG_HINT_TEXT)

def file_escape(s):
	s = s.replace("/", "-")
	s = s.replace(" ", "")
	s = ''.join([_ for _ in s if _ in string.letters+string.digits+'-'])
	if s == '':
		s += 'emptyname'
	return s

def get_yaml_info():
	initial = YAML_DATA_FILE
	while True:
		raw_yaml = user_file_input(initial = initial, extension = ".yaml")
		try:
			d = yaml.load(raw_yaml)
			if d is None:
				return (None, None)
			assert 'path' in d, "Path is mandatory"
			assert 'source' in d, "Source is mandatory"
			if d['path'][-1] != '/':
				d['path'] += '/'
			print d['path']
			assert os.path.isdir(d['path']), d['path'] + " directory non-existent"
			target = d['path'] + file_escape(d['source']) + '.tex'
			assert not os.path.isfile(target), target + " already taken"
		except AssertionError:
			# TOOD test this
			traceback.print_exc()
			alert_error_tryagain("Okie dokie?")
			initial = raw_yaml
		else:
			del d['path']
			return (target, yaml.dump(d).strip())


def do_add_problem(raw_text):
	"""Core procedure. Opens two instances of editors to solicit user input
	on problem and produce a problem instance."""

	# Get problem and solution
	bodies = get_bodies(raw_text)
	if bodies is None:
		print "Aborting due to empty input..."
		return
	target, out_yaml = get_yaml_info()
	if out_yaml is None:
		print "Aborting due to empty input..."
		return
	with open(target, 'w') as f:
		print >>f, NSEPERATOR.join([out_yaml]+bodies)
	print "Wrote to", target

parser = argparse.ArgumentParser(prog='add', description='Adds a problem to VON.')
parser.add_argument('filename', default = None, nargs = '?',
		help="If specified, uses contents of file as body")

def main(args):
	opts = parser.parse_args(args)
	if opts.filename is not None:
		with open(opts.filename) as f:
			initial_text = ''.join(f.readlines())
	else:
		initial_text = clipboard.paste()
		if initial_text.strip() == '':
			initial_text = '<++>'
	do_add_problem(initial_text)
