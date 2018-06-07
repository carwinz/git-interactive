import curses
from git_status_screen import GitStatusScreen

# Wrap the status window so it can be re-initialised after
# invoking other commands
class CursesWindow():

    def init(self):
        self.window = curses.initscr()
        curses.noecho() # Don't echo keys to the screen
        curses.cbreak() # react to keys without requiring the Enter key to be pressed
        self.window.keypad(1) # have curses translate special keys
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        self.window.refresh()

    def teardown(self):
        curses.nocbreak();
        self.window.keypad(0);
        curses.echo()
        curses.endwin()

    def get_window(self):
        return self.window
