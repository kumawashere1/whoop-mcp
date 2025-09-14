from http.server import BaseHTTPRequestHandler
import json
import urllib.request
from datetime import datetime, timedelta

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'Whoop MCP Running')
        return
    
    def do_POST(self):
        # REMPLACE CETTE LIGNE PAR TON TOKEN
        WHOOP_TOKEN = "Bearer TON_TOKEN_ICI"
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/event-stream')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        if data.get('method') == 'tools/list':
            tools = {
                "tools": [
                    {"name": "get_recovery", "description": "Récupération Whoop", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "get_sleep", "description": "Sommeil Whoop", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "get_strain", "description": "Strain Whoop", "inputSchema": {"type": "object", "properties": {}}}
                ]
            }
            response = f"data: {json.dumps(tools)}\n\n"
            self.wfile.write(response.encode())
            
        elif data.get('method') == 'tools/call':
            tool = data.get('params', {}).get('name')
            
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            headers = {
                'Authorization': WHOOP_TOKEN,
                'Content-Type': 'application/json'
            }
            
            try:
                if tool == "get_recovery":
                    url = f"https://api.whoop.com/developer/v1/recovery?start={start}&end={end}"
                elif tool == "get_sleep":
                    url = f"https://api.whoop.com/developer/v1/activity/sleep?start={start}&end={end}"
                elif tool == "get_strain":
                    url = f"https://api.whoop.com/developer/v1/cycle?start={start}&end={end}"
                else:
                    url = None
                
                if url:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req) as response:
                        result = json.loads(response.read().decode())
                else:
                    result = {"error": "Unknown tool"}
                    
            except Exception as e:
                result = {"error": str(e)}
            
            response_data = {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
            response = f"data: {json.dumps(response_data)}\n\n"
            self.wfile.write(response.encode())
        
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return
