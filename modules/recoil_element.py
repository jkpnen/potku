# coding=utf-8
"""
Created on 1.3.2018
Updated on 21.5.2018
"""
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n " \
             "Sinikka Siironen"
__version__ = "2.0"


class RecoilElement:
    """An element that has a list of points and a widget. The points are kept
    in ascending order by their x coordinate.
    """
    def __init__(self, element, points, widget=None):
        """Inits recoil element.

        Args:
            element: An Element class object.
            points: A list of Point class objects.
            widget: An ElementWidget class object.
        """
        self.element = element
        self.name = "Default"
        self.description = "This is a default rec setting file."
        self.type = "rec"
        # This is multiplied by 1e22
        self.reference_density = 4.98
        self._points = sorted(points)
        self.widget = widget
        self._edit_lock_on = True

    def delete_widget(self):
        self.widget.deleteLater()

    def lock_edit(self):
        self._edit_lock_on = True

    def unlock_edit(self):
        self._edit_lock_on = False

    def get_edit_lock_on(self):
        return self._edit_lock_on

    def _sort_points(self):
        """Sorts the points in ascending order by their x coordinate."""
        self._points.sort()
        self._xs = [point.get_x() for point in self._points]
        self._ys = [point.get_y() for point in self._points]

    def get_xs(self):
        """Returns a list of the x coordinates of the points."""
        return [point.get_x() for point in self._points]

    def get_ys(self):
        """Returns a list of the y coordinates of the points."""
        return [point.get_y() for point in self._points]

    def get_point_by_i(self, i):
        """Returns the i:th point."""
        return self._points[i]

    def get_points(self):
        return self._points

    def add_point(self, point):
        """Adds a point and maintains sort order."""
        self._points.append(point)
        self._sort_points()

    def remove_point(self, point):
        """Removes the given point."""
        self._points.remove(point)

    def get_left_neighbor(self, point):
        """Returns the point whose x coordinate is closest to but
        less than the given point's.
        """
        ind = self._points.index(point)
        if ind == 0:
            return None
        else:
            return self._points[ind - 1]

    def get_right_neighbor(self, point):
        """Returns the point whose x coordinate is closest to but
        greater than the given point's.
        """
        ind = self._points.index(point)
        if ind == len(self._points) - 1:
            return None
        else:
            return self._points[ind + 1]
