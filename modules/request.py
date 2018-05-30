# coding=utf-8
"""
Created on 11.4.2013
Updated on 28.5.2018

Potku is a graphical user interface for analyzation and 
visualization of measurement data collected from a ToF-ERD 
telescope. For physics calculations Potku uses external 
analyzation components.  
Copyright (C) Jarkko Aalto, Timo Konu, Samuli Kärkkäinen, Samuli Rahkonen and 
Miika Raunio

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

__author__ = "Jarkko Aalto \n Timo Konu \n Samuli Kärkkäinen " \
             "\n Samuli Rahkonen \n Miika Raunio \n Severi Jääskeläinen " \
             "\n Samuel Kaiponen \n Heta Rekilä \n Sinikka Siironen"
__version__ = "2.0"

import configparser
import logging
import os
import time
import re

from modules.element import Element
from modules.element_simulation import ElementSimulation
from modules.run import Run
from widgets.matplotlib.simulation.recoil_atom_distribution import RecoilElement
from modules.sample import Samples
from modules.measurement import Measurement
from modules.simulation import Simulation
from modules.settings import Settings
from modules.detector import Detector
from modules.target import Target


class Request:
    """Request class to handle all measurements.
    """

    def __init__(self, directory, name, statusbar, global_settings,
                 tabs):
        """ Initializes Request class.
        
        Args:
            directory: A String representing request directory.
            name: Name of the request.
            statusbar: A QtGui.QMainWindow's QStatusBar.
            global_settings: A GlobalSettings class object (of the program).
            tabs: A dictionary of MeasurementTabWidgets and SimulationTabWidgets
                  of the request.
        """
        # TODO: Get rid of statusbar.
        self.directory = directory
        self.request_name = name
        unused_directory, tmp_dirname = os.path.split(self.directory)
        self.settings = Settings(self.directory)
        self.global_settings = global_settings
        self.statusbar = statusbar
        self.samples = Samples(self)

        self.default_run = Run()
        # self.default_target = Target()

        self.__tabs = tabs
        self.__master_measurement = None
        self.__non_slaves = []  # List of measurements that aren't slaves,
        # easier.
        # This is used to number all the samples
        # e.g. Sample-01, Sample-02.optional_name,...
        self._running_int = 1  # TODO: Maybe be saved into .request file?

        # Check folder exists and make request file there.
        if not os.path.exists(directory):
            os.makedirs(directory)

        # If Default folder doesn't exist, create it.
        self.default_folder = os.path.join(self.directory, "Default")
        if not os.path.exists(self.default_folder):
            # Create Default folder under request folder
            os.makedirs(self.default_folder)

        # Try reading default objects from Default folder.
        self.default_measurement_file_path = os.path.join(self.default_folder,
                                                          "Default.measurement")
        self.create_default_detector()
        self.create_default_measurement()
        self.create_default_target()
        self.create_default_simulation()

        # Set default Run, Detector and Target objects to Measurement
        self.default_measurement.run = self.default_run
        self.default_measurement.detector = self.default_detector
        self.default_measurement.target = self.default_target

        # Set default Run, Detector and Target objects to Simulation
        self.default_simulation.run = self.default_run
        self.default_simulation.detector = self.default_detector
        self.default_simulation.target = self.default_target

        self.__set_request_logger()

        # Request file containing necessary information of the request.
        # If it exists, we assume old request is loaded.
        self.__request_information = configparser.ConfigParser()

        # tmp_dirname has extra .potku in it, need to remove it for the
        # .request file name
        stripped_tmp_dirname = tmp_dirname.replace(".potku", "")
        self.request_file = os.path.join(directory, "{0}.request".format(
            stripped_tmp_dirname))

        # Defaults
        self.__request_information.add_section("meta")
        self.__request_information.add_section("open_measurements")
        self.__request_information["meta"]["request_name"] = self.request_name
        self.__request_information["meta"]["created"] = \
            time.strftime("%c %z %Z", time.localtime(time.time()))
        self.__request_information["meta"]["master"] = ""
        self.__request_information["meta"]["nonslave"] = ""
        if not os.path.exists(self.request_file):
            self.save()
        else:
            self.load()

    def create_default_detector(self):
        # Detector
        self.default_detector_folder = os.path.join(self.default_folder,
                                                    "Detector")

        detector_path = os.path.join(self.directory,
                                     self.default_detector_folder,
                                     "Default.detector")
        if os.path.exists(detector_path):
            # Read detector from file
            self.default_detector = Detector.from_file(
                detector_path,
                self.default_measurement_file_path, self)
            self.default_detector.update_directories(
                self.default_detector_folder)
        else:
            # Create Detector folder under Default folder
            if not os.path.exists(self.default_detector_folder):
                os.makedirs(self.default_detector_folder)
            # Create default detector for request
            self.default_detector = Detector(
                os.path.join(self.default_detector_folder,
                             "Default.detector"),
                self.default_measurement_file_path, name="Default detector",
                description="These are default detector settings.")
            self.default_detector.update_directories(
                self.default_detector_folder)

        self.default_detector.to_file(os.path.join(self.default_folder,
                                                   "Detector",
                                                   "Default.detector"),
                                      self.default_measurement_file_path)

    def create_default_measurement(self):
        # Measurement
        measurement_info_path = os.path.join(self.default_folder,
                                             "Default.info")
        if os.path.exists(measurement_info_path):
            # Read measurement from file
            self.default_measurement = Measurement.from_file(
                measurement_info_path,
                os.path.join(self.default_folder, "Default.measurement"),
                os.path.join(self.default_folder, "Default.profile"),
                self)
            self.default_run = Run.from_file(self.default_measurement_file_path)
        else:
            # Create default measurement for request
            default_info_path = os.path.join(self.default_folder,
                                             "Default.info")
            self.default_measurement = Measurement(
                self, path=default_info_path,
                run=self.default_run,
                detector=self.default_detector,
                description="This is a default measurement.",
                profile_description="These are default profile parameters.",
                measurement_setting_file_description="These are default "
                                                     "measurement parameters.")
            self.default_measurement.info_to_file(
                os.path.join(self.default_folder,
                             self.default_measurement.name + ".info"))
            self.default_measurement.measurement_to_file(os.path.join(
                self.default_folder,
                self.default_measurement.measurement_setting_file_name
                + ".measurement"))
            self.default_measurement.profile_to_file(os.path.join(
                self.default_folder,
                self.default_measurement.profile_name + ".profile"))
            self.default_measurement.run.to_file(os.path.join(
                self.default_folder,
                self.default_measurement.measurement_setting_file_name +
                ".measurement"))

    def create_default_target(self):
        # Target
        target_path = os.path.join(self.default_folder, "Default.target")
        if os.path.exists(target_path):
            # Read target from file
            self.default_target = Target \
                .from_file(target_path, self.default_measurement_file_path, self)
        else:
            # Create default target for request
            self.default_target = Target(description="These are default "
                                                     "target parameters.")
            self.default_target.to_file(os.path.join(self.default_folder,
                                                     "Default.target"),
                                        self.default_measurement_file_path)

        self.default_target.to_file(os.path.join(self.default_folder,
                                                 self.default_target.name
                                                 + ".target"),
                                    self.default_measurement_file_path)

    def create_default_run(self):
        # Read default run from file.
        try:
            # Try reading Run parameters from .measurement file.
            self.default_run = Run.from_file(self.default_measurement_file_path)
        except KeyError:
            # Save new Run parameters to file.
            self.default_run.to_file(os.path.join(
                self.default_folder,
                self.default_measurement.measurement_setting_file_name +
                ".measurement"))

    def create_default_simulation(self):
        # Simulation
        simulation_path = os.path.join(self.default_folder,
                                       "Default.simulation")
        if os.path.exists(simulation_path):
            # Read default simulation from file
            self.default_simulation = Simulation.from_file(
                self, simulation_path)
        else:
            # Create default simulation for request
            self.default_simulation = Simulation(os.path.join(
                self.default_folder, "Default.simulation"), self,
                description="This is a default simulation.",
                measurement_setting_file_description="These are default "
                                                     "measurement parameters.")

        mcsimu_path = os.path.join(self.default_folder, "Default.mcsimu")
        if os.path.exists(mcsimu_path):
            # Read default element simulation from file
            self.default_element_simulation = \
                ElementSimulation.from_file(self, "4He", self.default_folder,
                                            mcsimu_path,
                                            os.path.join(
                                                self.default_folder,
                                                "Default.profile"))
        else:
            # Create default element simulation for request
            self.default_element_simulation = ElementSimulation(
                self.default_folder, self,
                [RecoilElement(Element.from_string("4He 3.0"), [])],
                description="These are default simulation parameters.")
            self.default_simulation.element_simulations.append(
                self.default_element_simulation)

    def exclude_slave(self, measurement):
        """ Exclude measurement from slave category under master.
        
        Args:
            measurement: A measurement class object.
        """
        name = measurement.name
        # Check if measurement is already excluded.
        if name in self.__non_slaves:
            return
        self.__non_slaves.append(name)
        self.__request_information["meta"]["nonslave"] = "|".join(
            self.__non_slaves)
        self.save()

    def include_slave(self, measurement):
        """ Include measurement to slave category under master.
        
        Args:
            measurement: A measurement class object.
        """
        name = measurement.name
        # Check if measurement is in the list.
        if name not in self.__non_slaves:
            return
        self.__non_slaves.remove(name)
        self.__request_information["meta"]["nonslave"] = "|".join(
            self.__non_slaves)
        self.save()

    def get_name(self):
        """ Get the request's name.
        
        Return:
            Returns the request's name.
        """
        return self.__request_information["meta"]["request_name"]

    def get_master(self):
        """ Get master measurement of the request.
        """
        return self.__master_measurement

    def get_samples_files(self):
        """
        Searches the directory for folders beginning with "Sample".

        Return:
            Returns all the paths for these samples.
        """
        samples = []
        for item in os.listdir(self.directory):
            if os.path.isdir(os.path.join(self.directory, item)) and \
                    item.startswith("Sample_"):
                samples.append(os.path.join(self.directory, item))
                # It is presumed that the sample numbers are of format
                # '01', '02',...,'10', '11',...
                match_object = re.search("\d", item)
                if match_object:
                    number_str = item[match_object.start()]
                    if number_str == "0":
                        self._running_int = int(item[match_object.start() + 1])
                    else:
                        self._running_int = int(item[match_object.start():
                                                     match_object.start() + 2])
        return samples

    def get_running_int(self):
        """
        Get the running int needed for numbering the samples.
        """
        return self._running_int

    def increase_running_int_by_1(self):
        """
        Increase running int by one.
        """
        self._running_int = self._running_int + 1

    def get_measurement_tabs(self, exclude_id=-1):
        """ Get measurement tabs of a request.
        """
        list_m = []
        keys = list(filter((exclude_id).__ne__, self.__measurement_tabs.keys()))
        for key in keys:
            list_m.append(self.__measurement_tabs[key])
        return list_m

    def get_nonslaves(self):
        """ Get measurement names that will be excluded from slave category.
        """
        return self.__non_slaves

    def has_master(self):
        """ Does request have master measurement? Check from config file as
        it is not loaded yet.
        
        This is used when loading request. As request has no measurement in it
        when inited so check is made in potku.py after loading all measurements
        via this method. The corresponding master title in treewidget is then
        set.
        """
        return self.__request_information["meta"]["master"]

    def load(self):
        """ Load request.
        """
        self.__request_information.read(self.request_file)
        self.__non_slaves = self.__request_information["meta"]["nonslave"] \
            .split("|")

    def save(self):
        """ Save request.
        """
        # TODO: Saving properly.
        with open(self.request_file, "wt+") as configfile:
            self.__request_information.write(configfile)

    def save_cuts(self, measurement):
        """ Save cuts for all measurements except for master.
        
        Args:
            measurement: A measurement class object that issued save cuts.
        """
        name = measurement.name
        if name == self.has_master():
            nonslaves = self.get_nonslaves()
            tabs = self.get_measurement_tabs(measurement.tab_id)
            for tab in tabs:
                tab_name = tab.measurement.name
                if tab.data_loaded and tab_name not in nonslaves and \
                        tab_name != name:
                    # No need to save same measurement twice.
                    tab.measurement.save_cuts()

    def save_selection(self, measurement):
        """ Save selection for all measurements except for master.
        
        Args:
            measurement: A measurement class object that issued save cuts.
        """
        directory = measurement.directory_data
        name = measurement.name
        selection_file = "{0}.selections".format(os.path.join(directory, name))
        if name == self.has_master():
            nonslaves = self.get_nonslaves()
            tabs = self.get_measurement_tabs(measurement.tab_id)
            for tab in tabs:
                tab_name = tab.measurement.name
                if tab.data_loaded and tab_name not in nonslaves and \
                        tab_name != name:
                    tab.measurement.selector.load(selection_file)
                    tab.histogram.matplotlib.on_draw()

    def set_master(self, measurement=None):
        """ Set master measurement for the request.
        
        Args:
            measurement: A measurement class object.
        """
        self.__master_measurement = measurement
        if not measurement:
            self.__request_information["meta"]["master"] = ""
        else:
            name = measurement.name
            self.__request_information["meta"]["master"] = name
        self.save()

    def __set_request_logger(self):
        """ Sets the logger which is used to log everything that doesn't happen
        in measurements.
        """
        logger = logging.getLogger("request")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - "
                                      "%(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        requestlog = logging.FileHandler(os.path.join(self.directory,
                                                      "request.log"))
        requestlog.setLevel(logging.INFO)
        requestlog.setFormatter(formatter)

        logger.addHandler(requestlog)