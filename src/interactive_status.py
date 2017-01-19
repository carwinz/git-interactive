#!/usr/bin/python

import signal
import sys
import curses
from subprocess import call
from subprocess import check_output
from status_wrapper import StatusWrapper

class InteractiveStatus():

    status_wrapper = StatusWrapper()

    def signal_handler(self, signal, frame):
        self.exit()
        sys.exit(0)

    def exit(self):
        curses.nocbreak(); self.stdscr.keypad(0); curses.echo()
        curses.endwin()

    def show_status(self):
        self.status_wrapper.update_status()
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, self.status_wrapper.current_status())
        file_section = self.status_wrapper.selected_file_section()
        if file_section == 'Staged':
            self.stdscr.addstr(self.status_wrapper.line_count(), 0, 'actions: d = view diff; u = unstage; f = commit; q = quit')
        if file_section == 'Not Staged':
            self.stdscr.addstr(self.status_wrapper.line_count(), 0, 'actions: a = add/stage; c = checkout; d = view diff; r = delete; f = commit; q = quit')
        if file_section == 'Untracked':
            self.stdscr.addstr(self.status_wrapper.line_count(), 0, 'actions: a = add/stage; i = ignore; r = delete; f = commit; q = quit')
        self.stdscr.refresh()
        self.update_cursor()

    def update_cursor(self):
        curses.setsyx(self.status_wrapper.selected_line_index, 0)
        curses.doupdate()

    def add(self):
        call(["git", "add", self.status_wrapper.selected_file()])
        self.show_status()

    def checkout(self):
        call(["git", "checkout", self.status_wrapper.selected_file()])
        self.show_status()

    def unstage(self):
        call(["git", "reset", "HEAD", self.status_wrapper.selected_file()])
        self.show_status()

    def ignore(self):
        with open(".gitignore", "a") as ignores:
            ignores.write(self.status_wrapper.selected_file())
        self.show_status()

    def git_rm(self):
        line = self.status_wrapper.selected_file()
        if self.status_wrapper.selected_file_section() == 'Untracked':
            call(["rm", line.strip()])
        else:
            call(["git", "rm", line.strip()])
        self.show_status()

    def commit(self):
        curses.echo()
        curses.raw()
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, 'Commit message: ')
        self.stdscr.refresh()
        output = check_output(["git", "commit", "-m", self.stdscr.getstr()])
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, output)
        self.stdscr.refresh()
        curses.noecho()
        curses.cbreak()

    def diff(self):
        command = ["git", "diff"]
        if self.status_wrapper.selected_file_section() == 'Staged':
            command.append('--staged')
        command.append(self.status_wrapper.selected_file())
        diff = check_output(command)
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, diff)
        self.stdscr.refresh()
        self.stdscr.getch()
        self.show_status()

    def run(self):

        self.stdscr = curses.initscr()

        curses.noecho() # Don't echo keys to the screen
        curses.cbreak() # react to keys without requiring the Enter key to be pressed
        self.stdscr.keypad(1) # have curses translate special keys

        signal.signal(signal.SIGINT, self.signal_handler)

        self.show_status()

        while 1:
            c = self.stdscr.getch()
            if c == ord('q'):
                break
            elif c == ord('a'):
                self.add()
            elif c == ord('c'):
                self.checkout()
            elif c == ord('d'):
                self.diff()
            elif c == ord('r'):
                self.git_rm()
            elif c == ord('i'):
                self.ignore()
            elif c == ord('u'):
                self.unstage()
            elif c == ord('f'):
                self.commit()
            elif c == curses.KEY_UP or c == ord('k'):
                self.status_wrapper.move_selection_up()
                self.show_status()
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.status_wrapper.move_selection_down()
                self.show_status()
            else:
                self.show_status()

        self.exit()
