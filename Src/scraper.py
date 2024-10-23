import requests
from bs4 import BeautifulSoup
import csv
import json

# Base URL of accountants directory
base_url = 'https://www.goudengids.nl/nl/bedrijven/accountants/'

# User-Agent to simulate a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
}

# Function to extract contact info from the listing
def extract_contact_info(listing):
    contact_info = {}
    
    # Extracting company name
    name_tag = listing.find('h2', class_='text-5 font-bold mb-2 is-paid')
    if name_tag:
        contact_info['name'] = name_tag.get_text(strip=True)

    # Extracting address components
    address_tag = listing.find('li', itemprop='address')
    if address_tag:
        street = address_tag.find("span", {"data-yext": "street"})
        postal_code = address_tag.find("span", {"data-yext": "postal-code"})
        city = address_tag.find("span", {"data-yext": "city"})
        
        contact_info['street'] = street.get_text(strip=True) if street else ''
        contact_info['postal_code'] = postal_code.get_text(strip=True) if postal_code else ''
        contact_info['city'] = city.get_text(strip=True) if city else ''
    
    # Extracting phone number from data-small-result attribute
    data_small_result = listing['data-small-result']
    small_result = json.loads(data_small_result)
    contact_info['phone'] = small_result.get('phone', '')

    # Extracting the company website (if available)
    contact_info['website'] = 'https://www.goudengids.nl' + listing['data-href']

    return contact_info

# Function to scrape all accountant listings
def scrape_accountants(base_url):
    # Send request to the base URL with headers
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all accountant listing blocks
    accountant_listings = soup.find_all('li', class_='result-item')

    # List to store all contact data
    contact_data = []

    # Loop through each accountant listing
    for listing in accountant_listings:
        contact_info = extract_contact_info(listing)
        if contact_info:
            contact_data.append(contact_info)

    return contact_data

# Function to save contact data to CSV
def save_to_csv(contact_data, filename='accountants_contacts.csv'):
    # Define CSV headers
    headers = ['name', 'street', 'postal_code', 'city', 'phone', 'website']

    # Writing to CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()  # Writing header
        for contact in contact_data:
            writer.writerow(contact)

    print(f"Data successfully saved to {filename}")

# Main script execution
if __name__ == "__main__":
    # Scrape accountants' contact info
    all_contact_data = scrape_accountants(base_url)

    # Save scraped data to CSV
    if all_contact_data:
        save_to_csv(all_contact_data)
    else:
        print("No contact data found.")

