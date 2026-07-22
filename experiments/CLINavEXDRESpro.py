import subprocess
import threading
import os
import webbrowser
import json
import time
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8000
DNS_SERVER = '8.8.8.8'
LATEST_RESPONSE = {
    "content": b"<html><body style='font-family:sans-serif;padding:2rem'><h1>Local Relay Active</h1><p>Enter a URL in the terminal to begin.</p></body></html>",
    "content_type": "text/html; charset=utf-8"
}
REQUEST_VERSION = {"v": "init"}
LOGS = []

def add_internal_log(msg):
    LOGS.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(LOGS) > 20: LOGS.pop(0)

def resolve_domain(domain, dns_server):
    add_internal_log(f"Resolving {domain} via {dns_server}...")
    try:
        # Cross-platform nslookup parsing
        result = subprocess.run(['nslookup', '-type=A', domain, dns_server],
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if 'Address:' in line and dns_server not in line:
                    ip = line.split(':')[1].strip()
                    add_internal_log(f"Success: {domain} -> {ip}")
                    return ip
    except Exception as e:
        add_internal_log(f"DNS Error: {str(e)}")
    return None

def fetch_url(ip, original_url, hostname):
    parsed = urlparse(original_url)
    path = parsed.path or '/'
    if parsed.query: path += '?' + parsed.query
    scheme = parsed.scheme or 'http'
    full_url = f"{scheme}://{ip}{path}"

    curl_cmd = ['curl', '-sL', full_url, '-H', f'Host: {hostname}', '--insecure']
    add_internal_log(f"Executing: {' '.join(curl_cmd)}")

    try:
        response = subprocess.run(curl_cmd, capture_output=True, timeout=10)
        if response.returncode == 0:
            return response.stdout
    except Exception as e:
        add_internal_log(f"Fetch Error: {str(e)}")
    return None

# This string contains the React UI served via CDN so it runs in your local browser without a build step.
UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TermiNav Pro - Local Engine</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #050505; color: #d4d4d8; font-family: monospace; margin: 0; overflow: hidden; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;

        function App() {
            const [version, setVersion] = useState("init");
            const [logs, setLogs] = useState([]);
            const [resolvedIp, setResolvedIp] = useState("---.---.---.---");

            // Polling logic to sync with Python state
            useEffect(() => {
                const interval = setInterval(async () => {
                    try {
                        const res = await fetch('/api/state');
                        const data = await res.json();
                        if (data.version !== version) setVersion(data.version);
                        setLogs(data.logs);
                        setResolvedIp(data.ip);
                    } catch (e) {}
                }, 1000);
                return () => clearInterval(interval);
            }, [version]);

            return (
                <div className="flex flex-col h-screen">
                    <header className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-[#0a0a0a]">
                        <div className="flex items-center space-x-3">
                            <i className="fas fa-shield-alt text-indigo-400 text-xl"></i>
                            <div>
                                <h1 className="text-sm font-bold tracking-widest text-white">WB-CLINAVAEXDRES <span className="text-[10px] bg-indigo-500/20 px-1 border border-indigo-500/30 rounded ml-1">LOCAL</span></h1>
                                <p className="text-[9px] text-zinc-500 uppercase">Memory Relay Engine Active</p>
                            </div>
                        </div>
                        <div className="flex gap-8 text-[11px]">
                            <div className="text-right">
                                <p className="text-zinc-600 font-bold uppercase text-[9px]">Resolved IP</p>
                                <p className="text-indigo-300">{resolvedIp}</p>
                            </div>
                            <div className="text-right border-l border-white/10 pl-8">
                                <p className="text-zinc-600 font-bold uppercase text-[9px]">Buffer Version</p>
                                <p className="text-emerald-400">{version}</p>
                            </div>
                        </div>
                    </header>

                    <main className="flex flex-1 overflow-hidden p-4 gap-4">
                        <section className="w-[400px] flex flex-col gap-4">
                            <div className="flex-1 bg-[#0d0d0f] rounded-xl border border-white/5 flex flex-col overflow-hidden">
                                <div className="bg-[#161618] px-4 py-2 border-b border-white/5 text-[10px] font-bold text-zinc-500 uppercase">Local System Logs</div>
                                <div className="flex-1 p-4 text-xs space-y-1 overflow-y-auto custom-scrollbar">
                                    {logs.map((log, i) => (
                                        <div key={i} className={i === 0 ? "text-indigo-300" : "text-zinc-600"}>{log}</div>
                                    ))}
                                </div>
                            </div>
                        </section>

                        <section className="flex-1 bg-[#0d0d0f] rounded-xl border border-white/5 flex flex-col overflow-hidden shadow-2xl">
                            <div className="h-10 bg-[#161618] border-b border-white/5 flex items-center px-4">
                                <div className="bg-black/40 border border-white/5 rounded px-3 py-1 flex items-center text-[11px] text-zinc-500 w-full">
                                    <i className="fas fa-lock text-emerald-500 mr-2 text-[10px]"></i>
                                    <span>http://localhost:8000/content?v={version}</span>
                                </div>
                            </div>
                            <div className="flex-1 bg-white">
                                <iframe src={`/content?v=${version}`} className="w-full h-full border-none" title="content-viewer"></iframe>
                            </div>
                        </section>
                    </main>

                    <footer className="h-8 bg-[#0a0a0a] border-t border-white/5 flex items-center px-6 justify-between text-[9px] font-bold text-zinc-700 uppercase">
                        <span>Status: 127.0.0.1:8000 Online</span>
                        <span>DNS: 8.8.8.8 (Manual Resolver)</span>
                    </footer>
                </div>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global LATEST_RESPONSE, REQUEST_VERSION, LOGS
        
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(UI_HTML.encode())
            
        elif self.path.startswith("/api/state"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {"version": REQUEST_VERSION["v"], "logs": LOGS[::-1], "ip": globals().get('resolved_ip_val', '---')}
            self.wfile.write(json.dumps(data).encode())

        elif self.path.startswith("/content"):
            self.send_response(200)
            self.send_header("Content-Type", LATEST_RESPONSE["content_type"])
            # Strip security headers that block iframes
            self.send_header("X-Frame-Options", "ALLOWALL")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(LATEST_RESPONSE["content"])
        else:
            self.send_error(404)

    def log_message(self, format, *args): return

def run_server():
    server = HTTPServer(('localhost', PORT), ProxyHandler)
    server.serve_forever()

if __name__ == "__main__":
    print(f"\n[+] WB-CLINAVAEXDRES ENGINE INITIALIZED")
    print(f"[+] Starting local relay on http://localhost:{PORT}")
    
    # Start server in background
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

    while True:
        try:
            url = input("\nEnter URL: ").strip()
            if not url: continue
            
            parsed = urlparse(url if '://' in url else 'http://' + url)
            domain = parsed.hostname
            
            # Step 1: DNS
            ip = resolve_domain(domain, DNS_SERVER)
            globals()['resolved_ip_val'] = ip
            
            if ip:
                # Step 2: Fetch
                html = fetch_url(ip, url, domain)
                if html:
                    LATEST_RESPONSE["content"] = html
                    REQUEST_VERSION["v"] = str(int(time.time()))
                    print(f"[+] Relay updated. Version: {REQUEST_VERSION['v']}")
                else:
                    print("[!] Failed to fetch content via CURL.")
            else:
                print("[!] DNS Resolution failed.")
                
        except (KeyboardInterrupt, EOFError):
            print("\n[+] Shutting down engine.")
            break