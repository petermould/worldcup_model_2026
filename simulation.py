import numpy as np
from scipy.stats import poisson
import pandas as pd

penalty_df = pd.read_csv('data/penalties.csv').set_index('team')

def get_penalty_prob(team):
    if team not in penalty_df.index:
        return 0.5
    row = penalty_df.loc[team]
    total = row['wins'] + row['losses']
    if total == 0:
        return 0.5
    return row['wins'] / total

def simulate_match(rating_a, rating_b, base_goals=1.3):
    lambda_a = base_goals * (rating_a / ((rating_a + rating_b) / 2))
    lambda_b = base_goals * (rating_b / ((rating_a + rating_b) / 2))

    goals_a = poisson.rvs(lambda_a)
    goals_b = poisson.rvs(lambda_b)

    return goals_a, goals_b

def simulate_penalties(team_a, team_b):
    prob_a = get_penalty_prob(team_a)
    prob_b = get_penalty_prob(team_b)
    total = prob_a + prob_b
    return 'a' if np.random.random() < (prob_a / total) else 'b'

def match_result(rating_a, rating_b, knockout=False, team_a=None, team_b=None):
    goals_a, goals_b = simulate_match(rating_a, rating_b)

    if goals_a > goals_b:
        return 'a', goals_a, goals_b
    elif goals_b > goals_a:
        return 'b', goals_a, goals_b
    else:
        if knockout:
            winner = simulate_penalties(team_a, team_b)
            return winner, goals_a, goals_b
        else:
            return 'draw', goals_a, goals_b

if __name__ == "__main__":
    print(match_result(0.82, 0.61, knockout=True))
    print(match_result(0.82, 0.61, knockout=False))

