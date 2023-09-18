import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
import time,getpass,platform,random
from dateutil import parser
from datetime import timedelta

INCOGNITO=0
PROXY=0

def waitfor(driver,xpth):
    try: 
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpth)))
    except:
        pass 

def newBrowser():
    SYSTEM_OS=platform.system()
    if SYSTEM_OS=='Windows':
        user_data_dir="D:\\airbnbscrapingprofile"
        browser_executable_path='C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    if SYSTEM_OS=='Linux':
        CURRENTUSER=getpass.getuser()
        user_data_dir=f"/home/{CURRENTUSER}/airbnbscrapingprofile"
        browser_executable_path='/usr/bin/brave-browser'
    options = uc.ChromeOptions()
    if INCOGNITO==1:
        options.add_argument("--incognito")
    if PROXY==1:
        driver=uc.Chrome(user_data_dir=user_data_dir,
                        browser_executable_path=browser_executable_path,options=options,
                        headless=False,seleniumwire_options={
            'proxy': {
                'http': "http://45.85.147.136:24003",
                'https': "http://45.85.147.136:24003"
                    }
                })
    else:
        driver=uc.Chrome(user_data_dir=user_data_dir,
                        browser_executable_path=browser_executable_path,options=options,
                        headless=False)
    return driver

def get_listings():
    cursor = connection.cursor()         
    cursor.execute("SELECT * FROM `availability` WHERE available=1")
    rows=cursor.fetchall()   
    row_headers=[x[0] for x in cursor.description] 
    initial_data=[]
    for result in rows:
        initial_data.append(dict(zip(row_headers,result)))
    print('Total rows : ',len(rows))
    return initial_data

def update_listing_price(listingId,calendarDate,price,pricewithfees):
    cursor = connection.cursor()    
    sql_select_query = """Update availability set price= %s,pricewithfees= %s where listingId = %s and calendarDate = %s """
    val=(price,pricewithfees,listingId,calendarDate)
    cursor.execute(sql_select_query,val)
    connection.commit()
    print(val)

def update_datedata(listingId,calendarDate,priceDate,Price):
    cursor = connection.cursor()    
    sql_insert_with_param = """REPLACE INTO datedata
                            (listingId,calendarDate,priceDate,Price) 
                            VALUES (%s,%s,%s,%s);"""
    val = (listingId,calendarDate,priceDate,Price)
    cursor.execute(sql_insert_with_param , val)
    connection.commit() 
    print(val)

if __name__ == "__main__":
    listings=get_listings()
    driver=newBrowser()
    COUNTER=0
    for listing in listings:
        COUNTER+=1
        if COUNTER%250==0:
            try:
                driver.close()
                driver.quit()
                driver=newBrowser()
            except Exception as e:
                print(e) 
        try:
            listingId=listing['listingId']
            calendarDate=listing['calendarDate']
            minNights=listing['minNights']
            checkindate=parser.parse(calendarDate)
            checkoutdate=checkindate+ timedelta(days=minNights)
            listingurl=f'https://www.airbnb.com/rooms/{listingId}?check_in={checkindate.strftime("%Y-%m-%d")}&check_out={checkoutdate.strftime("%Y-%m-%d")}'
            driver.get(listingurl)
            waitfor('//div[@data-section-id="BOOK_IT_SIDEBAR"]//span[@class="_tyxjp1"]')
            time.sleep(random.uniform(1,10))
            price=driver.find_element('xpath','//div[@data-section-id="BOOK_IT_SIDEBAR"]//span[@class="_tyxjp1"]').text.strip().split('$')[1].replace(',','')
            pricewithfees=0
            update_listing_price(listingId,calendarDate,price,pricewithfees)
            for i in range(minNights):
                priceDate=(checkindate+ timedelta(days=i)).strftime("%Y-%m-%d")
                update_datedata(listingId,calendarDate,priceDate,price)
        except Exception as e:
            print(e)
    connection.close()
    tunnel.close
