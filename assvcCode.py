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
from assvcPackage.stage import stage,  unstage, clear, seeStaged
from assvcPackage.status import status
from assvcPackage.utils import latest_release
from packaging import version


code_version = "1.2.0"

# CLI setup
parser = argparse.ArgumentParser(prog="assvc"
                                 , description="assVersionControl - A simple version control system")
sub = parser.add_subparsers(dest="command")

#start
sub.add_parser("start",help="Initialize a new .assvc folder in the current directory")

#installer
sub.add_parser("installer", help="Install or uninstall assvc to/from ~/.local/bin")

#repository group (import/export)
repo_parser = sub.add_parser("repository", help="Repository operations (import/export)")
repo_sub = repo_parser.add_subparsers(dest="repo_command")

import_parser = repo_sub.add_parser("import", help="Import repository data, latest commit, add argument zip_path")
import_parser.add_argument("zip_path", type=str, help="Path to the zip file to import")
repo_sub.add_parser("export", help="Export repository data")

#commit
commit_parser = sub.add_parser("commit", help="Create a new commit with a message")
commit_parser.add_argument("-m", "--message", type=str, default="Commit without message",
                           help="Commit message")


#compare group (compare/diff)
compare_group = sub.add_parser("compare", help="Compare and diff operations")
compare_sub = compare_group.add_subparsers(dest="compare_command")

compare_parser = compare_sub.add_parser("all", help="Compare changes between selected commit and working version (default: latest commit)")
compare_parser.add_argument("-s", "--sha", type=str, default="latest", help="SHA of the commit to compare to")
compare_parser.add_argument("-d", "--diff", action="store_true",help="Show diff output")

diff_parser = compare_sub.add_parser("diff", help="Show differences between working version and latest commit on singular files")
diff_parser.add_argument("-s", "--sha", type=str, default="latest", help="SHA of the commit to compare to")
diff_parser.add_argument("file_path", type=str, help="Path to the file to show differences for")

#history
history_parser = sub.add_parser("history", help="Show commit history")
history_parser.add_argument("-l", "--long", action="store_true",help="Show longer sha output")

#reverse
reverse_parser = sub.add_parser("reverse", help="Revert to a previous commit (default: latest commit)")
reverse_parser.add_argument("-s", "--sha", type=str, default="latest", help="SHA of the commit to revert to")
reverse_parser.add_argument("-f", "--force", action="store_true", help="Force reverse without confirmation")

#staging group
staging_group = sub.add_parser("staging", help="Staging operations")
staging_sub = staging_group.add_subparsers(dest="staging_command")

stage_parser = staging_sub.add_parser("stage", help="Stage files for commit")
stage_parser.add_argument("-a", '--all', action="store_true", help="Stage all changed files for commit")
stage_parser.add_argument("file_paths", nargs="*", type=str, help="Paths to files to stage for commit")

unstage_parser = staging_sub.add_parser("unstage", help="Unstage files from commit")
unstage_parser.add_argument("file_paths", nargs="+", type=str, help="Paths to files to unstage from commit")

staging_sub.add_parser("clear", help="Clear all staged files")

staging_sub.add_parser("show", help="See all staged files")

#status
status_parser = sub.add_parser("status", help="Show the status of staged and unstaged files")

#Help
sub.add_parser("help", help="Show help for staging commands")
tag = latest_release("Franciszek821", "assVersionControl")["tag"]
if version.parse(tag) > version.parse(code_version):
    print(f"Info: A new version of assvc is available: {tag} (current: {code_version}). Visit  https://github.com/Franciszek821/assVersionControl/releases for latest version.\n")
try:
    args = parser.parse_args()

    if args.command == "start":
        start()
    elif args.command == "commit":
        commit(message=args.message)
    elif args.command == "compare":
        if args.compare_command == "all":
            compare(commit_sha=args.sha, show_diff_var=args.diff, comparePrint=True)
        elif args.compare_command == "diff":
            diff(commit_sha=args.sha, file_path=args.file_path)
        else:
            compare_group.print_help()
    elif args.command == "installer":
        install()
    elif args.command == "history":
        printHistory(long=args.long)
    elif args.command == "reverse":
        reverse(commit_sha=args.sha, isPrintArgument=True, isForce=args.force)
    elif args.command == "repository":
        if args.repo_command == "import":
            comImport(args.zip_path)
        elif args.repo_command == "export":
            comExport()
        else:
            repo_parser.print_help()
    elif args.command == "staging":
        if args.staging_command == "stage":
            if args.all:
                stage(file_paths=[], stage_all=True)
            elif args.file_paths:
                stage(file_paths=args.file_paths, stage_all=False)
            else:
                print("Error: Either provide file paths or use -a to stage all changes")
        elif args.staging_command == "unstage":
            unstage(file_paths=args.file_paths)
        elif args.staging_command == "clear":
            clear()
        elif args.staging_command == "show":
            seeStaged()
        elif args.staging_command == "help":
            staging_group.print_help()
        else:
            staging_group.print_help()
    elif args.command == "status":
        status()
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
- compare sha to sha

ADVANCED:
- Add gui application

'''


#pyinstaller --onefile --name assvcLinux assvcCode.py

#pyinstaller --onefile --name assvcWindows assvcCode.py

