#!/usr/bin/python

import curses

class ScrollableWindowRenderer():

    def __init__(self):
        self.cursor_row_index = None
        self.resize()

    def resize(self):
        self.window = curses.newwin(curses.LINES - 1, curses.COLS - 1, 0, 0)
        self.window.scrollok(1)
        self.window.refresh()

    def max_rows_on_screen(self):
        return self.window.getmaxyx()[0] - 1 # curses has some issues with writing to the last line

    def display(self, lines, cursor_row_index, footer_line):
        self.window.erase()
        self._render(lines)
        if footer_line != None:
            self.window.addstr(self.max_rows_on_screen(), 0, footer_line)
            self.window.refresh()
        if cursor_row_index != None:
            self._update_cursor(cursor_row_index)


    def _update_cursor(self, cursor_row_index):
        curses.setsyx(cursor_row_index, 0)
        curses.doupdate()

    def _render(self, lines):
        index = 0
        while index < len(lines):
            line = lines[index]
            if 'colour' in line and line['colour'] != None:
                self.window.addstr(index, 0, line['text'], curses.color_pair(line['colour']))
            else:
                self.window.addstr(index, 0, line['text'])
            index = index + 1
        self.window.refresh()
