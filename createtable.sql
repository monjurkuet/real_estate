--
CREATE TABLE "availability" (
	"listingId"	TEXT,
	"available"	INTEGER,
	"calendarDate"	DATETIME,
	"maxNights"	INTEGER,
	"minNights"	INTEGER,
	"availableForCheckin"	INTEGER,
	"bookable"	INTEGER,
	"timestamp"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	UNIQUE("listingId","calendarDate")
)
--
CREATE TABLE "datedata" (
	"listingId"	TEXT,
	"calendarDate"	DATETIME,
	"priceDate"	DATETIME,
	"Price"	REAL,
	"booked_days"	TEXT,
	UNIQUE("listingId","calendarDate","priceDate","booked_days")
)
--
CREATE TABLE "listings" (
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
)
--
CREATE VIEW "average_daily_price" AS SELECT listingId,calendarDate,price,avg(price) FROM datedata GROUP by calendarDate