from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions

def setup_browser(self):
    """Initialize Selenium WebDriver with headless browser"""
    logger.info("🌐 Setting up browser...")
    
    try:
        # Use ChromeDriverManager to handle driver
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("✅ Chrome browser initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize browser: {e}")
        colab_status['error'] = f"Browser setup failed: {str(e)}"
        return False
