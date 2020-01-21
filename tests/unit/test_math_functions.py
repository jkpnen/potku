# coding=utf-8
"""
Created on TODO

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2013-2020 TODO

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (file named 'LICENCE').
"""

__author__ = "Juhani Sundell"
__version__ = ""  # TODO

import unittest
from modules import math_functions as mf


class TestListIntegration(unittest.TestCase):

    def test_bins_without_limits(self):
        """Tests integrate_bins function without limits"""

        # Empty lists return 0
        self.assertEqual(0, mf.integrate_bins([], []))

        # If x axis contains only one value, step size parameter
        # must be defined
        self.assertRaises(ValueError, lambda: mf.integrate_bins([0], [1]))
        self.assertEqual(10, mf.integrate_bins([0], [1], step_size=10))

        # Some regular integrals
        self.assertEqual(3, mf.integrate_bins([0, 1], [1, 2]))
        self.assertEqual(30, mf.integrate_bins([0, 10], [1, 2]))
        self.assertEqual(70, mf.integrate_bins([0, 10, 20], [1, 2, 4]))

        # Step size is calculated from first two bins. This can be overridden
        # with step size parameter
        self.assertEqual(30, mf.integrate_bins([0, 1], [1, 2], step_size=10))
        self.assertEqual(0, mf.integrate_bins([0, 10], [1, 2], step_size=0))
        self.assertEqual(-7, mf.integrate_bins([0, 10, 20], [1, 2, 4], step_size=-1))

    def test_uneven_axes(self):
        """Tests integrate_bins with uneven x and y axis sizes."""
        # Having uneven axis length does not matter as long as x axis
        # contains at least two values. Iteration stops, when the smaller
        # axis is exhausted.
        self.assertEqual(2, mf.integrate_bins([1, 2], [1, 1, 1]))
        self.assertEqual(1, mf.integrate_bins([1, 2, 3], [1]))

    def test_uneven_step_sizes(self):
        """Tests integrate_bins with uneven step sizes."""

        # Currently step size is assumed to be constant, so variations are
        # not taken into account. This may change in the future
        self.assertEqual(
            120, mf.integrate_bins([0, 10, 300, 600], [1, 2, 4, 5]))

        # Negative first step negates all other bins. X axis is assumed
        # to be in ascending order, no checks are performed.
        self.assertEqual(
            -120, mf.integrate_bins([0, -10, -300, 600], [1, 2, 4, 5]))

        # In similar vein, zero step size nullifies all other bins
        self.assertEqual(
            0, mf.integrate_bins([0, 0, -300, 600], [1, 2, 4, 5]))

    def test_bad_inputs(self):
        """Tests integrate_bins function with bad input values for x
        or y."""
        # Non-numerical values are included
        self.assertRaises(
            TypeError, lambda: mf.integrate_bins(["bar", "foo"], [1, 2]))
        self.assertRaises(
            TypeError, lambda: mf.integrate_bins([1, 1], ["foo", "bar"]))

        # Note that this will still work as strings are not in the integral
        # range
        self.assertEqual(
            20, mf.integrate_bins([0, 1, 2, "foo"], ["foo", 10, 10, 10], a=1, b=1))

    def test_integrating_with_limits(self):
        """Tests integrate_bins function with set limit values
        """
        x_axis = [0, 1, 2, 3, 4, 5]
        y_axis = [10, 10, 10, 10, 10]

        self.assertEqual(
            50, mf.integrate_bins(x_axis,
                                  y_axis,
                                  a=0, b=4.5))
        # Values before a are not included in the integral, but first
        # value after b is
        self.assertEqual(
            30, mf.integrate_bins(x_axis,
                                  y_axis,
                                  a=1.5, b=3.5))
        self.assertEqual(
            30, mf.integrate_bins(x_axis,
                                  y_axis,
                                  a=2, b=3))
        self.assertEqual(
            30, mf.integrate_bins(x_axis,
                                  y_axis,
                                  a=1.5, b=3))
        self.assertEqual(
            30, mf.integrate_bins(x_axis,
                                  y_axis,
                                  a=2, b=3.5))

        # Turning limits around returns 0
        self.assertEqual(
            0, mf.integrate_bins(x_axis,
                                 y_axis,
                                 a=3, b=2))

        self.assertEqual(
            20, mf.integrate_bins(x_axis,
                                  y_axis,
                                  a=3, b=3))

        self.assertEqual(
            0, mf.integrate_bins(x_axis,
                                 y_axis,
                                 a=10, b=15))

        self.assertEqual(
            0, mf.integrate_bins(x_axis,
                                 y_axis,
                                 a=-10, b=-15))

    def test_sum_y_values(self):
        """Tests sum_y_values function"""
        x_axis = [0, 1, 2, 3, 4, 5]
        y_axis = [10, 11, 12, 13, 14, 15]

        # Without limits, sum_y_values is same as sum
        self.assertEqual(sum(y_axis),
                         mf.sum_y_values(x_axis, y_axis))

        self.assertEqual(29,
                         mf.sum_y_values(x_axis, y_axis, a=4))

        self.assertEqual(21,
                         mf.sum_y_values(x_axis, y_axis, b=0))

        self.assertEqual(11 + 12 + 13 + 14,
                         mf.sum_y_values(x_axis, y_axis, a=1, b=3))

        self.assertEqual(12,
                         mf.sum_y_values(x_axis, y_axis, a=1.5, b=1.5))

        self.assertEqual(0,
                         mf.sum_y_values(x_axis, y_axis, a=2, b=1))

    def test_sum_running_avgs(self):
        """Tests sum_running_avgs function"""
        x_axis = [0, 1, 2]
        y_axis = [10, 11, 12]
        self.assertEqual(27, mf.sum_running_avgs(x_axis, y_axis))
        self.assertEqual(0, mf.sum_running_avgs(x_axis, y_axis, a=2, b=1))
        self.assertEqual(0, mf.sum_running_avgs(x_axis, y_axis, a=10))


    def test_calculate_running_avgs(self):
        """Tests calculate_running_avgs function"""
        x_axis = [0, 1, 2]
        y_axis = [10, 11, 12]

        # TODO first element should perhaps not be included in the output
        #      of the function
        self.assertEqual([(0, 5), (1, 10.5), (2, 11.5)],
                         list(mf.calculate_running_avgs(x_axis, y_axis)))

        self.assertEqual([(1, 5.5), (2, 11.5)],
                         list(mf.calculate_running_avgs(x_axis, y_axis, a=1)))

        self.assertEqual([(0, 5), (1, 10.5)],
                         list(mf.calculate_running_avgs(x_axis, y_axis, b=0)))

        self.assertEqual([(0, 5)],
                         list(mf.calculate_running_avgs(x_axis, y_axis, b=-1)))

        self.assertEqual([],
                         list(mf.calculate_running_avgs(x_axis, y_axis, a=100)))

    def test_get_elements_in_range(self):
        """Tests get_elements_in_range function"""
        x_axis = [0, 1, 2, 3, 4, 5]
        y_axis = [10, 11, 12, 13, 14, 15]

        # Without limits, get_elements_in_range is the same as zip
        self.assertEqual(list(zip(x_axis, y_axis)),
                         list(mf.get_elements_in_range(x_axis, y_axis)))

        # If a > b, nothing is returned
        self.assertEqual([],
                         list(mf.get_elements_in_range(x_axis, y_axis, a=2, b=1)))

        # First element after b is also returned,
        # TODO this behaviour is quite weird and should be checked if this is
        #      actually what is needed
        self.assertEqual([(1, 11), (2, 12)],
                         list(mf.get_elements_in_range(x_axis, y_axis, a=1, b=1)))

        self.assertEqual([(0, 10)],
                         list(mf.get_elements_in_range(x_axis, y_axis, b=-100)))

        # whereas first before a is not
        self.assertEqual([(2, 12)],
                         list(mf.get_elements_in_range(x_axis, y_axis, a=1.5, b=1.5)))

        self.assertEqual([],
                         list(mf.get_elements_in_range(x_axis, y_axis, a=100)))

        self.assertEqual([(1, 11), (2, 12), (3, 13)],
                         list(mf.get_elements_in_range(x_axis, y_axis, a=1, b=2)))

        # Limits can be set for only a or b
        self.assertEqual([(0, 10), (1, 11), (2, 12), (3, 13)],
                         list(mf.get_elements_in_range(x_axis, y_axis, b=2)))

        self.assertEqual([(3, 13), (4, 14), (5, 15)],
                         list(mf.get_elements_in_range(x_axis, y_axis, a=3)))

        # Function works for any x values that can be compared
        x_axis_str = ["a", "b", "c"]
        y_axis_str = [True, False, None]
        self.assertEqual([("a", True), ("b", False)],
                         list(mf.get_elements_in_range(x_axis_str,
                                                       y_axis_str,
                                                       a="a",
                                                       b="a")))

    def test_incomparable_element_ranges(self):
        # TypeError is raised if the range generator has to compare
        # objects that cannot be compared with each other (such as
        # str to int)
        x_axis = [0, 1, 2, 3, "foo", 5]
        y_axis = [10, "foo", "bar", 13, 14, 15]
        self.assertRaises(TypeError,
                          lambda: list(mf.get_elements_in_range(x_axis,
                                                                y_axis)))

        self.assertRaises(TypeError,
                          lambda: list(mf.get_elements_in_range(x_axis,
                                                                y_axis,
                                                                a=2,
                                                                b=3)))

        # Note that this will work as iteration stops before reaching an
        # incomparable value
        self.assertEqual(
            [(0, 10), (1, "foo"), (2, "bar"), (3, 13)],
            list(mf.get_elements_in_range(x_axis, y_axis, b=2))
        )


if __name__ == "__main__":
    unittest.main()