from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/test', methods=['POST'])
def test_endpoint():
    return jsonify({'message': 'Test endpoint works!'}), 200

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(debug=True, host='0.0.0.0', port=5000)