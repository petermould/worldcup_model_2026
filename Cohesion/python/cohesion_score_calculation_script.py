import pandas as pd
import numpy as np
from itertools import combinations

df = pd.read_csv("/mnt/user-data/outputs/wc_2026_clean.csv")

teams = df["team_country"].unique()
rows = []

for team in teams:
    squad = df[df["team_country"] == team]
    n = len(squad)

    # 1. Squad Experience: mean caps
    se = squad["caps"].mean()

    # 2. Club Network Density: share of teammate pairs at same club
    clubs = squad["club"].dropna().tolist()
    club_counts = pd.Series(clubs).value_counts()
    same_club_pairs = sum(c * (c - 1) / 2 for c in club_counts if c > 1)
    total_pairs = n * (n - 1) / 2
    cnd = same_club_pairs / total_pairs if total_pairs > 0 else 0

    # 3. Domestic Concentration: % not playing abroad
    dc = 1 - squad["plays_abroad"].mean()

    # 4. Age balance: std of age, scored against an "optimal" spread (~3.75 yrs)
    age_std = squad["age_years"].std()

    rows.append({
        "team_country": team,
        "squad_size": n,
        "avg_caps": round(se, 1),
        "club_pair_density": round(cnd, 4),
        "domestic_pct": round(dc * 100, 1),
        "age_std": round(age_std, 2),
        "avg_age": round(squad["age_years"].mean(), 1),
    })

res = pd.DataFrame(rows)

# Normalize each metric 0-100 across the 48 teams
def minmax(s):
    return (s - s.min()) / (s.max() - s.min()) * 100

res["SE_norm"] = minmax(res["avg_caps"])
res["CND_norm"] = minmax(res["club_pair_density"])
res["DC_norm"] = minmax(res["domestic_pct"])

# Age balance: u-shaped score around optimal std (~3.75), penalize deviation
optimal_std = 3.75
res["age_dev"] = (res["age_std"] - optimal_std).abs()
res["AEB_norm"] = 100 - minmax(res["age_dev"])

res["SCI"] = (
    0.30 * res["SE_norm"] +
    0.30 * res["CND_norm"] +
    0.20 * res["DC_norm"] +
    0.20 * res["AEB_norm"]
).round(1)

res = res.sort_values("SCI", ascending=False).reset_index(drop=True)
res.insert(0, "rank", res.index + 1)

res.to_csv("/mnt/user-data/outputs/sci_2026_rankings.csv", index=False)

print(res[["rank","team_country","SCI","avg_caps","club_pair_density","domestic_pct","avg_age","age_std"]].to_string(index=False))
