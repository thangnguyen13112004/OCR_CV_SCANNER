import http.server
import socketserver
import json
import os
import urllib.parse

PORT = 5000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == '/api/schema':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                # Ensure json directory exists
                os.makedirs('json', exist_ok=True)
                
                # Save the JSON data
                with open('json/schema.json', 'w', encoding='utf-8') as f:
                    f.write(post_data.decode('utf-8'))
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

import subprocess
import atexit
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Đang khởi động vLLM Server (5CD-AI/Vintern-1B-v3_5)...")
    vllm_cmd = [
        "vllm", "serve", "5CD-AI/Vintern-1B-v3_5",
        "--trust-remote-code",
        "--gpu-memory-utilization", "0.7"
    ]
    
    # Chạy vllm dưới dạng background process
    try:
        vllm_process = subprocess.Popen(vllm_cmd, shell=(sys.platform == "win32"))
    except Exception as e:
        print(f"Không thể khởi động vLLM: {e}")
        sys.exit(1)
        
    def cleanup():
        print("\nĐang đóng vLLM Server...")
        vllm_process.terminate()
        try:
            vllm_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            vllm_process.kill()
            
    atexit.register(cleanup)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Web Server đang chạy tại http://localhost:{PORT}")
        print("Bấm Ctrl+C để dừng hệ thống")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
