import seleniumwire.undetected_chromedriver as uc
from seleniumwire.utils import decode
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
    if SYSTEM_OS == 'Windows':
        browser_executable_path = BROWSER_EXECUTABLE_PATH_WINDOWS
    elif SYSTEM_OS == 'Linux':
        browser_executable_path = BROWSER_EXECUTABLE_PATH_LINUX
    driver = uc.Chrome(browser_executable_path=browser_executable_path, headless=False)
    return driver
# Create a reusable function for extracting real-time data
def extract_realtime_data(driver):
    availability_content = None
    details_content = None
    for request in driver.requests:
        if request.response:
            if DETAILS_API in request.url and request.response.status_code == 200:
                details_content = eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))
    if availability_content is not None and details_content is not None:
        availability_content = availability_content['data']
        details_content = details_content['data']
    return availability_content, details_content

def insert_details(listingId,listingLat,listingLng,bedType,roomType,personCapacity,descriptionLanguage,
                    isSuperhost,accuracyRating,checkinRating,cleanlinessRating,communicationRating,locationRating,
                    valueRating,guestSatisfactionOverall,visibleReviewCount,title):
    # Insert the data into the "listings" table
    cursor.execute('''REPLACE INTO listings (
        listingId, listingLat, listingLng, bedType, roomType, personCapacity, descriptionLanguage,
        isSuperhost, accuracyRating, checkinRating, cleanlinessRating, communicationRating, locationRating,
        valueRating, guestSatisfactionOverall, visibleReviewCount, title
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (
        listingId, listingLat, listingLng, bedType, roomType, personCapacity, descriptionLanguage,
        isSuperhost, accuracyRating, checkinRating, cleanlinessRating, communicationRating, locationRating,
        valueRating, guestSatisfactionOverall, visibleReviewCount, title
    ))
    conn.commit() 
    print(f"Crawled PropertyId : {listingId}")

def insert_availability(listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable):
    sql_insert_with_param = """REPLACE INTO availability
                            (listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable) 
                            VALUES (?, ?, ?, ?, ?, ?, ?);"""
    val = (listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable)
    cursor.execute(sql_insert_with_param , val)
    conn.commit() 
    print(val)

#ITEMS_LIST=[i.get_attribute('href') for i in driver.find_elements('xpath','//div[@id="FMP-target"]//div[@data-testid="card-container"]/a')]
ITEMS_LIST=["https://www.airbnb.com/rooms/plus/19017960?display_currency=USD",
            "https://www.airbnb.com/rooms/689828220112367064?display_currency=USD"]

driver=new_browser()
login(driver)

def login(driver):
    driver.get(LOGIN_URL)
    time.sleep(10)
    driver.find_element('xpath','//input[@name="email"]').send_keys(AIRDNA_EMAIL)
    driver.find_element('xpath','//input[@name="password"]').send_keys(AIRDNA_PASSWORD)
    driver.find_element('xpath','//input[@name="password"]').send_keys(Keys.ENTER)
    time.sleep(10)

SEARCH_URL='https://app.airdna.co/data/us/79503?tab=active-str-listings'
driver.get(SEARCH_URL)

for each_listing in ITEMS_LIST:
    print(each_listing)
    driver.get(each_listing)
    time.sleep(20)
    availability_content,details_content=extract_realtime_data(driver)
    if availability_content and details_content:
        # property data
        title=driver.find_element('xpath','//h1').text.strip()
        metadata=details_content['presentation']['stayProductDetailPage']['sections']['metadata']['loggingContext']['eventDataLogging']
        listingId=metadata['listingId']
        listingLat=metadata['listingLat']
        listingLng=metadata['listingLng']
        bedType=metadata['bedType']
        roomType=metadata['roomType']
        personCapacity=metadata['personCapacity']
        descriptionLanguage=metadata['descriptionLanguage']
        isSuperhost=metadata['isSuperhost']
        accuracyRating=metadata['accuracyRating']
        checkinRating=metadata['checkinRating']
        cleanlinessRating=metadata['cleanlinessRating']
        communicationRating=metadata['communicationRating']
        locationRating=metadata['locationRating']
        valueRating=metadata['valueRating']
        guestSatisfactionOverall=metadata['guestSatisfactionOverall']
        visibleReviewCount=metadata['visibleReviewCount']
        insert_details(listingId,listingLat,listingLng,bedType,roomType,personCapacity,descriptionLanguage,
        isSuperhost,accuracyRating,checkinRating,cleanlinessRating,communicationRating,locationRating,
        valueRating,guestSatisfactionOverall,visibleReviewCount,title)
        # availability data
        calendarMonths=availability_content['merlin']['pdpAvailabilityCalendar']['calendarMonths']
        for eachmonth in calendarMonths:
            for day in eachmonth['days']:
                calendarDate=day['calendarDate']
                available=day['available']
                maxNights=day['maxNights']
                minNights=day['minNights']
                availableForCheckin=day['availableForCheckin']
                bookable=day['bookable']
                insert_availability(listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable)
    del driver.requests

conn.close()
driver.close()
driver.quit()