import sys
root = "{}\\{}".format(__file__.split("\\",2)[0], __file__.split("\\",2)[1])
if not root in sys.path:
	sys.path.append(root)
