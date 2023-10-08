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


tax_assessed_value = re.search(r'"taxAssessedValue\\":(\d+)', html_content)
if tax_assessed_value:
    tax_assessed_value = tax_assessed_value.group(1)
property_tax = re.search(r'"taxPaid\\":(\d+\.\d+)', html_content)
if property_tax:
    property_tax = property_tax.group(1)

# Extract livingArea and lotAreaValue
living_area_match = re.search(r'"livingArea\\":(\d+)', html_content)
if living_area_match:
    livingArea = living_area_match.group(1).replace(',', '')
else:
    livingArea = None

lot_area_value_match = re.search(r'"lotSize\\":(\d+)', html_content)
if lot_area_value_match:
    lotAreaValue = lot_area_value_match.group(1).replace(',', '')
else:
    lotAreaValue = None

# Extract bathrooms and bedrooms
bathrooms_element = soup.find(string='bd').find_parent().find_parent()
bathrooms = bathrooms_element.get_text(strip=True).replace('bd', '')

bedrooms_element = soup.find(string='ba').find_parent().find_parent()
bedrooms = bedrooms_element.get_text(strip=True).replace('ba', '')

# Extract latitude, longitude, and year_built
latitude_match = re.search(r'"latitude\\":(-?\d+\.\d+)', html_content)
if latitude_match:
    latitude = latitude_match.group(1)
else:
    latitude = None

longitude_match = re.search(r'"longitude\\":(-?\d+\.\d+)', html_content)
if longitude_match:
    longitude = longitude_match.group(1)
else:
    longitude = None

year_built_element = re.search(r'"yearBuilt\\":(\d+)', html_content)
year_built = year_built_element.group(1)