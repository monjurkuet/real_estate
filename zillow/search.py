import pyautogui
import time,platform,random
import re
from tqdm import tqdm
import pandas as pd
import io
import subprocess
import signal
import os
import sqlite3

mitmprocess_command = f"mitmdump -s mitmSave.py -p 2191"
browserprocess_command = f"chromium-browser --proxy-server=127.0.0.1:2191 &>/dev/null &"
# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

browserprocess = subprocess.Popen(browserprocess_command, stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid, stderr=subprocess.PIPE)

def get_listings():       
    cursor.execute("SELECT * FROM 'airdna+address' WHERE class in ('building','place') and geoid not in (Select geoid from 'zillow')")
    rows=cursor.fetchall()   
    row_headers=[x[0] for x in cursor.description] 
    initial_data=[]
    for result in rows:
        initial_data.append(dict(zip(row_headers,result)))
    print('Total rows : ',len(rows))
    return initial_data

queue=get_listings()

for each_property in queue:
    geoid=each_property['geoid']
    address=each_property['display_name']
    driver.get(SEARCH_URL+address)
    if 'No matching results' in driver.page_source:
        continue
    zpid=re.search(r'"zpid":"(\d+)"', driver.page_source).group(1)
    zestimate=driver.find_element(By.XPATH,'//button[text()="Zestimate"]/following::*').text.replace('$','').replace(',','')
    rentZestimate=driver.find_element(By.XPATH,'//button[text()="Rent Zestimate"]/following::*').text.replace('$','').replace(',','')
    buffer = io.StringIO(driver.page_source)
    if 'Tax assessment' in taxAssessedValue:
        taxAssessedValue=pd.read_html(buffer)[0]['Tax assessment'][0].split(' ')[0].replace('$','').replace(',','')
        property_tax=pd.read_html(buffer)[0]['Property taxes'][0].split(' ')[0].replace('$','').replace(',','')
    livingArea=re.search(r'Total interior livable area:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source).group(1).replace(',','')
    lotAreaValue=re.search(r'Lot size:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source).group(1).replace(',','')
    bathrooms=driver.find_element(By.XPATH,'//span[text()="bd"]//parent::*').text.split(' ')[0]
    bedrooms=driver.find_element(By.XPATH,'//span[text()="ba"]//parent::*').text.split(' ')[0]
    latitude=re.search(r'"latitude":(-?\d+\.\d+)', driver.page_source).group(1)
    longitude=re.search(r'"longitude":(-?\d+\.\d+)', driver.page_source).group(1)
    year_built=driver.find_element(By.XPATH,'//span[text()="Year built:"]/following::*').text
    # Define the INSERT statement
    sqlite_insert_with_param = """REPLACE INTO zillow
                        (zpid, geoid, zestimate, rentZestimate, taxAssessedValue, livingArea, lotAreaValue, bathrooms, bedrooms, latitude, longitude, year_built, property_tax) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);""" 
    data_tuple = (zpid, geoid, zestimate, rentZestimate, taxAssessedValue, livingArea, lotAreaValue, bathrooms, bedrooms, latitude, longitude, year_built, property_tax)
    cursor.execute(sqlite_insert_with_param, data_tuple)
    # Commit the changes to the database
    conn.commit()
    print(data_tuple)
    time.sleep(random.uniform(3,9))