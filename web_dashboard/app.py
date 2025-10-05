from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
import sys
import os

# Add parent directory to path to import san_core
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from san_core.san_fabric import SANFabric
from san_core.security_engine import SecurityEngine

app = Flask(__name__)
san_fabric = SANFabric()
security_engine = SecurityEngine(san_fabric)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    threat_level, threat_message = security_engine.get_threat_level()
    
    dashboard_data = {
        'threat_level': threat_level,
        'threat_message': threat_message,
        'emergency_mode': san_fabric.emergency_mode,
        'total_devices': len(san_fabric.G.nodes()),
        'total_zones': len(san_fabric.config['zones']),
        'recent_attempts': len(san_fabric.access_log[-10:]),
        'granted_attempts': len([log for log in san_fabric.access_log if log['granted']])
    }
    
    return render_template('dashboard.html', **dashboard_data)

@app.route('/api/access_log')
def get_access_log():
    return jsonify(san_fabric.access_log[-20:])  # Last 20 entries

@app.route('/api/request_access', methods=['POST'])
def api_request_access():
    data = request.json
    initiator = data.get('initiator')
    target = data.get('target')
    access_type = data.get('access_type', 'read')
    
    granted, message = san_fabric.request_access(initiator, target, access_type)
    
    return jsonify({
        'granted': granted,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/emergency_mode', methods=['POST'])
def toggle_emergency_mode():
    data = request.json
    activate = data.get('activate', False)
    
    if activate:
        message = san_fabric.activate_emergency_mode()
    else:
        message = san_fabric.deactivate_emergency_mode()
    
    return jsonify({'message': message, 'emergency_mode': san_fabric.emergency_mode})

@app.route('/api/security_report')
@app.route('/api/security_report')
def get_security_report():
    # Generate fresh reports each time
    report = san_fabric.generate_security_report()
    analysis = security_engine.analyze_access_patterns()
    
    # Add current time to make each report unique
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = report.replace("Generated:", f"Report Generated: {current_time}")
    
    return jsonify({'report': report, 'analysis': analysis})

@app.route('/zones')
def zones_view():
    return render_template('zones.html', zones=san_fabric.config['zones'])

if __name__ == '__main__':
    print("🌐 Starting SAN Security Simulator Web Dashboard...")
    print("   Access at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True)