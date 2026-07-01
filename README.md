#World Cup 2026 Predictor

A Monte Carlo simulation engine that predicts the 2026 FIFA World Cup using a custom rating system built from real football data. Run it once and you get a single result. Run it 10,000 times and you get probabilities.


#Why I Built This

I work in football — specifically in goal-line technology — and I wanted to build something that combined my interest in the sport with the data and ML skills I'm developing. A World Cup predictor felt like the right project. It's got a clear output, real data you can argue about, and enough complexity under the hood to be interesting.


#How It Works

Every team gets a rating built from three factors:

1. xG Differential — Expected goals scored minus expected goals conceded per game, averaged across the 2018 and 2022 World Cups. This strips out luck and measures how well a team actually played, not just whether they won.

2. Squad Market Value — Total Transfermarkt squad value, log-scaled to stop the gap between elite and mid-tier nations from dominating everything else. This captures raw talent in a way match results alone can't.

3. Tournament Form — Points earned across the last two major tournaments per confederation (World Cup + Euros/Copa America/AFCON etc). Rewards teams that consistently perform on the big stage.


These three combine into a single rating:

Rating = (0.40 × xG Differential) + (0.35 × Market Value) + (0.25 × Form)


The weights were chosen based on reasoning and validated through backtesting — more on that below.

Once every team has a rating, matches are simulated using a Poisson distribution. If a team is expected to score 1.4 goals, the model samples from Poisson(1.4) to get the actual scoreline. Do that once and you get one possible version of the tournament. Do it 10,000 times and you get a probability distribution.


Drawn knockout games go to penalties. Rather than a coin flip, each team has a historical shootout win rate based on their record in major tournaments. England's 30% win rate hurts them. Argentina's 75% helps them.


Two Simulation Modes

Mode 1 — Pre-tournament
Simulates everything from scratch. All 12 groups play out, the best third-place teams qualify, then the full knockout bracket runs. Useful for pre-tournament predictions.

Mode 2 — Current state
Locks in real results from the tournament so far and simulates everything still to be played. Updated for the 2026 World Cup as it happens.


Backtesting

I ran the model against the 2022 World Cup knockout stage to see how well it predicted. Using the real Round of 16 bracket, Argentina came out as the most likely champion at 17.5%, with France second at 15.1%.

Argentina won the tournament. France reached the final.

Argentina     17.5%   ████████
France        15.1%   ███████
Spain         11.3%   █████
Brazil        10.2%   █████
England        7.7%   ███
Portugal       7.1%   ███
Morocco        5.9%   ██
...

Not perfect — Croatia and Morocco were underrated despite reaching the semi-finals — but the model correctly identified the winner and finalist, which is a decent result for three input factors.


Project Structure

world-cup-predictor/
│
├── data/
│   ├── teams.csv          # 49 teams with xG diff, market value, form
│   └── penalties.csv      # Historical shootout records per team
│
├── ratings.py             # Normalisation + composite rating calculation
├── simulation.py          # Poisson match sim + penalty shootout logic
├── tournament.py          # Group stage round-robin logic
├── monte_carlo.py         # Group-level probability engine
├── main.py                # Full tournament simulation (2 modes)
└── backtest.py            # 2022 World Cup validation


#How to Run

bashpip install pandas numpy scipy scikit-learn
python main.py

You'll be prompted to choose a mode. Results print to the terminal with a simple bar chart.


#Known Limitations

- The backtest uses current 2026 ratings rather than 2022-era ratings. Form scores include post-2022 results which weren't available at the time. A proper backtest would use historical rating snapshots for each tournament year.
- xG data isn't available before 2018. Teams missing from both tournaments use their confederation average as a proxy, which is a rough estimate.
- Penalty records are based on limited samples. Teams with no shootout history default to 50/50.
- Home advantage for the three co-hosts (USA, Canada, Mexico) is not currently modelled.
- Squad injuries, suspensions and managerial changes aren't captured. The model is a pre-tournament snapshot, not a live one.



#Data Sources

xG data — FBRef (2018 and 2022 World Cups)
Market values — Transfermarkt (2025)
Tournament form — Wikipedia / official confederation records
Penalty records — RSSSF / Wikipedia



#What I'd Improve Next

Source qualifying campaign xG for the 21 teams currently on confederation averages
Add recency weighting so 2022 counts more than 2018 in the xG calculation
Build a Streamlit dashboard so the output is visual rather than terminal text
Run a proper weight optimisation using grid search across backtested tournaments
