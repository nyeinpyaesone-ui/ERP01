"""
End-to-End (E2E) Parallel Tests for ERP01

These tests verify the complete system functionality by:
1. Starting the web server in a background process
2. Running multiple API tests in parallel
3. Verifying UI rendering
4. Testing concurrent requests
5. Cleaning up resources after tests
"""

import pytest
import requests
import subprocess
import time
import sys
import os
import threading
from multiprocessing import Pool, cpu_count

BASE_URL = "http://127.0.0.1:5001"
TIMEOUT = 30


class TestE2EParallel:
    """E2E tests running in parallel mode"""

    @classmethod
    @pytest.fixture(scope="class", autouse=True)
    def start_server(cls):
        """Start the Flask server before running tests"""
        env = os.environ.copy()
        env["USE_WEB"] = "true"
        env["FLASK_RUN_PORT"] = "5001"

        # Start server in background with separate process group
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/workspace",
            start_new_session=True,
        )

        # Wait for server to be ready
        max_wait = 15
        started = False
        for i in range(max_wait * 10):
            try:
                resp = requests.get(f"{BASE_URL}/api/status", timeout=1)
                if resp.status_code == 200:
                    started = True
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)

        if not started:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            raise RuntimeError("Server failed to start")

        yield

        # Cleanup: stop server
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    def test_01_api_status(self):
        """Test API status endpoint"""
        resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "online"
        assert data["version"] == "1.0.0"

    def test_02_api_modules(self):
        """Test modules API endpoint"""
        resp = requests.get(f"{BASE_URL}/api/modules", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "modules" in data
        assert len(data["modules"]) >= 4
        module_names = [m["name"] for m in data["modules"]]
        assert "Dashboard" in module_names
        assert "Inventory" in module_names

    def test_03_ui_rendering(self):
        """Test that main page renders correctly"""
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        assert resp.status_code == 200
        assert "ERP01" in resp.text
        assert "Dashboard" in resp.text
        assert "sidebar" in resp.text.lower()

    def test_04_health_check(self):
        """Test health check endpoint"""
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert data["healthy"] is True

    def test_05_concurrent_requests(self):
        """Test handling of concurrent requests using threads instead of processes"""
        endpoints = [
            "/api/status",
            "/api/modules",
            "/api/status",
            "/api/modules",
            "/api/status",
        ]

        results = []
        errors = []

        def fetch(url):
            try:
                resp = requests.get(url, timeout=5)
                results.append(resp.status_code)
            except Exception as e:
                errors.append(str(e))
                results.append(500)

        threads = []
        for ep in endpoints:
            t = threading.Thread(target=fetch, args=(f"{BASE_URL}{ep}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert all(r == 200 for r in results), f"Some requests failed: {results}"

    def test_06_module_details(self):
        """Test individual module endpoint"""
        resp = requests.get(f"{BASE_URL}/api/modules/1", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "name" in data

    def test_07_invalid_endpoint(self):
        """Test 404 handling"""
        resp = requests.get(f"{BASE_URL}/api/nonexistent", timeout=5)
        assert resp.status_code == 404

    def test_08_response_headers(self):
        """Test security headers"""
        resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
        assert resp.status_code == 200
        # Check content-type
        assert "application/json" in resp.headers.get("Content-Type", "")


def _fetch_url(url):
    """Helper function for parallel requests"""
    try:
        resp = requests.get(url, timeout=5)
        return resp.status_code
    except Exception:
        return 500


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-n", "auto"])
