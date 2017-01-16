#!/usr/bin/python

import signal
import sys
import curses
from subprocess import call
from subprocess import check_output
from status_wrapper import StatusWrapper

status_wrapper = StatusWrapper()

def signal_handler(signal, frame):
    exit()
    sys.exit(0)

def exit():
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

def show_status():
    status_wrapper.update_status()
    stdscr.clear()
    stdscr.addstr(0, 0, status_wrapper.current_status())
    stdscr.refresh()
    update_cursor()

def update_cursor():
    curses.setsyx(status_wrapper.selected_line_index, 0)
    curses.doupdate()

def add():
    call(["git", "add", status_wrapper.selected_file()])
    show_status()

def checkout():
    call(["git", "checkout", status_wrapper.selected_file()])
    show_status()

def unstage():
    call(["git", "reset", "HEAD", status_wrapper.selected_file()])
    show_status()

def ignore():
    with open(".gitignore", "a") as ignores:
        ignores.write(status_wrapper.selected_file())
    show_status()

def git_rm():
    line = status_wrapper.selected_file()
    call(["git", "rm", line.strip()])
    call(["rm", line.strip()])
    show_status()

def diff():
    diff = check_output(["git", "diff", "--staged", status_wrapper.selected_file()])
    stdscr.clear()
    stdscr.addstr(0, 0, diff)
    stdscr.refresh()
    stdscr.getch()
    show_status()

stdscr = curses.initscr()

curses.noecho() # Don't echo keys to the screen
curses.cbreak() # react to keys without requiring the Enter key to be pressed
stdscr.keypad(1) # have curses translate special keys

signal.signal(signal.SIGINT, signal_handler)

show_status()

while 1:
    c = stdscr.getch()
    if c == ord('q'):
        break
    elif c == ord('a'):
        add()
    elif c == ord('c'):
        checkout()
    elif c == ord('d'):
        diff()
    elif c == ord('r'):
        git_rm()
    elif c == ord('i'):
        ignore()
    elif c == ord('u'):
        unstage()
    elif c == curses.KEY_UP or c == ord('k'):
        status_wrapper.move_selection_up()
        update_cursor()
    elif c == curses.KEY_DOWN or c == ord('j'):
        status_wrapper.move_selection_down()
        update_cursor()
    else:
        show_status()

exit()
