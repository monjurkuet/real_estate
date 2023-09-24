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
);
--
CREATE TABLE "datedata" (
	"listingId"	TEXT,
	"calendarDate"	DATETIME,
	"priceDate"	DATETIME,
	"Price"	REAL,
	"booked_days"	TEXT,
	UNIQUE("listingId","calendarDate","priceDate","booked_days")
);
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
);
--
CREATE VIEW "average_daily_price" AS SELECT listingId,calendarDate,price,avg(price) FROM datedata GROUP by listingId,calendarDate;
--
CREATE TABLE [airdna_search] ( 
  [property_id] VARCHAR(255) NOT NULL,
  [airbnb_property_id] VARCHAR(255) NOT NULL,
  [vrbo_property_id] VARCHAR(255) NULL,
  [listing_type] VARCHAR(255) NULL,
  [bedrooms] INT NULL,
  [bathrooms] DECIMAL(3, 1) NULL,
  [accommodates] INT NULL,
  [rating] DECIMAL(3, 1) NULL,
  [reviews] INT NULL,
  [title] VARCHAR(255) NULL,
  [revenue_ltm] DECIMAL(10, 2) NULL,
  [revenue_potential_ltm] DECIMAL(10, 2) NULL,
  [occupancy_rate_ltm] DECIMAL(5, 2) NULL,
  [average_daily_rate_ltm] DECIMAL(10, 2) NULL,
  [days_available_ltm] INT NULL,
  [market_id] INT NULL,
  [market_name] VARCHAR(255) NULL,
  [currency] VARCHAR(10) NULL,
  [latitude] FLOAT NULL,
  [longitude] FLOAT NULL,
  [updated_at] DATETIME NULL DEFAULT CURRENT_TIMESTAMP ,
   PRIMARY KEY ([airbnb_property_id])
);
