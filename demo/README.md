# WADAS POC

## Dependencies

1. [Pytorch Wildlife](https://github.com/microsoft/CameraTraps)
2. [torch](https://pytorch.org/)
3. [intel-npu-acceleration-library](https://github.com/intel/intel-npu-acceleration-library)

## Environment setup

Reference IDE used for the project is Visual Studio Code, Conda (Miniconda) as package manager.
Instructions will reflect the above mentioned reference environment, users are free to choose any equivalent environment for development and execution of the project.

### Dependencies install

   1. Import the WADAS project into your IDE
   2. Create venv enviromnent (See https://code.visualstudio.com/docs/python/environments for detailed info about how to create virtual environment within VScode, we used conda.)
   3. Install dependencies:
      a. pip install -r requirements.txt .\poc\requirements.txt (or run Python: Create environment from VScode)
      b. Aditional useful dependencies to tune up jupyter kernels are: ipykernel jupyter

## Run animal detection demo

    1. Open demo.ipynb and make sure you have selected your local kernel (python venv) (in VScode run the command "Select Notebook Kernel")
    2. Run pw_demo.ipynb (animal detection only)

## Run animal detection + classification demo

### Prerequisites:

 1. Download the DeepFauna model "deepfaune-vit_large_patch14_dinov2.lvd142m.pt" from [this url](https://huggingface.co/Addax-Data-Science/Deepfaune_v1.1/resolve/main/deepfaune-vit_large_patch14_dinov2.lvd142m.pt?download=true).
 2. Update DeepFauna model local path in classify_Detections.py, L66.

    1. Open demo.ipynb and make sure you have selected your local kernel (python venv) (in VScode run the command "Select Notebook Kernel")
    2. Run df_demo.ipynb (animal detection + classification)

NOTE: Depending on the HW you're running the demo on, you could select different kernel to run the model on: npu, cuda or cpu. Make sure you properly configure the environment dependency of your custom kernel first.

## Development

We use the [pre-commit framework](https://pre-commit.com/) for hook management. The recommended way of installing it is using pip:

* `pip install pre-commit`

The hooks can then be installed into your local clone using:

* `pre-commit install [--allow-missing-config]`

--allow-missing-config is an optional argument that will allow users to have the hooks installed and be functional even if using an older branch that does not have them tracked. A warning will be displayed for such cases when the hooks are ran.

Uninstalling the hooks can be done using pre-commit uninstall.
