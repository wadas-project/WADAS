# Let's Encrypt Certificate Request Process [Windows]

### Prerequisites
- Windows 10/11
- Python3 installed and configured in $PATH variable
- Machine's IP Address and Port 80 reachable from Internet (for Let's Encrypt validation phase)

### Steps
1. Download WinACME from https://www.win-acme.com/.
2. Extract WinACME.
3. Copy/Paste the `cert_request.ps1` script into WinACME directory.
4. Enable Powershell script execution.
	- open a Powershell console as Administrator.
	- run `set-executionpolicy remotesigned`
5. Run `.\cert_request.ps1` from a Powershell console, passing the following parameters:
    - `domain`: the domain you want to generate a certificate for (e.g. `node1.wadas.it`).
    - `pemfilespath`: path to a folder you want to store the generated certificate.
6. Once the process is completed, copy the following files (located into the specified `pemfilespath` directory) into `WADAS_ROOT/wadas_webserver/web_cert`, renaming them in `cert.pem` and `key.pem`:
    - `DOMAIN-crt.pem` -> `cert.pem`
    - `DOMAIN-key.pem` -> `key.pem`