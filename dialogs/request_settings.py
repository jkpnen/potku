# coding=utf-8
"""
Created on 19.3.2013
Updated on 22.5.2018

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2013-2018 Jarkko Aalto, Severi Jääskeläinen, Samuel Kaiponen,
Timo Konu, Samuli Kärkkäinen, Samuli Rahkonen, Miika Raunio, Heta Rekilä and
Sinikka Siironen

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

Dialog for the request settings
"""
__author__ = "Jarkko Aalto \n Timo Konu \n Samuli Kärkkäinen " \
             "\n Samuli Rahkonen \n Miika Raunio \n Severi Jääskeläinen \n " \
             "Samuel Kaiponen \n Heta Rekilä \n Sinikka Siironen"
__version__ = "2.0"

import os
import time

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget, QApplication

import modules.masses as masses
from dialogs.element_selection import ElementSelectionDialog
from modules.calibration_parameters import CalibrationParameters
from modules.general_functions import open_file_dialog
from modules.general_functions import save_file_dialog
from modules.input_validator import InputValidator
from modules.measuring_settings import MeasuringSettings
from widgets.detector_settings import DetectorSettingsWidget
from widgets.measurement.settings import MeasurementSettingsWidget
from widgets.profile_settings import ProfileSettingsWidget
from widgets.simulation.settings import SimulationSettingsWidget


