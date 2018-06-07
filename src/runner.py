import curses
import sys
import signal
from git_status_screen import GitStatusScreen

class Runner():

    def signal_handler(self, signal, frame):
        self.exit()
        sys.exit(0)

    def exit(self):
        curses.nocbreak(); self.main_window.keypad(0); curses.echo()
        curses.endwin()

    def run(self):
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            self.main_window = curses.initscr()
            curses.noecho() # Don't echo keys to the screen
            curses.cbreak() # react to keys without requiring the Enter key to be pressed
            self.main_window.keypad(1) # have curses translate special keys
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            curses.init_pair(2, curses.COLOR_RED, -1)
            self.main_window.refresh()

            GitStatusScreen(self.main_window).show()
        finally:
            self.exit()
