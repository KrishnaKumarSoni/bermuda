"""
Firebase Functions entry point for Bermuda API
"""

from firebase_functions import https_fn, options, params
import json
import os

# Firebase will be initialized by firebase_integration.py

# Load .env file for local development
try:
    from pathlib import Path
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value
except Exception:
    pass  # Silently continue if .env loading fails

# Import our existing Flask apps
import sys
sys.path.append(os.path.dirname(__file__))

from respondent import app as respondent_app
from creator import app as creator_app

# Configure function options
api_options = options.CorsOptions(
    cors_origins=["*"],
    cors_methods=["GET", "POST", "OPTIONS"]
)

@https_fn.on_request(
    cors=api_options,
    timeout_sec=540,  # Increased timeout for large payloads
    memory=options.MemoryOption.MB_512,
    secrets=["OPENAI_API_KEY"]
)
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Main Firebase Function that routes to appropriate Flask apps
    """
    try:
        path = req.path
        
        # Handle preflight CORS requests
        if req.method == "OPTIONS":
            headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Max-Age": "3600"
            }
            return https_fn.Response("", status=204, headers=headers)
        
        # Route to appropriate app
        if path.startswith('/api/infer') or path.startswith('/api/save-form'):
            target_app = creator_app
        elif path.startswith('/api/forms') and '/responses' in path:
            # Form responses endpoint goes to creator app
            target_app = creator_app
        else:
            # All other endpoints (chat, extract, debug, health, anonymous form access) go to respondent app
            target_app = respondent_app
            
        # Create Flask test client and make request
        with target_app.test_client() as client:
            # Convert Firebase request to Flask request format
            flask_response = client.open(
                path=path,
                method=req.method,
                data=req.get_data(),
                headers=dict(req.headers),
                content_type=req.headers.get('content-type', 'application/json')
            )
            
            # Convert Flask response to Firebase response
            response_headers = dict(flask_response.headers)
            response_headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type"
            })
            
            return https_fn.Response(
                flask_response.get_data(),
                status=flask_response.status_code,
                headers=response_headers
            )
            
    except Exception as e:
        import traceback
        error_response = {
            "error": "Internal server error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        return https_fn.Response(
            json.dumps(error_response),
            status=500,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )