#!/usr/bin/env python3
"""
🎮 COLAB KEEPER - BROWSER EDITION (AI ADVANCED)
Keep your Google Colab sessions open 24/7 using real browser automation.
AI-powered auto-restart keeps everything running perfectly!
Deploy to Render for 24/7 uptime.
"""

import os
import sys
import time
import logging
from datetime import datetime
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
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
    try:
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
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/', methods=['GET'])
def index():
    """Home page"""
    return {
        'service': 'Colab Keeper - Browser Edition',
        'status': 'running',
        'version': '1.0.0',
        'uptime_seconds': (datetime.now() - colab_status['start_time']).total_seconds()
    }, 200

# ============================================================================
# AI MONITORING SYSTEM
# ============================================================================

class AIHealthMonitor:
    """AI system that monitors and auto-restarts Colab"""
    
    def __init__(self):
        self.health_history = []
        self.runtime_crashed_count = 0
        self.cell_stuck_count = 0
        
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
# COLAB KEEPER - MAIN CLASS
# ============================================================================

class ColabKeeper:
    """Main Colab keeper with AI monitoring and auto-restart"""
    
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.health_monitor = AIHealthMonitor()
        self.max_retries = 3
        
    def setup_browser(self):
        """Initialize Selenium WebDriver with webdriver-manager"""
        logger.info("🌐 Setting up browser...")
        
        try:
            # Chrome options for headless browser
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to handle driver
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Hide automation detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            colab_status['error'] = f"Browser setup failed: {str(e)}"
            return False
    
    def login_to_google(self):
        """Login to Google Account"""
        logger.info("🔐 Logging into Google...")
        
        for attempt in range(self.max_retries):
            try:
                # Navigate to Google login
                self.driver.get('https://accounts.google.com/signin')
                time.sleep(3)
                
                # Enter email
                email_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'identifierId'))
                )
                email_field.clear()
                email_field.send_keys(GOOGLE_EMAIL)
                
                # Click Next
                self.driver.find_element(By.ID, 'identifierNext').click()
                time.sleep(3)
                
                # Enter password
                password_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, 'password'))
                )
                password_field.clear()
                password_field.send_keys(GOOGLE_PASSWORD)
                
                # Click Next
                self.driver.find_element(By.ID, 'passwordNext').click()
                time.sleep(5)
                
                # Check if login successful
                try:
                    self.driver.find_element(By.CSS_SELECTOR, 'img[alt="Google"]')
                    logger.info("✅ Google login successful")
                    return True
                except:
                    # Might be on 2FA or other page
                    logger.info("⚠️ Possibly on 2FA page or already logged in")
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️ Login attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                    continue
        
        logger.error("❌ Google login failed after all attempts")
        colab_status['error'] = "Google login failed"
        return False
    
    def open_colab_notebook(self):
        """Open the Colab notebook"""
        logger.info(f"📓 Opening Colab notebook: {COLAB_NOTEBOOK_ID}")
        
        try:
            colab_url = f"https://colab.research.google.com/drive/{COLAB_NOTEBOOK_ID}"
            self.driver.get(colab_url)
            
            # Wait for notebook to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'notebook-container'))
            )
            
            time.sleep(5)  # Extra wait for full load
            logger.info("✅ Colab notebook loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to open Colab notebook: {e}")
            colab_status['error'] = f"Failed to open Colab: {str(e)}"
            return False
    
    def check_runtime_status(self):
        """Check if Colab runtime is alive and responding"""
        try:
            # Check for common error indicators
            error_selectors = [
                'div.error-message',
                'div[aria-label*="error"]',
                'div[class*="error"]',
                '//*[contains(text(), "Runtime") and contains(text(), "error")]',
                '//*[contains(text(), "disconnected")]'
            ]
            
            for selector in error_selectors:
                try:
                    if '//' in selector:
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        logger.warning("⚠️ Error messages detected in Colab")
                        return False
                except:
                    pass
            
            # Try to execute JavaScript to check if page is responsive
            try:
                self.driver.execute_script("return document.readyState")
                return True
            except:
                logger.warning("⚠️ Runtime may not be responsive")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Could not check runtime status: {e}")
            return True  # Assume ok if we can't check
    
    def detect_running_cells(self):
        """Detect which cells are running or stuck"""
        try:
            # Find running cells
            running_cells = self.driver.find_elements(By.CSS_SELECTOR, 'div.cell.running')
            
            # Check for cells running too long (more than 5 minutes)
            stuck_cells = 0
            for cell in running_cells:
                try:
                    # Look for timestamp or duration indicator
                    time_elements = cell.find_elements(By.CSS_SELECTOR, 'span.timestamp, div.runtime')
                    if time_elements:
                        time_text = time_elements[0].text.lower()
                        if 'min' in time_text or 'hour' in time_text:
                            stuck_cells += 1
                except:
                    pass
            
            return len(running_cells), stuck_cells
            
        except Exception as e:
            logger.warning(f"⚠️ Could not detect cells: {e}")
            return 0, 0
    
    def restart_stuck_cells(self):
        """Detect and restart stuck cells"""
        try:
            # Find stop buttons for running cells
            stop_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Stop"], button[aria-label*="stop"]')
            
            if stop_buttons:
                logger.warning(f"⚠️ Found {len(stop_buttons)} potentially stuck cell(s)")
                
                for i, button in enumerate(stop_buttons[:2]):  # Restart max 2 cells
                    try:
                        # Scroll to button
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        
                        # Click stop button
                        button.click()
                        time.sleep(2)
                        logger.info(f"   ⏹️ Stopped cell {i+1}")
                        colab_status['cells_restarted'] += 1
                        
                        # Find and click play button
                        play_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Run"], button[aria-label*="run"]')
                        if play_buttons:
                            play_buttons[0].click()
                            time.sleep(2)
                            logger.info(f"   ▶️ Restarted cell {i+1}")
                        
                    except Exception as e:
                        logger.warning(f"   Could not restart cell: {e}")
                
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking stuck cells: {e}")
            return False
    
    def restart_runtime(self):
        """Restart the entire runtime if needed"""
        try:
            # Click Runtime menu
            runtime_menus = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Runtime')]")
            if runtime_menus:
                runtime_menus[0].click()
                time.sleep(2)
                
                # Click "Restart runtime"
                restart_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Restart runtime')]")
                if restart_options:
                    restart_options[0].click()
                    time.sleep(2)
                    
                    # Confirm restart
                    confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Restart')]")
                    if confirm_buttons:
                        confirm_buttons[0].click()
                        
                    logger.info("✅ Runtime restart initiated")
                    colab_status['runtime_restarted'] += 1
                    time.sleep(15)  # Wait for restart
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Could not restart runtime: {e}")
            return False
    
    def health_check_cycle(self):
        """Run full health check and auto-repair cycle"""
        try:
            # Check runtime status
            runtime_ok = self.check_runtime_status()
            
            # Detect cells
            running_cells, stuck_cells = self.detect_running_cells()
            cells_ok = stuck_cells == 0
            
            # Check connection
            try:
                current_url = self.driver.current_url
                connection_ok = 'colab.research.google.com' in current_url
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
            if AUTO_RESTART_ENABLED:
                if stuck_cells > 0:
                    logger.info("   🔧 Attempting to restart stuck cells...")
                    self.restart_stuck_cells()
                
                if not runtime_ok:
                    logger.info("   🔧 Attempting to restart runtime...")
                    self.restart_runtime()
            
            # Predict crash
            if self.health_monitor.predict_crash():
                logger.warning("🚨 AI predicts Colab will crash soon!")
                if AUTO_RESTART_ENABLED:
                    logger.info("   🛡️ Performing preventive measures...")
                    self.simulate_user_activity(extended=True)
            
            return health_score > 50  # Session OK if score > 50
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            traceback.print_exc()
            return False
    
    def simulate_user_activity(self, extended=False):
        """Simulate real user activity to keep session alive"""
        try:
            logger.info("🖱️ Simulating user activity...")
            
            # Scroll in different patterns
            scroll_patterns = [
                (0, 300),   # Scroll down
                (0, -150),  # Scroll up a bit
                (0, 200),   # Scroll down more
                (0, -100),  # Scroll up
            ]
            
            for dx, dy in scroll_patterns:
                self.driver.execute_script(f"window.scrollBy({dx}, {dy});")
                time.sleep(0.5)
            
            # Click on safe areas
            safe_click_selectors = [
                'body',
                'div.notebook-container',
                'div.cell:first-child'
            ]
            
            for selector in safe_click_selectors[:2]:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(0.5)
                except:
                    pass
            
            # Extended activity if needed
            if extended:
                # Switch tabs (simulate Alt+Tab)
                self.driver.execute_script("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'Alt'}));")
                time.sleep(0.2)
                self.driver.execute_script("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'Tab'}));")
                time.sleep(0.2)
                self.driver.execute_script("window.dispatchEvent(new KeyboardEvent('keyup', {key: 'Tab'}));")
                time.sleep(0.2)
                self.driver.execute_script("window.dispatchEvent(new KeyboardEvent('keyup', {key: 'Alt'}));")
            
            logger.info("✅ Activity simulated successfully")
            colab_status['last_activity'] = datetime.now()
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Activity simulation failed: {e}")
            return False
    
    def reconnect(self):
        """Reconnect to Colab after disconnection"""
        logger.info("🔄 Attempting to reconnect...")
        
        try:
            # Clean up old driver
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            
            # Setup new browser
            if not self.setup_browser():
                return False
            
            # Login again
            if not self.login_to_google():
                return False
            
            # Open Colab again
            if not self.open_colab_notebook():
                return False
            
            logger.info("✅ Reconnected successfully")
            colab_status['disconnects_recovered'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Reconnection failed: {e}")
            return False
    
    def keep_alive_loop(self):
        """Main keep-alive loop with AI monitoring"""
        logger.info(f"🔄 Starting keep-alive loop (interval: {KEEP_ALIVE_INTERVAL}s)")
        logger.info(f"🤖 AI Auto-Restart: {'ENABLED' if AUTO_RESTART_ENABLED else 'DISABLED'}")
        
        last_health_check = 0
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check if browser is still alive
                if not self.driver:
                    logger.error("❌ Browser window closed!")
                    colab_status['is_connected'] = False
                    if AUTO_RESTART_ENABLED:
                        if self.reconnect():
                            continue
                        else:
                            break
                    else:
                        break
                
                # Run AI health check every MONITOR_INTERVAL seconds
                if current_time - last_health_check >= MONITOR_INTERVAL:
                    self.health_check_cycle()
                    last_health_check = current_time
                
                # Simulate activity
                self.simulate_user_activity()
                
                # Wait for next interval
                sleep_interval = KEEP_ALIVE_INTERVAL
                while sleep_interval > 0 and self.is_running:
                    time.sleep(1)
                    sleep_interval -= 1
                    
            except Exception as e:
                logger.error(f"❌ Error in keep-alive loop: {e}")
                colab_status['error'] = str(e)
                colab_status['is_connected'] = False
                traceback.print_exc()
                
                # Try to reconnect
                if AUTO_RESTART_ENABLED:
                    time.sleep(5)
                    if self.reconnect():
                        continue
                    else:
                        break
                else:
                    break
    
    def start(self):
        """Start the Colab keeper"""
        logger.info("🚀 Starting Colab Keeper (AI Advanced Edition)...")
        
        # Validate environment variables
        if not GOOGLE_EMAIL or not GOOGLE_PASSWORD or not COLAB_NOTEBOOK_ID:
            logger.error("❌ Missing required environment variables!")
            logger.error(f"   GOOGLE_EMAIL: {'✓' if GOOGLE_EMAIL else '✗'}")
            logger.error(f"   GOOGLE_PASSWORD: {'✓' if GOOGLE_PASSWORD else '✗'}")
            logger.error(f"   COLAB_NOTEBOOK_ID: {'✓' if COLAB_NOTEBOOK_ID else '✗'}")
            colab_status['error'] = "Missing environment variables"
            return False
        
        logger.info(f"📧 Email: {GOOGLE_EMAIL[:3]}...@gmail.com")
        logger.info(f"📓 Notebook ID: {COLAB_NOTEBOOK_ID}")
        
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
        
        logger.info("✅ Colab Keeper started successfully!")
        logger.info("="*60)
        logger.info("🎯 MONITORING ACTIVE:")
        logger.info(f"   • AI Health Monitoring: ✅ RUNNING")
        logger.info(f"   • Auto-Restart: {'✅ ENABLED' if AUTO_RESTART_ENABLED else '❌ DISABLED'}")
        logger.info(f"   • Cell Monitoring: ✅ ENABLED")
        logger.info(f"   • Runtime Monitoring: ✅ ENABLED")
        logger.info("="*60)
        
        # Start keep-alive loop
        self.keep_alive_loop()
    
    def cleanup(self):
        """Cleanup browser resources"""
        logger.info("🧹 Cleaning up...")
        
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        finally:
            self.driver = None
        
        self.is_running = False
        colab_status['is_connected'] = False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_colab_keeper():
    """Run Colab keeper in separate thread"""
    keeper = ColabKeeper()
    keeper.start()

def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("🎮 COLAB KEEPER - BROWSER EDITION (AI ADVANCED)")
    logger.info("="*60)
    logger.info(f"📍 Starting on port {PORT}")
    logger.info(f"⏱️  Keep-alive: Every {KEEP_ALIVE_INTERVAL}s")
    logger.info(f"🤖 Monitoring: Every {MONITOR_INTERVAL}s")
    logger.info(f"🔄 Auto-Restart: {'✅ ON' if AUTO_RESTART_ENABLED else '❌ OFF'}")
    logger.info("="*60)
    
    # Start Colab keeper in background thread
    keeper_thread = threading.Thread(target=run_colab_keeper, daemon=True)
    keeper_thread.start()
    
    # Give keeper time to initialize
    time.sleep(10)
    
    # Start Flask server
    logger.info(f"🚀 Starting health check server at http://0.0.0.0:{PORT}")
    logger.info(f"📊 Health endpoint: http://0.0.0.0:{PORT}/health")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ Flask server failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
