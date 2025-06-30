# ===================================================================
# FINAL SCRIPT: The Comeback Candidate Analyzer
# ===================================================================
# This script reads the raw data files, and filters them to 
# find all games that meet the specified comeback criteria for the league.
# ===================================================================

import pandas as pd
import os

# --- Configuration ---
# Define the input CSV file. (Make sure to replace 'YOUR_FILE_NAME.csv' with the actual file name, and the .csv is in the same folder as this script.)
INPUT_CSV = "YOUR_FILE_NAME.csv"

# Define the comeback threshold.
THRESHOLD = 18

def find_comebacks(league_name, input_csv, threshold):
    """
    Reads a CSV file, calculates comeback metrics, and filters for candidates.

    Args:
        league_name (str): The name of the league (e.g., "WNBA").
        input_csv (str): The path to the input CSV file for the specified league.
        threshold (int): The minimum halftime deficit in points for a game to be
                         considered a "comeback candidate."
    """
    print(f"--- Analyzing {league_name} Data ---")

    # Check if the input file exists before attempting to read it.
    if not os.path.exists(input_csv):
        print(f"ERROR: Cannot find the data file '{input_csv}'. Please make sure it's in the same folder as this script.")
        print("-" * 30) # Separator for readability
        return # Exit the function if the file is not found

    # Read the corrected data from the CSV file into a pandas DataFrame.
    df = pd.read_csv(input_csv)
    print(f"Successfully read {len(df)} games from '{input_csv}'.")

    # --- Data Preparation for Analysis ---
    # Extract the full date from the Game_URL column.
    # The regex extracts 8 digits (YYYYMMDD) followed by 3 digits and 3 uppercase letters, then '.html'.
    # This ensures we get the date part of the URL consistently.
    # .iloc[:, 0] selects the first (and only) captured group.
    # Convert the extracted date string to datetime objects and then format them as 'YYYY-MM-DD'.
    df['Game_Date'] = df['Game_URL'].str.extract(r'(\d{8})\d{3}[A-Z]{3}\.html').iloc[:, 0]
    df['Game_Date'] = pd.to_datetime(df['Game_Date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    # Calculate the absolute difference in halftime scores to get the deficit amount.
    df['Halftime_Deficit_Amount'] = abs(df['Halftime_Score_Home'] - df['Halftime_Score_Away'])

    # Determine which team was trailing at halftime.
    # If the home team's halftime score is less than the away team's, the home team was trailing.
    # Otherwise, the away team was trailing.
    df['Trailing_Team_Halftime'] = df.apply(
        lambda row: row['Home_Team'] if row['Halftime_Score_Home'] < row['Halftime_Score_Away'] else row['Away_Team'],
        axis=1
    )

    # --- Analysis: Filter for Potential Comebacks ---
    # Filter the DataFrame to include only games where the halftime deficit meets or exceeds the specified threshold.
    potential_comebacks = df[df['Halftime_Deficit_Amount'] >= threshold].copy()

    # --- Analysis: Identify Successful Comebacks ---
    # Filter the 'potential_comebacks' DataFrame further to identify games where the trailing team actually won.
    # This involves two conditions:
    # 1. The trailing team was the Home_Team, AND the Home_Team's Final_Score is greater than the Away_Team's.
    # 2. The trailing team was the Away_Team, AND the Away_Team's Final_Score is greater than the Home_Team's.
    successful_comebacks = potential_comebacks[
        ((potential_comebacks['Trailing_Team_Halftime'] == potential_comebacks['Home_Team']) & (potential_comebacks['Final_Score_Home'] > potential_comebacks['Final_Score_Away'])) |
        ((potential_comebacks['Trailing_Team_Halftime'] == potential_comebacks['Away_Team']) & (potential_comebacks['Final_Score_Away'] > potential_comebacks['Final_Score_Home']))
    ].copy()

    # --- Output Results ---
    # Check if any successful comebacks were found.
    if not successful_comebacks.empty:
        # Sort the successful comebacks by the largest deficit first for easier review.
        successful_comebacks.sort_values(by='Halftime_Deficit_Amount', ascending=False, inplace=True)

        # Define the output filename for the comeback candidates.
        output_filename = f"{league_name}_COMEBACK_CANDIDATES.csv"
        # Save the DataFrame of successful comebacks to a new CSV file.
        # index=False prevents pandas from writing the DataFrame index as a column in the CSV.
        successful_comebacks.to_csv(output_filename, index=False)

        print(f"\nSUCCESS! Found {len(successful_comebacks)} comeback candidates for the {league_name}.")
        print(f"Results saved to '{output_filename}'")
        print("\nHere are the games:")
        # Print the relevant columns of the resulting table to the console.
        # .to_string() ensures all rows are printed without truncation.
        print(successful_comebacks[['Game_Date', 'Home_Team', 'Away_Team', 'Halftime_Score_Home',
                                     'Halftime_Score_Away', 'Final_Score_Home', 'Final_Score_Away',
                                     'Trailing_Team_Halftime', 'Halftime_Deficit_Amount']].to_string())
    else:
        print(f"\nCOMPLETE. No games found for the {league_name} that met the {threshold}-point threshold for a comeback win.")
    print("-" * 30) # Separator for readability


if __name__ == '__main__':
    # This block ensures that the functions are called only when the script is executed directly.
    # Run the analysis for WNBA data using the defined threshold.
    # Replace "LEAGUE_NAME_HERE" with the actual league name ("NBA" or "WNBA").
    find_comebacks("LEAGUE_NAME_HERE", INPUT_CSV, THRESHOLD)
