#!/usr/bin/env python

import os
import sys
import uvicorn

# defining color codes
FAIL = '\033[91m'
WARNING = '\033[93m'
ENDC = '\033[0m'

if len(sys.argv)<=1:
    print(FAIL)
    print("ERROR:",ENDC, "Argument 'processor_folder' is missing")
    print("\n    Syntax: run-local.py <processor_folder>\n")
    sys.exit(1)

proc_folder=sys.argv[1]

try:
    print(f"\nSearching for processor in folder {WARNING}{proc_folder}{ENDC}...\n")
    sys.path.append(os.path.abspath(proc_folder))
    os.chdir(proc_folder)
except FileNotFoundError as e:
    print(FAIL)
    print("ERROR:",ENDC,"the given folder does not exist.")
    print()
    sys.exit(2)

try:
    # load processor module from python module 'processor'
    import processor as processorModule

    # run processor
    from anxprocessor import application
    application.run(processorModule)

except ModuleNotFoundError as e:

    print(FAIL)
    print(e)
    print("ERROR importing module 'processor' containing a process module")
    print(WARNING)
    print("  # # # How to fix # # #", ENDC)
    print("  Create a processor class derived from BaseProcessor")
    print("  and store it in a module named processor.py.\n")
    sys.exit(3)


###################################################
#
#
# Start with:
#
# 1. Either directly as python application (only for testing)
#    please uncomment these lines:
#
if __name__ == "__main__":
    uvicorn.run(application.app, host="0.0.0.0", port=8000, log_level=uvicorn.logging.logging.INFO)
#
#
# 2. Using uvicorn launcher
#    Run the following command on the command line:
#    $ uvicorn main:application.app --reload [--log-level debug|info|warning]
#
#
