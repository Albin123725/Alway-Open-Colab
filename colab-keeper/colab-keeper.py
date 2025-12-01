import os
import time
import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Global state
state = {
    "status": "initializing",
    "last_check": None,
    "cycle": 0,
    "error": None
}

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {msg}")

def setup_driver():
    """Setup Chrome driver for Render environment"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0")
    
    return webdriver.Chrome(options=chrome_options)

def keep_colab_alive():
    """Keep Colab session alive by accessing it periodically"""
    global state
    log("🟢 Starting Colab Keeper on Render")
    
    email = os.getenv('GOOGLE_EMAIL')
    password = os.getenv('GOOGLE_PASSWORD')
    notebook_id = os.getenv('COLAB_NOTEBOOK_ID')
    
    if not all([email, password, notebook_id]):
        log("❌ ERROR: Missing environment variables", "ERROR")
        log("Required: GOOGLE_EMAIL, GOOGLE_PASSWORD, COLAB_NOTEBOOK_ID", "ERROR")
        log("⚠️ Running in test mode", "WARN")
        test_mode()
        return
    
    driver = None
    try:
        driver = setup_driver()
        cycle = 0
        
        while True:
            try:
                cycle += 1
                state["cycle"] = cycle
                log(f"Cycle {cycle}: Keeping Colab session alive...")
                
                # Open Colab notebook
                url = f"https://colab.research.google.com/drive/{notebook_id}"
                log(f"Opening: {url}")
                driver.get(url)
                
                # Wait for page load
                time.sleep(5)
                
                # Check if login needed
                if "accounts.google.com" in driver.current_url:
                    log("Logging in to Google...", "INFO")
                    
                    # Enter email
                    email_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "identifierId"))
                    )
                    email_input.send_keys(email)
                    driver.find_element(By.ID, "identifierNext").click()
                    
                    # Enter password
                    time.sleep(2)
                    pwd_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "password"))
                    )
                    pwd_input.send_keys(password)
                    driver.find_element(By.ID, "passwordNext").click()
                    
                    time.sleep(5)
                
                # Check if we're in Colab
                if "colab" in driver.current_url:
                    log("✅ Colab session active", "INFO")
                    state["status"] = "active"
                    state["last_check"] = datetime.now().isoformat()
                    state["error"] = None
                else:
                    log("⚠️ Could not reach Colab", "WARN")
                    state["status"] = "warning"
                
                # Keep alive - wait 10 minutes before next check
                log(f"Cycle {cycle}: Session kept alive. Next check in 10 minutes...")
                time.sleep(600)
                
            except Exception as e:
                log(f"❌ Error in cycle {cycle}: {e}", "ERROR")
                state["status"] = "error"
                state["error"] = str(e)
                log("Retrying in 5 minutes...", "WARN")
                time.sleep(300)
    
    finally:
        if driver:
            driver.quit()

def test_mode():
    """Test mode when credentials not provided"""
    global state
    log("Running in TEST MODE")
    log("To enable actual Colab keeping, set environment variables:", "INFO")
    log("- GOOGLE_EMAIL", "INFO")
    log("- GOOGLE_PASSWORD", "INFO")
    log("- COLAB_NOTEBOOK_ID", "INFO")
    
    cycle = 0
    while True:
        cycle += 1
        state["cycle"] = cycle
        state["status"] = "test_mode"
        state["last_check"] = datetime.now().isoformat()
        log(f"Test cycle {cycle}: Simulating Colab keep-alive...")
        time.sleep(60)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health checks"""
    
    def do_GET(self):
        if self.path == '/health':
            response = {
                "status": state.get("status", "unknown"),
                "cycle": state.get("cycle", 0),
                "last_check": state.get("last_check"),
                "error": state.get("error"),
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            log(f"Health check request from {self.client_address[0]}")
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Colab Keeper Running\n")
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_health_server():
    """Start HTTP health check server"""
    port = int(os.getenv('PORT', 3000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    log(f"Health check server listening on port {port}")
    log(f"Health endpoint: http://0.0.0.0:{port}/health")
    server.serve_forever()

if __name__ == '__main__':
    try:
        # Start health check server in background thread
        server_thread = threading.Thread(target=start_health_server, daemon=True)
        server_thread.start()
        
        # Start Colab keeper in main thread
        keep_colab_alive()
    except KeyboardInterrupt:
        log("Shutting down...")
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
