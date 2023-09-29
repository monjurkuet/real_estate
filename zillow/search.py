import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time,getpass,platform,random
from dateutil import parser
from datetime import timedelta
import sqlite3
import re
import json
from tqdm import tqdm
import pandas as pd

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

def samelineprint(msg):
   LINE_FLUSH = '\r\033[K'
   UP_FRONT_LINE = '\033[F'
   print(UP_FRONT_LINE + LINE_FLUSH + str(msg))

# waitfor
def waitfor(driver,xpth):
    try: 
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpth)))
    except:
        pass 


def new_browser():
    SYSTEM_OS = platform.system()
    browser_executable_path = (
        BROWSER_EXECUTABLE_PATH_WINDOWS if SYSTEM_OS == 'Windows' else BROWSER_EXECUTABLE_PATH_LINUX
    )
    driver = uc.Chrome(browser_executable_path=browser_executable_path, headless=False)
    return driver

def solve_blocked(browser):
    try:
        element = WebDriverWait(browser,15).until(EC.presence_of_element_located((By.ID,'px-captcha')))
        # Wait for the px-captcha element styles to fully load
        time.sleep(0.5)
    except BaseException as e:
        samelineprint(f'px-captcha element not found')
        return
    samelineprint(f'solve blocked:{browser.current_url}')
    if  element:
        samelineprint(f'start press and hold')
        ActionChains(browser).click_and_hold(element).perform()
        start_time = time.time()
        while 1:
            if time.time() - start_time > random.uniform(8,10):
                ActionChains(browser).release(element).perform()
                return
            time.sleep(0.1)
    time.sleep(1)

def check_captcha(driver,url):
    captchapresence=len(driver.find_elements(By.ID,'px-captcha'))
    if not captchapresence:
        return
    solve_blocked(driver)
    time.sleep(5)
    driver.get(url)
    time.sleep(5)
    check_captcha(driver,url)

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
URL='https://www.zillow.com/'
driver.get(URL)
check_captcha(driver,URL)
queue=get_listings()

for each_property in queue[:1]:
    geoid=each_property['geoid']
    address=each_property['display_name']
    URL=SEARCH_URL+address
    driver.get(URL)
    check_captcha(driver,URL)
    zpid=re.search(r'"zpid":"(\d+)"', driver.page_source).group(1)
    address_=driver.title.split('|')[0].strip()
    zpid=re.search(r'"zpid":"(\d+)"', driver.page_source).group(1)
    zestimate=driver.find_element(By.XPATH,'//span[@data-testid="zestimate-text"]//span').text.strip().replace("$", "").replace(",", "")
    rentZestimate=driver.find_element(By.XPATH,'//button[text()="Rent Zestimate"]/following::*').text.strip().replace("$", "").replace(",", "")
    taxAssessedValue=driver.find_element(By.XPATH,'//table[@aria-label="Table of tax history"]').text

df_list = pd.read_html(driver.find_element(By.XPATH,'//table[@aria-label="Table of tax history"]'))

# Extract the table from the dataframe
table = df_list[0]

# Access the data in the table
data = table.to_dict('records')