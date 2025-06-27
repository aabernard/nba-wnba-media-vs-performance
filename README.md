# nba-wnba-media-vs-performance
Pilot study analyzing psychological drivers of basketball comebacks via media framing and game performance. This repository contains the code, data, and outputs comparing NBA and WNBA comeback games from 2023-24, and integrates qualitative media analysis with quantitative play-by-play data. Also contains code for scraping box score data for both leagues. 

## Project Summary
This study combines: 
- **Qualitative analysis:** AI assisted coding of 40 media articles (22 NBA, 18 WNBA) covering 12 major comeback games, with attention to psychological attributes like resilience, team cohesion, momentum language, and aftermath framing.
- **Quantitative analysis:** Statistical testing of play-by-play metrics (points, field goal %, turnovers, fouls, timeouts) in the 6-minute aftermath window following a comeback-tying score.
Research Questions:
1. Do comeback teams statistically outperform opponents after tying the game?
2. Do NBA vs. WNBA comeback performances differ?
3. Is the performance gap between comeback teams and opponents larger in the NBA vs. WNBA?

## TL;DR: Key Findings
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
│   ├── docs/
│   │   └── qualitative_data_codebook.pdf
│   ├── bothleague_aggregated_text_data.csv
│   ├── nba_aggregated_data.csv
│   ├── nba_comeback_candidates_2023.csv
│   ├── nba_comeback_candidates_2024.csv
│   ├── pbp_wnba_nba_data.csv
│   ├── wnba_aggregated_data.csv
│   ├── wnba_comeback_candidates_2023.csv
│   ├── wnba_comeback_candidates_2024.csv
scripts/
|   └── aggregate_text_data.R
|   └── nba_scraper.py
|   └── wnba_scraper.py
|   └── csv_analyzer.py
output/
│   └── analysis.Rmd  
│   └── analysis.html
├── README.md
```

## Requirements
- R 4.x
- Packages: `tidyverse`, `janitor`, `ggplot2`, `lme4`, `lmerTest`, `broom`, `knitr`, `kableExtra`, `influence.ME`

## License
This project is shared for academic purposes. Please cite if used.

## Contact
Alyssa A. Bernard  
a.bernard25@ncf.edu -- https://github.com/aabernard
