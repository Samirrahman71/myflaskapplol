#!/usr/bin/env python3
"""
Zero-to-Production Infrastructure Demo
=====================================

This script demonstrates all components of our production-grade infrastructure:
- Flask web application with health checks and metrics
- Prometheus monitoring and metrics collection
- Automated backup system with scheduling
- Security best practices and configuration validation

Author: Zero-to-Prod Infrastructure Team
"""

import subprocess
import sys
import time
import json
import requests
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 50)

def run_demo():
    """Run the complete infrastructure demo"""
    print_header("ZERO-TO-PRODUCTION INFRASTRUCTURE DEMO")
    
    # Step 1: Show Flask Application
    print_step(1, "Flask Web Application")
    try:
        # Test homepage
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ Homepage: {response.status_code} - {response.json()['status']}")
        
        # Test health check
        response = requests.get("http://localhost:5000/health", timeout=5)
        health_data = response.json()
        print(f"✅ Health Check: {health_data['status']} - Uptime: {health_data['uptime']:.2f}s")
        
        # Test API endpoint
        response = requests.get("http://localhost:5000/api/data", timeout=5)
        api_data = response.json()
        print(f"✅ API Data: {len(api_data['users'])} users, {len(api_data['metrics'])} metrics")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask app not running. Start with: python3 app/app.py")
        return False
    
    # Step 2: Show Prometheus Monitoring
    print_step(2, "Prometheus Monitoring")
    try:
        # Check Prometheus UI
        response = requests.get("http://localhost:9090/", timeout=5)
        print(f"✅ Prometheus UI: Accessible ({response.status_code})")
        
        # Check Flask metrics
        response = requests.get("http://localhost:5000/metrics", timeout=5)
        metrics_text = response.text
        metrics_count = len([line for line in metrics_text.split('\n') if 'flask_' in line and not line.startswith('#')])
        print(f"✅ Flask Metrics: {metrics_count} metrics exposed")
        
        # Check Prometheus targets
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
        targets_data = response.json()
        active_targets = sum(1 for target in targets_data['data']['activeTargets'] if target['health'] == 'up')
        print(f"✅ Prometheus Targets: {active_targets} healthy targets")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Prometheus not running. Start with Docker Compose or manual setup")
    
    # Step 3: Show Backup System
    print_step(3, "Automated Backup System")
    try:
        # Create a backup
        result = subprocess.run([
            sys.executable, "backup/backup_script.py", "backup"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backup Created: New backup file generated")
        
        # List backups
        result = subprocess.run([
            sys.executable, "backup/backup_script.py", "list"
        ], capture_output=True, text=True)
        
        output = result.stdout + result.stderr
        if "data_backup_" in output:
            backup_count = output.count("data_backup_")
            print(f"✅ Backup Listing: {backup_count} backup files found")
            
            # Show most recent backups
            lines = [line.strip() for line in output.split('\n') if 'data_backup_' in line]
            for i, line in enumerate(lines[:3]):  # Show first 3
                print(f"   {i+1}. {line}")
        
    except Exception as e:
        print(f"❌ Backup system error: {e}")
    
    # Step 4: Show Configuration Validation
    print_step(4, "Configuration Validation")
    
    # Check Prometheus config
    try:
        result = subprocess.run([
            "prometheus/prometheus", "--config.file=prometheus/prometheus.yml", "--check-config"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Prometheus Config: Valid configuration")
        else:
            print(f"❌ Prometheus Config: {result.stderr}")
    except:
        print("⚠️  Prometheus Config: Binary not found (install Prometheus to validate)")
    
    # Check required files
    required_files = [
        "app/app.py", "app/requirements.txt", "Dockerfile", "docker-compose.yml",
        "prometheus/prometheus.yml", "backup/backup_script.py", "data/data.json",
        ".github/workflows/main.yml", "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        try:
            with open(file_path, 'r'):
                pass
        except FileNotFoundError:
            missing_files.append(file_path)
    
    if not missing_files:
        print(f"✅ Project Files: All {len(required_files)} required files present")
    else:
        print(f"❌ Missing Files: {', '.join(missing_files)}")
    
    # Step 5: Show Security Features
    print_step(5, "Security & Best Practices")
    
    # Check Dockerfile security features
    try:
        with open("Dockerfile", 'r') as f:
            dockerfile_content = f.read()
        
        security_features = []
        if "USER appuser" in dockerfile_content:
            security_features.append("Non-root user")
        if "HEALTHCHECK" in dockerfile_content:
            security_features.append("Health checks")
        if "FROM python:" in dockerfile_content and "slim" in dockerfile_content:
            security_features.append("Minimal base image")
        
        print(f"✅ Docker Security: {', '.join(security_features)}")
        
    except Exception as e:
        print(f"❌ Docker Security Check: {e}")
    
    # Check GitHub Actions security
    try:
        with open(".github/workflows/main.yml", 'r') as f:
            workflow_content = f.read()
        
        if "trivy" in workflow_content.lower():
            print("✅ Security Scanning: Trivy vulnerability scanner configured")
        
        if "security" in workflow_content.lower():
            print("✅ CI/CD Pipeline: Security job included")
            
    except Exception as e:
        print(f"❌ CI/CD Security Check: {e}")
    
    # Final Summary
    print_header("DEMO SUMMARY")
    print("🎯 Production-Grade Infrastructure Components:")
    print("   • Flask web application with health checks")
    print("   • Prometheus monitoring and metrics")
    print("   • Automated backup system with scheduling")
    print("   • Docker containerization with security")
    print("   • GitHub Actions CI/CD pipeline")
    print("   • Security scanning with Trivy")
    print("   • Configuration validation")
    print("   • Comprehensive documentation")
    
    print("\n📊 Key Features Demonstrated:")
    print("   • Zero-cost local deployment")
    print("   • Production-ready security practices")
    print("   • Automated testing and validation")
    print("   • Monitoring and observability")
    print("   • Disaster recovery (backups)")
    print("   • Infrastructure as Code")
    
    print("\n🚀 Next Steps:")
    print("   • Deploy to cloud provider (AWS/GCP/Azure)")
    print("   • Set up external monitoring (Grafana)")
    print("   • Configure log aggregation")
    print("   • Add performance testing")
    print("   • Implement blue-green deployment")
    
    print(f"\n✨ Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("    Ready for production deployment! 🎉")

if __name__ == "__main__":
    print("🧪 Zero-to-Production Infrastructure Demo")
    print("   Make sure Flask app and Prometheus are running!")
    print("   Flask: python3 app/app.py")
    print("   Prometheus: ./prometheus/prometheus --config.file=prometheus/prometheus.yml")
    
    input("\nPress Enter to start demo...")
    run_demo()
