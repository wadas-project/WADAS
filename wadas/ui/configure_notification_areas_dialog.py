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
# Description: Notification areas configuration dialog

import copy
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from wadas.domain.camera import cameras
from wadas.domain.notification_area import NotificationArea
from wadas.domain.notifier import Notifier
from wadas.domain.telegram_recipient import TelegramRecipient
from wadas.ui.qt.ui_configure_notification_areas import Ui_ConfigureNotificationAreasDialog

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class _AddNotificationAreaDialog(QDialog):
    """Small dedicated dialog to input a new, unique notification area id."""

    def __init__(self, existing_ids, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add notification area")
        self.existing_ids = existing_ids

        layout = QVBoxLayout(self)
        self.label = QLabel("Notification area name:")
        self.lineEdit_area_id = QLineEdit()
        self.label_error = QLabel("")
        self.label_error.setStyleSheet("color: red")
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit_area_id)
        layout.addWidget(self.label_error)
        layout.addWidget(self.buttonBox)

        self.lineEdit_area_id.textChanged.connect(self._validate)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def _validate(self):
        name = self.lineEdit_area_id.text().strip()
        ok_button = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        if not name:
            self.label_error.setText("")
            ok_button.setEnabled(False)
        elif name in self.existing_ids:
            self.label_error.setText("A notification area with this name already exists.")
            ok_button.setEnabled(False)
        else:
            self.label_error.setText("")
            ok_button.setEnabled(True)

    def get_area_id(self):
        return self.lineEdit_area_id.text().strip()


