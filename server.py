# -*- coding: utf-8 -*-
"""
Local LAN HTTP Server for Genesis Telemetry
Serves index.html & simulator.html to any computer or tablet on the local network.
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import socket

latest_state = {
    "brand": "General Electric",
    "model": "GE-750KVA-IND",
    "rpm": 1500,
    "kw": 485.4,
    "hz": 50.02,
    "coolant": 84.5,
    "oil": 4.8,
    "tankBase": 84.0
}

class TelemetryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/telemetry':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(latest_state).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        global latest_state
        if self.path == '/api/telemetry':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                latest_state.update(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    port = 8000
    host_ip = get_ip()
    print("=" * 70)
    print("GENESIS TELEMETRY — LAN MULTI-COMPUTER SERVER")
    print(f"Main Dashboard URL : http://{host_ip}:{port}/index.html")
    print(f"Remote Controller  : http://{host_ip}:{port}/simulator.html")
    print("Open the Remote Controller on any phone, tablet, or another computer!")
    print("=" * 70)
    httpd = HTTPServer(('0.0.0.0', port), TelemetryHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
