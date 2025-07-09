"""
table_scraper.py

Scrapes tabular data from a web page using Selenium, extracts company names,
phone numbers, and emails, and exports the cleaned results to a CSV file.

Customize the target URL and the logic inside the row-processing loop to fit
your specific table structure.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import re

# ---------------------------
# CONFIGURATION
# ---------------------------

TARGET_URL = "http://example.com/table-page"  # <-- Replace with your actual URL
OUTPUT_FILE = "scraped_table_data.csv"

# ---------------------------
# SETUP SELENIUM (HEADLESS CHROME)
# ---------------------------

options = Options()
options.add_argument("--headless")  # Run browser in headless mode (no window)
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")

# Initialize Chrome WebDriver (make sure chromedriver is in your PATH)
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# ---------------------------
# LOAD TARGET PAGE
# ---------------------------

driver.get(TARGET_URL)

# Wait until table rows are present on the page
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.TAG_NAME, "tr"))
)

# ---------------------------
# EXTRACT TABLE DATA
# ---------------------------

rows = driver.find_elements(By.TAG_NAME, "tr")
data = []

for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if not cells:
        continue  # Skip empty or header rows

    # Combine all cell text for the row
    full_text = " ".join([cell.text.strip() for cell in cells if cell.text.strip()])

    # Example logic: first cell is assumed to be the company name
    company = cells[0].text.strip() if len(cells) > 0 else ""

    # Use regex to find phone numbers and emails in the full row text
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', full_text)
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', full_text)

    data.append({
        "Company": company,
        "Phone": phones[0] if phones else "",
        "Email": emails[0] if emails else ""
    })

# Close the browser
driver.quit()

# ---------------------------
# CREATE DATAFRAME & EXPORT
# ---------------------------

df = pd.DataFrame(data)

# Clean up company names (optional: keep only the first line)
df["Company"] = df["Company"].str.extract(r"^(.*?)(?:\n|$)").fillna(df["Company"])
df["Company"] = df["Company"].str.strip()

# Remove duplicates by company name
df.drop_duplicates(subset="Company", inplace=True)

# Save the cleaned data to a CSV file
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Data successfully saved to '{OUTPUT_FILE}'")
