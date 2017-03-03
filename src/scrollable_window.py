#!/usr/bin/python

import curses
import logging

class ScrollableWindow():

    def __init__(self, line_renderer, can_cursor_visit_line, dynamic_footer_creator, window_renderer):
        logging.basicConfig(filename='/tmp/git-interactive.log',level=logging.DEBUG)

        self.line_renderer = line_renderer
        self.can_cursor_visit_line = can_cursor_visit_line
        self.dynamic_footer_creator = dynamic_footer_creator
        self.window_renderer = window_renderer

        self.footer_line = None
        self.cursor_row_index = None
        self.first_row_of_visible_content = 0
        if (self.can_cursor_visit_line == None):
            self.can_cursor_visit_line = self._default_can_cursor_visit_line

    def resize(self):
        self.window_renderer.resize()
        self.display(self.lines, self.cursor_row_index)

    def _default_can_cursor_visit_line(self, line):
        return True

    def _usable_rows(self):
        usable_rows = self.window_renderer.max_rows_on_screen()
        if self.dynamic_footer_creator:
            usable_rows = usable_rows - 1
        return usable_rows

    def line_down(self):
        if self.cursor_row_index == None:
            return
        lines = self.lines
        moved = False
        num_lines_in_content = len(lines)
        potential_cursor = self.cursor_row_index
        new_cursor_index = self.cursor_row_index

        while (potential_cursor + self.first_row_of_visible_content) < (num_lines_in_content - 1):
            potential_cursor = potential_cursor + 1
            if self.can_cursor_visit_line(lines[potential_cursor + self.first_row_of_visible_content]):
                usable_rows = self._usable_rows()
                if potential_cursor >= usable_rows:
                    self.first_row_of_visible_content = self.first_row_of_visible_content + potential_cursor - usable_rows + 1
                    potential_cursor = usable_rows - 1
                moved = True
                new_cursor_index = potential_cursor
                break
        if not moved:   # maybe scroll content into view
            rows_on_screen = self.window_renderer.max_rows_on_screen()
            if ((rows_on_screen + self.first_row_of_visible_content + 1) < num_lines_in_content) and new_cursor_index - 1 >= 0:
                self.first_row_of_visible_content = self.first_row_of_visible_content + 1
                new_cursor_index = new_cursor_index - 1
                moved = True
        if moved:
            self.display(lines, new_cursor_index)

    def line_up(self):
        if self.cursor_row_index == None:
            return
        lines = self.lines
        moved = False
        potential_cursor = self.cursor_row_index
        new_cursor_index = self.cursor_row_index
        while potential_cursor + self.first_row_of_visible_content > 0:
            potential_cursor = potential_cursor - 1
            if self.can_cursor_visit_line(lines[potential_cursor + self.first_row_of_visible_content]):
                if potential_cursor < 0:
                    self.first_row_of_visible_content = self.first_row_of_visible_content + potential_cursor
                    potential_cursor = 0
                new_cursor_index = potential_cursor
                moved = True
                break
        if not moved:   # maybe scroll content into view
            if self.first_row_of_visible_content > 0:
                self.first_row_of_visible_content = self.first_row_of_visible_content - 1
                new_cursor_index = new_cursor_index + 1
                moved = True
        if moved:
            self.display(lines, new_cursor_index)

    def is_cursor_at_end(self, num_lines):
        return self.cursor_row_index + self.first_row_of_visible_content + 1 == num_lines

    def page_up(self):
        if self.cursor_row_index == None:
            return
        usable_rows = self._usable_rows()
        num_lines_in_content = len(self.lines)

        if num_lines_in_content <= usable_rows: # everything on one screen
            self.first_row_of_visible_content = 0
            potential_cursor = 0
            while potential_cursor < usable_rows and not self.can_cursor_visit_line(self.lines[potential_cursor]):
                potential_cursor = potential_cursor + 1
            self.display(self.lines, potential_cursor)
        else:
            first_row_of_visible_content = self.first_row_of_visible_content - usable_rows
            potential_cursor = 0
            logging.debug(str(first_row_of_visible_content + potential_cursor) + " " + str(self.can_cursor_visit_line(self.lines[first_row_of_visible_content + potential_cursor])))
            while first_row_of_visible_content + potential_cursor >= 0 and not self.can_cursor_visit_line(self.lines[first_row_of_visible_content + potential_cursor]):
                potential_cursor = potential_cursor + 1
                if potential_cursor >= usable_rows:
                    potential_cursor = potential_cursor - usable_rows
                    first_row_of_visible_content = first_row_of_visible_content - usable_rows

            self.first_row_of_visible_content = first_row_of_visible_content
            self.display(self.lines, potential_cursor)

    def page_down(self):
        if self.cursor_row_index == None:
            return
        usable_rows = self._usable_rows()
        num_lines_in_content = len(self.lines)
        if not self.is_cursor_at_end(num_lines_in_content):
            if num_lines_in_content <= usable_rows: # everything on one screen
                self.first_row_of_visible_content = 0
                potential_cursor = num_lines_in_content - 1
                while potential_cursor > 0 and not self.can_cursor_visit_line(self.lines[potential_cursor]):
                    potential_cursor = potential_cursor - 1

                self.display(self.lines, potential_cursor)
            else:
                first_row_of_visible_content = self.first_row_of_visible_content + usable_rows

                potential_cursor = 0
                while first_row_of_visible_content + potential_cursor < num_lines_in_content and not self.can_cursor_visit_line(self.lines[first_row_of_visible_content + potential_cursor]):
                    potential_cursor = potential_cursor + 1

                while potential_cursor > usable_rows - 1:
                    first_row_of_visible_content = first_row_of_visible_content + usable_rows
                    potential_cursor = potential_cursor - usable_rows

                # TODO: its weird that first_row_of_visible_content is outside of "display"
                self.first_row_of_visible_content = first_row_of_visible_content
                self.display(self.lines, potential_cursor)

    def display(self, lines, cursor_row_index):
        self.lines = lines
        self.cursor_row_index = cursor_row_index
        self.visible_lines = self._which_lines_are_visible(lines)
        if self.dynamic_footer_creator and self.cursor_row_index != None:
            self.footer_line = self.dynamic_footer_creator(lines[self.cursor_row_index + self.first_row_of_visible_content])
        self.window_renderer.display(self._lines_to_dict(self.visible_lines), self.cursor_row_index, self.footer_line)

    def _lines_to_dict(self, lines):
        result = []

        index = 0
        while index < len(lines):
            line = lines[index]
            colour, text = self.line_renderer(line)
            result.append({'colour': colour, 'text': text})
            index = index + 1

        return result

    def get_cursor_row_index(self):
        return self.cursor_row_index

    def get_visible_lines(self):
        return self.visible_lines

    def get_first_row_of_visible_content(self):
        return self.first_row_of_visible_content

    def get_current_line(self):
        return self.lines[self.cursor_row_index + self.first_row_of_visible_content] if self.cursor_row_index else None

    def get_footer_line(self):
        return self.footer_line

    def _which_lines_are_visible(self, lines):
        result = []
        line_on_screen = 0
        line_index = self.first_row_of_visible_content
        rows_on_screen = self.window_renderer.max_rows_on_screen()
        if self.dynamic_footer_creator:
            rows_on_screen = rows_on_screen - 1

        while line_on_screen < rows_on_screen and line_index < len(lines):
            result.append(lines[line_index])
            line_on_screen = line_on_screen + 1
            line_index = line_index + 1

        return result
