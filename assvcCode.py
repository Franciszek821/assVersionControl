import argparse
import sys
from assvcPackage.commit import commit
from assvcPackage.start import start
from assvcPackage.compare import compare
from assvcPackage.installer import install
from assvcPackage.history import printHistory
from assvcPackage.reverse import reverse
from assvcPackage.clone import comImport, comExport
from assvcPackage.diff import diff


# CLI setup
parser = argparse.ArgumentParser(prog="assvc"
                                 , description="assVersionControl - A simple version control system")
sub = parser.add_subparsers(dest="command")

#start
sub.add_parser("start",help="Initialize a new .assvc folder in the current directory")

#installer
sub.add_parser("installer", help="Install or uninstall assvc to/from ~/.local/bin")

#import/export
import_parser = sub.add_parser("import", help="Import repository data, latest commit, add argument zip_path")
import_parser.add_argument("zip_path", type=str, help="Path to the zip file to import")
sub.add_parser("export", help="Export repository data")

#commit
commit_parser = sub.add_parser("commit", help="Create a new commit with a message")
commit_parser.add_argument("-m", "--message", type=str, default="Commit without message",
                           help="Commit message")

#compare
compare_parser = sub.add_parser("compare", help="Compare changes between selected commit and working version (default: latest commit)")
compare_parser.add_argument("-s", "--sha", type=str, default="latest", help="SHA of the commit to compare to")
compare_parser.add_argument("-d", "--diff", action="store_true",help="Show diff output")

#history
history_parser = sub.add_parser("history", help="Show commit history")
history_parser.add_argument("-l", "--long", action="store_true",help="Show longer sha output")

#reverse
reverse_parser = sub.add_parser("reverse", help="Revert to a previous commit (default: latest commit)")
reverse_parser.add_argument("-s", "--sha", type=str, default="latest", help="SHA of the commit to revert to")
reverse_parser.add_argument("-f", "--force", action="store_true", help="Force reverse without confirmation")

#diff
diff_parser = sub.add_parser("diff", help="Show differences between working version and latest commit on singular files")
diff_parser.add_argument("-s", "--sha", type=str, default="latest", help="SHA of the commit to compare to")
diff_parser.add_argument("file_path", type=str, help="Path to the file to show differences for")


try:
    args = parser.parse_args()

    if args.command == "start":
        start()
    elif args.command == "commit":
        commit(message=args.message)
    elif args.command == "compare":
        compare(commit_sha=args.sha, show_diff_var=args.diff, comparePrint=True)
    elif args.command == "installer":
        install()
    elif args.command == "history":
        printHistory(long=args.long)
    elif args.command == "reverse":
        reverse(commit_sha=args.sha, isPrintArgument=True, isForce=args.force)
    elif args.command == "import":
        comImport(args.zip_path)
    elif args.command == "export":
        comExport()
    elif args.command == "diff":
        diff(commit_sha=args.sha, file_path=args.file_path)
    else:
        parser.print_help()
except KeyboardInterrupt:
    print("\n\nOperation cancelled by user.")
    sys.exit(0)
except Exception:
    print("Error: An unexpected error occurred.")
    sys.exit(1)


#TODO:
'''
- Add windows support
ADVANCED:
- Add gui application

'''


#pyinstaller --onefile --name assvcLinux assvcCode.py

#pyinstaller --onefile --name assvcWindows assvcCode.py

#pyinstaller --onefile --name assvcInstall installer.py