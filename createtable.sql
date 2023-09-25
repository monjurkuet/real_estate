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
CREATE TABLE "datedata" (
	"listingId"	TEXT,
	"calendarDate"	DATETIME,
	"priceDate"	DATETIME,
	"Price"	REAL,
	"booked_days"	TEXT,
	UNIQUE("listingId","calendarDate","priceDate","booked_days")
);
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
CREATE TABLE "osm_reverse_geocode" (
	"address"	JSON,
	"display_name"	INTEGER,
	"lat"	NUMERIC,
	"lon"	NUMERIC,
	"class"	TEXT,
	"geoid"	INTEGER,
	UNIQUE("lat","lon"),
	PRIMARY KEY("geoid")
);
CREATE TABLE "zillow" (
	"zpid"	INTEGER UNIQUE,
	"geoid"	INTEGER,
	"zestimate"	NUMERIC,
	"rentZestimate"	NUMERIC,
	"taxAssessedValue"	NUMERIC,
	"livingArea"	NUMERIC,
	"lotAreaValue"	NUMERIC,
	"bathrooms"	NUMERIC,
	"bedrooms"	NUMERIC,
	"latitude"	NUMERIC,
	"longitude"	NUMERIC,
	"year_built"	INTEGER,
	"property_tax"	NUMERIC,
	PRIMARY KEY("zpid")
);
CREATE VIEW "airdna+address" AS SELECT * FROM `airdna_search` LEFT JOIN osm_reverse_geocode on airdna_search.latitude=osm_reverse_geocode.lat and airdna_search.longitude=osm_reverse_geocode.lon;
CREATE VIEW "average_daily_price" AS SELECT listingId,calendarDate,price,avg(price) FROM datedata GROUP by listingId,calendarDate;