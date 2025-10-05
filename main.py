#!/usr/bin/env python3
"""
SAN Security Simulator - Main Application
Run with: python main.py
"""

import sys
import os
from san_core.san_fabric import SANFabric
from san_core.security_engine import SecurityEngine

def main():
    print("🚀 SAN Security Simulator Starting...")
    print("=" * 50)
    
    # Initialize SAN fabric
    san = SANFabric()
    security = SecurityEngine(san)
    
    print("✅ SAN Fabric initialized with:")
    print(f"   - {len(san.G.nodes())} devices")
    print(f"   - {len(san.config['zones'])} security zones")
    print(f"   - {len(san.config['storage_units'])} storage units")
    
    # Demo sequence
    print("\n🧪 Running Demo Sequence...")
    print("-" * 30)
    
    # Test 1: Normal access within same zone
    print("\n1. Testing normal zone access:")
    result, message = san.request_access("CEO_Workstation", "Financial_DB")
    print(f"   CEO_Workstation → Financial_DB: {message}")
    
    # Test 2: Cross-zone access (should fail)
    print("\n2. Testing cross-zone access (should fail):")
    result, message = san.request_access("Web_Server_01", "Financial_DB")
    print(f"   Web_Server_01 → Financial_DB: {message}")
    
    # Test 3: Time-based access
    print("\n3. Testing time-based access:")
    result, message = san.request_access("Backup_Server", "Financial_DB")
    print(f"   Backup_Server → Financial_DB: {message}")
    print("   Note: Backup server access depends on current time")
    
    # Test 4: Emergency mode
    print("\n4. Activating emergency mode:")
    print(f"   {san.activate_emergency_mode()}")
    
    # Test 5: Emergency access
    print("\n5. Testing emergency access:")
    result, message = san.request_access("Admin_Workstation", "Financial_DB")
    print(f"   Admin_Workstation → Financial_DB: {message}")
    
    # Test 6: Deactivate emergency
    print("\n6. Deactivating emergency mode:")
    print(f"   {san.deactivate_emergency_mode()}")
    
    # Generate reports
    print("\n7. Security Analysis:")
    print("-" * 20)
    print(security.analyze_access_patterns())
    
    print("\n8. Security Report:")
    print("-" * 15)
    print(san.generate_security_report())
    
    # Visualize SAN topology
    print("\n9. Generating SAN topology visualization...")
    try:
        san.visualize_fabric()
    except Exception as e:
        print(f"   Visualization skipped: {e}")
    
    # Start web dashboard
    print("\n🌐 Starting Web Dashboard...")
    print("   Access the dashboard at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run Flask app
    from web_dashboard.app import app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()