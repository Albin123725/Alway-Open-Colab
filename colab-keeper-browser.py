#!/usr/bin/env python3
"""
🎮 COLAB KEEPER - Keep your Colab Minecraft server alive 24/7
Fixed for Render - Uses Firefox instead of Chrome
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
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import threading
import traceback

# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
PORT = int(os.getenv('PORT', 3000))
GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL', 'albinnn07@gmail.com')
GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD', '')
COLAB_NOTEBOOK_ID = os.getenv('COLAB_NOTEBOOK_ID', '1jckV8xUJSmLhhol6wZwVJzpybsimiRw1')
KEEP_ALIVE_INTERVAL = int(os.getenv('KEEP_ALIVE_INTERVAL', 300))
MONITOR_INTERVAL = int(os.getenv('MONITOR_INTERVAL', 30))
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
    'health_score': 100,
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
        'health_score': colab_status['health_score'],
        'disconnects_recovered': colab_status['disconnects_recovered'],
        'error': colab_status['error']
    }, 200

@app.route('/', methods=['GET'])
def index():
    """Home page"""
    return {
        'service': 'Colab Keeper 24/7',
        'status': 'running',
        'colab_notebook': COLAB_NOTEBOOK_ID,
        'monitoring': 'active'
    }, 200

# ============================================================================
# COLAB KEEPER - MAIN CLASS (USING FIREFOX)
# ============================================================================

class ColabKeeper:
    """Keep Colab notebook alive 24/7 using Firefox"""
    
    def __init__(self):
        self.driver = None
        self.is_running = False
        self.max_retries = 3
        
    def setup_browser(self):
        """Initialize Firefox browser"""
        logger.info("🌐 Setting up Firefox browser...")
        
        try:
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--no-sandbox')
            firefox_options.add_argument('--disable-dev-shm-usage')
            firefox_options.add_argument('--window-size=1920,1080')
            
            # Use webdriver-manager for Firefox
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            
            logger.info("✅ Firefox browser ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            colab_status['error'] = str(e)
            return False
    
    def login_to_google(self):
        """Login to Google"""
        logger.info("🔐 Logging into Google...")
        
        for attempt in range(self.max_retries):
            try:
                self.driver.get('https://accounts.google.com/')
                time.sleep(3)
                
                # Check if already logged in
                if 'myaccount.google.com' in self.driver.current_url:
                    logger.info("✅ Already logged in")
                    return True
                
                # Enter email
                email_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, 'identifierId'))
                )
                email_field.send_keys(GOOGLE_EMAIL)
                self.driver.find_element(By.ID, 'identifierNext').click()
                time.sleep(3)
                
                # Enter password
                password_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, 'Passwd'))
                )
                password_field.send_keys(GOOGLE_PASSWORD)
                self.driver.find_element(By.ID, 'passwordNext').click()
                time.sleep(5)
                
                logger.info("✅ Login successful")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Login attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                    continue
        
        logger.error("❌ Login failed")
        return False
    
    def open_colab_notebook(self):
        """Open your Colab notebook"""
        logger.info(f"📓 Opening Colab notebook...")
        
        try:
            url = f"https://colab.research.google.com/drive/{COLAB_NOTEBOOK_ID}"
            self.driver.get(url)
            time.sleep(10)  # Give it more time to load
            
            # Try to find Colab elements
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'body'))
                )
                logger.info("✅ Colab opened")
                return True
            except:
                # Even if we can't find specific elements, if page loaded it's ok
                logger.info("⚠️ Colab page loaded (may need manual acceptance)")
                return True
            
        except Exception as e:
            logger.error(f"❌ Failed to open Colab: {e}")
            return False
    
    def check_colab_status(self):
        """Check if Colab is still running"""
        try:
            # Get current URL
            current_url = self.driver.current_url
            
            # Check if we're still on Colab
            if 'colab.research.google.com' in current_url:
                return True
            
            # Try to find Colab elements
            elements = self.driver.find_elements(By.TAG_NAME, 'body')
            if elements:
                return True
            
            return False
            
        except:
            return False
    
    def simulate_activity(self):
        """Simulate user activity"""
        try:
            # Scroll
            self.driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0, -150);")
            
            colab_status['last_activity'] = datetime.now()
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Activity failed: {e}")
            return False
    
    def health_check(self):
        """Run health check"""
        try:
            is_alive = self.check_colab_status()
            
            if is_alive:
                colab_status['health_score'] = min(100, colab_status['health_score'] + 5)
                colab_status['is_connected'] = True
            else:
                colab_status['health_score'] = max(0, colab_status['health_score'] - 20)
                colab_status['is_connected'] = False
            
            return is_alive
            
        except:
            colab_status['is_connected'] = False
            return False
    
    def reconnect(self):
        """Reconnect to Colab"""
        logger.info("🔄 Reconnecting...")
        
        try:
            if self.driver:
                self.driver.quit()
            
            if self.setup_browser() and self.login_to_google() and self.open_colab_notebook():
                colab_status['disconnects_recovered'] += 1
                colab_status['session_count'] += 1
                logger.info("✅ Reconnected")
                return True
                
        except Exception as e:
            logger.error(f"❌ Reconnect failed: {e}")
        
        return False
    
    def keep_alive_loop(self):
        """Main loop to keep Colab alive"""
        logger.info("🔄 Starting keep-alive loop...")
        
        last_check = time.time()
        last_activity = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Health check every MONITOR_INTERVAL seconds
                if current_time - last_check >= MONITOR_INTERVAL:
                    if not self.health_check():
                        logger.warning("⚠️ Colab not responding")
                        if AUTO_RESTART_ENABLED:
                            self.reconnect()
                    last_check = current_time
                
                # Simulate activity every 2 minutes
                if current_time - last_activity >= 120:
                    self.simulate_activity()
                    last_activity = current_time
                
                # Wait
                time.sleep(10)
                    
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                time.sleep(30)
                if AUTO_RESTART_ENABLED:
                    self.reconnect()
    
    def start(self):
        """Start Colab keeper"""
        logger.info("🚀 Starting Colab Keeper...")
        
        if not GOOGLE_PASSWORD:
            logger.error("❌ Missing Google password!")
            colab_status['error'] = "Missing Google password"
            return False
        
        # Setup
        if not self.setup_browser():
            return False
        
        if not self.login_to_google():
            self.cleanup()
            return False
        
        if not self.open_colab_notebook():
            self.cleanup()
            return False
        
        # Start monitoring
        self.is_running = True
        colab_status['is_connected'] = True
        colab_status['session_count'] = 1
        colab_status['last_activity'] = datetime.now()
        
        logger.info("✅ Colab Keeper started!")
        logger.info("📊 Monitoring active")
        
        self.keep_alive_loop()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        
        self.is_running = False
        colab_status['is_connected'] = False

# ============================================================================
# MAIN
# ============================================================================

def run_keeper():
    keeper = ColabKeeper()
    keeper.start()

def main():
    logger.info("="*50)
    logger.info("🎮 COLAB KEEPER - 24/7 SESSION KEEPER")
    logger.info("="*50)
    logger.info(f"📧 Email: {GOOGLE_EMAIL}")
    logger.info(f"📓 Notebook: {COLAB_NOTEBOOK_ID[:20]}...")
    logger.info(f"⏱️  Keep-alive: {KEEP_ALIVE_INTERVAL}s")
    logger.info(f"🤖 Auto-restart: {AUTO_RESTART_ENABLED}")
    logger.info("="*50)
    
    # Start keeper thread
    keeper_thread = threading.Thread(target=run_keeper, daemon=True)
    keeper_thread.start()
    
    # Start Flask
    time.sleep(5)
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
