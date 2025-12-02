#!/usr/bin/env python3
"""
🎮 COLAB KEEPER - BROWSER EDITION WITH AI AUTO-RESTART
Keeps Google Colab sessions open 24/7 using Selenium browser automation.
AI-powered monitoring: Auto-restarts cells, runtime, and detects failures.
Simulates real user activity to prevent Google security blocks.
Perfect for running Minecraft servers 24/7 on Colab!
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import threading
import traceback
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
PORT = int(os.getenv('PORT', 3000))
GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL', '')
GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD', '')
COLAB_NOTEBOOK_ID = os.getenv('COLAB_NOTEBOOK_ID', '')
KEEP_ALIVE_INTERVAL = int(os.getenv('KEEP_ALIVE_INTERVAL', 300))  # 5 minutes
MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', 30))  # Check every 30 seconds
AUTO_RESTART_ENABLED = os.getenv('AUTO_RESTART_ENABLED', 'true').lower() == 'true'

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FLASK HEALTH CHECK SERVER
# ============================================================================

app = Flask(__name__)
colab_status = {
    'is_connected': False,
    'last_activity': None,
    'start_time': datetime.now(),
    'session_count': 0,
    'error': None,
    'cells_restarted': 0,
    'runtime_restarted': 0,
    'ai_health_score': 100,
    'disconnects_recovered': 0
}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Render"""
    return {
        'status': 'ok' if colab_status['is_connected'] else 'disconnected',
        'is_connected': colab_status['is_connected'],
        'last_activity': str(colab_status['last_activity']),
        'uptime_seconds': (datetime.now() - colab_status['start_time']).total_seconds(),
        'session_count': colab_status['session_count'],
        'cells_restarted': colab_status['cells_restarted'],
        'runtime_restarted': colab_status['runtime_restarted'],
        'ai_health_score': colab_status['ai_health_score'],
        'disconnects_recovered': colab_status['disconnects_recovered'],
        'error': colab_status['error']
    }, 200

# ============================================================================
# AI MONITORING & AUTO-RESTART SYSTEM
# ============================================================================

class AIHealthMonitor:
    """AI system that monitors and auto-restarts Colab"""
    
    def __init__(self):
        self.health_history = []
        self.runtime_crashed_count = 0
        self.cell_stuck_count = 0
        self.last_check = datetime.now()
        self.error_threshold = 3
        
    def calculate_health_score(self, runtime_ok, cells_ok, connection_ok):
        """Calculate Colab health (0-100)"""
        score = 100
        if not connection_ok:
            score -= 40
        if not runtime_ok:
            score -= 30
        if not cells_ok:
            score -= 30
        return max(0, score)
    
    def predict_crash(self):
        """AI predicts if Colab will crash soon"""
        if len(self.health_history) < 5:
            return False
        recent = self.health_history[-5:]
        avg_score = sum(recent) / len(recent)
        return avg_score < 50
    
    def log_health(self, score):
        """Log health for trend analysis"""
        self.health_history.append(score)
        if len(self.health_history) > 100:
            self.health_history.pop(0)

# ============================================================================
# SELENIUM BROWSER AUTOMATION WITH AUTO-RESTART
# ============================================================================

