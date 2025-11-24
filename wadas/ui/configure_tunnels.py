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
# Description: Configure tunnel mode UI module

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
)

from wadas.domain.camera import cameras
from wadas.domain.tunnel import Tunnel
from wadas.ui.configure_tunnel import DialogConfigureTunnel
from wadas.ui.qt.ui_configure_tunnels import Ui_DialogTunnels

module_dir_path = Path(__file__).parent


class DialogConfigureTunnels(QDialog, Ui_DialogTunnels):
    """Class to configure Tunnel mode"""

    def __init__(self):
        super(DialogConfigureTunnels, self).__init__()
        self.ui = Ui_DialogTunnels()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(str(module_dir_path.parent / "img" / "mainwindow_icon.jpg")))

        # Tunnel modifications status
        self.local_tunnels = Tunnel.tunnels.copy()
        self.cameras_not_in_tunnels = [camera.id for camera in cameras]

        # Signals
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.pushButton_add_tunnel.clicked.connect(self.on_add_tunnel_clicked)
        self.ui.pushButton_remove_tunnel.clicked.connect(self.on_remove_tunnel_clicked)
        self.ui.pushButton_edit_tunnel.clicked.connect(self.on_edit_tunnel_clicked)
        self.ui.listWidget.itemSelectionChanged.connect(self.on_tunnel_selection_changed)

        #Init dialog
        self.update_tunnels_list()
        self.update_cameras_not_in_tunnel()
        self.ui.listWidget.clearSelection()
        self.on_tunnel_selection_changed()

    def update_cameras_not_in_tunnel(self):
        """Method to build the list of available cameras not already associated with a tunnel"""

        for tunnel in self.local_tunnels:
            if tunnel.camera_entrance_1 in self.cameras_not_in_tunnels:
                self.cameras_not_in_tunnels.remove(tunnel.camera_entrance_1)
            if tunnel.camera_entrance_2 in self.cameras_not_in_tunnels:
                self.cameras_not_in_tunnels.remove(tunnel.camera_entrance_2)

    def update_tunnels_list(self):
        """Method to initialize tunnel combobox with existing tunnel objects"""

        self.ui.listWidget.clear()
        for tunnel in self.local_tunnels:
            self.ui.listWidget.addItem(tunnel.id)

    def on_add_tunnel_clicked(self):
        """Method to handle new tunnel insertion"""

        if (dlg := DialogConfigureTunnel(self.cameras_not_in_tunnels)).exec():
            self.local_tunnels.append(dlg.tunnel)
            self.cameras_not_in_tunnels.remove(dlg.tunnel.camera_entrance_1)
            self.cameras_not_in_tunnels.remove(dlg.tunnel.camera_entrance_2)
            self.update_tunnels_list()

    def on_remove_tunnel_clicked(self):
        """Method to remove a tunnel"""

        if selected_item := self.ui.listWidget.currentItem():
            selected_tunnel_id = selected_item.text()
            for tunnel in tuple(self.local_tunnels):
                if tunnel.id == selected_tunnel_id:
                    self.cameras_not_in_tunnels.append(tunnel.camera_entrance_1)
                    self.cameras_not_in_tunnels.append(tunnel.camera_entrance_2)
                    self.local_tunnels.remove(tunnel)
                    break
            self.update_tunnels_list()
            self.ui.listWidget.clearSelection()
            self.on_tunnel_selection_changed()

    def on_edit_tunnel_clicked(self):
        """Method to handle tunnel editing"""

        if selected_item := self.ui.listWidget.currentItem():
            selected_tunnel_id = selected_item.text()
            for tunnel in self.local_tunnels:
                if tunnel.id == selected_tunnel_id:
                    orig_camera_1 = tunnel.camera_entrance_1
                    orig_camera_2 = tunnel.camera_entrance_2
                    if orig_camera_1 not in self.cameras_not_in_tunnels:
                        self.cameras_not_in_tunnels.append(orig_camera_1)
                    if orig_camera_2 not in self.cameras_not_in_tunnels:
                        self.cameras_not_in_tunnels.append(orig_camera_2)
                    if (dlg := DialogConfigureTunnel(self.cameras_not_in_tunnels, tunnel)).exec():
                        tunnel.id = dlg.tunnel.id
                        tunnel.camera_entrance_1 = dlg.tunnel.camera_entrance_1
                        tunnel.entrance_1_direction = dlg.tunnel.entrance_1_direction
                        tunnel.entrance_2_direction = dlg.tunnel.entrance_2_direction
                        tunnel.camera_entrance_2 = dlg.tunnel.camera_entrance_2
                        if (orig_camera_1 != tunnel.camera_entrance_1 and orig_camera_1 != tunnel.camera_entrance_2):
                            self.cameras_not_in_tunnels.append(orig_camera_1)
                        if (orig_camera_2 != tunnel.camera_entrance_2 and orig_camera_2 != tunnel.camera_entrance_1):
                            self.cameras_not_in_tunnels.append(orig_camera_2)
                    break
            self.update_cameras_not_in_tunnel()
            self.update_tunnels_list()
            self.ui.listWidget.clearSelection()
            self.on_tunnel_selection_changed()

    def on_tunnel_selection_changed(self):
        """Method to handle list item selection"""

        selected = bool(self.ui.listWidget.currentItem())
        self.ui.pushButton_edit_tunnel.setEnabled(selected)
        self.ui.pushButton_remove_tunnel.setEnabled(selected)

    def accept_and_close(self):
        """Method to apply changed before closing dialog."""

        Tunnel.tunnels = self.local_tunnels
        self.accept()