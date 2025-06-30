library(dplyr)
library(readr)

# Define narrative code columns
code_cols <- c(
  "ATT. Ind. Resilience", "ATT. Self-Efficacy", "ATT. Team Efficacy/Cohesion",
  "ATT. Verbal Persuasion", "ATT. Emotional Reg.",
  "AFT. Momentum Lang.", "AFT. Draining Lang", "AFT. Perf. Outcome Lang.", "Gendered Lang."
)

# ---------- WNBA DATA ----------
# Load WNBA data
wnba_raw <- read_csv("wnba_raw_text_data.csv")

# Fix typo in column name if present
if ("ATT. Ind. Resillence" %in% names(wnba_raw)) {
  wnba_raw <- wnba_raw %>%
    rename(`ATT. Ind. Resilience` = `ATT. Ind. Resillence`)
}

# Aggregate WNBA data
wnba_aggregated <- wnba_raw %>%
  group_by(`URL of Article`) %>%
  summarise(
    `Game ID` = first(`Game ID`),
    League = first(League),
    `Comeback Team (CBT)` = first(`Comeback Team (CBT)`),
    `Opponent Team (OPP)` = first(`Opponent Team (OPP)`),
    `Game Date` = first(`Game Date`),
    `Media Outlet` = first(`Media Outlet`),
    Headline = first(Headline),
    `Author Written` = sum(`Snippet Type` == "authorwritten", na.rm = TRUE),
    `Player Quotes` = sum(`Snippet Type` == "playerquote", na.rm = TRUE),
    `Coach Quotes` = sum(`Snippet Type` == "coachquote", na.rm = TRUE),
    across(
      all_of(code_cols),
      list(
        `C` = ~sum(. == "C", na.rm = TRUE),
        `O` = ~sum(. == "O", na.rm = TRUE)
      ),
      .names = "{.fn}- {.col}"
    ),
    .groups = "drop"
  ) %>%
  rename_with(
    ~ gsub("C-", "C- ", gsub("O-", "O- ", .)),
    matches("C_|O_")
  ) %>%
  relocate(`URL of Article`, .after = `Media Outlet`)

# Export WNBA aggregated data
write_csv(wnba_aggregated, "wnba_aggregated_data.csv")

library(dplyr)
library(readr)

library(dplyr)
library(readr)

# ---------- NBA DATA ----------

# Load NBA data
nba_raw <- read_csv("nba_raw_text_data.csv")

# Fix typo in column name if present
if ("ATT. Ind. Resillience" %in% names(nba_raw)) {
  nba_raw <- nba_raw %>%
    rename(`ATT. Ind. Resilience` = `ATT. Ind. Resillience`)
}

# Rename 'Publication Date' to 'Game Date' if necessary
if ("Publication Date" %in% names(nba_raw)) {
  nba_raw <- nba_raw %>%
    rename(`Game Date` = `Publication Date`)
}

# Define all expected narrative code columns
all_possible_codes <- c(
  "ATT. Ind. Resilience", "ATT. Self-Efficacy", "ATT. Team Efficacy/Cohesion",
  "ATT. Verbal Persuasion", "ATT. Emotional Reg.",
  "AFT. Momentum Lang.", "AFT. Draining Lang", "AFT. Perf. Outcome Lang.", "Gendered Lang."
)

# Filter to only existing columns in this dataset
code_cols <- intersect(all_possible_codes, names(nba_raw))

# Aggregate NBA data
nba_aggregated <- nba_raw %>%
  group_by(`URL of Article`) %>%
  summarise(
    `Game ID` = first(`Game ID`),
    League = first(League),
    `Comeback Team (CBT)` = first(`Comeback Team (CBT)`),
    `Opponent Team (OPP)` = first(`Opponent Team (OPP)`),
    `Game Date` = first(`Game Date`),
    `Media Outlet` = first(`Media Outlet`),
    Headline = first(Headline),
    `Author Written` = sum(`Snippet Type` == "authorwritten", na.rm = TRUE),
    `Player Quotes` = sum(`Snippet Type` == "playerquote", na.rm = TRUE),
    `Coach Quotes` = sum(`Snippet Type` == "coachquote", na.rm = TRUE),
    across(
      all_of(code_cols),
      list(
        `C` = ~sum(. == "C", na.rm = TRUE),
        `O` = ~sum(. == "O", na.rm = TRUE)
      ),
      .names = "{.fn}- {.col}"
    ),
    .groups = "drop"
  ) %>%
  rename_with(
    ~ gsub("C-", "C- ", gsub("O-", "O- ", .)),
    matches("C_|O_")
  ) %>%
  relocate(`URL of Article`, .after = `Media Outlet`)

# Export aggregated NBA data
write_csv(nba_aggregated, "nba_aggregated_data.csv")