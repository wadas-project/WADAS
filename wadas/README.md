# WADAS POC

## Environment setup
1. Install conda (https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
2. Import the WADAS project into your IDE
3. Run the command  ```conda env create --file="<PROJECT_FOLDER>\WADAS\wadas\conda_env_setup.yml"```
4. Select the created environment in your IDE (N.B. Reference IDE used for the project is PyCharm)
5. Using conda env you might have to export following environment variable:
```QT_PLUGIN_PATH=%VIRTUAL_ENV%\Lib\site-packages\PySide6\plugins``` to let the UI work properly.

## Run WADAS (with UI)

    1. Run main.py

## Development

We use the [pre-commit framework](https://pre-commit.com/) for hook management. The recommended way of installing it is using pip:

* `pip install pre-commit`

The hooks can then be installed into your local clone using:

* `pre-commit install [--allow-missing-config]`

--allow-missing-config is an optional argument that will allow users to have the hooks installed and be functional even if using an older branch that does not have them tracked. A warning will be displayed for such cases when the hooks are ran.

Uninstalling the hooks can be done using pre-commit uninstall.
