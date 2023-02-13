import sys
from autobackup.main import Main

main_obj = Main(sys.argv)
sys.exit(main_obj.execute())
