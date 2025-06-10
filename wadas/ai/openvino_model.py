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
# Date: 2024-10-11
# Description: Module containing OpenVino class and methods.


import os

import openvino as ov
import openvino.properties as props
import torch
from huggingface_hub import snapshot_download

core = ov.Core()
core.set_property({props.cache_dir: "cache"})

__model_folder__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "model")


class OVModel:
    def __init__(self, model_name, device):
        """Base class for OpenVino models"""
        self.device = device
        self.model = self.compile_model(self.load_model(model_name))

    def load_model(self, model_name):
        """Load model from file"""
        return core.read_model(os.path.join(__model_folder__, model_name))

    def get_available_device(self):
        """Get available devices"""
        return core.available_devices

    def compile_model(self, model):
        """Compile model"""
        return ov.compile_model(
            model,
            device_name=self.device.upper(),
        )

    def __call__(self, input: torch.Tensor) -> torch.Tensor | list[torch.Tensor]:
        """Run model"""
        results = [torch.tensor(t) for t in self.model(input).values()]
        if len(results) == 1:
            return results[0]
        return results

    @staticmethod
    def check_model(model_name):
        """Check if model is initialized"""
        return os.path.exists(os.path.join(__model_folder__, model_name))

    @staticmethod
    def download_model(model_name, force: bool = False):
        """Check if model is initialized"""
        return snapshot_download(
            repo_id="wadas-it/wadas",
            repo_type="model",
            revision="main",
            local_dir=__model_folder__,
            force_download=force,
            allow_patterns=[f"{model_name}.xml", f"{model_name}.bin"],
        )
