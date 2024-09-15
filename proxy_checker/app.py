from flask import Flask, render_template, request, jsonify
import requests
import time
import socks
import socket

app = Flask(__name__)

# Fungsi untuk cek proxy HTTP atau HTTPS
def check_http_proxy(ip, port, user=None, password=None, proxy_type='http'):
    proxy = {proxy_type: f"{proxy_type}://{ip}:{port}"}
    if user and password:
        proxy = {
            proxy_type: f"{proxy_type}://{user}:{password}@{ip}:{port}"
        }
    start_time = time.time()
    try:
        response = requests.get("http://www.google.com", proxies=proxy, timeout=3)
        response_time = time.time() - start_time
        return response.status_code == 200, response_time
    except:
        return False, None

# Fungsi untuk cek proxy SOCKS5
def check_socks_proxy(ip, port, user=None, password=None):
    if user and password:
        socks.setdefaultproxy(socks.SOCKS5, ip, int(port), True, user, password)
    else:
        socks.setdefaultproxy(socks.SOCKS5, ip, int(port))
    socket.socket = socks.socksocket
    start_time = time.time()
    try:
        response = requests.get("http://www.google.com", timeout=3)
        response_time = time.time() - start_time
        return response.status_code == 200, response_time
    except:
        return False, None

# Fungsi untuk memparsing format proxy
def parse_proxy(proxy_string):
    parts = proxy_string.split(':')
    
    if len(parts) == 4:
        # Format: IP:PORT:USER:PASS
        return {"ip": parts[0], "port": parts[1], "type": "socks5", "user": parts[2], "password": parts[3]}
    elif len(parts) == 3:
        # Format: IP:PORT:TYPE (TYPE can be http or https)
        return {"ip": parts[0], "port": parts[1], "type": parts[2], "user": None, "password": None}
    else:
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_proxy', methods=['POST'])
def check_proxy():
    proxies = request.json.get('proxies', [])
    results = []
    total_proxies = len(proxies)

    for idx, proxy_string in enumerate(proxies):
        proxy = parse_proxy(proxy_string.strip())
        if proxy:
            ip, port, proxy_type, user, password = proxy['ip'], proxy['port'], proxy['type'], proxy['user'], proxy['password']
            if proxy_type in ['http', 'https']:
                is_alive, response_time = check_http_proxy(ip, port, user, password, proxy_type)
            elif proxy_type == 'socks5':
                is_alive, response_time = check_socks_proxy(ip, port, user, password)
            else:
                is_alive, response_time = False, None
            
            results.append({
                'ip': ip,
                'port': port,
                'type': proxy_type,
                'status': 'alive' if is_alive else 'dead',
                'response_time': response_time if is_alive else '-',
                'progress': (idx + 1) / total_proxies * 100
            })
        else:
            results.append({
                'ip': 'Invalid format',
                'port': '-',
                'type': '-',
                'status': 'Error',
                'response_time': '-',
                'progress': (idx + 1) / total_proxies * 100
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
