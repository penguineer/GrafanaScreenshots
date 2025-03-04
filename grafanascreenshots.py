import os
import signal
import sys
import time
from urllib.parse import urlparse, urlencode, urlunparse, ParseResult, parse_qs

import paho.mqtt.client as mqtt
import schedule
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def check_env_var(var_name):
    var_value = os.getenv(var_name)
    if var_value is None:
        print(f"Environment variable {var_name} is not set. Exiting...")
        sys.exit(1)
    return var_value


# Define signal handler function
def signal_handler(_sig, _frame):
    print('Exiting gracefully...')
    # stop the scheduler
    schedule.clear()


def capture_screenshot():
    # Setup webdriver
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.set_window_size(window_width, window_height)

    # Define the selectors
    selector_r0 = (By.ID, ':r0:')
    selector_r1 = (By.ID, ':r1:')
    selector_submit = (By.XPATH, '//button[@type="submit"]')

    # Navigate to Grafana dashboard
    driver.get(dashboard_url)

    # Wait for specific elements to load
    try:
        WebDriverWait(driver, timeout=5).until(ec.presence_of_element_located(selector_r0))
        WebDriverWait(driver, timeout=1).until(ec.presence_of_element_located(selector_r1))
        WebDriverWait(driver, timeout=1).until(ec.presence_of_element_located(selector_submit))

        # Try to log in if the login form is present
        print("Logging in...")
        driver.find_element(*selector_r0).send_keys(username)
        driver.find_element(*selector_r1).send_keys(password)
        driver.find_element(*selector_submit).click()

        # Wait for the dashboard to load
        time.sleep(5)
    except TimeoutException:
        print("Timeout loading login form, assuming that we are already logged in")

    # Capture screenshot
    screenshot_data = driver.get_screenshot_as_png()

    # Publish screenshot data to MQTT
    client.publish(mqtt_topic, screenshot_data)
    print("Screenshot published to MQTT")

    driver.quit()


def get_dashboard_url():
    url = check_env_var('GRAFANA_DASHBOARD_URL')

    # Parse the URL into components
    url_parts = urlparse(url)

    query = parse_qs(url_parts.query)

    # Construct the new URL
    new_url_parts = ParseResult(
        scheme=url_parts.scheme,
        netloc=url_parts.netloc,
        path=url_parts.path,
        params=url_parts.params,
        query=urlencode(query, doseq=True),
        fragment=url_parts.fragment,
    )
    new_url = urlunparse(new_url_parts)

    # Append the "autofitpanels" and "kiosk" query parameter
    new_url = str(new_url) + "&autofitpanels&kiosk"

    return new_url

def setup_chrome_profile_path():
    path = os.getenv('CHROME_PROFILE', '/app/chrome-profile')
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except OSError as e:
        raise OSError(f"Failed to create CHROME_PROFILE directory: {e}")

# Register signal handler for SIGINT and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

broker_url = check_env_var('MQTT_BROKER_URL')
mqtt_topic = check_env_var('MQTT_TOPIC')

dashboard_url = get_dashboard_url()
print(f"Dashboard URL: {dashboard_url}")

username = check_env_var('GRAFANA_USERNAME')
password = check_env_var('GRAFANA_PASSWORD')

window_width = int(os.getenv('WINDOW_WIDTH', '1280'))
window_height = int(os.getenv('WINDOW_HEIGHT', '1024'))

# Setup MQTT client
client = mqtt.Client()
client.connect(broker_url)

# Setup browser options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--kiosk")

# Set the user profile directory for Chrome
chrome_profile = setup_chrome_profile_path()
chrome_options.add_argument(f"--user-data-dir={chrome_profile}")

capture_screenshot()
# Capture a screenshot every 30 seconds
schedule.every(30).seconds.do(capture_screenshot)

# Schedule is cleared when signal is received
while schedule.get_jobs():
    schedule.run_pending()
    time.sleep(1)

client.disconnect()

print("All jobs have been completed. Exiting...")
