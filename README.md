# assvc
Version control made by me.

## Commands

Initialize repository:

* `assvc start` — create a `.assvc` folder in the current directory

Create a commit:

* `assvc commit -m "message"` — commit current changes
* `assvc commit` — commit with default message

Compare changes:

* `assvc compare` — show differences between latest commit and working directory 
* `assvc compare -s "sha"` — show differences between selected commit and working directory
* `assvc compare -d` — show differences between selected commit and working directory with show diff output

View history:

* `assvc history` — list previous commits

Install tool:

* `assvc installer` — install or uninstall `assvc` to `~/.local/bin`

Reverse:

* `assvc reverse` — reverse the working directory to latest commit
* `assvc reverse -s "sha"` — reverse the working directory to selected commit