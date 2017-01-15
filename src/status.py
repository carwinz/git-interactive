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

def move_cursor_to_closest_line():
    line = current_line()
    if line == None or not is_line_a_file(line):
        move_cursor_up()
        line = current_line()
    if line == None or not is_line_a_file(line):
        move_cursor_down()

def show_status():
    global status
    status = check_output(["git", "status"])
    stdscr.clear()
    stdscr.addstr(0, 0, status)
    stdscr.refresh()
    curses.setsyx(cursor_line, 0)
    curses.doupdate()
    move_cursor_to_closest_line()

def current_line():
    global cursor_line
    global status
    lines = status.split('\n')
    if cursor_line + 1 > len(lines):
        return None
    return lines[cursor_line]

def move_cursor_up():
    global cursor_line
    global status
    status_lines = status.split('\n')
    potential_line = cursor_line
    if potential_line > len(status_lines):
        potential_line = len(status_lines)-1
    while potential_line > 0:
        potential_line = potential_line - 1
        if is_line_a_file(status_lines[potential_line]):
            cursor_line = potential_line
            curses.setsyx(cursor_line, 0)
            curses.doupdate()
            break

def move_cursor_down():
    global cursor_line
    global status
    status_lines = status.split('\n')
    potential_line = cursor_line
    if potential_line > len(status_lines):
        potential_line = len(status_lines)-1
    while potential_line < len(status_lines)-1:
        potential_line = potential_line + 1
        if is_line_a_file(status_lines[potential_line]):
            cursor_line = potential_line
            curses.setsyx(cursor_line, 0)
            curses.doupdate()
            break

def is_line_a_file(line):
    return line.startswith("	")

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

def git_rm():
    line = selected_line().replace('deleted:', '')
    call(["git", "rm", line.strip()])
    show_status()

def delete():
    line = selected_line()
    call(["rm", line.strip()])
    show_status()

stdscr = curses.initscr()

curses.noecho() # Don't echo keys to the screen
curses.cbreak() # react to keys without requiring the Enter key to be pressed
stdscr.keypad(1) # have curses translate special keys

signal.signal(signal.SIGINT, signal_handler)

show_status()
move_cursor_down()

while 1:
    c = stdscr.getch()
    if c == ord('q'):
        break
    elif c == ord('a'):
        add()
    elif c == ord('c'):
        checkout()
    elif c == ord('d'):
        delete()
    elif c == ord('r'):
        git_rm()
    elif c == ord('i'):
        ignore()
    elif c == ord('u'):
        unstage()
    elif c == curses.KEY_UP or c == ord('k'):
        move_cursor_up()
    elif c == curses.KEY_DOWN or c == ord('j'):
        move_cursor_down()
    else:
        show_status()

exit()
