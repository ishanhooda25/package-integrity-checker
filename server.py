"""Zero-dependency web server with dynamic repository path scanning."""

import http.server
import socketserver
import json
import os
from checker.explain import explain

PORT = 8080

class SecurityDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                with open("templates/index.html", "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"Error: templates/index.html not found.")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                finding = {
                    "path": data.get("path", "custom_input"),
                    "category": data.get("category", "web_analysis"),
                    "reason": data.get("reason", "Submitted via web dashboard"),
                    "severity": data.get("severity", "high"),
                    "signals": [{"kind": "user_snippet", "snippet": data.get("code", "")}]
                }
                analysis_result = explain(finding)
                response = json.dumps({"status": "success", "analysis": analysis_result}).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response)
            except Exception as e:
                err_res = json.dumps({"status": "error", "message": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(err_res)
                
        elif self.path == '/api/scan-repo':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                # Read the folder path provided dynamically from the browser frontend
                repo_path = data.get("repo_path", "")
                malicious_dir = os.path.join(repo_path, "osv", "malicious")
                
                results = []
                if os.path.exists(malicious_dir):
                    count = 0
                    for root, dirs, files in os.walk(malicious_dir):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
                            if file.endswith('.json') and count < 15:
                                file_path = os.path.join(root, file)
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    advisory = json.load(f)
                                results.append({
                                    "id": advisory.get('id', 'Unknown'),
                                    "summary": advisory.get('summary', 'No summary'),
                                    "path": file_path,
                                    "details": advisory.get('details', '')[:400]
                                })
                                count += 1
                
                response = json.dumps({"status": "success", "packages": results}).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(response)
            except Exception as e:
                err_res = json.dumps({"status": "error", "message": str(e)}).encode('utf-8')
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(err_res)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), SecurityDashboardHandler) as httpd:
        print(f"🚀 Dashboard running locally at: http://127.0.0.1:{PORT}")
        httpd.serve_forever()