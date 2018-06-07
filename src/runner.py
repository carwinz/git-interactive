import curses
import sys
import signal
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
            GitStatusScreen(self.curses_window).show()
        finally:
            self.exit()
