# Assvc
Version control made by me.

## Instaling Linux
Use command "chmod +x ./assvcLinux" to give permision to file.
To install globally to work everywhere use command "./assvcLinux install".
After installing globally you can use command "assvc -h".
## Instaling Linux
To install globally to work everywhere use command "assvcWindows.exe install".
After installing globally you can use command "assvc -h".

## Requirements
- Python 3.10+
- No external dependencies


## Commands

Initialize repository:

* `assvc start` — Initialize a new `.assvc` folder in the current directory

Install tool:

* `assvc installer` — Install or uninstall `assvc` to/from `~/.local/bin`

Import / Export:

* `assvc import <zip_path>` — Import repository data from a zip file
* `assvc export` — Export repository data

Create a commit:

* `assvc commit -m "message"` — Create a new commit with a message (default: "Commit without message")
* `assvc commit` — Commit with default message

Compare changes:

* `assvc compare` — Compare changes between latest commit and working directory
* `assvc compare -s <sha>` — Compare changes between selected commit and working directory 
* `assvc compare -d` — Compare changes (with diff output) between selected commit and working directory

View history:

* `assvc history` — Show commit history


Reverse:

* `assvc reverse` — Revert the working directory to latest commit
* `assvc reverse -s <sha>` — Revert the working directory to selected commit
* `assvc reverse -f` — Revert without confirmation


Diff:
* `assvc diff <file_path>` — Write the differences between lates commit and curent version of singular file
* `assvc diff -s <sha> <file_path>` — Write the differences between selected commit and curent version of singular file

## Other functions

Ignore
* `.assignore` — you can  add file called .assignore where you can add files and folder that you dont want to commit, compare, reverse or show diff.
