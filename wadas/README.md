# WADAS

## Environment setup

1. Install Python 3.11 (https://www.python.org/downloads/)
2. Import the WADAS project into your IDE
3. Create a virtual environment from the project root:
   ```
   python3.11 -m venv .venv
   ```
4. Activate the virtual environment:
   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **Windows (cmd):** `.venv\Scripts\activate.bat`
   - **Linux/macOS:** `source .venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r <WADAS_ROOT_DIR>/requirements.txt
   ```
6. Select the `.venv` environment in your IDE (N.B. Reference IDE used for the project is PyCharm)

### Additional dependencies

#### OpenSSL (required by `wadas-runtime`)

Install via [Chocolatey](https://chocolatey.org/) on Windows. Run the following in an **elevated PowerShell** session:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install openssl
```

#### WMIC (Windows only)

Enable **WMIC** via Windows Optional Features:

1. Open **Settings** → **System** → **Optional features** (or run `optionalfeatures` from Run)
2. Search for **WMIC** and enable it

## Run WADAS (with UI)

1. Run `main.py`

## Development

We use the [pre-commit framework](https://pre-commit.com/) for hook management. The recommended way of installing it is using pip:

* `pip install pre-commit`

The hooks can then be installed into your local clone using:

* `pre-commit install [--allow-missing-config]`

`--allow-missing-config` is an optional argument that will allow users to have the hooks installed and be functional even if using an older branch that does not have them tracked. A warning will be displayed for such cases when the hooks are ran.

Uninstalling the hooks can be done using `pre-commit uninstall`.
