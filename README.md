
Make the __git status__ command interactive.

Instead of running 'git status' and then running another command for each file (e.g. git add somedir/somefile), this removes the need for the second command. Instead you can hit a single key to stage, checkout, etc files.

Simply use the arrow keys to go the appropriate line and press one of the following:

* a - to add/stage
* c - to checkout/revert a file
* d - to delete a file
* i - to add to the ignore file
* u - to unstage the file

## Installation

  cp dist/git-interactive /usr/local/bin/
  chmod +x /usr/local/bin/git-interactive

Then run:

  git interactive
