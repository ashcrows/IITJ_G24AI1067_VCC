from flask import Flask, render_template
import platform
import psutil

app = Flask(__name__)

@app.route('/')
def index():
    info = {
        'Hostname': platform.node(),
        'System': platform.system(),
        'Release': platform.release(),
        'Version': platform.version(),
        'Machine': platform.machine(),
        'Processor': platform.processor(),
        'CPU Cores': psutil.cpu_count(logical=False),
        'Total RAM': f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
        'IP Address': psutil.net_if_addrs()['enp0s3'][0].address
    }
    return render_template('index.html', info=info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
