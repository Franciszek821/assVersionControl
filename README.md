# Assvc

Version control app for one person project, made for both terminal and graphic possibilities.

## Requirements
- Python 3.10+
- External dependencies are listed in the requirements.txt file which you can install with command `pip install -r requirements.txt`.

## Installing assvc terminal version on linux

Use command `chmod +x ./assvc` to give permission to file. To install globally to work everywhere use command `./assvc install`. After installing globally you can use command `assvc -h`.

## Installing assvc graphic version on linux
Use command `chmod +x ./assvc-gui` to give permission to file. There is no need to install globally.

# Assvc terminal
## Commands

### Initialize repository:
*  `assvc start` — Initialize a new `.assvc` folder in the current directory

### Repository operations

*  `assvc repository import <zip_path>` — Import repository data from a zip file

*  `assvc repository export` — Export repository data

  

### Create a commit:

*  `assvc commit -m "message"` — Create a new commit with a message (default: "Commit without message")

*  `assvc commit` — Commit with default message

### Compare changes:

*  `assvc compare all -s ` — Compare changes between latest commit and working directory

*  `assvc compare all -s <sha>` — Compare changes between selected commit and working directory

*  `assvc compare all -d` — Compare changes (with diff output) between selected commit and working directory

*  `assvc compare diff <file_path>` — Write the differences between latest commit and current version of singular file

*  `assvc compare diff -s <sha> <file_path>` — Write the differences between selected commit and current version of singular file

### View history:

*  `assvc history` — Show history of the repository

### Reverse:
*  `assvc reverse` — Revert the working directory to latest commit

*  `assvc reverse -s <sha>` — Revert the working directory to selected commit

*  `assvc reverse -f` — Revert without confirmation

*  `assvc reverse -s <sha> <file_path>` — Revert a single file to selected commit

*  `assvc reverse <file_path>` — Revert a single file to latest commit

### Staging

*  `assvc staging stage <file_path>` — Stage files for commit

*  `assvc staging stage -a` — Stage all changed files for commit

*  `assvc staging unstage <file_path>` — Unstage files from commit

*  `assvc staging clear` — Clear all staged files

*  `assvc staging show` — See all staged files
### Help
*  `assvc help` — Shows help message

## Other functions
### Ignore

*  `.assignore` — you can add file called .assignore where you can add files and folder that you dont want to commit, compare, reverse or show diff.

# Assvc gui
## Main screen
On the main screen you have 3 main options:
* Import Repository - Imports a .assvc repository and unpacks it from a .zip file. First you choose a zip file later a destination for the repository.
* New Repository - You choose a repository destination and the app creates the .assvc folder in directory.
* Open Repository - You choose a repository and the app opens the repository for you.

![Main screen](https://github.com/Franciszek821/assVersionControl/blob/main/readmePictures/main.png)


## Repository Screen
### Changes screen
In the changes screen we have:

On the left sidebar you have (From the top):
- Name of the repository.
- Tabs (Changes/History).
- Amount of changed files and a refresh button.
- list of the changed files ([Go to Schemat of files](#schemat-of-files)).
- 2 buttons, one for staging all and second for reverting the changes for all files.
- The input for message for commit.
- The button for commiting the working version to repository

In the space thats left we have:
- The name of the selected file
- 2 codeblocks with the version before changes and version after changes, the deleted things are marked with red highlighter and added are marked with green highlighter.

![Changes Screen](https://github.com/Franciszek821/assVersionControl/blob/main/readmePictures/child-diff.png)

### History screen
In the history screen we have: 
- Name of the repository.
- Tabs (Changes/History).
- Amount of commits and a refresh button.
- List of the commits we shorten sha, message, and date/hour.
- The input for message for commit.
- The button for commiting the working version to repository

![Changes Screen](https://github.com/Franciszek821/assVersionControl/blob/main/readmePictures/child-history.png)

### Keybinds
* F1 - New Repository
* F2 - Open Repository
* F3 - Open in Explorer
* F4 - Import Repository
* F5 - Export Repository
* F6 - Help
* F7 - About


### Schemat of files

#### First we have the icon for status of the file:
- Yellow circle with a square yellow outline for modified file
- Red minus with a square red outline for deleted file
- Green plus with a square green outline for added file

#### After a status icon we have the name of the file.
#### After that we have the 3 buttons:
- First one for opening the file location in file explorer
- Second one for staging the file
- Third one for reversing the change, deletion or adding


