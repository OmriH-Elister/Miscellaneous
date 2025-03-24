#!/usr/bin/env python3
import subprocess
import threading
import os
import webbrowser
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

PORT = 8000
DNS_SERVER = '8.8.8.8'
LATEST_RESPONSE = {
    "content": b"<html><body><h1>No content yet</h1></body></html>",
    "content_type": "text/html; charset=utf-8"
}
REQUEST_VERSION = {"v": str(int(time.time()))}

def resolve_domain(domain, dns_server):
    result = subprocess.run(['nslookup', '-type=A', domain, dns_server],
                            capture_output=True, text=True)
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if 'Address:' in line and dns_server not in line:
                return line.split(':')[1].strip()
    print(f"[!] DNS resolution failed:\n{result.stderr}")
    return None

def fetch_url(ip, original_url, hostname):
    parsed = urlparse(original_url)
    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query
    scheme = parsed.scheme or 'http'
    full_url = f"{scheme}://{ip}{path}"

    curl_cmd = [
        'curl', '-sL', full_url,
        '-H', f'Host: {hostname}',
        '--insecure'
    ]
    print(f"[+] curl: {' '.join(curl_cmd)}")

    try:
        response = subprocess.run(curl_cmd, capture_output=True)
        if response.returncode == 0:
            return response.stdout
        else:
            print(f"[!] curl failed: {response.stderr.decode()}")
    except Exception as e:
        print(f"[!] Error running curl: {e}")
    return None

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            wrapper = f"""
            <html>
                <head><title>DNS Bypass Viewer</title></head>
                <body style="margin:0;padding:0">
                    <iframe id="viewer" src="/content?v=init" width="100%" height="100%" style="border:none;"></iframe>
                    <script>
                        let currentVersion = "init";
                        async function pollForUpdates() {{
                            try {{
                                const res = await fetch('/version');
                                const newVersion = await res.text();
                                if (newVersion !== currentVersion) {{
                                    currentVersion = newVersion;
                                    document.getElementById('viewer').src = '/content?v=' + currentVersion;
                                }}
                            }} catch (err) {{
                                console.error('Version check failed', err);
                            }}
                        }}
                        setInterval(pollForUpdates, 2000);
                    </script>
                </body>
            </html>
            """
            self.wfile.write(wrapper.encode())
        elif self.path.startswith("/content"):
            self.send_response(200)
            self.send_header("Content-Type", LATEST_RESPONSE["content_type"])
            self.end_headers()
            self.wfile.write(LATEST_RESPONSE["content"])
        elif self.path.startswith("/version"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(REQUEST_VERSION["v"].encode())
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        return  # Suppress default noisy HTTP server logs

def start_server():
    server = HTTPServer(('localhost', PORT), ProxyHandler)
    print(f"[+] Local web server started at http://localhost:{PORT}")
    threading.Thread(target=server.serve_forever, daemon=True).start()

def main():
    start_server()

    webbrowser.open(f"http://localhost:{PORT}", new=2)

    while True:
        try:
            url = input("URL: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[+] Exiting.")
            break

        if not url:
            continue

        parsed = urlparse(url)
        if not parsed.hostname:
            print("[!] Invalid URL")
            continue

        domain = parsed.hostname
        ip = resolve_domain(domain, DNS_SERVER)
        if not ip:
            continue

        print(f"[+] Resolved {domain} -> {ip}")
        print("[+] Fetching page...")

        html = fetch_url(ip, url, domain)
        if html:
            LATEST_RESPONSE["content"] = html
            REQUEST_VERSION["v"] = str(int(time.time()))
            print(f"[+] Content updated. Browser should refresh.")
        else:
            print("[!] Failed to fetch content.")

if __name__ == "__main__":
    main()
