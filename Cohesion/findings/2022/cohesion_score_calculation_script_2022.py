import pandas as pd

df = pd.read_csv("/mnt/user-data/outputs/wc_2022_clean.csv")
df["dob"] = pd.to_datetime(df["dob"], errors="coerce")

KICKOFF = pd.Timestamp("2022-11-20")
df["age_years"] = ((KICKOFF - df["dob"]).dt.days / 365.25)

teams = df["team_country"].dropna().unique()
rows = []

for team in teams:
    squad = df[df["team_country"] == team]
    n = len(squad)
    if n < 2:
        continue

    clubs = squad["club"].dropna().str.strip().tolist()
    club_counts = pd.Series(clubs).value_counts()
    same_club_pairs = sum(c * (c - 1) / 2 for c in club_counts if c > 1)
    total_pairs = n * (n - 1) / 2
    cnd = same_club_pairs / total_pairs if total_pairs > 0 else 0

    age_std = squad["age_years"].std()

    rows.append({
        "team_country": team,
        "squad_size": n,
        "club_pair_density": round(cnd, 4),
        "avg_age": round(squad["age_years"].mean(), 1),
        "age_std": round(age_std, 2),
    })

res = pd.DataFrame(rows)

def minmax(s):
    return (s - s.min()) / (s.max() - s.min()) * 100

res["CND_norm"] = minmax(res["club_pair_density"])

optimal_std = 3.75
res["age_dev"] = (res["age_std"] - optimal_std).abs()
res["AEB_norm"] = 100 - minmax(res["age_dev"])

# Reweighted: CND 60%, AEB 40% (SE and DC dropped - not available/leakage risk for 2022)
res["SCI_partial"] = (0.60 * res["CND_norm"] + 0.40 * res["AEB_norm"]).round(1)

res = res.sort_values("SCI_partial", ascending=False).reset_index(drop=True)
res.insert(0, "rank", res.index + 1)

final = res[["rank","team_country","SCI_partial","club_pair_density",
             "avg_age","age_std"]].rename(columns={
    "rank": "Rank",
    "team_country": "Team",
    "SCI_partial": "Cohesion Score (0-100, Partial)",
    "club_pair_density": "Club Teammate Density",
    "avg_age": "Avg Squad Age",
    "age_std": "Age Spread (Std Dev)",
})

final.to_csv("/mnt/user-data/outputs/squad_cohesion_index_2022_rankings.csv", index=False)
print(final.to_string(index=False))
