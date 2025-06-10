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
# Date: 2024-10-01
# Description: Camera Actuator management module

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QPushButton,
    QTreeView,
)

from wadas.domain.actuator import Actuator
from wadas.domain.database import DataBase


class DialogCameraActuatorManagement(QDialog):
    """Dialog to edit Actuator(s) list of a given camera"""

    def __init__(self, camera, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Manage Actuators for Camera ID: {camera.id}")
        self.camera = camera
        self.original_actuators = camera.actuators.copy()  # Save original list for cancel action
        self.db_enabled = bool(DataBase.get_enabled_db())

        layout = QGridLayout(self)

        self.actuator_model = QStandardItemModel()
        self.actuator_model.setHorizontalHeaderLabels(["Actuators"])

        # Populate actuators for the camera in the model
        self.populate_actuator_model()

        # Tree view for actuators
        self.actuator_tree_view = QTreeView()
        self.actuator_tree_view.setModel(self.actuator_model)
        self.actuator_tree_view.selectionModel().selectionChanged.connect(
            self.update_remove_button_state
        )
        layout.addWidget(self.actuator_tree_view, 0, 0, 1, 3)

        # Dropdown for selecting possible actuators
        self.actuator_dropdown = QComboBox()
        self.populate_actuator_dropdown()
        layout.addWidget(self.actuator_dropdown, 1, 0)

        # Add and Remove actuator buttons
        self.add_button = QPushButton("Add Actuator")
        self.remove_button = QPushButton("Remove Actuator")
        self.remove_button.setEnabled(False)  # Initially disabled
        layout.addWidget(self.add_button, 1, 1)
        layout.addWidget(self.remove_button, 1, 2)

        # OK and Cancel buttons in a dialog button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box, 2, 0, 1, 3)

        # Slots
        self.add_button.clicked.connect(self.add_actuator)
        self.remove_button.clicked.connect(self.remove_selected_actuator)
        self.button_box.accepted.connect(self.apply_changes)
        self.button_box.rejected.connect(self.reject)

    def populate_actuator_model(self):
        """Populate the QTreeView model with the actuators associated with this camera."""
        # Clean model before population
        self.actuator_model.removeRows(0, self.actuator_model.rowCount())

        for actuator in self.camera.actuators:
            item = QStandardItem(f"Actuator ID: {actuator.id} - {actuator.type.value}")
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Make items non-editable
            self.actuator_model.appendRow(item)

    def populate_actuator_dropdown(self):
        """Populate the dropdown with the list of available actuators."""
        self.actuator_dropdown.clear()
        for actuator_id, actuator in Actuator.actuators.items():
            if actuator.enabled and actuator not in self.camera.actuators:
                self.actuator_dropdown.addItem(f"{actuator_id} - {actuator.type.value}", actuator)

    def add_actuator(self):
        """Add the selected actuator to the camera's actuator list."""
        actuator = self.actuator_dropdown.currentData()
        if actuator and actuator.enabled and actuator not in self.camera.actuators:
            self.camera.actuators.append(actuator)
            self.populate_actuator_dropdown()
            self.populate_actuator_model()

    def remove_selected_actuator(self):
        """Remove the selected actuator from the camera's actuator list."""
        selected_indexes = self.actuator_tree_view.selectedIndexes()
        if selected_indexes:
            row = selected_indexes[0].row()
            del self.camera.actuators[row]
            self.populate_actuator_dropdown()
            self.populate_actuator_model()

    def apply_changes(self):
        """Apply changes to the camera's actuator list and accept the dialog."""

        if self.db_enabled:
            # Apply changes into db
            for actuator in self.camera.actuators:
                if not actuator in self.original_actuators:
                    DataBase.add_actuator_to_camera(self.camera, actuator)
            for actuator in self.original_actuators:
                if not actuator in self.camera.actuators:
                    DataBase.remove_actuator_from_camera(self.camera, actuator)
        # Changes are directly applied to self.camera.actuators, so we just accept the dialog
        self.accept()

    def reject(self):
        """Discard changes by resetting actuators to the original list."""
        self.camera.actuators = self.original_actuators
        super().reject()

    def update_remove_button_state(self):
        """Enable the remove button only if an actuator is selected in the tree view."""
        self.remove_button.setEnabled(bool(self.actuator_tree_view.selectedIndexes()))
