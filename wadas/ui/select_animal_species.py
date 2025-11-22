# This file is part of WADAS project.
#
# WADAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WADAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WADAS. If not, see <https://www.gnu.org/licenses/>.
#
# Author(s): Stefano Dell'Osa, Alessandro Palla, Cesare Di Mauro, Antonio Farina
# Date: 2024-12-23
# Description: Select Custom animal species UI dialog


import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QFrame, QCheckBox, QDialogButtonBox

from wadas.ai.models import txt_animalclasses
from wadas.domain.operation_mode import OperationMode
from wadas.domain.ai_model import AiModel
from wadas.ui.qt.ui_select_animal_species import Ui_DialogSelectAnimalSpecies

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogSelectAnimalSpecies(QDialog,Ui_DialogSelectAnimalSpecies):
    """Class to create a UI dialog to select animal species to run classification on."""
    def __init__(self, parent=None):
        super(DialogSelectAnimalSpecies, self).__init__()
        self.selected_species = []
        self.ui = Ui_DialogSelectAnimalSpecies()

        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)

        # GroupBox
        group_layout = QVBoxLayout()
        self.ui.groupBox_select_animal_species.setLayout(group_layout)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Container widget inside scroll area
        container = QFrame()
        scroll.setWidget(container)

        # Layout inside the scroll container
        container_layout = QVBoxLayout(container)

        # Add dynamic checkboxes corresponding to animal species
        self.checkboxes = []
        animal_species = txt_animalclasses[AiModel.classification_model_version][AiModel.language]
        for animal_class in animal_species:
            cb = QCheckBox(animal_class)
            container_layout.addWidget(cb)
            cb.clicked.connect(self.on_checkbox_checked)
            self.checkboxes.append(cb)

        group_layout.addWidget(scroll)

        # Init Ok button status
        self.initialize_species_selection()

    def initialize_species_selection(self):
        """Method to initialize animal species selection from saved configuration, if any."""

        for species in OperationMode.cur_custom_classification_species:
            for checkbox in self.checkboxes:
                if species == checkbox.text():
                    checkbox.setChecked(True)
                    break
        self.on_checkbox_checked()

    def on_checkbox_checked(self):
        """Method to handle Ok button enablement basing on checkboxes' selection."""

        checkbox_selected = False
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                checkbox_selected = True
                break

        if checkbox_selected:
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def accept_and_close(self):
        """When Ok is clicked, save Ai model config info before closing."""

        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                self.selected_species.append(checkbox.text())
        OperationMode.cur_custom_classification_species = self.selected_species
        self.accept()