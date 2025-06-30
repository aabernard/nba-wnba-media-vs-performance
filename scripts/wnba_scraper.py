# ===================================================================
# FINAL WNBA SCRAPER (v21 - Max Stability & Stealth)
# ===================================================================
# This is the most advanced version, including stealth mode and
# ad-blocking settings to handle the difficult WNBA pages.
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
from selenium_stealth import stealth # Import the stealth library

# --- Configuration, change as needed---
SEASON_YEAR = 2023
COMEBACK_THRESHOLD = 11
SAVE_PROGRESS_EVERY = 5 
PAGE_LOAD_TIMEOUT = 30
POLITE_DELAY_MIN = 3
POLITE_DELAY_MAX = 7
LEAGUE = "WNBA"

def setup_driver():
    """Sets up a VISIBLE, STEALTHY Chrome WebDriver."""
    print("Setting up fresh, STEALTH Chrome driver...")
    chrome_options = ChromeOptions()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Experimental Ad-Blocking Settings
    prefs = { "profile.managed_default_content_settings.images": 2 }
    chrome_options.add_experimental_option("prefs", prefs)

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Apply Stealth Settings
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
            
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

def run_wnba_scrape():
    """Manages the entire WNBA scraping and analysis process."""
    
    raw_data_filename = f"{LEAGUE.lower()}_raw_data_{SEASON_YEAR}.csv"
    
    # --- Step 1: Discover all WNBA Game URLs ---
    driver = setup_driver()
    try:
        print(f"--- Discovering all {LEAGUE} game URLs for the {SEASON_YEAR} season... ---")
        base_url = f"https://www.basketball-reference.com/wnba/years/{SEASON_YEAR}_games.html"
        driver.get(base_url)
        time.sleep(3) 
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_game_urls = sorted([f"https://www.basketball-reference.com{a['href']}" for a in soup.select("td[data-stat='box_score_text'] a")])
        total_games_found = len(all_game_urls)
        print(f"--- Successfully discovered {total_games_found} unique game URLs. ---")
    finally:
        driver.quit()

    if not all_game_urls: return

    # --- Step 2: Scrape all games with Resume Logic ---
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
                    wait = WebDriverWait(driver, 20)
                    comment_wrapper = wait.until(EC.presence_of_element_located((By.ID, "all_line-score")))
                    comment_html = driver.execute_script("return arguments[0].innerHTML;", comment_wrapper)
                    time.sleep(random.uniform(POLITE_DELAY_MIN, POLITE_DELAY_MAX))
                    comment_soup = BeautifulSoup(comment_html, 'html.parser')
                    line_score_table = comment_soup.find('table', id='line-score')
                    
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
                    halftime_away = away_q1 + away_q2
                    halftime_home = home_q1 + home_q2
                    
                    main_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    full_title = main_soup.find('h1').text
                    game_date = full_title.split(',')[-1].strip()
                    
                    game_info = {
                        "Game_Date": game_date, "Home_Team": teams[1], "Away_Team": teams[0],
                        "Halftime_Score_Home": halftime_home, "Halftime_Score_Away": halftime_away,
                        "Final_Score_Home": correct_home_final, "Final_Score_Away": correct_away_final, "Game_URL": url
                    }
                    all_games_data.append(game_info)
                except Exception as e:
                    print(f"---! FAILED on {url}. Skipping. Error: {e}")
                    failed_urls.append(url)
                if (i + 1) % SAVE_PROGRESS_EVERY == 0 and all_games_data:
                    pd.DataFrame(all_games_data).to_csv(raw_data_filename, index=False)
                    print(f"\n--- Saving progress... ---")
        finally:
            driver.quit()
            if all_games_data:
                pd.DataFrame(all_games_data).to_csv(raw_data_filename, index=False)
                print("--- Performing final save. ---")

    # --- Final Analysis ---
    if not os.path.exists(raw_data_filename): return
    print(f"\nScraping complete. {len(failed_urls)} games failed.")
    if failed_urls: print("Failed URLs:", failed_urls)
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

if __name__ == '__main__':
    run_wnba_scrape()