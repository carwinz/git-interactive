
Make the __git status__ command interactive.

Instead of running 'git status' and then running another command for each file (e.g. git add somedir/somefile), this removes the need for typing follow-up commands. Instead you can hit a single key to stage a file, checkout a file, etc.

Simply use the arrow keys to go the appropriate line and press one of the following:

* a - to add/stage
* c - to checkout/revert a file
* d - to delete a file
* i - to add to the ignore file
* u - to unstage the file

## Building

    ./scripts/bundle

## Installation

    ./scripts/install

Then run:

    git interactive

## Running locally

    ./scripts/bundle && dist/git-interactive

## Roadmap

* BUG: when status has a log of lines, the app crashes
* Use colour in the status
* Stage individual chunks
* Show which commits
* Make git log easier
