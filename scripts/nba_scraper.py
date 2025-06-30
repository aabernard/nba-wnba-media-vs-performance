# ===================================================================
# NBA Scraper
# ===================================================================
# This script does everything from start to finish: discovers URLs,
# scrapes data with the corrected score logic, saves progress,
# and performs the final comeback deficit analysis.
# ===================================================================

import pandas as pd
import time
import random
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================================
# --- Main Configuration ---
# Customize these settings as needed for your scraping task.
# ==========================================================
LEAGUE = "NBA"
SEASON_YEAR = 2025 # Change this to the desired season year
COMEBACK_THRESHOLD = 20 # Minimum halftime deficit in points to be considered a comeback candidate, change as needed
SAVE_PROGRESS_EVERY = 5 # Change this to how often you want to save progress (every N games
PAGE_LOAD_TIMEOUT = 20 # Maximum time to wait for a page to load before driver gives up and moves on
POLITE_DELAY_MIN = 2 # Minimum delay between requests to avoid overwhelming the server
POLITE_DELAY_MAX = 5 # Maximum delay between requests to avoid overwhelming the server

# ==========================================================

def setup_driver():
    """
    Sets up a VISIBLE Chrome WebDriver.
    The driver is set to be visible and not stealthy for debugging purposes. If you want to use stealth, you can 
    modify this function to include stealth settings, look to wnba_scraper.py.
    """
    print("Setting up fresh Chrome driver...")
    chrome_options = ChromeOptions()
    # chrome_options.add_argument("--headless") # Uncomment this line to run in headless mode

    # Download and install the correct ChromeDriver version automatically
    service = ChromeService(ChromeDriverManager().install())

    # Initialize the Chrome driver with the specified service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Set a timeout for page loads to prevent hanging on slow pages
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

