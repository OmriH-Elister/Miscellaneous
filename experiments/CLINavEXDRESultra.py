import subprocess
import threading
import os
import webbrowser
import json
import time
import re
from urllib.parse import urlparse, parse_qs, urlencode
from http.server import BaseHTTPRequestHandler, HTTPServer
from html.parser import HTMLParser

PORT = 8000
DNS_SERVER = '8.8.8.8'
LATEST_RESPONSE = {
    "content": b"<html><body style='font-family:sans-serif;padding:2rem;background:#050505;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:80vh'><h1>TermiNav Relay Active</h1><p style='color:#71717a'>Waiting for CLI input... Enter a URL in your terminal to begin.</p></body></html>",
    "content_type": "text/html; charset=utf-8"
}
REQUEST_VERSION = {"v": "init"}
LOGS = []

def add_internal_log(msg):
    LOGS.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(LOGS) > 30: LOGS.pop(0)

class FormParser(HTMLParser):
    """Parses HTML to find interactive fields with friendly descriptions."""
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.current_form = None

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'form':
            self.current_form = attr_dict.get('action', '')
        if tag in ['input', 'textarea', 'select']:
            name = attr_dict.get('name')
            type_ = attr_dict.get('type', 'text')
            placeholder = attr_dict.get('placeholder', '')
            label = attr_dict.get('aria-label', '')
            
            if name and type_ != 'hidden':
                # Build a friendly hint
                hint = label or placeholder or name
                self.inputs.append({
                    'name': name, 
                    'type': type_, 
                    'hint': hint,
                    'value': attr_dict.get('value', '')
                })

def resolve_domain(domain, dns_server):
    add_internal_log(f"DNS Bypass: nslookup {domain} via {dns_server}")
    try:
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

def fetch_url(ip, original_url, hostname, data=None):
    parsed = urlparse(original_url)
    path = parsed.path or '/'
    if parsed.query: path += '?' + parsed.query
    scheme = parsed.scheme or 'http'
    base_url = f"{scheme}://{hostname}"
    full_url = f"{scheme}://{ip}{path}"

    curl_cmd = ['curl', '-sL', full_url, '-H', f'Host: {hostname}', '--insecure']
    if data:
        post_fields = urlencode(data)
        curl_cmd += ['-d', post_fields]
        add_internal_log(f"POST Payload: {post_fields}")

    add_internal_log(f"Executing: {' '.join(curl_cmd)}")

    try:
        response = subprocess.run(curl_cmd, capture_output=True, timeout=12)
        if response.returncode == 0:
            content = response.stdout
            try:
                html_str = content.decode('utf-8', errors='ignore')
                # Inject <base> tag immediately after <head> to fix assets
                base_tag = f'<base href="{base_url}/">'
                if '<head>' in html_str:
                    html_str = html_str.replace('<head>', f'<head>{base_tag}', 1)
                else:
                    html_str = f'<html><head>{base_tag}</head>{html_str}'
                return html_str.encode('utf-8')
            except:
                return content
    except Exception as e:
        add_internal_log(f"Fetch Error: {str(e)}")
    return None

UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TermiNav Pro - Dashboard</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #050505; color: #d4d4d8; font-family: ui-monospace, monospace; margin: 0; overflow: hidden; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #27272a; border-radius: 10px; }
        .browser-shadow { box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8); }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect } = React;

        function App() {
            const [version, setVersion] = useState("init");
            const [logs, setLogs] = useState([]);
            const [status, setStatus] = useState("IDLE");
            const [sidebarOpen, setSidebarOpen] = useState(true);
            const [viewportSize, setViewportSize] = useState('full');

            useEffect(() => {
                const interval = setInterval(async () => {
                    try {
                        const res = await fetch('/api/state');
                        const data = await res.json();
                        setVersion(data.version);
                        setLogs(data.logs);
                        setStatus(data.status);
                    } catch (e) {}
                }, 1000);
                return () => clearInterval(interval);
            }, []);

            const getViewportWidth = () => {
                if (viewportSize === 'mobile') return '375px';
                if (viewportSize === 'tablet') return '768px';
                if (viewportSize === 'desktop') return '1024px';
                return '100%';
            };

            return (
                <div className="flex flex-col h-screen overflow-hidden">
                    <header className="flex items-center justify-between px-6 py-3 border-b border-white/5 bg-[#0a0a0a] z-50">
                        <div className="flex items-center space-x-4">
                            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-white/5 rounded-lg text-zinc-500 transition-colors">
                                <i className={`fas ${sidebarOpen ? 'fa-indent' : 'fa-outdent'}`}></i>
                            </button>
                            <h1 className="text-xs font-black tracking-[0.2em] text-white underline decoration-indigo-500/50 underline-offset-4">WB-CLINAVAEXDRES <span className="text-indigo-400 text-[10px] ml-2">PRO_ENGINE</span></h1>
                        </div>
                        <div className="flex items-center space-x-6">
                            <div className="flex items-center space-x-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/5 text-[10px]">
                                <i className={`fas fa-circle text-[8px] ${status === 'IDLE' ? 'text-zinc-700' : 'text-emerald-500 animate-pulse'}`}></i>
                                <span className="text-zinc-500 font-bold uppercase tracking-widest">{status}</span>
                            </div>
                        </div>
                    </header>

                    <main className="flex flex-1 overflow-hidden">
                        <aside className={`transition-all bg-[#0d0d0f] border-r border-white/5 flex flex-col overflow-hidden ${sidebarOpen ? 'w-[360px]' : 'w-0'}`}>
                            <div className="bg-[#161618] px-4 py-2.5 border-b border-white/5 flex items-center justify-between min-w-[360px]">
                                <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">Relay Diagnostics</span>
                                <i className="fas fa-microchip text-zinc-700 text-[10px]"></i>
                            </div>
                            <div className="flex-1 p-5 text-[11px] space-y-2 overflow-y-auto custom-scrollbar min-w-[360px] font-mono">
                                {logs.length === 0 && <div className="text-zinc-800 italic">Listening for local relay traffic...</div>}
                                {logs.map((log, i) => (
                                    <div key={i} className={i === 0 ? "text-indigo-300 font-bold" : "text-zinc-600"}>{log}</div>
                                ))}
                            </div>
                        </aside>

                        <section className="flex-1 bg-[#050505] flex flex-col items-center justify-center relative p-6 transition-all">
                            <div className="absolute top-8 flex items-center space-x-1 bg-[#161618] p-1 rounded-xl border border-white/10 shadow-xl z-20">
                                {['mobile', 'tablet', 'desktop', 'full'].map(mode => (
                                    <button key={mode} onClick={() => setViewportSize(mode)} className={`p-2 px-3 rounded-lg text-[10px] font-bold transition-all uppercase ${viewportSize === mode ? 'bg-indigo-600 text-white' : 'text-zinc-500 hover:text-white'}`}>
                                        <i className={`fas fa-${mode === 'mobile' ? 'mobile-alt' : mode === 'tablet' ? 'tablet-alt' : mode === 'desktop' ? 'desktop' : 'expand'} mr-2`}></i>{mode}
                                    </button>
                                ))}
                            </div>

                            <div className="transition-all bg-white rounded-2xl overflow-hidden browser-shadow flex flex-col relative" style={{ width: getViewportWidth(), height: viewportSize === 'full' ? '100%' : '85%' }}>
                                <div className="h-10 bg-[#f1f1f1] border-b border-gray-200 flex items-center px-4 justify-between shrink-0">
                                    <div className="flex items-center space-x-1.5"><div className="w-2.5 h-2.5 rounded-full bg-red-400"></div><div className="w-2.5 h-2.5 rounded-full bg-yellow-400"></div><div className="w-2.5 h-2.5 rounded-full bg-green-400"></div></div>
                                    <div className="bg-white border border-gray-300 rounded-md px-3 py-1 flex items-center text-[11px] text-gray-400 w-full max-w-lg mx-8 overflow-hidden">
                                        <i className="fas fa-lock text-emerald-500 mr-2 text-[10px]"></i>
                                        <span className="truncate">localhost:8000/content?v={version}</span>
                                    </div>
                                    <i className="fas fa-sync-alt text-gray-400 text-xs"></i>
                                </div>
                                <div className="flex-1 bg-white relative">
                                    <iframe src={`/content?v=${version}`} className="w-full h-full border-none" title="content"></iframe>
                                </div>
                            </div>
                        </section>
                    </main>
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
            self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers()
            self.wfile.write(UI_HTML.encode())
        elif self.path.startswith("/api/state"):
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
            data = {"version": REQUEST_VERSION["v"], "logs": LOGS[::-1], "status": globals().get('engine_status', 'IDLE')}
            self.wfile.write(json.dumps(data).encode())
        elif self.path.startswith("/content"):
            self.send_response(200); self.send_header("Content-Type", LATEST_RESPONSE["content_type"])
            self.send_header("X-Frame-Options", "ALLOWALL"); self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers(); self.wfile.write(LATEST_RESPONSE["content"])
        else: self.send_error(404)

    def log_message(self, format, *args): return

def run_server():
    server = HTTPServer(('localhost', PORT), ProxyHandler)
    server.serve_forever()

if __name__ == "__main__":
    print(f"\n[+] WB-CLINAVAEXDRES PRO EDITION")
    print(f"[+] Local Relay: http://localhost:{PORT}")
    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

    while True:
        try:
            globals()['engine_status'] = 'IDLE'
            url = input("\nEnter URL: ").strip()
            if not url: continue
            
            parsed = urlparse(url if '://' in url else 'http://' + url)
            domain = parsed.hostname
            if not domain: continue
                
            globals()['engine_status'] = 'BUSY'
            ip = resolve_domain(domain, DNS_SERVER)
            
            if ip:
                html_bytes = fetch_url(ip, url, domain)
                if html_bytes:
                    LATEST_RESPONSE["content"] = html_bytes
                    REQUEST_VERSION["v"] = str(int(time.time()))
                    
                    parser = FormParser()
                    try:
                        parser.feed(html_bytes.decode('utf-8', errors='ignore'))
                        if parser.inputs:
                            print(f"\n[!] Interactive Forms Detected ({len(parser.inputs)} fields)")
                            interact = input("Would you like to fill these out? (y/n): ").lower()
                            if interact == 'y':
                                form_data = {}
                                print("\n--- CLI FORM ENTRY ---")
                                for field in parser.inputs:
                                    prompt = f"  > Enter {field['hint']} "
                                    if field['type'] == 'password':
                                        prompt += "(SECRET): "
                                    else:
                                        prompt += f"({field['type']}): "
                                    
                                    val = input(prompt)
                                    form_data[field['name']] = val
                                
                                print("\n[+] Resubmitting as POST request via relay...")
                                html_bytes = fetch_url(ip, url, domain, data=form_data)
                                if html_bytes:
                                    LATEST_RESPONSE["content"] = html_bytes
                                    REQUEST_VERSION["v"] = str(int(time.time()))
                    except Exception as e:
                        add_internal_log(f"Parser Warning: {str(e)}")
                    
                    print(f"[+] Graphical view updated.")
                else:
                    print("[!] Fetch failed.")
            else:
                print("[!] DNS Resolution failed.")
                
        except (KeyboardInterrupt, EOFError):
            print("\n[+] Shutting down."); break