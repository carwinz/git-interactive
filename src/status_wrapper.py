#!/usr/bin/python

from subprocess import check_output

class StatusWrapper():

    selected_line_index = 0
    status = ''
    status_lines = []

    def update_status(self):
        self.status = check_output(["git", "status"])
        self.status_lines = self._split_status_into_lines()
        self.move_selection_to_closest_line()

    def move_selection_to_closest_line(self):
        line = self.current_line()
        if line == None or not self._is_line_a_file(line):
            self.move_selection_up()
            line = self.current_line()
        if line == None or not self._is_line_a_file(line):
            self.move_selection_down()

    def current_line(self):
        if self.selected_line_index + 1 > len(self.status_lines):
            return None
        return self.status_lines[self.selected_line_index]

    def move_selection_up(self):
        potential_line = self.selected_line_index
        if potential_line > len(self.status_lines):
            potential_line = len(self.status_lines)-1
        while potential_line > 0:
            potential_line = potential_line - 1
            if self._is_line_a_file(self.status_lines[potential_line]):
                self.selected_line_index = potential_line
                break

    def move_selection_down(self):
        potential_line = self.selected_line_index
        if potential_line > len(self.status_lines):
            potential_line = len(self.status_lines)-1
        while potential_line < len(self.status_lines)-1:
            potential_line = potential_line + 1
            if self._is_line_a_file(self.status_lines[potential_line]):
                self.selected_line_index = potential_line
                break

    def _split_status_into_lines(self):
        return self.status.split('\n')

    def _is_line_a_file(self, line):
        return line.startswith("	")

    def selected_file(self):
        return self.selected_line().replace('new file:','').replace('modified:', '').replace('deleted:', '').strip()

    def selected_line(self):
        return self.status_lines[self.selected_line_index]

    def current_status(self):
        return self.status
