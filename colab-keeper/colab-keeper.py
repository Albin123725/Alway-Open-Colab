import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
                else:
                    log("⚠️ Could not reach Colab", "WARN")
                
                # Keep alive - wait 10 minutes before next check
                log(f"Cycle {cycle}: Session kept alive. Next check in 10 minutes...")
                time.sleep(600)
                
            except Exception as e:
                log(f"❌ Error in cycle {cycle}: {e}", "ERROR")
                log("Retrying in 5 minutes...", "WARN")
                time.sleep(300)
    
    finally:
        if driver:
            driver.quit()

def test_mode():
    """Test mode when credentials not provided"""
    log("Running in TEST MODE")
    log("To enable actual Colab keeping, set environment variables:", "INFO")
    log("- GOOGLE_EMAIL", "INFO")
    log("- GOOGLE_PASSWORD", "INFO")
    log("- COLAB_NOTEBOOK_ID", "INFO")
    
    for i in range(100):
        log(f"Test cycle {i+1}: Simulating Colab keep-alive...")
        time.sleep(60)

if __name__ == '__main__':
    try:
        keep_colab_alive()
    except KeyboardInterrupt:
        log("Shutting down...")
    except Exception as e:
        log(f"Fatal error: {e}", "ERROR")
