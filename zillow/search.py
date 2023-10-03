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
from bs4 import BeautifulSoup

mitmprocess_command = f"mitmdump -s mitmSave.py -p 2191"
browserprocess_command = f"chromium-browser --proxy-server=127.0.0.1:2191 &>/dev/null &"
SEARCH_URL='https://www.zillow.com/homes/'
# Connect to the database (creates a new one if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

browserprocess = subprocess.Popen(browserprocess_command, stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid, stderr=subprocess.PIPE)

def enter_navbar_text(textvalue):
    subprocess.run(['wmctrl','-xa','chromium'])
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

queue=get_listings()

for each_property in queue[:1]:
    geoid=each_property['geoid']
    address=each_property['display_name']
    enter_navbar_text(SEARCH_URL+address)
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

with open('zillowdata.html','r') as f:
        htmldata=f.read()

# Assuming you have the HTML content as a string
html_content = htmldata  # Replace this with your HTML content

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'lxml')

# Extract zpid using regex
zpid_match = re.search(r'"zpid":"(\d+)"', html_content)
if zpid_match:
    zpid = zpid_match.group(1)
else:
    zpid = None

# Extract zestimate and rentZestimate
zestimate_element = soup.find('button', text='Zestimate').find_next()
zestimate = zestimate_element.get_text(strip=True).replace('$', '').replace(',', '')

rent_zestimate_element = soup.find(text='Rent Zestimate').find_next_sibling().find_next()
rentZestimate = rent_zestimate_element.get_text(strip=True).replace('$', '').replace(',', '')

# Extract taxAssessedValue and property_tax
tax_assessed_value = None
property_tax = None

if 'Tax assessment' in html_content:
    df = pd.read_html(io.StringIO(html_content))[0]
    if 'Tax assessment' in df.columns:
        tax_assessed_value = df['Tax assessment'][0].split(' ')[0].replace('$', '').replace(',', '')
    if 'Property taxes' in df.columns:
        property_tax = df['Property taxes'][0].split(' ')[0].replace('$', '').replace(',', '')

# Extract livingArea and lotAreaValue
living_area_match = re.search(r'Total interior livable area:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', html_content)
if living_area_match:
    livingArea = living_area_match.group(1).replace(',', '')
else:
    livingArea = None

lot_area_value_match = re.search(r'Lot size:\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*sqft', html_content)
if lot_area_value_match:
    lotAreaValue = lot_area_value_match.group(1).replace(',', '')
else:
    lotAreaValue = None

# Extract bathrooms and bedrooms
bathrooms_element = soup.find(text='bd').find_parent()
bathrooms = bathrooms_element.get_text(strip=True).split(' ')[0]

bedrooms_element = soup.find(text='ba').find_parent()
bedrooms = bedrooms_element.get_text(strip=True).split(' ')[0]

# Extract latitude, longitude, and year_built
latitude_match = re.search(r'"latitude":(-?\d+\.\d+)', html_content)
if latitude_match:
    latitude = latitude_match.group(1)
else:
    latitude = None

longitude_match = re.search(r'"longitude":(-?\d+\.\d+)', html_content)
if longitude_match:
    longitude = longitude_match.group(1)
else:
    longitude = None

year_built_element = soup.find(text='Year built:').find_next_sibling()
year_built = year_built_element.get_text(strip=True)

domain=extract_data(htmldata)
savetodatabase(linkedin_url,domain)
os.remove('companyhtmldata.html')