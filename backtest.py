from simulation import match_result
from ratings_2022 import df

ratings = df['rating'].to_dict()

# Actual 2022 World cup group draw 
GROUPS = {
    'A': ['Qatar', 'Ecuador', 'Senegal', 'Netherlands'],
    'B': ['England', 'Iran', 'USA', 'Wales'],
    'C': ['Argentina', 'Saudi Arabia', 'Mexico', 'Poland'],
    'D': ['France', 'Australia', 'Denmark', 'Tunisia'],
    'E': ['Spain', 'Costa Rica', 'Germany', 'Japan'],
    'F': ['Belgium', 'Canada', 'Morocco', 'Croatia'],
    'G': ['Brazil', 'Serbia', 'Switzerland', 'Cameroon'],
    'H': ['Portugal', 'Ghana', 'Uruguay', 'South Korea'],
}

# Real 2022 knockout bracket structure (which group finishers meet in the R16)
# e.g. ('A', 1, 'B', 2) means Group A winner vs Group B runner-up
R16_FIXTURES = [
    ('A', 1, 'B', 2),
    ('C', 1, 'D', 2),
    ('D', 1, 'C', 2),
    ('B', 1, 'A', 2),
    ('E', 1, 'F', 2),
    ('G', 1, 'H', 2),
    ('F', 1, 'E', 2),
    ('H', 1, 'G', 2),
]
# QF pairings by R16 match index (0-indexed above)
QF_PAIRS = [(0, 1), (4, 5), (2, 3), (6, 7)]
# SF pairings by QF index
SF_PAIRS = [(0, 1), (2, 3)]


def play_match(team_a, team_b, knockout=False):
    winner_flag, ga, gb = match_result(
        ratings[team_a], ratings[team_b],
        knockout=knockout, team_a=team_a, team_b=team_b
    )
    if winner_flag == 'draw':
        return None, ga, gb
    return (team_a if winner_flag == 'a' else team_b), ga, gb


def simulate_group(teams):
    table = {t: {'pts': 0, 'gf': 0, 'ga': 0} for t in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            a, b = teams[i], teams[j]
            winner, ga, gb = play_match(a, b, knockout=False)
            table[a]['gf'] += ga
            table[a]['ga'] += gb
            table[b]['gf'] += gb
            table[b]['ga'] += ga
            if winner == a:
                table[a]['pts'] += 3
            elif winner == b:
                table[b]['pts'] += 3
            else:
                table[a]['pts'] += 1
                table[b]['pts'] += 1
    ranked = sorted(
        teams,
        key=lambda t: (table[t]['pts'], table[t]['gf'] - table[t]['ga'], table[t]['gf']),
        reverse=True
    )
    return ranked[0], ranked[1]  # winner, runner-up


def simulate_tournament():
    group_result = {g: simulate_group(teams) for g, teams in GROUPS.items()}

    r16_winners = []
    for grp_a, pos_a, grp_b, pos_b in R16_FIXTURES:
        team_a = group_result[grp_a][pos_a - 1]
        team_b = group_result[grp_b][pos_b - 1]
        winner, _, _ = play_match(team_a, team_b, knockout=True)
        r16_winners.append(winner)

    qf_winners = []
    for i, j in QF_PAIRS:
        winner, _, _ = play_match(r16_winners[i], r16_winners[j], knockout=True)
        qf_winners.append(winner)

    sf_winners = []
    for i, j in SF_PAIRS:
        winner, _, _ = play_match(qf_winners[i], qf_winners[j], knockout=True)
        sf_winners.append(winner)

    champion, _, _ = play_match(sf_winners[0], sf_winners[1], knockout=True)
    return champion


def run_backtest(n=10000):
    win_counts = {}
    for _ in range(n):
        champion = simulate_tournament()
        win_counts[champion] = win_counts.get(champion, 0) + 1

    results = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\n2022 World Cup Backtest — full tournament simulated from the real group draw ({n:,} runs)")
    print("Model only uses data available before Nov 20, 2022 kickoff.")
    print("Actual winner: Argentina\n")
    print(f"{'Team':<15} {'Probability':>12}")
    print("-" * 32)
    for team, count in results:
        prob = round((count / n) * 100, 1)
        bar = '█' * int(prob / 2)
        print(f"{team:<15} {prob:>10}%   {bar}")

    argentina_rank = [t for t, _ in results].index('Argentina') + 1
    argentina_prob = round((win_counts.get('Argentina', 0) / n) * 100, 1)
    print(f"\nArgentina finished #{argentina_rank} in the model's rankings at {argentina_prob}% to win it all.")


if __name__ == "__main__":
    run_backtest(n=10000)
