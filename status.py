#!/usr/bin/python

import signal
import sys
import curses
from subprocess import call
from subprocess import check_output

cursor_line = 0
status = ''

def signal_handler(signal, frame):
    exit()
    sys.exit(0)

def exit():
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

def show_status():
    global status
    status = check_output(["git", "status"])
    stdscr.clear()
    stdscr.addstr(0, 0, status)
    stdscr.refresh()
    curses.setsyx(cursor_line, 0)
    curses.doupdate()

def move_cursor_up():
    global cursor_line
    if cursor_line > 0:
        cursor_line = cursor_line - 1
    curses.setsyx(cursor_line, 0)
    curses.doupdate()

def move_cursor_down():
    global cursor_line
    cursor_line = cursor_line + 1
    curses.setsyx(cursor_line, 0)
    curses.doupdate()

def selected_line():
    return status.split('\n')[cursor_line]

def add():
    line = selected_line().replace('modified:', '')
    call(["git", "add", line.strip()])
    show_status()

def checkout():
    line = selected_line().replace('modified:', '')
    call(["git", "checkout", line.strip()])
    show_status()

def unstage():
    line = selected_line().replace('modified:', '')
    call(["git", "reset", "HEAD", line.strip()])
    show_status()

def ignore():
    line = selected_line()
    with open(".gitignore", "a") as ignores:
        ignores.write(line.strip())
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
    elif c == ord('i'):
        ignore()
    elif c == ord('u'):
        unstage()
    elif c == curses.KEY_UP:
        move_cursor_up()
    elif c == curses.KEY_DOWN:
        move_cursor_down()
    else:
        show_status()

exit()
