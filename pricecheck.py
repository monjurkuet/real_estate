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
USER_DATA_DIR_WINDOWS = "D:\\airbnbscrapingprofile"
USER_DATA_DIR_LINUX = f"/home/{getpass.getuser()}/airbnbscrapingprofile"
BROWSER_EXECUTABLE_PATH_WINDOWS = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
BROWSER_EXECUTABLE_PATH_LINUX = '/usr/bin/brave-browser'

# Constants for API URLs
DETAILS_API = 'https://www.airbnb.com/api/v3/StaysPdpSections'

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
    return details_content

# Create a reusable browser function
def new_browser():
    SYSTEM_OS = platform.system()
    if SYSTEM_OS == 'Windows':
        user_data_dir = USER_DATA_DIR_WINDOWS
        browser_executable_path = BROWSER_EXECUTABLE_PATH_WINDOWS
    elif SYSTEM_OS == 'Linux':
        user_data_dir = USER_DATA_DIR_LINUX
        browser_executable_path = BROWSER_EXECUTABLE_PATH_LINUX
    driver = uc.Chrome(user_data_dir=user_data_dir, browser_executable_path=browser_executable_path, headless=False)
    return driver

def get_listings():       
    cursor.execute("SELECT * FROM `availability` WHERE available=1")
    rows=cursor.fetchall()   
    row_headers=[x[0] for x in cursor.description] 
    initial_data=[]
    for result in rows:
        initial_data.append(dict(zip(row_headers,result)))
    print('Total rows : ',len(rows))
    return initial_data

def update_datedata(listingId,calendarDate,priceDate,Price,booked_days):
    sql_insert_with_param = """REPLACE INTO datedata
                            (listingId,calendarDate,priceDate,Price,booked_days) 
                            VALUES (?,?,?,?,?);"""
    val = (listingId,calendarDate,priceDate,Price,booked_days)
    cursor.execute(sql_insert_with_param , val)
    conn.commit() 
    print(val)

def crawl_price_data(listing,minNights,driver):
    try:
        listingId=listing['listingId']
        calendarDate=listing['calendarDate']
        checkindate=parser.parse(calendarDate)
        checkoutdate=checkindate+ timedelta(days=minNights)
        listingurl=f'https://www.airbnb.com/rooms/{listingId}?check_in={checkindate.strftime("%Y-%m-%d")}&check_out={checkoutdate.strftime("%Y-%m-%d")}&display_currency=USD'
        driver.get(listingurl)
        waitfor(driver,'//div[@data-section-id="BOOK_IT_SIDEBAR"]')
        time.sleep(random.uniform(1,10))
        details_content=extract_realtime_data(driver)
        if 'Those dates are not available' not in json.dumps(details_content):
            try:
                price=re.search(r'"price": "(.*?)"', json.dumps(details_content)).group(1).strip().split('$')[1].replace(',','')
            except:
                price=re.search(r'"discountedPrice": "(.*?)"', json.dumps(details_content)).group(1).strip().split('$')[1].replace(',','')
            for i in range(minNights):
                priceDate=(checkindate+ timedelta(days=i)).strftime("%Y-%m-%d")
                update_datedata(listingId,calendarDate,priceDate,price,minNights)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    listings=get_listings()
    driver=new_browser()
    COUNTER=0
    for listing in tqdm(listings):
        COUNTER+=1
        if COUNTER%250==0:
            try:
                driver.close()
                driver.quit()
                driver=new_browser()
            except Exception as e:
                print(e) 
        minNights=listing['minNights']
        crawl_price_data(listing,minNights,driver)
        if minNights==1:
            for i in range(2,4):
                try:
                    crawl_price_data(listing,i,driver)
                except Exception as e:
                    print(e)
    print('Crawling complete....') 
    conn.close()
    driver.quit()