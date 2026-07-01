from tournament import simulate_group
from ratings import df

def monte_carlo_group(group, ratings, n=10000):
    first_place = {team: 0 for team in group}
    second_place = {team: 0 for team in group}

    for _ in range(n):
        standings = simulate_group(group, ratings)
        first_place[standings[0][0]] += 1
        second_place[standings[1][0]] += 1

    results = {}
    for team in group:
        results[team] = {
            'win_group': round((first_place[team] / n) * 100, 1),
            'qualify':   round(((first_place[team] + second_place[team]) / n) * 100, 1)
        }

    return sorted(results.items(), key=lambda x: x[1]['qualify'], reverse=True)

if __name__ == "__main__":
    ratings = df['rating'].to_dict()
    group = ['England', 'Brazil', 'Morocco', 'Saudi Arabia']
    for team, stats in monte_carlo_group(group, ratings, n=10000):
        print(f"{team}: Win Group {stats['win_group']}% | Qualify {stats['qualify']}%")