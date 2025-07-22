#!/usr/bin/env python3
"""
Local development server for testing Bermuda chat API
"""

import os
import sys
sys.path.append('api')

from flask import Flask
from respondent import app as respondent_app

# Configure for local testing
app = Flask(__name__)

# Mount the respondent app
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def catch_all(path):
    """Route all requests to respondent app"""
    with respondent_app.test_client() as client:
        # Forward the request to the respondent app
        if path.startswith('api/'):
            api_path = '/' + path
        else:
            api_path = '/api/' + path if path else '/api/'
            
        # Get request data
        request_method = request.method if 'request' in globals() else 'GET'
        request_data = None
        request_headers = {}
        
        try:
            from flask import request
            request_method = request.method
            request_data = request.get_data()
            request_headers = dict(request.headers)
        except:
            pass
        
        response = client.open(
            path=api_path,
            method=request_method,
            data=request_data,
            headers=request_headers,
            content_type=request_headers.get('content-type', 'application/json')
        )
        
        return response.get_data(), response.status_code, dict(response.headers)

if __name__ == '__main__':
    # Set environment for local testing
    os.environ['FLASK_ENV'] = 'development'
    
    print("🚀 Starting local Bermuda API server...")
    print("📍 Server will be available at: http://127.0.0.1:5000")
    print("📍 Health check: http://127.0.0.1:5000/api/health")
    print("📍 Test form: http://127.0.0.1:5000/api/forms/test-form-coffee")
    print("💡 Use Ctrl+C to stop the server")
    
    # Import respondent app directly to run it locally
    from respondent import app
    app.run(host='127.0.0.1', port=5000, debug=True)