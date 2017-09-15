from . import add
from . import asy
from . import clear
from . import edit
from . import index
from . import po
from . import search
from . import show
from . import status
from . import cd
from . import solve

class VonController:
	do_asy = asy.main
	do_add = add.main
	do_clear = clear.main
	do_edit = edit.main
	do_index = index.main
	do_show = show.main

	do_search = search.main
	do_s = search.main

	do_status = status.main
	do_ss = status.main

	do_cd = cd.main
	def do_ls(self, argv):
		self.do_cd(['.'] + argv)
	do_cs = do_cd

	do_po = po.main
	do_solve = solve.main
