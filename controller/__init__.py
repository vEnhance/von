from rc import VON_BASE_PATH
import argparse
import model

import controller.add
import controller.clear
import controller.edit
import controller.reindex
import controller.search
import controller.show
import controller.ss
import controller.cd

class VonController:
	do_add = controller.add.main
	do_clear = controller.clear.main
	do_edit = controller.edit.main
	do_reindex = controller.reindex.main
	do_search = controller.search.main
	do_show = controller.show.main

	do_status = controller.ss.main
	do_ss = controller.ss.main

	do_cd = controller.cd.main
	def do_ls(self, argv):
		self.do_cd(['.'] + argv)
	do_cs = do_cd
