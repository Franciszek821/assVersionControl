# Assvc
Version control made by me.

## Instaling Linux
Use command "chmod +x ./assvcLinux" to give permision to file.
To install globally to work everywhere use command "./assvcLinux install".
After installing globally you can use command "assvc -h".

## Requirements
- Python 3.10+
- All of the needed dependencies are in the file called requirements.txt 


## Commands

### Initialize repository:

* `assvc start` — Initialize a new `.assvc` folder in the current directory

### Install tool:

* `assvc installer` — Install or uninstall `assvc` to/from `~/.local/bin`


### Repository operations

* `assvc repository import <zip_path>` — Import repository data from a zip file
* `assvc repository export` — Export repository data

### Create a commit:

* `assvc commit -m "message"` — Create a new commit with a message (default: "Commit without message")
* `assvc commit` — Commit with default message


### Compare changes:

* `assvc compare all -s ` — Compare changes between latest commit and working directory
* `assvc compare all -s <sha>` — Compare changes between selected commit and working directory 
* `assvc compare all -d` — Compare changes (with diff output) between selected commit and working directory
* `assvc compare diff <file_path>` — Write the differences between lates commit and curent version of singular file
* `assvc compare diff -s <sha> <file_path>` — Write the differences between selected commit and curent version of singular file

### View history:

* `assvc history` — Show commit history


### Reverse:

* `assvc reverse` — Revert the working directory to latest commit
* `assvc reverse -s <sha>` — Revert the working directory to selected commit
* `assvc reverse -f` — Revert without confirmation


### Staging
* `assvc staging stage <file_path>` — Stage files for commit
* `assvc staging stage -a` — Stage all changed files for commit
* `assvc staging unstage <file_path>` — Unstage files from commit
* `assvc staging clear` — Clear all staged files
* `assvc staging show` — See all staged files

### Help
* `assvc help` — Shows help message



## Other functions

### Ignore
* `.assignore` — you can  add file called .assignore where you can add files and folder that you dont want to commit, compare, reverse or show diff.