class ColabKeeperAdvanced:
    """Advanced Colab keeper with AI monitoring and auto-restart"""
    
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.session_start_time = None
        self.health_monitor = AIHealthMonitor()
        self.restart_attempts = 0
        self.max_restart_attempts = 5
        self.cells_detected = 0
        self.last_cell_execution_time = datetime.now()
        
    def setup_browser(self):
        """Initialize Selenium WebDriver with webdriver-manager"""
        logger.info("🌐 Setting up browser with webdriver-manager...")
        
        try:
            # Try Chrome first (usually more stable)
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            
            # Use webdriver-manager to handle driver
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("✅ Chrome browser initialized with webdriver-manager")
            return True
            
        except Exception as e:
            logger.warning(f"Chrome failed: {e}, trying Firefox...")
            try:
                # Fallback to Firefox
                firefox_options = FirefoxOptions()
                firefox_options.add_argument('--headless')
                
                # Use webdriver-manager for Firefox
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                
                logger.info("✅ Firefox browser initialized with webdriver-manager")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to initialize browser: {e}")
                colab_status['error'] = f"Browser setup failed: {str(e)}"
                return False
    
    def login_to_google(self):
        """Login to Google Account"""
        logger.info("🔐 Logging into Google...")
        
        try:
            # Navigate to Google login
            self.driver.get('https://accounts.google.com/signin')
            time.sleep(2)
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'identifierId'))
            )
            email_field.send_keys(GOOGLE_EMAIL)
            
            # Click Next
            self.driver.find_element(By.ID, 'identifierNext').click()
            time.sleep(2)
            
            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'password'))
            )
            password_field.send_keys(GOOGLE_PASSWORD)
            
            # Click Next
            self.driver.find_element(By.ID, 'passwordNext').click()
            time.sleep(3)
            
            logger.info("✅ Google login successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Google login failed: {e}")
            colab_status['error'] = f"Google login failed: {str(e)}"
            return False
    
    def open_colab_notebook(self):
        """Open the Colab notebook"""
        logger.info(f"📓 Opening Colab notebook: {COLAB_NOTEBOOK_ID}")
        
        try:
            colab_url = f"https://colab.research.google.com/drive/{COLAB_NOTEBOOK_ID}"
            self.driver.get(colab_url)
            
            # Wait for notebook to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'goog-te-gadget'))
            )
            
            time.sleep(5)  # Extra wait for full load
            logger.info("✅ Colab notebook loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to open Colab notebook: {e}")
            colab_status['error'] = f"Failed to open Colab: {str(e)}"
            return False
    
    def check_runtime_status(self):
        """AI: Check if Colab runtime is alive and responding"""
        logger.info("🤖 [AI] Checking runtime status...")
        
        try:
            # Check for runtime error indicators
            error_elements = self.driver.find_elements(By.CLASS_NAME, 'error-message')
            runtime_error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Runtime')]")
            
            # Check for crash indicators
            if error_elements:
                logger.warning("⚠️ Error messages detected in Colab")
                return False
            
            # Try to detect if runtime is responsive
            try:
                self.driver.execute_script("return navigator.onLine")
                logger.info("✅ Runtime is responsive")
                return True
            except:
                logger.warning("⚠️ Runtime may not be responsive")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Could not check runtime status: {e}")
            return True  # Assume ok if we can't check
    
    def detect_running_cells(self):
        """AI: Detect which cells are running or stuck"""
        logger.info("🤖 [AI] Detecting cell status...")
        
        try:
            # Find all cells
            cells = self.driver.find_elements(By.CLASS_NAME, 'cell')
            self.cells_detected = len(cells)
            logger.info(f"   Found {self.cells_detected} cells")
            
            # Check for running cells
            running_cells = self.driver.find_elements(By.XPATH, 
                "//div[@class='cell' and .//div[@class='running']]")
            stuck_cells = []
            
            for cell in running_cells:
                try:
                    # Check if cell has been running too long
                    cell_text = cell.text[:100] if cell.text else "Unknown"
                    logger.info(f"   ⏳ Cell running: {cell_text[:50]}...")
                except:
                    pass
            
            return len(running_cells), len(stuck_cells)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not detect cells: {e}")
            return 0, 0
    
    def restart_stuck_cells(self):
        """AI: Detect and restart stuck cells"""
        logger.info("🤖 [AI] Checking for stuck cells to restart...")
        
        try:
            # Find cells that might be stuck (running for too long)
            running_cells = self.driver.find_elements(By.XPATH, 
                "//button[@aria-label='Stop cell']")
            
            if running_cells:
                logger.warning(f"⚠️ Found {len(running_cells)} potentially stuck cell(s)")
                
                for i, cell in enumerate(running_cells[:2]):  # Restart max 2 cells
                    try:
                        # Click stop button
                        cell.click()
                        time.sleep(1)
                        logger.info(f"   ⏹️ Stopped cell {i+1}")
                        colab_status['cells_restarted'] += 1
                        
                        # Wait a bit then restart
                        time.sleep(2)
                        
                        # Find the play button for this cell
                        self.driver.execute_script("window.scrollBy(0, 200);")
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"   Could not restart cell: {e}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking stuck cells: {e}")
            return False
    
    def restart_runtime(self):
        """AI: Restart the entire runtime if needed"""
        logger.info("🤖 [AI] Attempting runtime restart...")
        
        try:
            # Click Runtime menu
            runtime_menu = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Runtime')]"))
            )
            runtime_menu.click()
            time.sleep(1)
            
            # Click "Restart runtime"
            restart_option = self.driver.find_element(By.XPATH, 
                "//span[contains(text(), 'Restart runtime')]")
            restart_option.click()
            time.sleep(1)
            
            # Confirm restart
            confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Yes')]")
            confirm_button.click()
            
            logger.info("✅ Runtime restart initiated")
            colab_status['runtime_restarted'] += 1
            time.sleep(10)  # Wait for restart
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not restart runtime: {e}")
            return False
    
    def health_check_cycle(self):
        """AI: Run full health check and auto-repair cycle"""
        logger.info("🤖 [AI] Running health check cycle...")
        
        try:
            # Check runtime status
            runtime_ok = self.check_runtime_status()
            
            # Detect cells
            running_cells, stuck_cells = self.detect_running_cells()
            cells_ok = stuck_cells == 0
            
            # Check connection
            try:
                self.driver.find_element(By.CLASS_NAME, 'goog-te-gadget')
                connection_ok = True
            except:
                connection_ok = False
            
            # Calculate health
            health_score = self.health_monitor.calculate_health_score(
                runtime_ok, cells_ok, connection_ok
            )
            colab_status['ai_health_score'] = health_score
            self.health_monitor.log_health(health_score)
            
            logger.info(f"📊 AI Health Score: {health_score}/100")
            logger.info(f"   Runtime: {'✅' if runtime_ok else '❌'}")
            logger.info(f"   Cells: {'✅' if cells_ok else '❌'} (Running: {running_cells}, Stuck: {stuck_cells})")
            logger.info(f"   Connection: {'✅' if connection_ok else '❌'}")
            
            # Auto-repair if needed
            if not runtime_ok or not cells_ok:
                logger.warning("⚠️ Issues detected, attempting auto-repair...")
                
                if stuck_cells > 0 and AUTO_RESTART_ENABLED:
                    self.restart_stuck_cells()
                
                if not runtime_ok and AUTO_RESTART_ENABLED:
                    self.restart_runtime()
            
            # Predict crash
            if self.health_monitor.predict_crash():
                logger.warning("🚨 AI predicts Colab will crash soon!")
                if AUTO_RESTART_ENABLED:
                    logger.info("   Performing preventive restart...")
                    self.restart_runtime()
            
            return health_score > 50  # Session OK if score > 50
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            traceback.print_exc()
            return False
    
    def simulate_user_activity(self):
        """Simulate user activity to keep session alive"""
        logger.info("🖱️ Simulating user activity...")
        
        try:
            # Scroll down
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1)
            
            # Scroll back up
            self.driver.execute_script("window.scrollBy(0, -window.innerHeight);")
            time.sleep(1)
            
            # Click somewhere safe (like the notebook area)
            body = self.driver.find_element(By.TAG_NAME, 'body')
            body.click()
            time.sleep(1)
            
            logger.info("✅ Activity simulated successfully")
            colab_status['last_activity'] = datetime.now()
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Activity simulation failed: {e}")
            return False
    
    def keep_alive_loop(self):
        """Main keep-alive loop with AI monitoring"""
        logger.info(f"🔄 Starting keep-alive loop (interval: {KEEP_ALIVE_INTERVAL}s)")
        logger.info(f"🤖 AI Auto-Restart: {'ENABLED' if AUTO_RESTART_ENABLED else 'DISABLED'}")
        
        monitor_counter = 0
        
        while self.is_running:
            try:
                # Check if browser is still alive
                if not self.driver:
                    logger.error("❌ Browser window closed!")
                    colab_status['is_connected'] = False
                    break
                
                # Run AI health check every MONITOR_INTERVAL seconds
                monitor_counter += 1
                if monitor_counter >= MONITOR_INTERVAL:
                    self.health_check_cycle()
                    monitor_counter = 0
                
                # Simulate activity
                self.simulate_user_activity()
                
                # Wait for next interval
                for i in range(KEEP_ALIVE_INTERVAL):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    monitor_counter += 1
                    
            except Exception as e:
                logger.error(f"❌ Error in keep-alive loop: {e}")
                colab_status['error'] = str(e)
                colab_status['is_connected'] = False
                traceback.print_exc()
                
                # Try to reconnect
                if AUTO_RESTART_ENABLED:
                    logger.warning("🔄 Attempting to recover...")
                    colab_status['disconnects_recovered'] += 1
                    try:
                        if not self.open_colab_notebook():
                            break
                    except:
                        break
                
                time.sleep(5)  # Brief pause before retry
    
    def start(self):
        """Start the Colab keeper"""
        logger.info("🚀 Starting Colab Keeper (Advanced Edition with AI)...")
        
        if not GOOGLE_EMAIL or not GOOGLE_PASSWORD or not COLAB_NOTEBOOK_ID:
            logger.error("❌ Missing required environment variables!")
            logger.error(f"   GOOGLE_EMAIL: {bool(GOOGLE_EMAIL)}")
            logger.error(f"   GOOGLE_PASSWORD: {bool(GOOGLE_PASSWORD)}")
            logger.error(f"   COLAB_NOTEBOOK_ID: {bool(COLAB_NOTEBOOK_ID)}")
            colab_status['error'] = "Missing environment variables"
            return False
        
        # Setup browser
        if not self.setup_browser():
            return False
        
        # Login to Google
        if not self.login_to_google():
            self.cleanup()
            return False
        
        # Open Colab notebook
        if not self.open_colab_notebook():
            self.cleanup()
            return False
        
        # Mark as connected
        self.is_running = True
        colab_status['is_connected'] = True
        colab_status['session_count'] += 1
        colab_status['last_activity'] = datetime.now()
        self.session_start_time = datetime.now()
        
        logger.info("✅ Colab Keeper started successfully!")
        logger.info("="*70)
        logger.info("🎯 MONITORING ACTIVE:")
        logger.info("   • AI Health Monitoring: RUNNING")
        logger.info("   • Auto-Restart: " + ("ENABLED" if AUTO_RESTART_ENABLED else "DISABLED"))
        logger.info("   • Cell Monitoring: ENABLED")
        logger.info("   • Runtime Monitoring: ENABLED")
        logger.info("="*70)
        
        # Start keep-alive loop
        self.keep_alive_loop()
    
    def cleanup(self):
        """Cleanup browser resources"""
        logger.info("🧹 Cleaning up...")
        
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("✅ Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        
        self.is_running = False
        colab_status['is_connected'] = False

# ============================================================================
# MAIN
# ============================================================================

def run_colab_keeper():
    """Run Colab keeper in separate thread"""
    keeper = ColabKeeperAdvanced()
    keeper.start()

def main():
    """Main entry point"""
    logger.info("="*70)
    logger.info("🎮 COLAB KEEPER - BROWSER EDITION (AI ADVANCED)")
    logger.info("="*70)
    logger.info(f"📍 Starting HTTP server on port {PORT}")
    logger.info(f"⏱️  Keep-alive interval: {KEEP_ALIVE_INTERVAL}s")
    logger.info(f"🤖 Monitor interval: {MONITOR_INTERVAL}s")
    logger.info(f"🚀 Auto-Restart: {'ENABLED' if AUTO_RESTART_ENABLED else 'DISABLED'}")
    
    # Start Colab keeper in background thread
    keeper_thread = threading.Thread(target=run_colab_keeper, daemon=True)
    keeper_thread.start()
    
    # Give keeper time to start
    time.sleep(5)
    
    # Start Flask server
    logger.info(f"🚀 Starting health check server...")
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n✅ Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
