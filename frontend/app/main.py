from flask import Flask, request, jsonify
from prometheus_client import start_http_server, Counter
import logging

# Flask app
app = Flask(__name__)

# Setup logging (so logs go to stdout, visible in kubectl logs)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Prometheus metrics
REQUESTS = Counter("hello_requests_total", "Total hello requests")
ERRORS = Counter("hello_errors_total", "Total error responses")
ENDPOINT_REQUESTS = Counter("endpoint_requests_total", "Requests per endpoint", ["method", "endpoint", "status"])

@app.before_request
def log_request_info():
    logging.info(f"Incoming {request.method} request on {request.path}")

@app.after_request
def log_response_info(response):
    # Increment counters
    REQUESTS.inc()
    ENDPOINT_REQUESTS.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
    logging.info(f"Response: {response.status_code} for {request.method} {request.path}")
    return response

@app.route("/", methods=["GET"])
def hello():
    return "Hello, Minikube World!"

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json or {}
    return jsonify({"received": data}), 201

@app.route("/update", methods=["PUT"])
def update():
    return "Updated successfully!", 200

@app.route("/delete", methods=["DELETE"])
def delete():
    return "Deleted successfully!", 200

@app.route("/error", methods=["GET"])
def trigger_error():
    ERRORS.inc()
    return "Something went wrong!", 500

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    # Run Flask app on port 5000
    app.run(host="0.0.0.0", port=5000)
