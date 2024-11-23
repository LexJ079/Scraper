import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import json
from fake_useragent import UserAgent  # Import fake_useragent

# Initialize the UserAgent object to get random user agents
ua = UserAgent()

# Bright Data ISP Proxy Configuration
BRIGHT_DATA_PROXY = "http://brd.superproxy.io:22225"
BRIGHT_DATA_USERNAME = "brd-customer-hl_a081c981-zone-isp_proxy1"
BRIGHT_DATA_PASSWORD = "kq5qh08tb54h"

# Function to scrape a single page with retry logic
def scrape_page(url, retries=2, seen_names=None):
    if seen_names is None:
        seen_names = set()
    attempt = 0
    while attempt <= retries:
        try:
            # Use a random user agent for each request
            headers = {
                'User-Agent': ua.random
            }

            # Define proxy with authentication
            proxies = {
                "http": f"http://{BRIGHT_DATA_USERNAME}:{BRIGHT_DATA_PASSWORD}@brd.superproxy.io:22225",
                "https": f"http://{BRIGHT_DATA_USERNAME}:{BRIGHT_DATA_PASSWORD}@brd.superproxy.io:22225",
            }
            
            # Make the request with proxies
            response = requests.get(url, headers=headers, proxies=proxies)
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
                    
                    # Skip duplicate company names
                    if name in seen_names:
                        continue
                    seen_names.add(name)
                    
                    # Extract phone number from data attribute (in JSON format)
                    data_small_result = listing.get('data-small-result')
                    if data_small_result:
                        data_json = json.loads(data_small_result)
                        phone = data_json.get('phone', 'N/A')
                    else:
                        phone = "N/A"
                    
                    # Extract address details
                    address_tag = listing.select_one('li[itemprop="address"]')
                    if address_tag:
                        street = address_tag.select_one('span[data-yext="street"]').get_text(strip=True) if address_tag.select_one('span[data-yext="street"]') else "N/A"
                        postal_code = address_tag.select_one('span[data-yext="postal-code"]').get_text(strip=True) if address_tag.select_one('span[data-yext="postal-code"]') else "N/A"
                        city = address_tag.select_one('span[data-yext="city"]').get_text(strip=True) if address_tag.select_one('span[data-yext="city"]') else "N/A"
                        address = f"{street}, {postal_code} {city}"
                    else:
                        address = "N/A"
                    
                    # Extract email address
                    email_tag = listing.select_one('div[data-js-event="email"]')
                    email = email_tag.get('data-js-value') if email_tag else "N/A"
                    
                    # Add to scraped data
                    scraped_data.append({
                        'name': name,
                        'address': address,
                        'phone': phone,
                        'email': email
                    })
                
                except Exception as e:
                    print(f"Error extracting data for a listing: {e}")
                    continue
            
            return scraped_data, seen_names  # Return data if successful

        except requests.exceptions.RequestException as e:
            print(f"Error scraping page {url}: {e}")
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 403:
                attempt += 1
                print(f"403 Forbidden encountered. Retrying... Attempt {attempt} of {retries}.")
                time.sleep(random.uniform(3, 5))  # Wait before retrying
            else:
                break  # Exit for other exceptions
    
    print(f"Failed to scrape page {url} after {retries + 1} attempts.")
    return [], seen_names

# Function to scrape multiple pages
def scrape_multiple_pages(category, start_page, num_pages):
    all_data = []
    base_url = f"https://www.goudengids.nl/nl/zoeken/{category}/"
    seen_names = set()
    
    for page_num in range(start_page, start_page + num_pages):
        page_url = f"{base_url}?page={page_num}"
        print(f"Scraping page: {page_url}")
        data, seen_names = scrape_page(page_url, seen_names=seen_names)
        
        if data:
            all_data.extend(data)
        
        # Implement random wait time to avoid getting blocked
        wait_time = random.uniform(3, 7)
        print(f"Waiting for {wait_time:.2f} seconds before scraping the next page...")
        time.sleep(wait_time)
    
    return all_data

# Save to CSV files
def save_to_csv(scraped_data, category, start_page, end_page):
    # Create the folder if it doesn't exist
    base_folder = "Collected Data"
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    # Create subfolders for each data type
    subfolders = {
        "all_data": os.path.join(base_folder, "All Data"),
        "phones": os.path.join(base_folder, "Phone Numbers"),
        "emails": os.path.join(base_folder, "Emails"),
        "addresses": os.path.join(base_folder, "Addresses")
    }
    
    for folder in subfolders.values():
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # Save combined data file
    all_data_file = os.path.join(
        subfolders["all_data"],
        f"{category}_pages_{start_page}_to_{end_page}_all_data.csv".replace(" ", "_")
    )
    with open(all_data_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'address', 'phone', 'email'])
        writer.writeheader()
        for data in scraped_data:
            writer.writerow(data)
    print(f"All data saved to {all_data_file}")

    # Save individual data files
    def save_individual_file(data_type, fieldname, subfolder):
        file_path = os.path.join(
            subfolders[subfolder],
            f"{category}_pages_{start_page}_to_{end_page}_{data_type}.csv".replace(" ", "_")
        )
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', fieldname])
            writer.writeheader()
            for data in scraped_data:
                writer.writerow({
                    'name': data['name'],
                    fieldname: data[fieldname]
                })
        print(f"{data_type.capitalize()} data saved to {file_path}")

    save_individual_file("phone", "phone", "phones")
    save_individual_file("email", "email", "emails")
    save_individual_file("address", "address", "addresses")

# Main script
if __name__ == "__main__":
    # Ask the user for the category, start page, and number of pages to scrape
    try:
        category = input("Enter the category of company to scrape (e.g., Accountants, Aannemers): ").strip()
        start_page = int(input("Enter the starting page number: "))
        num_pages_to_scrape = int(input("Enter the number of pages you want to scrape: "))
        
        # Scrape the data
        scraped_data = scrape_multiple_pages(category, start_page, num_pages_to_scrape)
        
        # Save the data to CSV files
        save_to_csv(scraped_data, category, start_page, start_page + num_pages_to_scrape - 1)
        
        print("Scraping complete.")
    
    except ValueError:
        print("Please enter a valid number for the starting page and number of pages.")

