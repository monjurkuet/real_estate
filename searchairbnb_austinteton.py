import seleniumwire.undetected_chromedriver as uc
from seleniumwire.utils import decode
import time
import getpass
import platform

def jsclick(xpth):
    try: 
        element=driver.find_element('xpath',xpth)
        driver.execute_script("arguments[0].click();", element)
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
    driver=uc.Chrome(user_data_dir=user_data_dir,
                     browser_executable_path=browser_executable_path,
                     headless=False)
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

def insert_details(listingId,listingLat,listingLng,bedType,roomType,personCapacity,descriptionLanguage,
                    isSuperhost,accuracyRating,checkinRating,cleanlinessRating,communicationRating,locationRating,
                    valueRating,guestSatisfactionOverall,visibleReviewCount,location,title):
    cursor = connection.cursor()  
    sql_insert_with_param = """REPLACE INTO listings
                            (listingId,listingLat,listingLng,bedType,roomType,personCapacity,descriptionLanguage,
                            isSuperhost,accuracyRating,checkinRating,cleanlinessRating,communicationRating,locationRating,
                            valueRating,guestSatisfactionOverall,visibleReviewCount,location,title) 
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    val = (listingId,listingLat,listingLng,bedType,roomType,personCapacity,descriptionLanguage,
            isSuperhost,accuracyRating,checkinRating,cleanlinessRating,communicationRating,locationRating,
            valueRating,guestSatisfactionOverall,visibleReviewCount,location,title)
    cursor.execute(sql_insert_with_param , val)
    connection.commit() 
    print(val)

def insert_availability(listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable):
    cursor = connection.cursor()  
    sql_insert_with_param = """REPLACE INTO availability
                            (listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable) 
                            VALUES (%s,%s,%s,%s,%s,%s,%s);"""
    val = (listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable)
    cursor.execute(sql_insert_with_param , val)
    connection.commit() 
    print(val)

# URLS
AVAILABILITY_API='https://www.airbnb.com/api/v3/PdpAvailabilityCalendar'
DETAILS_API='https://www.airbnb.com/api/v3/StaysPdpSections'
# global variables
null=None
true=True
false=False


#url='https://www.airbnb.com/wishlists/v/1311753801?s=67&unique_share_id=4d3f13a2-43e0-4e3a-8d0d-8a180f0b491b'
driver=newBrowser()
#driver.get(url)
time.sleep(10)
#ITEMS_LIST=[i.get_attribute('href') for i in driver.find_elements('xpath','//div[@id="FMP-target"]//div[@data-testid="card-container"]/a')]
ITEMS_LIST=["https://www.airbnb.com/rooms/plus/19017960?display_currency=USD",
            "https://www.airbnb.com/rooms/689828220112367064?display_currency=USD"]

for each_listing in ITEMS_LIST:
    print(each_listing)
    driver.get(each_listing)
    time.sleep(20)
    availability_content,details_content=extractReadltimeData(driver)
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
    location=driver.find_element('xpath','//span[@class="_9xiloll"]').text.strip()
    insert_details(listingId,listingLat,listingLng,bedType,roomType,personCapacity,descriptionLanguage,
    isSuperhost,accuracyRating,checkinRating,cleanlinessRating,communicationRating,locationRating,
    valueRating,guestSatisfactionOverall,visibleReviewCount,location,title)
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

driver.close()
driver.quit()