import controller.add
import controller.clear
import controller.edit
import controller.index
import controller.po
import controller.search
import controller.show
import controller.status
import controller.cd

class VonController:
	do_add = controller.add.main
	do_clear = controller.clear.main
	do_edit = controller.edit.main
	do_index = controller.index.main
	do_show = controller.show.main

	do_search = controller.search.main
	do_s = controller.search.main

	do_status = controller.status.main
	do_ss = controller.status.main

	do_cd = controller.cd.main
	def do_ls(self, argv):
		self.do_cd(['.'] + argv)
	do_cs = do_cd

	do_po = controller.po.main