class RequestSettingsDialog(QtWidgets.QDialog):

    def __init__(self, request, icon_manager):
        """Constructor for the program

        Args:
            request: Request class object.
        """
        super().__init__()
        self.ui = uic.loadUi(os.path.join("ui_files", "ui_settings.ui"), self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        screen_geometry = QDesktopWidget \
            .availableGeometry(QApplication.desktop())
        self.resize(self.geometry().width(),
                    screen_geometry.size().height() * 0.8)

        self.request = request
        self.icon_manager = icon_manager

        # Connect buttons.
        self.ui.OKButton.clicked.connect(self.update_and_close_settings)
        self.ui.applyButton.clicked.connect(self.update_settings)
        self.ui.cancelButton.clicked.connect(self.close)
        double_validator = InputValidator()
        positive_double_validator = InputValidator(bottom=0)

        # Add measurement settings view to the settings view
        self.measurement_settings_widget = MeasurementSettingsWidget(
            self.request.default_measurement)
        self.ui.tabs.addTab(self.measurement_settings_widget, "Measurement")

        self.measurement_settings_widget.ui.beamIonButton.clicked.connect(
            lambda: self.__change_element(
                self.measurement_settings_widget.ui.beamIonButton,
                self.measurement_settings_widget.ui.isotopeComboBox))

        self.measurement_settings_widget.ui.picture.setScaledContents(True)
        pixmap = QtGui.QPixmap(os.path.join("images", "hardwaresetup.png"))
        self.measurement_settings_widget.ui.picture.setPixmap(pixmap)

        # Add detector settings view to the settings view
        self.detector_settings_widget = DetectorSettingsWidget(
            self.request.default_detector, self.request, self.icon_manager,
            self.request.default_measurement)
        self.ui.tabs.addTab(self.detector_settings_widget, "Detector")

        self.detector_settings_widget.ui.saveButton.clicked \
            .connect(lambda: self.__save_file("DETECTOR_SETTINGS"))

        # Add simulation settings view to the settings view
        self.simulation_settings_widget = SimulationSettingsWidget()
        self.ui.tabs.addTab(self.simulation_settings_widget, "Simulation")

        self.simulation_settings_widget.ui.generalParametersGroupBox \
            .setEnabled(True)
        self.simulation_settings_widget.ui.physicalParametersGroupBox \
            .setEnabled(True)
        self.simulation_settings_widget.ui.saveButton.clicked \
            .connect(lambda: self.__save_file("SIMULATION_SETTINGS"))

        self.request.default_simulation = self.request.default_simulation \
            .from_file(self.request, os.path.join(self.request.default_folder,
                                                  "Default.simulation"))
        self.request.default_element_simulation = \
            self.request.default_element_simulation \
                .from_file(self.request, "",
                           self.request.default_folder,
                           os.path.join(self.request.default_folder,
                                        "Default.mcsimu"),
                           os.path.join(self.request.default_folder,
                                        "Default.profile"))
        self.request.default_simulation.element_simulations.append(
            self.request.default_element_simulation)

        # Add profile settings view to the settings view
        self.profile_settings_widget = ProfileSettingsWidget(
            self.request.default_measurement)
        self.ui.tabs.addTab(self.profile_settings_widget, "Profile")

        self.show_simulation_settings()

        self.exec_()

    def show_simulation_settings(self):
        """ Show simulation settings in simulation tab widget.
        """
        widget = self.simulation_settings_widget
        elem_simu = self.request.default_element_simulation
        widget.nameLineEdit.setText(elem_simu.name)
        widget.dateLabel.setText(time.strftime("%c %z %Z", time.localtime(
            elem_simu.modification_time)))
        widget.descriptionPlainTextEdit.setPlainText(elem_simu.description)
        widget.modeComboBox.setCurrentIndex(widget.modeComboBox.findText(
            elem_simu.simulation_mode, Qt.MatchFixedString))
        widget.typeOfSimulationComboBox.setCurrentIndex(
            widget.typeOfSimulationComboBox.findText(self.request
                                                     .default_element_simulation
                                                     .simulation_type,
                                                     Qt.MatchFixedString))
        widget.minimumScatterAngleDoubleSpinBox.setValue(
            elem_simu.minimum_scattering_angle)
        widget.minimumMainScatterAngleDoubleSpinBox.setValue(
            elem_simu.minimum_main_scattering_angle)
        widget.minimumEnergyDoubleSpinBox.setValue(elem_simu.minimum_energy)
        widget.numberOfIonsSpinBox.setValue(elem_simu.number_of_ions)
        widget.numberOfPreIonsSpinBox.setValue(elem_simu.number_of_preions)
        widget.seedSpinBox.setValue(elem_simu.seed_number)
        widget.numberOfRecoilsSpinBox.setValue(elem_simu.number_of_recoils)
        widget.numberOfScalingIonsSpinBox.setValue(
            elem_simu.number_of_scaling_ions)

    def __load_file(self, settings_type):
        """ Opens file dialog and loads and shows selected ini file's values.

        Args:
            settings_type: (string) selects which settings file type will be
                           loaded.
                           Can be "MEASURING_UNIT_SETTINGS",
                           "DEPTH_PROFILE_SETTINGS" or "CALIBRATION_SETTINGS"
        """
        # TODO .ini files should not be used anymore.

        filename = open_file_dialog(self, self.request.directory,
                                    "Open settings file",
                                    "Settings file (*.ini)")

        if settings_type == "MEASURING_UNIT_SETTINGS":
            settings = MeasuringSettings()
            settings.load_settings(filename)
            masses.load_isotopes(settings.element.symbol,
                                 self.isotopeComboBox,
                                 str(settings.element.isotope))
            settings.show(self)
        elif settings_type == "DEPTH_PROFILE_SETTINGS":
            pass
        elif settings_type == "CALIBRATION_SETTINGS":
            settings = CalibrationParameters()
            settings.show(self.detector_settings_widget)
        else:
            return

    def __save_file(self, settings_type):
        """Opens file dialog and sets and saves the settings to a ini file.
        """
        if settings_type == "MEASURING_UNIT_SETTINGS":
            settings = MeasuringSettings()
        elif settings_type == "DEPTH_PROFILE_SETTINGS":
            pass
        elif settings_type == "CALIBRATION_SETTINGS":
            settings = CalibrationParameters()
        elif settings_type == "DETECTOR_SETTINGS":
            pass
        elif settings_type == "MEASUREMENT_SETTINGS":
            pass
        elif settings_type == "SIMULATION_SETTINGS":
            pass
        else:
            return

        filename = save_file_dialog(self, self.request.directory,
                                    "Open measuring unit settings file",
                                    "Settings file (*.ini)")

        self.update_settings()
        if filename:
            if settings_type == "CALIBRATION_SETTINGS":
                settings.set_settings(self.detector_settings_widget)
                settings.save_settings(filename)
            elif settings_type == "MEASUREMENT_SETTINGS":
                self.request.default_measurement.save_settings(filename)
            elif settings_type == "SIMULATION_SETTINGS":
                self.request.default_simulation.save_settings(filename)
            elif settings_type == "DETECTOR_SETTINGS":
                self.request.default_detector.save_settings(filename)
            else:
                settings.set_settings(self.measurement_settings_widget)
                settings.save_settings(filename)

    def update_and_close_settings(self):
        """Updates measuring settings values with the dialog's values and
        saves them to default settings file.
        """
        try:
            self.__update_settings()
            self.close()
        except TypeError:
            # Message has already been shown in update_settings()
            pass

    def update_settings(self):
        """Update values from dialog to every setting object.
        """
        try:
            self.__update_settings()
        except TypeError:
            # Message is already displayed within private method.
            pass

    def __update_settings(self):
        """Reads values from Request Settings dialog and updates them in
        default objects.
        """
        # TODO: Proper checking for all setting values
        try:
            self.measurement_settings_widget.update_settings()
            self.profile_settings_widget.update_settings()

            default_measurement_settings_file = os.path.join(
                self.request.default_measurement.directory,
                "Default.measurement")
            self.request.default_measurement.profile_to_file(os.path.join(
                self.request.default_measurement.directory, "Default.profile"))
            self.request.default_measurement.run.to_file(
                default_measurement_settings_file)
            self.request.default_target.to_file(
                None, default_measurement_settings_file)

            # Detector settings
            self.detector_settings_widget.update_settings()

            self.request.default_detector.to_file(os.path.join(
                self.request.default_detector_folder, "Default.detector"),
                default_measurement_settings_file)

            # Simulation settings
            elem_simu = self.request.default_element_simulation
            elem_simu.name = self.simulation_settings_widget.nameLineEdit.text()
            elem_simu.description = self.simulation_settings_widget\
                .descriptionPlainTextEdit. toPlainText()
            elem_simu.simulation_type = self.simulation_settings_widget \
                .typeOfSimulationComboBox.currentText().lower()
            elem_simu.simulation_mode = self.simulation_settings_widget \
                .modeComboBox.currentText().lower()
            elem_simu.number_of_ions = self.simulation_settings_widget \
                .numberOfIonsSpinBox.value()
            elem_simu.number_of_preions = self.simulation_settings_widget \
                .numberOfPreIonsSpinBox.value()
            elem_simu.seed_number = self.simulation_settings_widget\
                .seedSpinBox.value()
            elem_simu.number_of_recoils = self.simulation_settings_widget \
                .numberOfRecoilsSpinBox.value()
            elem_simu.number_of_scaling_ions = self.simulation_settings_widget \
                .numberOfScalingIonsSpinBox.value()
            elem_simu.minimum_scattering_angle = \
                self.simulation_settings_widget\
                    .minimumScatterAngleDoubleSpinBox.value()
            elem_simu.minimum_main_scattering_angle = self \
                .simulation_settings_widget \
                .minimumMainScatterAngleDoubleSpinBox.value()
            elem_simu .minimum_energy = self.simulation_settings_widget \
                .minimumEnergyDoubleSpinBox.value()

            self.request.default_simulation.to_file(os.path.join(
                self.request.default_folder, "Default.simulation"))
            elem_simu.mcsimu_to_file(os.path.join(self.request.default_folder,
                                                  "Default.mcsimu"))
        except TypeError:
            QtWidgets.QMessageBox.question(self, "Warning",
                                           "Some of the setting values have "
                                           "not been set.\n" +
                                           "Please input setting values to "
                                           "save them.",
                                           QtWidgets.QMessageBox.Ok,
                                           QtWidgets.QMessageBox.Ok)
            raise TypeError

    def __change_element(self, button, combo_box):
        """ Opens element selection dialog and loads selected element's isotopes
        to a combobox.

        Args:
            button: button whose text is changed accordingly to the made
            selection.
        """
        dialog = ElementSelectionDialog()
        if dialog.element:
            button.setText(dialog.element)
            # Enabled settings once element is selected
            self.__enabled_element_information()
            masses.load_isotopes(dialog.element, combo_box)

    def __enabled_element_information(self):
        """
        Change the UI accordingly when an element is selected.
        """
        self.measurement_settings_widget.ui.isotopeComboBox.setEnabled(True)
        self.measurement_settings_widget.ui.isotopeLabel.setEnabled(True)
        self.ui.OKButton.setEnabled(True)