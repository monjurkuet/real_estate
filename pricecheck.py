import seleniumwire.undetected_chromedriver as uc
from seleniumwire.utils import decode
import time,getpass,platform
from datetime import datetime
import sshtunnel
from sshtunnel import SSHTunnelForwarder
import pymysql
import logging
from dateutil import parser
from datetime import timedelta
# myql ssh tunnel
ssh_host = '161.97.97.183'
ssh_username = 'root'
ssh_password = '$C0NTaB0vps8765%%$#'
database_username = 'root'
database_password = '$C0NTaB0vps8765%%$#'
database_name = 'airbnb'
localhost = '127.0.0.1'

def open_ssh_tunnel(verbose=False):
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG
    global tunnel
    tunnel = SSHTunnelForwarder(
        (ssh_host, 22),
        ssh_username = ssh_username,
        ssh_password = ssh_password,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    tunnel.start()

def mysql_connect():
    global connection
    connection = pymysql.connect(
        host='127.0.0.1',
        user=database_username,
        passwd=database_password,
        db=database_name,
        port=tunnel.local_bind_port
    )

def newBrowser():
    SYSTEM_OS=platform.system()
    if SYSTEM_OS=='Windows':
        user_data_dir="G:\\airbnbscrapingprofile"
        browser_executable_path='C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'
    if SYSTEM_OS=='Linux':
        CURRENTUSER=getpass.getuser()
        user_data_dir=f"/home/{CURRENTUSER}/airbnbscrapingprofile"
        browser_executable_path='/usr/bin/brave-browser'
    driver=uc.Chrome(user_data_dir=user_data_dir,
                     browser_executable_path=browser_executable_path,version_main=113,
                     headless=False,seleniumwire_options={
        'proxy': {
            'http': "http://45.85.147.136:24003",
            'https': "http://45.85.147.136:24003"
                }
            })
    return driver

def get_listings():
    cursor = connection.cursor()         
    cursor.execute("SELECT * FROM `availability` WHERE available=1")
    rows=cursor.fetchall()   
    row_headers=[x[0] for x in cursor.description] 
    initial_data=[]
    for result in rows:
        initial_data.append(dict(zip(row_headers,result)))
    print('Total rows : ',len(rows))
    return initial_data

if __name__ == "__main__":
    listings=get_listings()
    driver=newBrowser()
    open_ssh_tunnel()
    mysql_connect()
    for listing in listings[:1]:
        listingId=listing['listingId']
        calendarDate=listing['calendarDate']
        minNights=listing['minNights']
        checkindate=parser.parse(calendarDate)
        checkoutdate=checkindate+ timedelta(days=minNights)
        listingurl=f'https://www.airbnb.com/rooms/{listingId}?check_in={checkindate.strftime("%Y-%m-%d")}&check_out={checkoutdate.strftime("%Y-%m-%d")}'
        driver.get(listingurl)
    
    connection.close()
    tunnel.close