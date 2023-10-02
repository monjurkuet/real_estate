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
import pandas as pd
import io

# Constants for file paths
BROWSER_EXECUTABLE_PATH_WINDOWS = "C:\\Users\\muham\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
#BROWSER_EXECUTABLE_PATH_WINDOWS = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
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
    cursor.execute("SELECT * FROM 'airdna+address' WHERE class in ('building','place') and geoid not in (Select geoid from 'zillow')")
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
    if 'No matching results' in driver.page_source:
        continue
    zpid=re.search(r'"zpid":"(\d+)"', driver.page_source).group(1)
    zestimate=driver.find_element(By.XPATH,'//button[text()="Zestimate"]/following::*').text.replace('$','').replace(',','')
    rentZestimate=driver.find_element(By.XPATH,'//button[text()="Rent Zestimate"]/following::*').text.replace('$','').replace(',','')
    buffer = io.StringIO(driver.page_source)
    if 'Tax assessment' in taxAssessedValue:
        taxAssessedValue=pd.read_html(buffer)[0]['Tax assessment'][0].split(' ')[0].replace('$','').replace(',','')
        property_tax=pd.read_html(buffer)[0]['Property taxes'][0].split(' ')[0].replace('$','').replace(',','')
    livingArea=re.search(r'Total interior livable area:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source).group(1).replace(',','')
    lotAreaValue=re.search(r'Lot size:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source).group(1).replace(',','')
    bathrooms=driver.find_element(By.XPATH,'//span[text()="bd"]//parent::*').text.split(' ')[0]
    bedrooms=driver.find_element(By.XPATH,'//span[text()="ba"]//parent::*').text.split(' ')[0]
    latitude=re.search(r'"latitude":(-?\d+\.\d+)', driver.page_source).group(1)
    longitude=re.search(r'"longitude":(-?\d+\.\d+)', driver.page_source).group(1)
    year_built=driver.find_element(By.XPATH,'//span[text()="Year built:"]/following::*').text
    # Define the INSERT statement
    sqlite_insert_with_param = """REPLACE INTO zillow
                        (zpid, geoid, zestimate, rentZestimate, taxAssessedValue, livingArea, lotAreaValue, bathrooms, bedrooms, latitude, longitude, year_built, property_tax) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);""" 
    data_tuple = (zpid, geoid, zestimate, rentZestimate, taxAssessedValue, livingArea, lotAreaValue, bathrooms, bedrooms, latitude, longitude, year_built, property_tax)
    cursor.execute(sqlite_insert_with_param, data_tuple)
    # Commit the changes to the database
    conn.commit()
    print(data_tuple)
    time.sleep(random.uniform(3,9))