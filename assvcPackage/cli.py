#!/usr/bin/env python3

import argparse
from assvcPackage.commit import commit
from assvcPackage.start import start
from assvcPackage.compare import compare
from assvcPackage.setup import setup

def main():
    # CLI setup
    parser = argparse.ArgumentParser(prog="assvc")
    sub = parser.add_subparsers(dest="command")


    sub.add_parser("start")


    commit_parser = sub.add_parser("commit")
    commit_parser.add_argument("-m", "--message", type=str, default="Initial commit",
                               help="Commit message")

    sub.add_parser("setup")

    sub.add_parser("compare")


    args = parser.parse_args()


    if args.command == "start":
        start()
    elif args.command == "commit":
        commit(message=args.message)
    elif args.command == "setup":
        setup()
    elif args.command == "compare":
        compare()



    else:
        parser.print_help()

if __name__ == "__main__":
    main()


#python3 -m PyInstaller --onefile cli.py --name assvc
#python3 -m PyInstaller     --onefile     --name install_assvc     --add-data "assvcPackage/dist/assvc:assvcPackage/dist"     install