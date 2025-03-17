import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def scrape_static_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}  # Pretend to be a browser
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        courts = []
        
        for court in soup.find_all("div", class_="court-listing"):
            name = court.find("h2").text.strip()
            address = court.find("p", class_="address").text.strip()
            courts.append({"Name": name, "Address": address})
        
        return pd.DataFrame(courts)  # Convert to DataFrame for easy handling
    
    else:
        print("Failed to retrieve data")
        return None
    
def scrape_dynamic_page(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in the background
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    time.sleep(3)  # Wait for page to load
    
    courts = []
    listings = driver.find_elements(By.CLASS_NAME, "court-listing")
    
    for listing in listings:
        name = listing.find_element(By.TAG_NAME, "h2").text
        address = listing.find_element(By.CLASS_NAME, "address").text
        courts.append({"Name": name, "Address": address})
    
    driver.quit()  # Close browser
    return pd.DataFrame(courts)

def save_to_csv(dataframe, filename="pickleball_courts.csv"):
    dataframe.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

"""
CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"  # Adjust if needed

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    return driver

"""


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    # Initialize the Chrome driver using the updated webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def scrape_pickleheads():
    url = "https://sanjosepickleballclub.org/places-to-play/"
    driver = setup_driver()
    driver.get(url)
    
    time.sleep(5)  # Wait for JavaScript to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    courts = []
    
    # Find all court listings
    listings = soup.find_all("div", class_="css-16vw16x")  # Adjust class name if needed
    
    for listing in listings:
        try:
            name = listing.find("h3").text.strip() if listing.find("h3") else "Unknown"
            location = listing.find("p", class_="css-10v2xd8").text.strip() if listing.find("p", class_="css-10v2xd8") else "No Address"
            courts.append({"Name": name, "Location": location})
        except Exception as e:
            print(f"Error parsing listing: {e}")

    return pd.DataFrame(courts)

if __name__ == "__main__":
    print("Scraping Pickleheads Pickleball Courts...")
    df = scrape_pickleheads()
    
    if not df.empty:
        save_to_csv(df)
        print(df.head())  # Show first 5 results
    else:
        print("No data scraped.")
