import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
import time,getpass,platform,random
from dateutil import parser
from datetime import timedelta
import mysql.connector
import re
import json
from tqdm import tqdm

# Constants for API URLs
DETAILS_API = 'https://www.airbnb.com/api/v3/StaysPdpSections'
AIRBNB_BASE_URL='https://www.airbnb.com/rooms/'

#Fix variables for python
null=None
true=True
false=False

# Connect to the database 
conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='real_estate',
        port=3306
        )
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

def get_listings():       
    cursor.execute("SELECT airbnb_property_id FROM `airdna_search`")
    rows=cursor.fetchall()   
    rows=[x[0] for x in rows] 
    return rows

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
            cleaning_fee=driver.find_element(By.XPATH,'//*[text()="Cleaning fee"]/following::*/following::*').text.strip().split('$')[1].replace(',','')
            service_fee=driver.find_element(By.XPATH,'//*[text()="Airbnb service fee"]/following::*/following::*').text.strip().split('$')[1].replace(',','')
            for i in range(minNights):
                priceDate=(checkindate+ timedelta(days=i)).strftime("%Y-%m-%d")
                update_datedata(listingId,calendarDate,priceDate,price,minNights)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    listings_id_list=get_listings()
    driver=uc.Chrome()
    COUNTER=0
    for listing in tqdm(listings):
        COUNTER+=1
        if COUNTER%250==0:
            try:
                driver.close()
                driver.quit()
                driver=uc.Chrome()
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