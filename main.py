from simulation import match_result
from tournament import simulate_group
from ratings import df

ratings = df['rating'].to_dict()

GROUPS = {
    'A': ['Mexico', 'South Africa', 'South Korea', 'Czechia'],
    'B': ['Switzerland', 'Canada', 'Bosnia', 'Curacao'],
    'C': ['Brazil', 'Morocco', 'Japan', 'New Zealand'],
    'D': ['USA', 'Australia', 'Paraguay', 'Turkiye'],
    'E': ['Germany', 'Cote dIvoire', 'Ecuador', 'Haiti'],
    'F': ['Netherlands', 'Sweden', 'Iraq', 'Uzbekistan'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cabo Verde', 'Uruguay', 'Saudi Arabia'],
    'I': ['France', 'Norway', 'Senegal', 'Iraq'],
    'J': ['Argentina', 'Austria', 'Algeria', 'Jordan'],
    'K': ['Colombia', 'Portugal', 'Congo DR', 'Uzbekistan'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

# Real R32 results already confirmed
R32_CONFIRMED = ['Canada', 'Brazil', 'Paraguay', 'Morocco']

# Remaining R32 matchups
R32_REMAINING = [
    ('Cote dIvoire', 'Norway'),
    ('France', 'Sweden'),
    ('Mexico', 'Ecuador'),
    ('England', 'Congo DR'),
    ('Belgium', 'Senegal'),
    ('USA', 'Bosnia'),
    ('Spain', 'Austria'),
    ('Portugal', 'Croatia'),
    ('Switzerland', 'Algeria'),
    ('Colombia', 'Ghana'),
    ('Argentina', 'Cabo Verde'),
    ('Australia', 'Egypt'),
]

def get_best_third_place(group_results):
    # Collect all third place teams across groups
    third_place = []
    for group_name, standings in group_results.items():
        team, stats = standings[2]
        third_place.append((team, stats['points'], stats['gd']))

    # Sort by points then goal difference
    third_place.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Return top 8 team names
    return [t[0] for t in third_place[:8]]

def simulate_knockout_stage(teams):
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
    return remaining[0]

def mode1_pretournament(n=10000):
    print("\n" + "=" * 55)
    print("MODE 1 — PRE-TOURNAMENT SIMULATION")
    print(f"Simulating full tournament {n:,} times")
    print("=" * 55)

    win_counts = {}

    for _ in range(n):
        group_results = {}
        r32 = []

        # Simulate all 12 groups
        for group_name, teams in GROUPS.items():
            standings = simulate_group(teams, ratings)
            group_results[group_name] = {
                standings[i][0]: standings[i][1] for i in range(4)
            }
            # Store as list of tuples for third place logic
            group_results[group_name] = standings
            r32.append(standings[0][0])  # 1st place
            r32.append(standings[1][0])  # 2nd place

        # Get best 8 third place teams
        third_place_qualifiers = get_best_third_place(group_results)
        r32.extend(third_place_qualifiers)

        # Simulate knockout
        champion = simulate_knockout_stage(r32)
        win_counts[champion] = win_counts.get(champion, 0) + 1

    print_results(win_counts, n)

def mode2_current_state(n=10000):
    print("\n" + "=" * 55)
    print("MODE 2 — CURRENT TOURNAMENT STATE")
    print(f"Simulating from Round of 32 {n:,} times")
    print("Confirmed through: Canada, Brazil, Paraguay, Morocco")
    print("=" * 55)

    win_counts = {}

    for _ in range(n):
        r16 = list(R32_CONFIRMED)

        # Simulate remaining R32 matches
        for team_a, team_b in R32_REMAINING:
            w, _, _ = match_result(
                ratings[team_a], ratings[team_b],
                knockout=True,
                team_a=team_a, team_b=team_b
            )
            r16.append(team_a if w == 'a' else team_b)

        # Simulate knockout from R16 onwards
        champion = simulate_knockout_stage(r16)
        win_counts[champion] = win_counts.get(champion, 0) + 1

    print_results(win_counts, n)

def print_results(win_counts, n):
    results = sorted(win_counts.items(), key=lambda x: x[1], reverse=True)
    print(f"\n{'Team':<20} {'Probability':>12}")
    print("-" * 45)
    for team, count in results:
        prob = round((count / n) * 100, 1)
        bar = '█' * int(prob / 2)
        print(f"{team:<20} {prob:>10}%   {bar}")

if __name__ == "__main__":
    print("\nWorld Cup 2026 Simulator")
    print("1 — Pre-tournament simulation (full group stage)")
    print("2 — Current tournament state (from Round of 32)")
    choice = input("\nSelect mode (1 or 2): ")

    if choice == '1':
        mode1_pretournament(n=10000)
    elif choice == '2':
        mode2_current_state(n=10000)
    else:
        print("Invalid choice, please enter 1 or 2")