def run_scrape():
    """
    Manages the entire autonomous scraping and analysis process which discovers game URLs, scrapes data, 
    handles resuming, and filters comeback candidates.
    """

    # --- Step 0: Prepare the output filename for storing scraped data ---
    raw_data_filename = f"{LEAGUE.lower()}_raw_data_{SEASON_YEAR}_bball_ref.csv"

    # --- Step 1: Discover all Game URLs for the season ---
    driver = setup_driver()
    try:
        print(f"--- Pulling all game URLs for {LEAGUE} {SEASON_YEAR}... ---")
        
        # Construct the base URL for the season's game log page on Basketball Reference
        url_template = "https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html"
        start_month = "october"
        base_url = url_template.format(year=SEASON_YEAR, month=start_month) # Formats the URL for the starting month
            
        driver.get(base_url) # Navigate the browser to the initial game log page
        time.sleep(3) # Pause execution to allow the page to fully load before parsing
        
        # Parse the HTML content of the current page to find links to other months
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Select all 'a' (anchor) tags whose 'href' attribute contains '_games-' (indicates a month link)
        # Store these unique links in a set to avoid duplicates
        month_links = {f"https://www.basketball-reference.com{a['href']}" for a in soup.select('a[href*="_games-"]')}
        # If no month links are found (e.g., for some WNBA seasons where all games are on one page), 
        # add the base URL itself to ensure it's processed
        if not month_links: month_links.add(base_url) 
        
        all_game_urls = set() # Initialize a set to store all unique game URLs discovered 
        print(f"Found {len(month_links)} page(s) to check for game links...")

        # Iterate through each unique month's game log page (or just the main page if only one)
        for link in sorted(list(month_links)):
            try:
                print(f"Getting URLs from: {link}")
                driver.get(link) # Navigate the browser to the specific month's game log page
                time.sleep(1.5) # Short pause to allow the page to load
                month_soup = BeautifulSoup(driver.page_source, 'html.parser') # Parse the HTML content of the month page
                # Select all 'a' (anchor) tags within 'td' elements that have a 'data-stat' attribute equal to 'box_score_text'
                game_links = {f"https://www.basketball-reference.com{a['href']}" for a in month_soup.select("td[data-stat='box_score_text'] a")} # Add these newly discovered game URLs to the main set
                all_game_urls.update(game_links) # Add these newly discovered game URLs to the main set
            except Exception as e: 
                print(f"Could not load month page {link}: {e}") # Log errors 

        all_game_urls = sorted(list(all_game_urls))
        total_games_found = len(all_game_urls)
        print(f"--- Successfully discovered {total_games_found} unique game URLs. ---")
    finally:
        driver.quit() 

    if not all_game_urls:
        print("Could not discover any game URLs. Exiting.")
        return

    # --- Step 2: Scrape all games with Resume and Error Handling ---
    all_games_data = []
    failed_urls = []
    
    if os.path.exists(raw_data_filename):
        print(f"\nFound existing data file '{raw_data_filename}'. Resuming scrape.")
        existing_df = pd.read_csv(raw_data_filename)
        all_games_data = existing_df.to_dict('records')
        scraped_urls = set(existing_df['Game_URL'])
        urls_to_process = [url for url in all_game_urls if url not in scraped_urls]
    else:
        urls_to_process = all_game_urls
        
    if not urls_to_process:
        print("All discovered games have already been scraped.")
    else:
        print(f"\nStarting scrape for {len(urls_to_process)} remaining games.")
        driver = setup_driver()
        try:
            for i, url in enumerate(urls_to_process):
                current_game_num = len(all_games_data) + 1
                print(f"Scraping game {current_game_num}/{total_games_found}: {url}")
                try:
                    driver.get(url)
                    
                    wait = WebDriverWait(driver, 15)
                    comment_wrapper = wait.until(EC.presence_of_element_located((By.ID, "all_line_score")))
                    comment_html = driver.execute_script("return arguments[0].innerHTML;", comment_wrapper)
                    
                    time.sleep(random.uniform(POLITE_DELAY_MIN, POLITE_DELAY_MAX))
                    
                    comment_soup = BeautifulSoup(comment_html, 'html.parser')
                    line_score_table = comment_soup.find('table', id='line_score')

                    # --- The Correct Parsing Logic You Provided ---
                    rows = line_score_table.select("tbody tr")
                    teams_data = line_score_table.select("tbody th a")
                    teams = [th.text.strip() for th in teams_data]

                    away_row = rows[0]
                    home_row = rows[1]

                    away_q1 = int(away_row.find('td', {'data-stat': '1'}).text)
                    away_q2 = int(away_row.find('td', {'data-stat': '2'}).text)
                    correct_away_final = int(away_row.find('td', {'data-stat': 'T'}).text)
                    
                    home_q1 = int(home_row.find('td', {'data-stat': '1'}).text)
                    home_q2 = int(home_row.find('td', {'data-stat': '2'}).text)
                    correct_home_final = int(home_row.find('td', {'data-stat': 'T'}).text)

                    # Calculate halftime scores
                    halftime_away = away_q1 + away_q2
                    halftime_home = home_q1 + home_q2
                    
                    main_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    game_date = main_soup.select_one(".scorebox_meta div").text.strip()
                    
                    game_info = {
                        "Game_Date": game_date, "Home_Team": teams[1], "Away_Team": teams[0],
                        "Halftime_Score_Home": halftime_home, "Halftime_Score_Away": halftime_away,
                        "Final_Score_Home": correct_home_final, "Final_Score_Away": correct_away_final, "Game_URL": url
                    }
                    all_games_data.append(game_info)
                except Exception as e:
                    print(f"---! FAILED on {url}. Will be skipped. Error: {e}")
                    failed_urls.append(url)

                if (i + 1) % SAVE_PROGRESS_EVERY == 0 and all_games_data:
                    pd.DataFrame(all_games_data).to_csv(raw_data_filename, index=False)
                    print(f"\n--- Saving progress... ---")
        finally:
            driver.quit()
            if all_games_data:
                pd.DataFrame(all_games_data).to_csv(raw_data_filename, index=False)
                print("--- Performing final save. ---")

    # --- Step 3: Final Analysis ---
    if not os.path.exists(raw_data_filename):
        print("No data was scraped.")
        return

    print(f"\nScraping complete. Final dataset has {len(pd.read_csv(raw_data_filename))} games.")
    if failed_urls:
        print(f"{len(failed_urls)} games failed to scrape and were skipped.")
        
    full_df = pd.read_csv(raw_data_filename).drop_duplicates(subset=['Game_URL'], keep='last')
    
    full_df['Halftime_Deficit_Amount'] = abs(full_df['Halftime_Score_Home'] - full_df['Halftime_Score_Away'])
    full_df['Trailing_Team_Halftime'] = full_df.apply(lambda row: row['Home_Team'] if row['Halftime_Score_Home'] < row['Halftime_Score_Away'] else row['Away_Team'], axis=1)
    comebacks = full_df[full_df['Halftime_Deficit_Amount'] >= COMEBACK_THRESHOLD].copy()
    comebacks = comebacks[((comebacks['Trailing_Team_Halftime'] == comebacks['Home_Team']) & (comebacks['Final_Score_Home'] > comebacks['Final_Score_Away'])) | ((comebacks['Trailing_Team_Halftime'] == comebacks['Away_Team']) & (comebacks['Final_Score_Away'] > comebacks['Final_Score_Home']))]
    
    if not comebacks.empty:
        comeback_filename = f"{LEAGUE.lower()}_COMEBACK_CANDIDATES_{SEASON_YEAR}.csv"
        comebacks.to_csv(comeback_filename, index=False)
        print(f"\nSUCCESS! Found {len(comebacks)} comeback candidates.")
    else:
        print(f"\nCOMPLETE. No games found that met the {COMEBACK_THRESHOLD}-point threshold.")

# ==========================================================
# --- Script Entry Point ---
# ==========================================================
if __name__ == '__main__':
    run_scrape()