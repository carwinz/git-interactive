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

    def _selected_line(self):
        return self.status_lines[self.selected_line_index]

    def line_count(self):
        return len(self.status_lines)

    def selected_file(self):
        return self._selected_line().replace('new file:','').replace('modified:', '').replace('deleted:', '').strip()

    def selected_file_section(self):
        line = self.selected_line_index
        while line > 0:
            line = line - 1
            if  (len(self.status_lines) > line):
                if self._is_untracked_line(self.status_lines[line]):
                    return 'Untracked'
                if self._is_not_staged_line(self.status_lines[line]):
                    return 'Not Staged'
                if self._is_staged_line(self.status_lines[line]):
                    return 'Staged'
        return None

    def _is_untracked_line(self, line):
        return 'Untracked files:' == line

    def _is_not_staged_line(self, line):
        return 'Changes not staged for commit:' == line

    def _is_staged_line(self, line):
        return 'Changes to be committed:' == line

    def can_amend_commit(self):
        for line in self.status_lines:
            if line.startswith('Your branch is ahead of'):
                return True
        return False

    def current_status(self):
        return self.status

    def current_status_annotated(self):
        result = []
        section = None
        for line in self.status_lines:
            if self._is_untracked_line(line):
                section = 'Untracked'
            if self._is_not_staged_line(line):
                section = 'Not Staged'
            if self._is_staged_line(line):
                section = 'Staged'
            result.append({'line': line, 'section': section, 'isAFile': self._is_line_a_file(line)})
        return result
