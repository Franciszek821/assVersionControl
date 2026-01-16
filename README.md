# assvc
Version control made by me.
Linux version only for now.
To install globally to work everywhere use command ./assvcLinux install.
After installing globally use command "assvc -h".

## Commands

Initialize repository:

* `assvc start` — Initialize a new `.assvc` folder in the current directory

Create a commit:

* `assvc commit -m "message"` — Create a new commit with a message (default: "Commit without message")
* `assvc commit` — Commit with default message

Compare changes:

* `assvc compare` — Compare changes between latest commit and working directory
* `assvc compare -s "sha"` — Compare changes between selected commit and working directory
* `assvc compare -d` — Compare changes (with diff output) between selected commit and working directory

View history:

* `assvc history` — Show commit history

Install tool:

* `assvc installer` — Install or uninstall `assvc` to/from `~/.local/bin`

Reverse:

* `assvc reverse` — Revert the working directory to latest commit
* `assvc reverse -s "sha"` — Revert the working directory to selected commit

Import / Export:

* `assvc import <zip_path>` — Import repository data from a zip file
* `assvc export` — Export repository data

Ignore
* `.assignore` — you can  add file called .assignore where you can add files and folder that you dont want to commit and/or compare and/or reversed
