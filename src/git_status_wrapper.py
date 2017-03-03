#!/usr/bin/python

from subprocess import check_output

class GitStatusWrapper():

    status = ''
    status_lines = []

    def update_status(self):
        self.status = check_output(["git", "status"])
        self.status_lines = self._split_status_into_lines()

    def _split_status_into_lines(self):
        return self.status.split('\n')

    def _is_line_a_file(self, line):
        return line.startswith("\t")

    def line_count(self):
        return len(self.status_lines)

    def selected_file(self):
        return self._extract_filename(self._selected_line())

    def _extract_filename(self, line):
        return line.replace('new file:','').replace('both modified:', '').replace('modified:', '').replace('deleted by them:', '').replace('deleted:', '').strip()

    def _is_untracked_line(self, line):
        return 'Untracked files:' == line

    def _is_not_staged_line(self, line):
        return 'Changes not staged for commit:' == line

    def _is_staged_line(self, line):
        return 'Changes to be committed:' == line

    def _is_unmerged_line(self, line):
        return 'Unmerged paths:' == line

    def can_amend_commit(self):
        for line in self.status_lines:
            if line.startswith('Your branch is ahead of'):
                return True
        return False

    def current_status(self):
        return self.status

    def last_status_annotated(self):
        result = []
        section = None
        for line in self.status_lines:
            if self._is_untracked_line(line):
                section = 'Untracked'
            if self._is_not_staged_line(line):
                section = 'Not Staged'
            if self._is_staged_line(line):
                section = 'Staged'
            if self._is_unmerged_line(line):
                section = 'Unmerged'
            isAFile = self._is_line_a_file(line)
            filename = self._extract_filename(line) if isAFile else None
            result.append({'line': line, 'section': section, 'isAFile': isAFile, 'filename': filename})
        return result
