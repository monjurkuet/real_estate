import sqlite3

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Define the table name
table_name1 = 'listings'

# Define the column names and their data types
columns1 = [
    'listingId TEXT',
    'listingLat FLOAT',
    'listingLng FLOAT',
    'bedType TEXT',
    'roomType TEXT',
    'personCapacity INTEGER',
    'descriptionLanguage TEXT',
    'isSuperhost INTEGER',
    'accuracyRating FLOAT',
    'checkinRating FLOAT',
    'cleanlinessRating FLOAT',
    'communicationRating FLOAT',
    'locationRating FLOAT',
    'valueRating FLOAT',
    'guestSatisfactionOverall FLOAT',
    'visibleReviewCount INTEGER',
    'location TEXT',
    'title TEXT'
]

# Create the table if it doesn't exist
create_table1_query = f"CREATE TABLE IF NOT EXISTS {table_name1} ({', '.join(columns1)})"
cursor.execute(create_table1_query)

# Commit the changes and close the connection
conn.commit()
conn.close()
