import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
# Define the CREATE listings TABLE statement
create_table_sql = """
CREATE TABLE IF NOT EXISTS "listings" (
    "listingId" TEXT,
    "listingLat" FLOAT,
    "listingLng" FLOAT,
    "bedType" TEXT,
    "roomType" TEXT,
    "personCapacity" INTEGER,
    "descriptionLanguage" TEXT,
    "isSuperhost" INTEGER,
    "accuracyRating" FLOAT,
    "checkinRating" FLOAT,
    "cleanlinessRating" FLOAT,
    "communicationRating" FLOAT,
    "locationRating" FLOAT,
    "valueRating" FLOAT,
    "guestSatisfactionOverall" FLOAT,
    "visibleReviewCount" INTEGER,
    "title" TEXT,
    "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("listingId")
);
"""
# Execute the CREATE TABLE statement
cursor.execute(create_table_sql)
conn.commit()
# Define the CREATE availability TABLE statement 
create_table_sql = """
CREATE TABLE IF NOT EXISTS "availability" (
    "listingId" TEXT,
    "available" INTEGER,
    "calendarDate" DATETIME,
    "maxNights" INTEGER,
    "minNights" INTEGER,
    "availableForCheckin" INTEGER,
    "bookable" INTEGER,
    "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
# Execute the CREATE TABLE statement
cursor.execute(create_table_sql)
conn.commit()
#close connection
conn.close()