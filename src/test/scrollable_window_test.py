import unittest
import curses
from scrollable_window import ScrollableWindow
import logging

class WindowRenderer():
    def __init__(self, rows_on_screen):
        self.rows_on_screen = rows_on_screen
    def max_rows_on_screen(self):
        return self.rows_on_screen
    def display(self, lines, cursor_row, footer):
        pass

class ScrollableWindowTestCase(unittest.TestCase):

    def test_renders_lines(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(2))

        lines = ["One", "Two"]
        scrollable_window.display(lines, 0)

        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), lines)

    def test_renders_lines_truncating_when_not_enough_lines(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(2))

        lines = ["One", "Two", "Three"]
        scrollable_window.display(lines, 0)

        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two"])

    def test_moves_cursor_down_a_line(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(2))

        lines = ["One", "Two", "Three"]
        scrollable_window.display(lines, 0)
        scrollable_window.line_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)

    def test_scrolls_window_down_a_line(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(2))

        lines = ["One", "Two", "Three", "Four"]
        scrollable_window.display(lines, 0)
        scrollable_window.line_down()
        scrollable_window.line_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 1)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Two", "Three"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)

    def test_moving_down_stops_at_the_last_line(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(2))

        lines = ["One", "Two", "Three"]
        scrollable_window.display(lines, 0)
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 1)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Two", "Three"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)

    def test_moves_cursor_up_a_line(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(2))

        lines = ["One", "Two", "Three", "Four", "Five"]
        scrollable_window.display(lines, 0)
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()
        scrollable_window.line_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 3)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Four", "Five"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)

        scrollable_window.line_up()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 3)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Four", "Five"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

        scrollable_window.line_up()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 2)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Three", "Four"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

    def test_dynamic_footer_creator_shows_contextual_lines(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, self._dynamic_footer_creator, WindowRenderer(2))
        lines = ["One", "Two"]
        scrollable_window.display(lines, 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One"])
        self.assertEqual(scrollable_window.get_footer_line(), "One footer")

        scrollable_window.line_down()
        self.assertEqual(scrollable_window.get_visible_lines(), ["Two"])
        self.assertEqual(scrollable_window.get_footer_line(), "Two footer")

        scrollable_window.line_up()
        self.assertEqual(scrollable_window.get_visible_lines(), ["One"])
        self.assertEqual(scrollable_window.get_footer_line(), "One footer")

    def test_page_up_moves_cursor_when_all_content_fits_on_one_page(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(10))

        lines = ["One", "Two", "Three", "Four"]
        scrollable_window.display(lines, 3)
        scrollable_window.page_up()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three", "Four"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

    def test_page_down_moves_cursor_to_first_visitable_line_when_all_content_fits_on_one_page(self):
        scrollable_window = ScrollableWindow(self._line_renderer, self._can_cursor_visit_line_not_one, None, WindowRenderer(10))

        lines = ["One", "Two", "Three", "Four"]
        scrollable_window.display(lines, 3)
        scrollable_window.page_up()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three", "Four"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)

    def test_page_up_scrolls_the_page(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(3))

        lines = ["One", "Two", "Three", "Four", "Five", "Six"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()
        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 3)
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

        scrollable_window.page_up()
        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

    def test_page_up_scrolls_the_page_putting_cursor_on_next_visitable_line(self):

        scrollable_window = ScrollableWindow(self._line_renderer, self._can_cursor_visit_line_not_one, None, WindowRenderer(3))

        lines = ["One", "Two", "Three", "Four", "Five", "Six"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()
        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 3)
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

        scrollable_window.page_up()
        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)


    def test_page_up_scrolls_the_multiple_pages_till_it_finds_a_visitable_line(self):

        scrollable_window = ScrollableWindow(self._line_renderer, self._can_cursor_visit_line_not_four_five_six, None, WindowRenderer(3))

        lines = ["One", "Two", "Three", "Four", "Five", "Six", "Seven"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()
        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 6)
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

        scrollable_window.page_up()
        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

    def test_page_down_moves_cursor_when_all_content_fits_on_one_page(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(10))

        lines = ["One", "Two", "Three", "Four"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three", "Four"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 3)

    def test_page_down_moves_cursor_to_last_visitable_line_when_all_content_fits_on_one_page(self):
        scrollable_window = ScrollableWindow(self._line_renderer, self._can_cursor_visit_line_not_four, None, WindowRenderer(10))

        lines = ["One", "Two", "Three", "Four"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three", "Four"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 2)

    def test_page_down_moves_cursor_when_content_length_matches_page_size(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(4))

        lines = ["One", "Two", "Three", "Four"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 0)
        self.assertEqual(scrollable_window.get_visible_lines(), ["One", "Two", "Three", "Four"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 3)

    def test_page_down_scrolls_the_page(self):
        scrollable_window = ScrollableWindow(self._line_renderer, None, None, WindowRenderer(3))

        lines = ["One", "Two", "Three", "Four", "Five", "Six"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 3)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Four", "Five", "Six"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

    def test_page_down_scrolls_the_page_putting_cursor_on_next_visitable_line(self):

        scrollable_window = ScrollableWindow(self._line_renderer, self._can_cursor_visit_line_not_four, None, WindowRenderer(3))

        lines = ["One", "Two", "Three", "Four", "Five", "Six"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 3)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Four", "Five", "Six"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 1)

    def test_page_down_scrolls_the_multiple_pages_till_it_finds_a_visitable_line(self):
        scrollable_window = ScrollableWindow(self._line_renderer, self._can_cursor_visit_line_not_four_five_six, None, WindowRenderer(3))

        lines = ["One", "Two", "Three", "Four", "Five", "Six", "Seven"]
        scrollable_window.display(lines, 0)
        scrollable_window.page_down()

        self.assertEqual(scrollable_window.get_first_row_of_visible_content(), 6)
        self.assertEqual(scrollable_window.get_visible_lines(), ["Seven"])
        self.assertEqual(scrollable_window.get_cursor_row_index(), 0)

    def _can_cursor_visit_line_not_one(self, line):
        return line != "One"

    def _can_cursor_visit_line_not_four(self, line):
        return line != "Four"

    def _can_cursor_visit_line_not_four_five_six(self, line):
        return line != "Four" and line != "Five" and line != "Six"

    def _dynamic_footer_creator(self, line):
        return line + ' footer'

    def _line_renderer(self, line):
        return None, line
