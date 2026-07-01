"""
Lightweight cleaning/standardisation of World Cup player datasets (2018, 2022, 2026).
No heavy compute - just pandas on small CSVs (<1100 rows each).
Outputs one unified, tidy CSV per tournament + a combined file, ready for
feature engineering (e.g. a team cohesion score) in a later step.
"""

import re
import pandas as pd

pd.set_option("display.max_columns", None)

UPLOAD = "/mnt/user-data/uploads/"
OUT = "/mnt/user-data/outputs/"

# ---------------------------------------------------------------------------
# 1. 2018 World Cup squads
# ---------------------------------------------------------------------------
df18 = pd.read_csv(UPLOAD + "world_cup_2018_players.csv", encoding="latin-1")
df18.columns = [c.strip() for c in df18.columns]

def parse_age(dob_str):
    """Extract age from strings like '(1973-01-15)15 January 1973 (aged 45)'."""
    if pd.isna(dob_str):
        return None
    m = re.search(r"aged (\d+)", str(dob_str))
    return int(m.group(1)) if m else None

def parse_dob(dob_str):
    if pd.isna(dob_str):
        return None
    m = re.search(r"\((\d{4}-\d{2}-\d{2})\)", str(dob_str))
    return m.group(1) if m else None

clean18 = pd.DataFrame({
    "tournament_year": 2018,
    "player_name": df18["Player"].str.strip(),
    "team_country": df18["Country"].str.strip(),
    "position": df18["Pos."].str.strip(),
    "club": df18["Club"].str.strip(),
    "dob": df18["Date of birth (age)"].apply(parse_dob),
    "age_at_tournament": df18["Date of birth (age)"].apply(parse_age),
    "caps": pd.to_numeric(df18["Caps"], errors="coerce"),
    "goals": pd.to_numeric(df18["Goals"], errors="coerce"),
})

# ---------------------------------------------------------------------------
# 2. 2022 World Cup squads
# ---------------------------------------------------------------------------
df22 = pd.read_csv(UPLOAD + "FIFA_WC_2022_Players_Stats.csv")
df22.columns = [c.strip() for c in df22.columns]

def to_num(series):
    return pd.to_numeric(series.astype(str).str.replace("%", "", regex=False).str.strip(),
                          errors="coerce")

clean22 = pd.DataFrame({
    "tournament_year": 2022,
    "player_name": df22["Player Name"].str.strip(),
    "team_country": df22["Nationality"].str.strip(),
    "position": df22["Position"].str.strip(),
    "club": df22["Club"].str.strip(),
    "fifa_ranking": pd.to_numeric(df22["FIFA Ranking"], errors="coerce"),
    "jersey_number": pd.to_numeric(df22["National Team Jersey Number"], errors="coerce"),
    "dob_raw": df22["Player DOB"],
    "appearances": to_num(df22["Appearances"]),
    "goals": to_num(df22["Goals Scored"]),
    "assists": to_num(df22["Assists Provided"]),
    "dribbles_per90": to_num(df22["Dribbles per 90"]),
    "interceptions_per90": to_num(df22["Interceptions per 90"]),
    "tackles_per90": to_num(df22["Tackles per 90"]),
    "duels_won_per90": to_num(df22["Total Duels Won per 90"]),
    "save_pct": to_num(df22["Save Percentage"]),
    "clean_sheets_pct": to_num(df22["Clean Sheets"]),
    "kit_sponsor": df22["National Team Kit Sponsor"].str.strip(),
})
clean22["dob"] = pd.to_datetime(clean22["dob_raw"], errors="coerce").dt.strftime("%Y-%m-%d")
clean22 = clean22.drop(columns=["dob_raw"])

# ---------------------------------------------------------------------------
# 3. 2026 World Cup squads -- official squad lists (much cleaner, no gaps)
# ---------------------------------------------------------------------------
df26 = pd.read_csv(UPLOAD + "SquadLists.csv", encoding="utf-8-sig")
df26.columns = [c.strip() for c in df26.columns]

def split_club_country(club_str):
    """'Lille OSC (FRA)' -> ('Lille OSC', 'FRA')"""
    if pd.isna(club_str):
        return None, None
    m = re.match(r"(.+?)\s*\(([A-Z]{2,4})\)\s*$", str(club_str).strip())
    if m:
        return m.group(1).strip(), m.group(2)
    return str(club_str).strip(), None

club_split = df26["Club"].apply(split_club_country)
club_name = club_split.apply(lambda t: t[0])
club_country = club_split.apply(lambda t: t[1])

clean26 = pd.DataFrame({
    "tournament_year": 2026,
    "player_name": df26["Player Name"].str.strip(),
    "team_country": df26["Team"].str.strip(),
    "team_code": df26["Team Code"].str.strip(),
    "shirt_number": pd.to_numeric(df26["Number"], errors="coerce"),
    "position": df26["Position"].str.strip(),
    "club": club_name,
    "club_country": club_country,           # is the player playing abroad?
    "plays_abroad": club_country.notna() & (club_country != df26["Team Code"].str.strip()),
    "dob": pd.to_datetime(df26["DOB"], format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m-%d"),
    "height_cm": pd.to_numeric(df26["Height (cm)"], errors="coerce"),
    "caps": pd.to_numeric(df26["Caps"], errors="coerce"),
    "goals": pd.to_numeric(df26["Goals"], errors="coerce"),
})

# age as of tournament kickoff (11 June 2026)
KICKOFF = pd.Timestamp("2026-06-11")
dob_dt = pd.to_datetime(clean26["dob"], errors="coerce")
clean26["age_years"] = ((KICKOFF - dob_dt).dt.days / 365.25).apply(
    lambda x: int(x) if pd.notna(x) else None)

# ---------------------------------------------------------------------------
# 4. Tidy + save individual files
# ---------------------------------------------------------------------------
for name, d in [("2018", clean18), ("2022", clean22), ("2026", clean26)]:
    d["player_name"] = d["player_name"].str.strip()
    d["team_country"] = d["team_country"].str.strip()
    d.to_csv(f"{OUT}wc_{name}_clean.csv", index=False)

# ---------------------------------------------------------------------------
# 5. A combined "core" file -- common columns only, useful as the backbone
#    for joining a future cohesion score (built from games-played-together,
#    club-overlap, squad-tenure, etc.)
# ---------------------------------------------------------------------------
core18 = clean18[["tournament_year", "player_name", "team_country", "position",
                   "club", "age_at_tournament", "caps", "goals"]].rename(
    columns={"age_at_tournament": "age", "caps": "appearances"})

core22 = clean22[["tournament_year", "player_name", "team_country", "position",
                   "club", "appearances", "goals"]].copy()
core22["age"] = None

core26 = clean26[["tournament_year", "player_name", "team_country", "position",
                   "club", "caps", "goals", "age_years"]].rename(
    columns={"caps": "appearances", "age_years": "age"})

combined = pd.concat([core18, core22, core26], ignore_index=True)
combined = combined[["tournament_year", "player_name", "team_country", "position",
                      "club", "age", "appearances", "goals"]]
combined.to_csv(f"{OUT}wc_combined_core.csv", index=False)

print("Done.")
print("2018:", clean18.shape, "2022:", clean22.shape, "2026:", clean26.shape)
print("Combined core:", combined.shape)
print(combined.head(10))
