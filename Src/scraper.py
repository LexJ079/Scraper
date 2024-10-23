import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape a category page
def scrape_category(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all company listings
    companies = soup.find_all('div', class_='company-listing')

    scraped_data = []
    
    # Loop through all company listings
    for company in companies:
        name = company.find('h2').text.strip() if company.find('h2') else 'No Name'
        address = company.find('address').text.strip() if company.find('address') else 'No Address'
        phone = company.find('a', class_='phone-link').text.strip() if company.find('a', class_='phone-link') else 'No Phone'
        website = company.find('a', class_='website-link')['href'] if company.find('a', class_='website-link') else 'No Website'

        # Save data for each company
        scraped_data.append([name, address, phone, website])

    return scraped_data

# Function to handle pagination
def scrape_all_pages(base_url):
    page_number = 1
    all_companies = []

    while True:
        print(f"Scraping page {page_number}...")

        url = f"{base_url}?page={page_number}"
        companies = scrape_category(url)

        if not companies:  # Break loop if no more companies found (end of pages)
            break

        all_companies.extend(companies)
        page_number += 1

    return all_companies

# Save the data to a CSV file
def save_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'Phone', 'Website'])
        writer.writerows(data)

# URL of the category you want to scrape (replace 'category_name' with actual category)
base_url = 'https://www.goudengids.nl/nl/bedrijven/accountants/'

# Scrape the category
all_data = scrape_all_pages(base_url)

# Save the scraped data to CSV
save_to_csv(all_data, 'companies.csv')

print("Scraping completed. Data saved to companies.csv")

