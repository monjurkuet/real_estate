import seleniumwire.undetected_chromedriver as uc
from seleniumwire.utils import decode
from selenium.webdriver.common.keys import Keys
import time
import getpass
import platform
import sqlite3
from config import AIRDNA_EMAIL,AIRDNA_PASSWORD

# Constants for API URLs
DETAILS_API = 'https://api.airdna.co/api/explorer/v1/market/'
LOGIN_URL='https://app.airdna.co/data/login'

# Constants for file paths
BROWSER_EXECUTABLE_PATH_WINDOWS = "C:\\Users\\muham\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
#BROWSER_EXECUTABLE_PATH_WINDOWS = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
BROWSER_EXECUTABLE_PATH_LINUX = '/usr/bin/brave-browser'

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create a reusable browser function
def new_browser():
    SYSTEM_OS = platform.system()
    browser_executable_path = (
        BROWSER_EXECUTABLE_PATH_WINDOWS if SYSTEM_OS == 'Windows' else BROWSER_EXECUTABLE_PATH_LINUX
    )
    driver = uc.Chrome(browser_executable_path=browser_executable_path, headless=False)
    return driver

# Create a reusable function for extracting real-time data
def extract_realtime_data(driver):
    details_content=None
    #Fix variables for python
    null=None
    true=True
    false=False
    for request in driver.requests:
        if request.response:
            if DETAILS_API in request.url and request.response.status_code == 200 and 'listings' in request.url :
                details_content = eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))['payload']['listings']
                break
    del driver.requests
    return details_content

def login(driver):
    driver.get(LOGIN_URL)
    time.sleep(10)
    driver.find_element('xpath','//input[@name="email"]').send_keys(AIRDNA_EMAIL)
    driver.find_element('xpath','//input[@name="password"]').send_keys(AIRDNA_PASSWORD)
    driver.find_element('xpath','//input[@name="password"]').send_keys(Keys.ENTER)
    time.sleep(10)
    
def insert_property(data):
    insert_statement = """
        REPLACE INTO airdna_search (
            property_id, airbnb_property_id, vrbo_property_id, listing_type, bedrooms, bathrooms,
            accommodates, rating, reviews, title, revenue_ltm, revenue_potential_ltm,
            occupancy_rate_ltm, average_daily_rate_ltm, days_available_ltm, market_id,
            market_name, latitude,longitude, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    # Execute the INSERT statement with data from the dictionary
    cursor.execute(insert_statement, (
    data["property_id"], data["airbnb_property_id"], data["vrbo_property_id"],
    data["listing_type"], data["bedrooms"], data["bathrooms"], data["accommodates"],
    data["rating"], data["reviews"], data["title"], data["revenue_ltm"],
    data["revenue_potential_ltm"], data["occupancy_rate_ltm"],
    data["average_daily_rate_ltm"], data["days_available_ltm"],
    data["market_id"], data["market_name"],
    data["location"]['lat'],data["location"]['lng'],  data["currency"]
    ))
    print(data["airbnb_property_id"])

driver=new_browser()
login(driver)

SEARCH_URL='https://app.airdna.co/data/us/79503?tab=active-str-listings'
driver.get(SEARCH_URL)
RETRYCOUNTER=0
while True and RETRYCOUNTER!=5:
    details_content=extract_realtime_data(driver)
    if details_content is None:
        RETRYCOUNTER+=1
    else:
        for data in details_content:
            try:
                insert_property(data)
            except:
                pass
        conn.commit() 
    print('Scrolling....')
    # Scroll down to bottom
    driver.execute_script("arguments[0].scrollIntoView();", driver.find_elements(By.XPATH, '//img[@alt="carousel_image_0"]')[-1])
    # Wait to load page
    time.sleep(10)
    RETRYCOUNTER-=1

    


conn.close()
driver.close()
driver.quit()