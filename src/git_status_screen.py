#!/usr/bin/python

import sys
import curses
import os
import subprocess
from subprocess import call
from git_status_wrapper import GitStatusWrapper
from git_diff_screen import GitDiffScreen
from git import Git
from scrollable_window import ScrollableWindow
from scrollable_window_renderer import ScrollableWindowRenderer

class GitStatusScreen():

    status_wrapper = GitStatusWrapper()

    def __init__(self, main_window):
        self.main_window = main_window

    def show_status(self, section, fileToHighlight):
        self.status_wrapper.update_status()
        self._determine_cursor_row_and_render_lines(section, fileToHighlight)

    def _determine_cursor_row_and_render_lines(self, section, fileToHighlight):
        cursor_row = None
        if fileToHighlight != None:
            cursor_row = self._line_index_of_filename(section, fileToHighlight)
        if cursor_row == None and section != None:
            cursor_row = self._line_index_of_last_file_in_section(section)
        if cursor_row == None:
            cursor_row = self._line_index_of_first_file()

        self.status_window.display(self.status_wrapper.last_status_annotated(), cursor_row)

    def _line_index_of_last_file_in_section(self, section):
        i = 0
        result = None
        for line in self.status_wrapper.last_status_annotated():
            if line['section'] == section and line['isAFile']:
                section, nextFile = self._find_status_file_after(line['section'], line['filename'])
                result = i
            i = i + 1

        return result

    def _line_index_of_first_file(self):
        i = 0
        for line in self.status_wrapper.last_status_annotated():
            if line['isAFile']:
                return i
            i = i + 1
        return None

    def _line_index_of_filename(self, section, filename):
        i = 0
        for line in self.status_wrapper.last_status_annotated():
            if line['section'] == section and line['isAFile'] and line['filename'] == filename:
                return i
            i = i + 1
        return 0

    def _find_status_file_after(self, section, filename):
        found = False
        for line in self.status_wrapper.last_status_annotated():
            if line["isAFile"]:
                if found:
                    return line['section'], line['filename']
                if line['section'] == section and line['filename'] == filename:
                    found = True
        return None, None

    def _footer_shortcut_reminders(self, line):
        commitOptions =  "f = commit; " + ('g = commit amend; ' if self.status_wrapper.can_amend_commit() else '')
        stashOptions = 's = stash menu; '
        quitOptions = "q = quit"
        pushOptions = ('p = push; ' if self.status_wrapper.can_amend_commit() else '')
        file_section = line['section']
        if file_section == 'Staged':
            return 'actions: d = view diff; u = unstage; ' + commitOptions + pushOptions + stashOptions + quitOptions
        if file_section == 'Not Staged':
            return 'actions: a = add/stage; c = checkout; d = view diff; r = delete; ' + commitOptions + pushOptions + stashOptions + quitOptions
        if file_section == 'Unmerged':
            return 'actions: a = add/stage; r = delete; ' + pushOptions + stashOptions + quitOptions
        if file_section == 'Untracked':
            return 'actions: a = add/stage; i = ignore; r = delete; ' + commitOptions + pushOptions + stashOptions + quitOptions
        return pushOptions + quitOptions

    def ignore(self, filename):
        # TODO needs to be smarter and find the root of the git repo
        # TODO perhaps it could stage the change as well if there are no other changes
        with open(".gitignore", "a") as ignores:
            ignores.write(filename + '\n')

    def git_rm(self, filename, section):
        if section == 'Untracked':
            call(["rm", filename])
        elif section == 'Not Staged':
            call(["git", "rm", "-f", filename])
        else:
            call(["git", "rm", filename])

    def _show_text(self, text):
        self.main_window.clear()
        self.main_window.addstr(text)
        self.main_window.refresh()

    def _show_text_and_wait_for_keypress(self, text):
        self._show_text(text)
        self.main_window.getch()
        self.main_window.clear()
        self.main_window.refresh()

    def push(self):
        self.main_window.clear()
        self.main_window.addstr(0, 0, 'Pushing to remote...\n')
        self.main_window.refresh()

        cmd = ["git", "push", "--porcelain"]

        output = ''
        for line in self.execute_streaming(cmd):
            output = output + line
            self.main_window.clear()
            self.main_window.addstr(output)
            self.main_window.refresh()

        self.main_window.addstr("Push finished. Press any key")
        self.main_window.refresh()

        self.main_window.getch()
        self.main_window.clear()
        self.main_window.refresh()

    def execute_streaming(self, cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ''):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def commit(self):
        curses.echo()
        curses.raw()
        self.main_window.clear()
        self.main_window.addstr(0, 0, 'Commit message: ')
        self.main_window.refresh()
        command = ["git", "commit", "-m", self.main_window.getstr()]
        curses.noecho()
        curses.cbreak()

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.main_window.clear()
        stdout, stderr = p.communicate()
        self.main_window.addstr(0, 0, stdout)
        self.main_window.refresh()
        self.main_window.getch()

    def _can_cursor_visit_line(self, line):
        return line['isAFile']

    def _git_status_line_renderer(self, line):
        if line['isAFile'] and line['section'] == 'Staged':
            return 1, line['line']
        elif line['isAFile']:
            return 2, line['line']
        else:
            return None, line['line']

    def show(self):
        followupWith = None
        self.status_window = ScrollableWindow(self._git_status_line_renderer, self._can_cursor_visit_line, self._footer_shortcut_reminders, ScrollableWindowRenderer())
        self.show_status(None, None)
        while 1:
            if followupWith:
                c = followupWith
                followupWith = None
            else:
                c = self.main_window.getch()
            line = self.status_window.get_current_line()
            if c == curses.KEY_UP or c == ord('k'):
                self.status_window.line_up()
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.status_window.line_down()
            elif c == curses.KEY_PPAGE:
                self.status_window.page_up()
            elif c == curses.KEY_NPAGE:
                self.status_window.page_down()
            elif c == ord('a'):
                if line['isAFile']:
                    section, nextFile = self._find_status_file_after(line['section'], line['filename'])
                    if not section:
                        section = line['section']
                    subprocess.call(["git", "add", line['filename']], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
                    self.show_status(section, nextFile)
            elif c == ord('c'):
                if line['isAFile']:
                    section, nextFile = self._find_status_file_after(line['section'], line['filename'])
                    call(["git", "checkout", line['filename']])
                    self.show_status(section, nextFile)
            elif c == ord('d'):
                if line['isAFile']:
                    section, nextFile = line['section'], line['filename']
                    result = GitDiffScreen(self.main_window).show(line['filename'], line['section'] == 'Staged', line['section'] == 'Untracked', self._footer_shortcut_reminders(line))
                    if result != ord('q'):
                        followupWith = result
                    else:
                        self.show_status(line['section'], line['filename'])
            elif c == ord('r'):
                if line['isAFile']:
                    section, nextFile = self._find_status_file_after(line['section'], line['filename'])
                    self.git_rm(line['filename'], line['section'])
                    self.show_status(section, nextFile)
            elif c == ord('i'):
                if line['isAFile']:
                    section, nextFile = self._find_status_file_after(line['section'], line['filename'])
                    self.ignore(line['filename'])
                    self.show_status(section, nextFile)
            elif c == ord('u'):
                if line['isAFile']:
                    section, nextFile = self._find_status_file_after(line['section'], line['filename'])
                    subprocess.call(["git", "reset", "HEAD", line['filename']], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
                    self.show_status(section, nextFile)
            elif c == ord('f'):
                self.commit()
                self.show_status(None, None)
            elif c == ord('g'):
                if self.status_wrapper.can_amend_commit():
                    Git.commit_amend()
                    self.show_status(None, None)
            elif c == ord('s'): # stash "submenu"
                while 1:
                    self._show_text("Stash:\n * s to stash changes\n * a to apply changes\n * p to pop changes\n * q to go back")
                    c = self.main_window.getch()
                    if c == ord('s'):
                        output = Git.stash()
                        self._show_text_and_wait_for_keypress(output + "\nPress any key")
                        self.show_status(None, None)
                        break
                    elif c == ord('p'):
                        Git.stash_pop()
                        self.show_status(None, None)
                        break
                    elif c == ord('a'):
                        Git.stash_apply()
                        self.show_status(None, None)
                        break
                    elif c == ord('q'):
                        self.show_status(None, None)
                        break

            elif c == ord('p'):
                self.push()
                self.show_status(None, None)
            elif c == ord('q'):
                return
            elif c == curses.KEY_RESIZE:
                self.status_window.resize()
                self._determine_cursor_row_and_render_lines(line['section'], line['filename'])
            else:
                # self._show_text("Unhandled key " + str(c))
                # c = self.main_window.getch()
                self.show_status(None, None)
