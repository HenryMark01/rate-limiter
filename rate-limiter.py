import time
from collections import defaultdict
from flask import Flask, request, jsonify

app = Flask(__name__)

# Rate limit configuration
RATE_LIMIT = 2  # Maximum requests per second per user
WINDOW_SIZE = 1  # Time window in seconds

# In-memory storage for IP request counts
request_counts = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    current_time = time.time()
    # Remove timestamps older than the window size
    request_counts[ip] = [timestamp for timestamp in request_counts[ip] if current_time - timestamp < WINDOW_SIZE]
    
    # Check if the number of requests exceeds the limit
    return len(request_counts[ip]) >= RATE_LIMIT

def log_request(ip: str):
    request_counts[ip].append(time.time())

@app.route('/api/<path:endpoint>', methods=['GET'])
def rate_limit(endpoint):
    ip = request.remote_addr

    if is_rate_limited(ip):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    log_request(ip)
    return jsonify({"message": "Request successful"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)