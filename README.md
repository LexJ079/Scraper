---

# **Web Scraper for Goudengids.nl**

This Python-based web scraper extracts business details (name, address, phone, and email) from [Goudengids.nl](https://www.goudengids.nl/). It utilizes proxy servers and random user agents to bypass potential restrictions and saves the collected data in structured CSV files.

---

## **Features**
- Scrapes business information, including:
  - Name
  - Address
  - Phone number
  - Email
- Handles retries and avoids duplicate entries.
- Saves data into organized folders:
  - `All Data`: Contains all scraped data in a single CSV file.
  - `Phone Numbers`: Phone numbers grouped in a separate CSV file.
  - `Emails`: Emails grouped in a separate CSV file.
  - `Addresses`: Addresses grouped in a separate CSV file.

---

## **Requirements**
- Python 3.7 or higher
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `fake-useragent`

---

## **Setup Instructions**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/goudengids-scraper.git
   cd goudengids-scraper
   ```

2. **Install Dependencies**
   Install the required packages using the `requirements.txt` file:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Proxy Configuration**
   Update the `BRIGHT_DATA_PROXY`, `BRIGHT_DATA_USERNAME`, and `BRIGHT_DATA_PASSWORD` variables in the script to match your proxy service credentials.

---

## **Usage**

1. **Run the Scraper**
   Execute the script to start scraping:
   ```bash
   python3 scraper.py
   ```

2. **Provide Input**
   The script will prompt for:
   - **Category**: The business type to scrape (e.g., `Accountants` or `Aannemers`).
   - **Start Page**: The page number to begin scraping.
   - **Number of Pages**: The total number of pages to scrape.

3. **Data Output**
   - The scraped data will be saved in the `Collected Data` folder, organized by type (`All Data`, `Phone Numbers`, etc.).

---

## **Folder Structure**
```
Collected Data/
├── All Data/
│   └── {category}_pages_{start}_to_{end}_all_data.csv
├── Phone Numbers/
│   └── {category}_pages_{start}_to_{end}_phone.csv
├── Emails/
│   └── {category}_pages_{start}_to_{end}_email.csv
└── Addresses/
    └── {category}_pages_{start}_to_{end}_address.csv
```

---

## **Error Handling**
- **403 Forbidden or IP Blacklisting**: The script retries with a new proxy or user agent. Ensure your proxy credentials are valid.
- **Connection Issues**: If multiple retries fail, the script skips the page and logs an error.

---
