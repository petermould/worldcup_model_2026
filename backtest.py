from simulation import match_result
from ratings import df

ratings = df['rating'].to_dict()

R16 = [
    'Netherlands', 'USA',
    'Argentina', 'Australia',
    'France', 'Poland',
    'England', 'Senegal',
    'Japan', 'Croatia',
    'Brazil', 'South Korea',
    'Morocco', 'Spain',
    'Portugal', 'Switzerland',
]

def simulate_knockout(teams, n=10000):
   
    win_counts = {}

    for _ in range(n):
        remaining = list(teams)

        while len(remaining) > 1:
            next_round = []
            for i in range(0, len(remaining), 2):
                a, b = remaining[i], remaining[i+1]
                w, _, _ = match_result(
                    ratings[a], ratings[b],
                    knockout=True,
                    team_a=a, team_b=b
                )
                next_round.append(a if w == 'a' else b)
            remaining = next_round

        champion = remaining[0]
        win_counts[champion] = win_counts.get(champion, 0) + 1

    results = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"\n2022 World Cup Backtest ({n:,} simulations)")
    print(f"Actual winner: Argentina\n")
    print(f"{'Team':<20} {'Probability':>12}")
    print("-" * 35)
    for team, count in results:
        prob = round((count / n) * 100, 1)
        bar = '█' * int(prob / 2)
        print(f"{team:<20} {prob:>10}%   {bar}")

if __name__ == "__main__":
    simulate_knockout(R16, n=10000)