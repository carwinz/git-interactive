#!/usr/bin/python

import curses
import mimetypes
import os.path
from subprocess import check_output
from scrollable_window import ScrollableWindow
from scrollable_window_renderer import ScrollableWindowRenderer

class GitDiff():

    def __init__(self, main_window):
        self.main_window = main_window

    def _line_renderer(self, line):
        if line.startswith('+'):
            return 1, line
        elif line.startswith('-'):
            return 2, line
        else:
            return None, line

    def _is_binary_file(self, filename):
        textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
        is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
        return is_binary_string(open(filename, 'rb').read(1024))

    def show(self, filename, isStaged, isUntracked, footerText):
        self.footerText = footerText

        if self._is_binary_file(filename):
            diff = "Unable to diff binary files"
        else:
            if isUntracked:
                if os.path.isfile(filename):
                    with open(filename, 'r') as myfile:
                        diff = myfile.read()
                else:
                    diff = 'File no longer exists or is a directory'
            else:
                command = ["git", "diff"]
                if isStaged:
                    command.append('--staged')
                command.append(filename)
                diff = check_output(command)

        self.diff_window = ScrollableWindow(self._line_renderer, None, self._footer_text, ScrollableWindowRenderer())
        self.diff_window.display(diff.split("\n"), 0)

        while 1:
            c = self.main_window.getch()
            if c == curses.KEY_UP or c == ord('k'):
                self.diff_window.line_up()
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.diff_window.line_down()
            elif c == curses.KEY_PPAGE:
                self.diff_window.page_up()
            elif c == curses.KEY_NPAGE:
                self.diff_window.page_down()
            elif c == curses.KEY_RESIZE:
                self.diff_window.display(diff.split("\n"), 0)
            else:
                return c

    def _footer_text(self, line):
        return self.footerText
