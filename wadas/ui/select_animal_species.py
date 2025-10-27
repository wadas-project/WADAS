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
from PySide6.QtWidgets import QDialog

from wadas.ai.models import txt_animalclasses
from wadas.domain.ai_model import AiModel
from wadas.ui.qt.ui_select_animal_species import Ui_DialogSelectAnimalSpecies

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogSelectAnimalSpecies(QDialog,Ui_DialogSelectAnimalSpecies):
    """Class to create a UI dialog to select animal species to run classification on."""
    def __init__(self, parent=None):
        super(DialogSelectAnimalSpecies, self).__init__()
        self.selected_species = None
        self.ui = Ui_DialogSelectAnimalSpecies()

        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.buttonBox.accepted.connect(self.accept_and_close)

        self.populate_species_dropdown()

    def populate_species_dropdown(self):
        """Populate the dropdown with the list of available actuators."""
        self.ui.comboBox_select_species.clear()
        for species in txt_animalclasses[AiModel.classification_model_version][AiModel.language]:
            self.ui.comboBox_select_species.addItem(species)

    def accept_and_close(self):
        """When Ok is clicked, save Ai model config info before closing."""

        self.selected_species = self.ui.comboBox_select_species.currentText()
        self.accept()