import pyautogui
import time,random
import re
from tqdm import tqdm
import pandas as pd
import io
import subprocess
import os
import sqlite3
from selenium import webdriver   
from selenium.webdriver.common.by import By

mitmprocess_command = f"mitmdump -s mitmSave.py -p 2191"
browserprocess_command = f"brave --proxy-server=127.0.0.1:2191 &>/dev/null &"
SEARCH_URL='https://www.zillow.com/homes/'
# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def enter_navbar_text(textvalue):
    subprocess.run(['wmctrl','-xa','brave'])
    time.sleep(.5)
    pyautogui.hotkey('alt', 'd')
    time.sleep(.5)
    pyautogui.press('backspace') 
    time.sleep(.5)
    pyautogui.write(textvalue+'/', interval=0.05)
    time.sleep(.5)
    pyautogui.press('backspace') 
    time.sleep(.5)
    pyautogui.press('enter')

def get_listings():       
    cursor.execute("SELECT * FROM 'airdna+address' WHERE class in ('building','place') and geoid not in (Select geoid from 'zillow')")
    rows=cursor.fetchall()   
    row_headers=[x[0] for x in cursor.description] 
    initial_data=[]
    for result in rows:
        initial_data.append(dict(zip(row_headers,result)))
    print('Total rows : ',len(rows))
    return initial_data

def extract_data(queue):
    for each_property in tqdm(queue):
        geoid=each_property['geoid']
        address=each_property['display_name']
        enter_navbar_text(SEARCH_URL+address)
        time.sleep(15)
        driver.get('file:///home/shovon/Desktop/vm shared folder/github/airbnb/zillow/zillowdata.html')
        if 'No matching results' in driver.page_source:
            continue
        if not driver.find_elements(By.XPATH,'//button[text()="Zestimate"]/following::*'):
            continue
        zpid=re.search(r'"zpid":"(\d+)"', driver.page_source).group(1)
        zestimate=driver.find_element(By.XPATH,'//button[text()="Zestimate"]/following::*').text.replace('$','').replace(',','')
        if driver.find_elements(By.XPATH,'//button[text()="Rent Zestimate"]/following::*'):
            rentZestimate=driver.find_element(By.XPATH,'//button[text()="Rent Zestimate"]/following::*').text.replace('$','').replace(',','')
        else:
            rentZestimate=None
        buffer = io.StringIO(driver.page_source)
        if 'Tax assessment' in driver.page_source:
            taxAssessedValue=pd.read_html(buffer)[-1]['Tax assessment'][0].split(' ')[0].replace('$','').replace(',','')
        else:
            taxAssessedValue=None
        if 'Property taxes' in driver.page_source:
            try:
                property_tax=pd.read_html(buffer)[-1]['Property taxes'][0].split(' ')[0].replace('$','').replace(',','')
            except:
                property_tax=None
        else:
            property_tax=None
        if 'Total interior livable area' in driver.page_source:
            livingArea=re.search(r'Total interior livable area:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source).group(1).replace(',','')
        else:
            livingArea=None
        if re.search(r'Lot size:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source):
            lotAreaValue=re.search(r'Lot size:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', driver.page_source).group(1).replace(',','')
        else:
            lotAreaValue=None
        if driver.find_elements(By.XPATH,'//span[text()="bd"]//parent::*'):
            bathrooms=driver.find_element(By.XPATH,'//span[text()="bd"]//parent::*').text.split(' ')[0]
        else:
            bathrooms=None
        if driver.find_elements(By.XPATH,'//span[text()="ba"]//parent::*'):
            bedrooms=driver.find_element(By.XPATH,'//span[text()="ba"]//parent::*').text.split(' ')[0]
        else:
            bedrooms=None
        latitude=re.search(r'"latitude\\":(-?\d+\.\d+)', driver.page_source).group(1)
        longitude=re.search(r'"longitude\\":(-?\d+\.\d+)', driver.page_source).group(1)
        if driver.find_elements(By.XPATH,'//span[text()="Year built:"]/following::*'):
            year_built=driver.find_element(By.XPATH,'//span[text()="Year built:"]/following::*').text
        else:
            year_built=None
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
        os.remove('zillowdata.html')
    driver.quit()

queue=get_listings()
driver = webdriver.Chrome()
extract_data(queue)