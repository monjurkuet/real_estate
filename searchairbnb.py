import seleniumwire.undetected_chromedriver as uc
from seleniumwire.utils import decode
import time,getpass,platform
from datetime import datetime

def jsclick(xpth):
    try: 
        element=driver.find_element('xpath',xpth)
        driver.execute_script("arguments[0].click();", element)
    except:
        pass  

def newBrowser():
    SYSTEM_OS=platform.system()
    if SYSTEM_OS=='Windows':
        user_data_dir="G:\\airbnbscrapingprofile"
        browser_executable_path='C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    if SYSTEM_OS=='Linux':
        CURRENTUSER=getpass.getuser()
        user_data_dir=f"/home/{CURRENTUSER}/airbnbscrapingprofile"
        browser_executable_path='/usr/bin/brave-browser'
    driver=uc.Chrome(user_data_dir=user_data_dir,
                     browser_executable_path=browser_executable_path,version_main=113,
                     headless=False,seleniumwire_options={
        'proxy': {
            'http': "http://45.85.147.136:24003",
            'https': "http://45.85.147.136:24003"
                }
            })
    return driver

def extractReadltimeData(driver):
    # Access requests via the `requests` attribute
    for request in driver.requests:
        if request.response:
            if AVAILABILITY_API in request.url and request.response.status_code==200:
                #request_payload=eval(request.body)
                availability_content=eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))
            if DETAILS_API in request.url and request.response.status_code==200:
                #request_payload=eval(request.body)
                details_content=eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))
    availability_content=availability_content['data']
    details_content=details_content['data']
    return availability_content,details_content

# URLS
AVAILABILITY_API='https://www.airbnb.com/api/v3/PdpAvailabilityCalendar'
DETAILS_API='https://www.airbnb.com/api/v3/StaysPdpSections'
# global variables
null=None
true=True
false=False


url='https://www.airbnb.com/wishlists/v/1311753801?s=67&unique_share_id=4d3f13a2-43e0-4e3a-8d0d-8a180f0b491b'
driver=newBrowser()
driver.get(url)
time.sleep(10)
ITEMS_LIST=[i.get_attribute('href') for i in driver.find_elements('xpath','//div[@id="FMP-target"]//div[@data-testid="card-container"]/a')]
for each_listing in ITEMS_LIST:
    print(each_listing)
    driver.get(each_listing)
availability_content,details_content=extractReadltimeData(driver)
del driver.requests

metadata=details_content['presentation']['stayProductDetailPage']['sections']['metadata']['loggingContext']['eventDataLogging']

driver.close()
driver.quit()
