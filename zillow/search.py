import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
import time,getpass,platform,random
from dateutil import parser
from datetime import timedelta
import sqlite3
import re
import json
from tqdm import tqdm

# Constants for file paths
BROWSER_EXECUTABLE_PATH_WINDOWS = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
BROWSER_EXECUTABLE_PATH_LINUX = '/usr/bin/brave-browser'

# Constants for API URLs
DETAILS_API = 'https://www.zillow.com/search/GetSearchPageState.htm'
SEARCH_URL='https://www.zillow.com/homes/'
#Fix variables for python
null=None
true=True
false=False

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# waitfor
def waitfor(driver,xpth):
    try: 
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpth)))
    except:
        pass 

#extract data
def extract_realtime_data(driver):
    details_content = None
    for request in driver.requests:
        if request.response:
            if DETAILS_API in request.url and request.response.status_code == 200:
                details_content = eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))
    if details_content is not None:
        details_content = details_content['data']
    del driver.requests
    return details_content

def new_browser():
    SYSTEM_OS = platform.system()
    browser_executable_path = (
        BROWSER_EXECUTABLE_PATH_WINDOWS if SYSTEM_OS == 'Windows' else BROWSER_EXECUTABLE_PATH_LINUX
    )
    driver = uc.Chrome(browser_executable_path=browser_executable_path, headless=False)
    return driver

def get_listings():       
    cursor.execute("SELECT * FROM 'airdna+address' WHERE class in ('building','place')")
    rows=cursor.fetchall()   
    row_headers=[x[0] for x in cursor.description] 
    initial_data=[]
    for result in rows:
        initial_data.append(dict(zip(row_headers,result)))
    print('Total rows : ',len(rows))
    return initial_data

driver=new_browser()
queue=get_listings()

for each_property in queue:
    geoid=each_property['geoid']
    address=each_property['display_name']
    driver.get(SEARCH_URL+address)