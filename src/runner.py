import curses
import sys
import signal

from git import Git
from git_status_screen import GitStatusScreen
from curses_window import CursesWindow

class Runner():

    def signal_handler(self, signal, frame):
        self.exit()
        sys.exit(0)

    def exit(self):
        self.curses_window.teardown()

    def run(self):
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            self.curses_window = CursesWindow()
            self.curses_window.init()
            if not Git.is_a_git_project():
                self.curses_window.get_window().addstr("This does not appear to be a git repository. Run git init?")
                self.curses_window.get_window().refresh()
                c = self.curses_window.get_window().getch()
                if c != ord('y') and c != 10:
                    self.exit()
                    return
                Git.create_repository()

            GitStatusScreen(self.curses_window).show()
        finally:
            self.exit()
