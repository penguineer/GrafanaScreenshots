import os
import paho.mqtt.client as mqtt
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import schedule
import signal
import sys
from urllib.parse import urlparse, urlencode, urlunparse, ParseResult, parse_qs
import time


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
    except TimeoutException:
        print("Timed out waiting for page to load")
        driver.quit()
        return

    # If your Grafana dashboard requires login
    driver.find_element(*selector_r0).send_keys(username)
    driver.find_element(*selector_r1).send_keys(password)
    driver.find_element(*selector_submit).click()

    # Wait for navigation and capture screenshot
    time.sleep(5)
    screenshot_data = driver.get_screenshot_as_png()

    # Publish screenshot data to MQTT
    client.publish(mqtt_topic, screenshot_data)

    driver.quit()


def get_dashboard_url():
    url = check_env_var('GRAFANA_DASHBOARD_URL')

    # Parse the URL into components
    url_parts = urlparse(url)

    # Append the "autofitpanels" query parameter
    query = parse_qs(url_parts.query)
    query.update({"kiosk": ["tv"]})

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

    new_url = str(new_url) + "&autofitpanels"

    return new_url


# Register signal handler for SIGINT and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

broker_url = check_env_var('MQTT_BROKER_URL')
mqtt_topic = check_env_var('MQTT_TOPIC')
dashboard_url = get_dashboard_url()
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


capture_screenshot()
# Capture a screenshot every 30 seconds
schedule.every(30).seconds.do(capture_screenshot)


while True:
    schedule.run_pending()
    time.sleep(1)
