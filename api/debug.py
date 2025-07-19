from http.server import BaseHTTPRequestHandler
import json
import os
import traceback

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            dump = data.get('dump', '').strip()
            
            # Test environment variables
            openai_key = os.getenv('OPENAI_API_KEY')
            
            # Try basic HTTP request
            import urllib.request
            import urllib.parse
            
            test_payload = {
                'model': 'gpt-4o-mini',
                'messages': [{'role': 'user', 'content': 'Say hello'}],
                'max_tokens': 10
            }
            
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=json.dumps(test_payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {openai_key}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            debug_info = {
                'status': 'success',
                'dump_length': len(dump),
                'openai_key_present': bool(openai_key),
                'openai_key_prefix': openai_key[:10] if openai_key else None,
                'openai_response': result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            }
            
            self.wfile.write(json.dumps(debug_info).encode())
            
        except Exception as e:
            error_info = {
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'openai_key_present': bool(os.getenv('OPENAI_API_KEY'))
            }
            self.wfile.write(json.dumps(error_info).encode())