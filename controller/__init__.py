from . import add
from . import asy
from . import cd
from . import clear
from . import edit
from . import index
from . import paths
from . import po
from . import search
from . import show
from . import solve
from . import status

class VonController:
	def do_ls(self, argv):
		self.do_cd(['.'] + argv)

	do_add = add.main
	do_asy = asy.main
	do_cd = cd.main
	do_clear = clear.main
	do_cs = do_cd
	do_edit = edit.main
	do_index = index.main
	do_paths = paths.main
	do_po = po.main
	do_s = search.main
	do_search = search.main
	do_show = show.main
	do_solve = solve.main
	do_solve = solve.main
	do_ss = status.main
	do_status = status.main
