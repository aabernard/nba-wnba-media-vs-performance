# nba-wnba-media-vs-performance
Pilot study analyzing psychological drivers of basketball comebacks via media framing and game performance. This repository contains the code, data, and outputs comparing NBA and WNBA comeback games from the 2022-23 and 2023-24 seasons, and integrates qualitative media analysis with quantitative play-by-play data. 

## Project Summary
This study combines: 
- **Qualitative analysis:** AI assisted coding of 40 media articles (22 NBA, 18 WNBA) covering 12 major comeback games, with attention to psychological attributes like resilience, team cohesion, momentum language, and aftermath framing.
- **Quantitative analysis:** Statistical testing of play-by-play metrics (points, field goal %, turnovers, fouls, timeouts) in the 6-minute aftermath window following a comeback-tying score.
  
## Research Questions:
1. Do comeback teams statistically outperform opponents after tying the game?
2. Do NBA vs. WNBA comeback performances differ?
3. Is the performance gap between comeback teams and opponents larger in the NBA vs. WNBA?

## TL;DR: Findings
- Comeback teams significantly outperformed opponents in points, field goal %, and turnovers during the aftermath for both leagues.
- NBA articles emphasized psychological drivers more than WNBA, but actual performance gaps were small when aftermath of ties were tested.
- Media narratives disproportionately focus on comeback team resilience and success, often neglecting opponent psychology and performance, though play by play data supported this focus.

## Repo Structure
```
data/
├── raw/
│   ├── nba_raw_data_2023.csv
│   ├── nba_raw_data_2024.csv
│   ├── nba_raw_text_data.csv
│   ├── wnba_raw_data_2023.csv
│   ├── wnba_raw_data_2024.csv
│   ├── wnba_raw_text_data.csv
├── processed/
│   ├── bothleague_aggregated_text_data.csv
│   ├── nba_aggregated_data.csv
│   ├── nba_comeback_candidates_2023.csv
│   ├── nba_comeback_candidates_2024.csv
│   ├── pbp_wnba_nba_data.csv
│   ├── wnba_aggregated_data.csv
│   ├── wnba_comeback_candidates_2023.csv
│   ├── wnba_comeback_candidates_2024.csv
docs/
│   ├── comeback_literature_review.pdf
│   ├── literature_review_notes.pdf
│   ├── qualitative_data_codebook.pdf
│   ├── qualitative_data_coding_prompt.pdf
scripts/
|   └── aggregate_text_data.R
|   └── nba_scraper.py
|   └── wnba_scraper.py
|   └── csv_analyzer.py
output/
│   └── analysis.Rmd  
├── README.md
├── comeback_research_2025.Rproj
```

## How to Run
Data Analysis can be viewed without setup at:
https://rpubs.com/abernard25/1326059

Otherwise, start by cloning this repo, then open `comeback_research_2025.Rproj` to set the proper working directory. Next, install the required packages if you don't have them already. Then you're ready to knit or view the code that built `analysis.Rmd`. The `scripts` folder contains two https://www.basketball-reference.com/ scrapers (one for NBA and one for WNBA, written in Python, working as of June 2025) for both NBA and WNBA, script to aggregate text data based on `game_id` (R), as well as a script (Python) that was used for double check comeback candidates from full season data. These are optional unless you intend to regenerate your own similar data set or extend the currently available ones. 

## Requirements
- R 4.x
- Packages: `tidyverse`, `janitor`, `ggplot2`, `lme4`, `lmerTest`, `broom`, `knitr`, `kableExtra`, `influence.ME`

## Credits/Acknowledgements
This project was completed as part of a research assistantship at New College of Florida under the direction of Professor Andrey Skripnokov, and shared for academic purposes. Please cite if any elements are used. Google's Gemini was used as a tool for code generation (building scrapers and some R code) and article quote extraction. 

## Contact
Alyssa A. Bernard  
a.bernard25@ncf.edu -- https://github.com/aabernard