class ConfigureNotificationAreasDialog(QDialog, Ui_ConfigureNotificationAreasDialog):
    """Class to configure notification areas"""

    _NOTIFIER_RECIPIENTS_ATTR = {
        Notifier.NotifierTypes.EMAIL: "recipients_email",
        Notifier.NotifierTypes.WHATSAPP: "recipient_numbers",
        Notifier.NotifierTypes.TELEGRAM: "recipients",
    }

    def __init__(self):
        super(ConfigureNotificationAreasDialog, self).__init__()
        self.ui = Ui_ConfigureNotificationAreasDialog()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.pushButton_remove_area.setEnabled(False)
        self.ui.label_errorMessage.setStyleSheet("color: red")

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.pushButton_add_area.clicked.connect(self.add_notification_area)
        self.ui.pushButton_remove_area.clicked.connect(self.remove_notification_area)
        self.ui.comboBox_select_notification_method.currentIndexChanged.connect(
            self.on_notification_method_changed
        )

        # create working copy of notification_area attribute (deep copy so that
        # Cancel discards changes and does not mutate Notifier.notification_areas).
        self.notification_areas = copy.deepcopy(Notifier.notification_areas)

        # state for the currently selected notification area
        self.selected_area_id = None

        # notification area(s) list widget
        self.listWidget_notification_areas = QListWidget()
        areas_layout = QVBoxLayout(self.ui.scrollAreaWidgetContents_notification_areas)
        areas_layout.setContentsMargins(0, 0, 0, 0)
        areas_layout.addWidget(self.listWidget_notification_areas)
        self.listWidget_notification_areas.currentItemChanged.connect(
            self.on_area_selection_changed
        )

        # widgets layouts (created once, cleared/repopulated on refresh)
        self.ui.scrollAreaWidgetContents_cameras.setLayout(QVBoxLayout())
        self.ui.scrollAreaWidgetContents_contacts.setLayout(QVBoxLayout())

        # Init dialog
        self.initialize_dialog()

    # ------------------------------------------------------------------ #
    # Initialization
    # ------------------------------------------------------------------ #

    def initialize_notification_method_combobox(self):
        """Method to initialize combo box with enabled notification methods"""
        self.ui.comboBox_select_notification_method.blockSignals(True)
        self.ui.comboBox_select_notification_method.clear()
        for notifier_type in Notifier.NotifierTypes:
            notifier_instance = Notifier.notifiers.get(notifier_type.value)
            if notifier_instance and notifier_instance.is_configured():
                self.ui.comboBox_select_notification_method.addItem(
                    notifier_type.value, notifier_type
                )
        self.ui.comboBox_select_notification_method.blockSignals(False)

    def initialize_dialog(self):
        """Method to initialize dialog with existing values (if any)."""
        self.initialize_notification_method_combobox()
        self.refresh_notification_areas_list()
        self.ui.comboBox_select_notification_method.setEnabled(bool(self.notification_areas))

        if self.notification_areas:
            first_id = next(iter(self.notification_areas))
            self.select_area(first_id)
        else:
            # No notification area yet: cameras/contacts lists are still shown
            # (unchecked/disabled) for the currently selected notification method.
            self.populate_cameras_list()
            self.populate_contacts_list()

        self.validate()

    # ------------------------------------------------------------------ #
    # Notification area(s) list (left column)
    # ------------------------------------------------------------------ #

    def refresh_notification_areas_list(self):
        """Rebuild the notification area(s) list widget from self.notification_areas."""
        self.listWidget_notification_areas.blockSignals(True)
        self.listWidget_notification_areas.clear()

        selected_row = -1
        for row, area_id in enumerate(self.notification_areas):
            item = QListWidgetItem(area_id)
            self.listWidget_notification_areas.addItem(item)
            if area_id == self.selected_area_id:
                selected_row = row

        if selected_row >= 0:
            self.listWidget_notification_areas.setCurrentRow(selected_row)

        self.listWidget_notification_areas.blockSignals(False)

    def on_area_selection_changed(self, current, previous):
        """Slot triggered when the user clicks/selects a different area in the list."""
        area_id = current.text() if current else None
        self.select_area(area_id)

    def select_area(self, area_id):
        """Select a notification area and refresh dependent widgets (cameras, contacts)."""
        self.selected_area_id = area_id
        self.ui.pushButton_remove_area.setEnabled(area_id is not None)

        self.populate_cameras_list()
        self.populate_contacts_list()
        self.validate()

    # ------------------------------------------------------------------ #
    # Add / remove notification area
    # ------------------------------------------------------------------ #

    def add_notification_area(self):
        """Method to add a new notification area into the list"""
        dialog = _AddNotificationAreaDialog(set(self.notification_areas.keys()), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            area_id = dialog.get_area_id()
            if not area_id or area_id in self.notification_areas:
                # should not happen given dialog validation, but guard anyway
                self.ui.label_errorMessage.setText(
                    "Notification area name is empty or already exists."
                )
                self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                return
            self.notification_areas[area_id] = NotificationArea(area_id)
            self.selected_area_id = area_id
            self.refresh_notification_areas_list()
            self.ui.comboBox_select_notification_method.setEnabled(True)
            self.select_area(area_id)

    def remove_notification_area(self):
        """Remove selected notification area from the list"""
        if self.selected_area_id is None:
            return
        del self.notification_areas[self.selected_area_id]
        self.selected_area_id = None
        self.refresh_notification_areas_list()

        if self.notification_areas:
            self.select_area(next(iter(self.notification_areas)))
        else:
            self.ui.pushButton_remove_area.setEnabled(False)
            self.ui.comboBox_select_notification_method.setEnabled(False)
            self.populate_cameras_list()
            self.populate_contacts_list()
            self.validate()

    # ------------------------------------------------------------------ #
    # Camera(s) list (middle column)
    # ------------------------------------------------------------------ #

    def populate_cameras_list(self):
        """Populate camera checkboxes for the currently selected notification area."""
        layout = self.ui.scrollAreaWidgetContents_cameras.layout()
        self._clear_layout(layout)

        area = self.notification_areas.get(self.selected_area_id) if self.selected_area_id else None

        for camera in cameras:
            checkbox = QCheckBox(camera.id)
            checkbox.setChecked(bool(area) and camera.id in area.camera_ids)
            checkbox.setEnabled(area is not None)
            checkbox.stateChanged.connect(
                lambda state, cid=camera.id: self.on_camera_checkbox_changed(cid, state)
            )
            layout.addWidget(checkbox)
        layout.addStretch()

    def on_camera_checkbox_changed(self, camera_id, state):
        """Update the selected area's camera_ids when a camera checkbox is toggled."""
        area = self.notification_areas.get(self.selected_area_id)
        if not area:
            return
        if state == Qt.CheckState.Checked.value:
            area.add_camera(camera_id)
        else:
            area.remove_camera(camera_id)
        self.validate()

    # ------------------------------------------------------------------ #
    # Notification contact(s) list (right column)
    # ------------------------------------------------------------------ #

    def on_notification_method_changed(self, _index):
        self.populate_contacts_list()

    def _get_available_contacts(self, notifier_type):
        """Return the full distribution list of contacts configured for the given
        notifier type, from which the user picks the area subset.

        Returns plain strings for Email/WhatsApp, TelegramRecipient objects for
        Telegram (handled by _contact_label_and_key)."""
        notifier_instance = Notifier.notifiers.get(notifier_type.value)
        if not notifier_instance:
            return []
        attr = self._NOTIFIER_RECIPIENTS_ATTR.get(notifier_type)
        if attr is None:
            return []
        return list(getattr(notifier_instance, attr, []) or [])

    def _contact_label_and_key(self, contact):
        """Return a (display_label, storage_key) pair for a contact.

        storage_key is what gets saved into area.contacts: must be a plain,
        serializable string, stable across reloads.
        - Email/WhatsApp: contact is already the string (address/number) -> used as-is.
        - Telegram: contact is a TelegramRecipient -> use recipient_id as key,
          name (if set) or recipient_id as label.
        """
        if isinstance(contact, TelegramRecipient):
            key = str(contact.recipient_id)
            label = contact.name if contact.name else key
            return label, key

        # Email / WhatsApp: plain string
        return contact, contact

    def populate_contacts_list(self):
        """Populate contact checkboxes for the selected area and notification method.

        If no notification area is currently selected (e.g. none exist yet),
        the available contacts for the selected notification method are still
        shown, but unchecked and disabled, since there is no area to store
        the selection into.
        """
        layout = self.ui.scrollAreaWidgetContents_contacts.layout()
        self._clear_layout(layout)

        area = self.notification_areas.get(self.selected_area_id) if self.selected_area_id else None
        notifier_type = self.ui.comboBox_select_notification_method.currentData()

        if notifier_type is None:
            return

        available_contacts = self._get_available_contacts(notifier_type)
        if not available_contacts:
            layout.addWidget(QLabel("No contacts configured for this notification method."))
            return

        selected_contacts = area.contacts.get(notifier_type.value, []) if area else []
        for contact in available_contacts:
            label, key = self._contact_label_and_key(contact)
            checkbox = QCheckBox(label)
            checkbox.setChecked(area is not None and key in selected_contacts)
            checkbox.setEnabled(area is not None)
            checkbox.stateChanged.connect(
                lambda state, nt=notifier_type, k=key: self.on_contact_checkbox_changed(nt, k, state)
            )
            layout.addWidget(checkbox)
        layout.addStretch()

    def on_contact_checkbox_changed(self, notifier_type, contact, state):
        """Update the selected area's contacts when a contact checkbox is toggled."""
        area = self.notification_areas.get(self.selected_area_id)
        if not area:
            return
        if state == Qt.CheckState.Checked.value:
            area.add_contact(notifier_type.value, contact)
        else:
            area.remove_contact(notifier_type.value, contact)
        self.validate()

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #

    def validate(self):
        """Method to validate current notification area configuration.

        Validation order:
        1. At least one camera must exist in the system; otherwise the user
           is redirected to camera configuration.
        2. At least one notification method must be configured; otherwise
           the user is redirected to notifier configuration.
        3. At least one notification area must be configured.
        4. Each notification area must have at least one associated camera.
        5. Each notification area must have at least one selected contact,
           across all notification methods (not required for every single
           method).
        """
        error_message = ""

        if not cameras:
            error_message = (
                "No camera configured. Please configure at least one camera first."
            )
        elif self.ui.comboBox_select_notification_method.count() == 0:
            error_message = (
                "No notification method configured. Please configure at least one "
                "notification method (Email, WhatsApp, Telegram) first."
            )
        elif not self.notification_areas:
            error_message = "At least one notification area must be configured."
        else:
            for area_id, area in self.notification_areas.items():
                if not area.camera_ids:
                    error_message = f"Notification area '{area_id}' has no camera associated."
                    break
                if not any(contacts for contacts in area.contacts.values()):
                    error_message = f"Notification area '{area_id}' has no contact associated."
                    break

        self.ui.label_errorMessage.setText(error_message)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not error_message)

    # ------------------------------------------------------------------ #
    # Accept / close
    # ------------------------------------------------------------------ #

    def accept_and_close(self):
        """When Ok is clicked, save notification areas before closing."""
        Notifier.notification_areas = self.notification_areas

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #

    @staticmethod
    def _clear_layout(layout):
        """Remove and delete all widgets from a layout, keeping the layout itself."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
