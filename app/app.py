#!/usr/bin/env python3
"""
Production-ready Flask web application with Prometheus metrics
"""

import os
import time
import logging
from datetime import datetime
from flask import Flask, jsonify, request, Response, render_template
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize start time - compatible with Gunicorn
if not hasattr(app, 'start_time'):
    app.start_time = time.time()

# Prometheus metrics
REQUEST_COUNT = Counter('flask_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('flask_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('flask_active_connections', 'Active connections')
APP_INFO = Gauge('flask_app_info', 'Application info', ['version', 'env'])

# Set application info
APP_INFO.labels(version='1.0.0', env=os.getenv('ENVIRONMENT', 'development')).set(1)

# Mock data counter for demonstration
page_views = Counter('page_views_total', 'Total page views', ['page'])

def track_metrics(func):
    """Decorator to track request metrics"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = func(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            REQUEST_COUNT.labels(
                method='GET', 
                endpoint=func.__name__, 
                status=status_code
            ).inc()
            return response
        except Exception as e:
            REQUEST_COUNT.labels(
                method='GET', 
                endpoint=func.__name__, 
                status=500
            ).inc()
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
        finally:
            REQUEST_DURATION.labels(
                method='GET', 
                endpoint=func.__name__
            ).observe(time.time() - start_time)
            ACTIVE_CONNECTIONS.dec()
    
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/')
def home():
    """Homepage endpoint"""
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    
    logger.info("Homepage accessed")
    
    return render_template('index.html')

@app.route('/health')
@track_metrics
def health_check():
    """Health check endpoint"""
    logger.info("Health check accessed")
    
    # Simulate basic health checks
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': time.time() - getattr(app, 'start_time', time.time()),
        'checks': {
            'database': 'ok',  # Mock database check
            'memory': 'ok',
            'disk': 'ok'
        }
    }
    
    return jsonify(health_status), 200

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    logger.info("Metrics endpoint accessed")
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/robots.txt')
def robots():
    return Response('User-agent: *\nAllow: /', mimetype='text/plain')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.svg')

@app.route('/api/data')
@track_metrics
def get_data():
    """Mock API endpoint that returns sample data"""
    page_views.labels(page='api').inc()
    
    try:
        # Read mock data
        with open('/app/data/data.json', 'r') as f:
            data = json.load(f)
        
        logger.info("API data accessed successfully")
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except FileNotFoundError:
        logger.warning("Data file not found, returning mock data")
        return jsonify({
            'success': True,
            'data': {'message': 'Mock data - file not found'},
            'timestamp': datetime.utcnow().isoformat()
        })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    REQUEST_COUNT.labels(method='GET', endpoint='not_found', status=404).inc()
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    REQUEST_COUNT.labels(method='GET', endpoint='internal_error', status=500).inc()
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Record app start time for uptime calculation
    app.start_time = time.time()
    
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found.',
            'available_endpoints': [
                '/',
                '/health',
                '/api/data',
                '/metrics'
            ]
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong on our end.',
            'status': 'error'
        }), 500

    app.run(host='0.0.0.0', port=5000, debug=False)
