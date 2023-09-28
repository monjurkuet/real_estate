import json
from fake_useragent import UserAgent
import requests as rq
import time
import sqlite3
import json

base_url='https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&email=muhamad.manjur@outlook.com'

ua = UserAgent()
headers = {'user-agent': ua.random}

# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

sql_select_Query = "SELECT DISTINCT latitude,longitude FROM `airdna_search` where (latitude,longitude) not in (SELECT DISTINCT lat,lon FROM osm_reverse_geocode)"
cursor = conn.cursor()
cursor.execute(sql_select_Query)
geocodes = cursor.fetchall()

for latitude,longitude in geocodes:
    response=rq.get(base_url.format(latitude=latitude,longitude=longitude),headers=headers).json()
    address=response['address']
    display_name=response['display_name']
    class_=response['class']
    sqlite_insert_with_param = """REPLACE INTO osm_reverse_geocode
                          (address,display_name,lat,lon,class) 
                          VALUES (?,?,?,?,?);""" 
    data_tuple = (json.dumps(address),display_name,latitude,longitude,class_)
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    print(data_tuple)
    time.sleep(1)

conn.close()