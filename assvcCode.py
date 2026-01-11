#!/usr/bin/env python3

import argparse
import os
from assvcPackage.commit import commit, find_assvc
from assvcPackage.start import start
from assvcPackage.compare import compare
from assvcPackage.installer import install
from assvcPackage.history import printHistory
#from assvcPackage.reverse import reverse


# CLI setup
parser = argparse.ArgumentParser(prog="assvc"
                                 , description="assVersionControl - A simple version control system")
sub = parser.add_subparsers(dest="command")


sub.add_parser(
    "start",
    help="Initialize a new .assvc folder in the current directory"
)

sub.add_parser("installer", help="Install or uninstall assvc to/from ~/.local/bin")


commit_parser = sub.add_parser("commit", help="Create a new commit with a message")
commit_parser.add_argument("-m", "--message", type=str, default="Commit without message",
                           help="Commit message")


sub.add_parser("compare", help="Compare changes between latest commit and working version")

sub.add_parser("history", help="Show commit history")


#current_path = os.path.join(find_assvc(), "head/current")
#with open(current_path, "r") as f:
#    commit_sha = f.read().strip()
#reverse_pareser = sub.add_parser("reverse", help="Revert to a previous commit (default: latest commit)")
#reverse_pareser.add_argument("-s", "-S", type=str, default=commit_sha, help="SHA of the commit to revert to")


args = parser.parse_args()


if args.command == "start":
    start()
elif args.command == "commit":
    commit(message=args.message)
elif args.command == "compare":
    compare()
elif args.command == "installer":
    install()
elif args.command == "history":
    printHistory()
#elif args.command == "reverse":
#    reverse(sha=args.s)

else:
    parser.print_help()

#pyinstaller --onefile --name assvcLinux assvcCode.py

#pyinstaller --onefile --name assvcWindows assvcCode.py

#pyinstaller --onefile --name assvcInstall installer.py