from simulation import match_result
from ratings import df

def simulate_group(group, ratings):
    results = {team: {'points': 0, 'gd': 0} for team in group}
    fixtures = [(group[i], group[j]) for i in range(len(group)) for j in range(i+1, len(group))]

    for team_a, team_b in fixtures:
        winner, ga, gb = match_result(ratings[team_a], ratings[team_b], knockout=False)

        if winner == 'a':
            results[team_a]['points'] += 3
        elif winner == 'b':
            results[team_b]['points'] += 3
        else:
            results[team_a]['points'] += 1
            results[team_b]['points'] += 1

        results[team_a]['gd'] += ga - gb
        results[team_b]['gd'] += gb - ga

    standings = sorted(results.items(), key=lambda x: (x[1]['points'], x[1]['gd']), reverse=True)
    return standings

if __name__ == "__main__":
    ratings = df['rating'].to_dict()
    group = ['England', 'Brazil', 'Morocco', 'Saudi Arabia']
    print(simulate_group(group, ratings))