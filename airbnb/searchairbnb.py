import seleniumwire.undetected_chromedriver as uc
from seleniumwire.utils import decode
import time
import mysql.connector

# Constants for API URLs
AVAILABILITY_API = 'https://www.airbnb.com/api/v3/PdpAvailabilityCalendar'
DETAILS_API = 'https://www.airbnb.com/api/v3/StaysPdpSections'
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

# Create a reusable function for extracting real-time data
def extract_realtime_data(driver):
    availability_content = None
    details_content = None
    for request in driver.requests:
        if request.response:
            if AVAILABILITY_API in request.url and request.response.status_code == 200:
                availability_content = eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))
            if DETAILS_API in request.url and request.response.status_code == 200:
                details_content = eval(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8'))
    if availability_content is not None and details_content is not None:
        availability_content = availability_content['data']
        details_content = details_content['data']
    return availability_content, details_content

def insert_details(listingId, listingLat, listingLng, bedType, roomType, personCapacity, descriptionLanguage,
                    isSuperhost, accuracyRating, checkinRating, cleanlinessRating, communicationRating, locationRating,
                    valueRating, guestSatisfactionOverall, visibleReviewCount, title):
    # Define the MySQL INSERT statement
    insert_query = '''REPLACE INTO airbnb_listings (
        listingId, listingLat, listingLng, bedType, roomType, personCapacity, descriptionLanguage,
        isSuperhost, accuracyRating, checkinRating, cleanlinessRating, communicationRating, locationRating,
        valueRating, guestSatisfactionOverall, visibleReviewCount, title
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    # Define the parameter values
    values = (listingId, listingLat, listingLng, bedType, roomType, personCapacity, descriptionLanguage,
              isSuperhost, accuracyRating, checkinRating, cleanlinessRating, communicationRating, locationRating,
              valueRating, guestSatisfactionOverall, visibleReviewCount, title)
    # Execute the INSERT statement
    cursor.execute(insert_query, values)
    # Commit the transaction
    conn.commit()
    print(f"Crawled PropertyId: {listingId}")

def insert_availability(listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable):
    sql_insert_with_param = """REPLACE INTO airbnb_availability
                            (listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable) 
                            VALUES (%s, %s, %s, %s, %s, %s,%s);"""
    val = (listingId,available,calendarDate,maxNights,minNights,availableForCheckin,bookable)
    cursor.execute(sql_insert_with_param , val)
    conn.commit() 
    print(val)

#ITEMS_LIST=[i.get_attribute('href') for i in driver.find_elements('xpath','//div[@id="FMP-target"]//div[@data-testid="card-container"]/a')]
ITEMS_LIST=["https://www.airbnb.com/rooms/plus/19017960?display_currency=USD",
            "https://www.airbnb.com/rooms/689828220112367064?display_currency=USD"]

driver=uc.Chrome()
time.sleep(10)

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