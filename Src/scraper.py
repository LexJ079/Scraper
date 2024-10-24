import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import json
from fake_useragent import UserAgent  # Import fake_useragent

# Initialize the UserAgent object to get random user agents
ua = UserAgent()

# URL of the base search page
base_url = "https://www.goudengids.nl/nl/zoeken/Accountants/"

# Function to scrape a single page
def scrape_page(url):
    try:
        # Use a random user agent for each request
        headers = {
            'User-Agent': ua.random
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Locate the listings
        listings = soup.find_all('li', class_='result-item')  # Adjust class if needed
        
        scraped_data = []
        
        for listing in listings:
            try:
                # Extract company name
                name_tag = listing.select_one('h2[itemprop="name"]')
                name = name_tag.get_text(strip=True) if name_tag else "N/A"
                
                # Extract phone number from data attribute
                data_small_result = listing.get('data-small-result')
                if data_small_result:
                    data_json = json.loads(data_small_result)
                    phone = data_json.get('phone', 'N/A')
                else:
                    phone = "N/A"
                
                # Extract address details
                address_tag = listing.select_one('li[itemprop="address"]')
                if address_tag:
                    street = address_tag.select_one('span[data-yext="street"]').get_text(strip=True)
                    postal_code = address_tag.select_one('span[data-yext="postal-code"]').get_text(strip=True)
                    city = address_tag.select_one('span[data-yext="city"]').get_text(strip=True)
                    address = f"{street}, {postal_code} {city}"
                else:
                    address = "N/A"
                
                # Extract website if available (use placeholder for now)
                website = "N/A"  # Modify this to extract if needed

                # Extract email address
                email_tag = listing.select_one('div[data-js-event="email"]')
                email = email_tag.get('data-js-value') if email_tag else "N/A"
                
                # Add to scraped data
                scraped_data.append({
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'email': email,  # Include email in the output
                    'website': website
                })
            
            except Exception as e:
                print(f"Error extracting data for a listing: {e}")
                continue
        
        return scraped_data
    
    except Exception as e:
        print(f"Error scraping page {url}: {e}")
        return []

# Function to scrape multiple pages
def scrape_multiple_pages(num_pages):
    all_data = []
    
    for page_num in range(1, num_pages + 1):
        page_url = f"{base_url}?page={page_num}"
        print(f"Scraping page: {page_url}")
        data = scrape_page(page_url)
        
        if data:
            all_data.extend(data)
        
        # Implement random wait time to avoid getting blocked
        wait_time = random.uniform(3, 7)
        print(f"Waiting for {wait_time:.2f} seconds before scraping the next page...")
        time.sleep(wait_time)
    
    return all_data

# Save to CSV
def save_to_csv(scraped_data, filename="output.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'address', 'phone', 'email', 'website'])
        writer.writeheader()
        for data in scraped_data:
            writer.writerow(data)

# Example usage
num_pages_to_scrape = 5  # Change this to scrape the desired number of pages
scraped_data = scrape_multiple_pages(num_pages_to_scrape)
save_to_csv(scraped_data)
print("Scraping complete. Data saved to output.csv")

