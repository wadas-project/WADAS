param (
    [string]$domain,
    [string]$pemfilespath
)

if (-not $domain -or -not $pemfilespath) {
    Write-Host "Usage: .\cert_request.ps1 -domain tuodominio.com -pemfilespath C:\path\to\pem"
    exit 1
}

$tempFolder = Join-Path $env:TMP ("wadas_cert_process_" + [System.Guid]::NewGuid().ToString().Substring(0, 8))
New-Item -ItemType Directory -Path $tempFolder | Out-Null

# Start HTTP Server for certificate challenge
$pythonProcess = Start-Process -NoNewWindow -PassThru -FilePath "python" -ArgumentList "-m http.server --directory `"$tempFolder`" 80"
Write-Host "HTTP Server started in: $tempFolder"
Start-Sleep -Seconds 5

# Start win-acme to generate the certificate
Write-Host "Starting certificate generation for $domain..."
.\wacs.exe --target manual --host $domain --validation filesystem --webroot $tempFolder --accepttos --emailaddress info@wadas.it --store pemfiles --pemfilespath $pemfilespath

# Stop HTTP Server
Write-Host "Stopping HTTP Server..."
Stop-Process -Id $pythonProcess.Id -Force

Write-Host "Certificate successfully generated and saved in: $pemfilespath"
