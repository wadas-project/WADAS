from flask import Flask, jsonify
import subprocess
import re
import psutil
import wmi

app = Flask(__name__)
w = wmi.WMI(namespace="root\\CIMV2")

# --- GPU UTILIZATION (via PowerShell) ---
def get_gpu_utilization():
    try:
        output = subprocess.check_output([
            'powershell',
            '-Command',
            'Get-Counter "\\GPU Engine(*)\\Utilization Percentage"'
        ], universal_newlines=True)

        matches = re.findall(r'GPU Engine\((.*?)\)\s+:\s+([0-9.]+)', output)
        total_usage = sum(float(usage) for _, usage in matches)
        return {"total_gpu_utilization_percent": round(total_usage, 2)}
    except Exception as e:
        return {"error": str(e)}

# --- Flask Endpoint ---
@app.route('/status')
def status():
    return jsonify({
        "gpu": get_gpu_utilization()
    })

# --- Run server ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)