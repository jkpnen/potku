# coding=utf-8
"""
Created on 3.5.2018
Updated on 30.10.2018

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2013-2018 Jarkko Aalto, Severi Jääskeläinen, Samuel Kaiponen,
Timo Konu, Samuli Kärkkäinen, Samuli Rahkonen, Miika Raunio, Heta Rekilä and
Sinikka Siironen, 2020 Juhani Sundell, 2021 Joonas Koponen

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
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n " \
             "Sinikka Siironen \n Juhani Sundell \n Joonas Koponen"
__version__ = "2.0"

import widgets.binding as bnd
import widgets.gui_utils as gutils

from modules.element_simulation import ElementSimulation
from modules.recoil_element import RecoilElement

from PyQt5 import QtWidgets
from PyQt5 import uic

from widgets.scientific_spinbox import ScientificSpinBox


class ReferenceDensityDialog(QtWidgets.QDialog,
                             bnd.PropertyBindingWidget,
                             metaclass=gutils.QtABCMeta):
    """Dialog for editing the name, description and reference density
    of a recoil element.
    """
    # TODO possibly track name changes
    reference_density = bnd.bind("scientific_spinbox")

    @property
    def name(self):
        return self.recoil_element.name

    @property
    def description(self):
        return self.recoil_element.description

    @property
    def color(self):
        return self.recoil_element.color

    def __init__(self, recoil_element: RecoilElement,
                 element_simulation: ElementSimulation):
        """Inits a recoil info dialog.

        Args:
            recoil_element: A RecoilElement object.
            element_simulation: Element simulation that has the recoil element.
        """
        super().__init__()

        uic.loadUi(gutils.get_ui_dir() / "ui_reference_density_dialog.ui", self)

        self.recoil_element = recoil_element
        self.element_simulation = element_simulation

        value = self.recoil_element.reference_density
        self.scientific_spinbox = ScientificSpinBox(
            value=value, minimum=0.01, maximum=9.99e23)

        if self.recoil_element.manual_reference_density_checked:
            self.scientific_spinbox.setDisabled(False)
            self.userSelectionCheckBox.setChecked(True)
        else:
            self.scientific_spinbox.setDisabled(True)
            self.userSelectionCheckBox.setChecked(False)

        self.userSelectionCheckBox.stateChanged.connect(self._state_changed)

        self.okPushButton.clicked.connect(self._accept_settings)
        self.cancelPushButton.clicked.connect(self.close)

        self.fields_are_valid = True

        self.formLayout.insertRow(
            4,
            QtWidgets.QLabel(r"Reference density [at./cm<sup>3</sup>]:"),
            self.scientific_spinbox)
        self.formLayout.removeRow(self.widget)

        self.isOk = False

        self.exec_()

    def _state_changed(self):
        if self.userSelectionCheckBox.isChecked():
            self.scientific_spinbox.setDisabled(False)
        else:
            self.scientific_spinbox.setDisabled(True)

    def _density_valid(self):
        """
        Check if density value is valid and in limits.

        Return:
            True or False.
        """
        try:
            self.scientific_spinbox.get_value()
            return True
        except TypeError:
            return False

    def _accept_settings(self):
        """Function for accepting the current settings and closing the dialog
        window.
        """
        if not self.fields_are_valid or not self._density_valid():
            QtWidgets.QMessageBox.critical(
                self, "Warning",
                "Some of the setting values are invalid.\n"
                "Please input values in fields indicated in red.",
                QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return

        # If current recoil is used in a running simulation
        if self.recoil_element is \
                self.element_simulation.get_main_recoil():
            if (self.element_simulation.is_simulation_running() or
                    self.element_simulation.is_optimization_running()) and \
                    self.name != self.recoil_element.name:
                reply = QtWidgets.QMessageBox.question(
                    self, "Recoil used in simulation",
                    "This recoil is used in a simulation that is "
                    "currently running.\nIf you change the name of "
                    "the recoil, the running simulation will be "
                    "stopped.\n\n"
                    "Do you want to save changes anyway?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No |
                    QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)
                if reply == QtWidgets.QMessageBox.No or reply == \
                        QtWidgets.QMessageBox.Cancel:
                    return
                else:
                    self.element_simulation.stop()

        self.isOk = True
        self.close()