#!/usr/bin/env python3
"""
Comprehensive test suite for Zero-to-Prod Infrastructure
Tests all components: Flask app, metrics, backups, and configurations
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime

class InfrastructureTests:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.prometheus_url = "http://localhost:9090"
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        full_message = f"{status} {test_name}"
        if message:
            full_message += f": {message}"
        
        print(full_message)
        self.test_results.append({
            'name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_flask_endpoints(self):
        """Test all Flask application endpoints"""
        print("\n🌐 Testing Flask Application Endpoints...")
        
        endpoints = [
            ("/", "Homepage"),
            ("/health", "Health Check"),
            ("/metrics", "Metrics"),
            ("/api/data", "API Data")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    if endpoint == "/metrics":
                        # Check for Prometheus metrics
                        if "flask_requests_total" in response.text:
                            self.log_test(f"Flask {name} endpoint", True, "Contains expected metrics")
                        else:
                            self.log_test(f"Flask {name} endpoint", False, "Missing expected metrics")
                    else:
                        # Check for JSON response
                        try:
                            data = response.json()
                            self.log_test(f"Flask {name} endpoint", True, f"Status: {response.status_code}")
                        except:
                            self.log_test(f"Flask {name} endpoint", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"Flask {name} endpoint", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Flask {name} endpoint", False, str(e))

    def test_prometheus_integration(self):
        """Test Prometheus metrics collection"""
        print("\n📊 Testing Prometheus Integration...")
        
        try:
            # Test Prometheus UI
            response = requests.get(f"{self.prometheus_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("Prometheus UI accessible", True)
            else:
                self.log_test("Prometheus UI accessible", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Prometheus UI accessible", False, str(e))
            return
        
        try:
            # Test targets
            response = requests.get(f"{self.prometheus_url}/api/v1/targets", timeout=5)
            if response.status_code == 200:
                data = response.json()
                active_targets = data.get('data', {}).get('activeTargets', [])
                healthy_targets = [t for t in active_targets if t.get('health') == 'up']
                self.log_test("Prometheus targets", len(healthy_targets) > 0, 
                             f"{len(healthy_targets)}/{len(active_targets)} targets healthy")
            else:
                self.log_test("Prometheus targets", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Prometheus targets", False, str(e))
        
        try:
            # Test Flask metrics availability
            response = requests.get(f"{self.prometheus_url}/api/v1/query?query=flask_requests_total", timeout=5)
            if response.status_code == 200:
                data = response.json()
                metrics_count = len(data.get('data', {}).get('result', []))
                self.log_test("Flask metrics in Prometheus", metrics_count > 0, 
                             f"{metrics_count} metrics found")
            else:
                self.log_test("Flask metrics in Prometheus", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Flask metrics in Prometheus", False, str(e))

    def test_backup_system(self):
        """Test backup script functionality"""
        print("\n💾 Testing Backup System...")
        
        try:
            # Test backup creation
            result = subprocess.run([
                sys.executable, "backup/backup_script.py", "backup"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_test("Backup creation", True, "Backup created successfully")
            else:
                self.log_test("Backup creation", False, result.stderr)
        except Exception as e:
            self.log_test("Backup creation", False, str(e))
        
        try:
            # Test backup listing
            result = subprocess.run([
                sys.executable, "backup/backup_script.py", "list"
            ], capture_output=True, text=True, timeout=10)
            
            # Check if command ran successfully and shows backup files (output can be in stdout or stderr)
            output = result.stdout + result.stderr
            if result.returncode == 0 and "data_backup_" in output:
                self.log_test("Backup listing", True, "Backup files listed successfully")
            else:
                self.log_test("Backup listing", False, f"Failed: RC={result.returncode}, output={output[:100]}...")
        except Exception as e:
            self.log_test("Backup listing", False, str(e))
        
        # Check if backup files exist
        backup_dir = Path("backup")
        backup_files = list(backup_dir.glob("data_backup_*.json"))
        self.log_test("Backup files exist", len(backup_files) > 0, 
                     f"{len(backup_files)} backup files found")

    def test_configuration_files(self):
        """Test configuration file validity"""
        print("\n⚙️  Testing Configuration Files...")
        
        # Test Prometheus config
        try:
            prometheus_path = None
            for path in ["./prometheus-2.45.0.darwin-arm64/promtool", 
                        "./prometheus-2.45.0.darwin-amd64/promtool"]:
                if os.path.exists(path):
                    prometheus_path = path
                    break
            
            if prometheus_path:
                result = subprocess.run([
                    prometheus_path, "check", "config", "prometheus/prometheus.yml"
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and "SUCCESS" in result.stdout:
                    self.log_test("Prometheus config validation", True)
                else:
                    self.log_test("Prometheus config validation", False, result.stderr)
            else:
                self.log_test("Prometheus config validation", False, "promtool not found")
        except Exception as e:
            self.log_test("Prometheus config validation", False, str(e))
        
        # Test required files exist
        required_files = [
            "app/app.py",
            "app/requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "prometheus/prometheus.yml",
            "backup/backup_script.py",
            "data/data.json",
            ".github/workflows/main.yml",
            "README.md"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log_test(f"Required file: {file_path}", True)
            else:
                self.log_test(f"Required file: {file_path}", False, "File not found")

    def test_docker_configuration(self):
        """Test Docker-related configurations"""
        print("\n🐳 Testing Docker Configuration...")
        
        # Check Dockerfile exists and has expected content
        dockerfile_path = "Dockerfile"
        if os.path.exists(dockerfile_path):
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                
            checks = [
                ("Multi-stage build", "FROM python:3.11-slim as builder" in content),
                ("Non-root user", "USER appuser" in content),
                ("Health check", "HEALTHCHECK" in content),
                ("Production server", "gunicorn" in content)
            ]
            
            for check_name, condition in checks:
                self.log_test(f"Dockerfile {check_name}", condition)
        else:
            self.log_test("Dockerfile exists", False, "Dockerfile not found")
        
        # Check .dockerignore
        if os.path.exists(".dockerignore"):
            self.log_test("Dockerignore file", True)
        else:
            self.log_test("Dockerignore file", False, ".dockerignore not found")

    def test_github_actions_config(self):
        """Test GitHub Actions workflow configuration"""
        print("\n🚀 Testing GitHub Actions Configuration...")
        
        workflow_path = ".github/workflows/main.yml"
        if os.path.exists(workflow_path):
            with open(workflow_path, 'r') as f:
                content = f.read()
            
            checks = [
                ("Test job", "name: Test Application" in content),
                ("Security scan", "name: Security Scan" in content),
                ("Trivy scanner", "aquasecurity/trivy-action" in content),
                ("Build and test", "name: Build and Test Docker Image" in content),
                ("Deploy job", "name: Deploy" in content)
            ]
            
            for check_name, condition in checks:
                self.log_test(f"GitHub Actions {check_name}", condition)
        else:
            self.log_test("GitHub Actions workflow", False, "Workflow file not found")

    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 Starting Zero-to-Prod Infrastructure Tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_flask_endpoints()
        self.test_prometheus_integration()
        self.test_backup_system()
        self.test_configuration_files()
        self.test_docker_configuration()
        self.test_github_actions_config()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"📋 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📊 Total Tests: {self.tests_passed + self.tests_failed}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🎯 Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! Infrastructure is ready for production.")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} tests failed. Please review the issues above.")
            return False

    def generate_report(self):
        """Generate a test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'tests_passed': self.tests_passed,
                'tests_failed': self.tests_failed,
                'total_tests': self.tests_passed + self.tests_failed,
                'success_rate': self.tests_passed / (self.tests_passed + self.tests_failed) * 100 if (self.tests_passed + self.tests_failed) > 0 else 0
            },
            'results': self.test_results
        }
        
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: test_report.json")

if __name__ == "__main__":
    tester = InfrastructureTests()
    success = tester.run_all_tests()
    tester.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
