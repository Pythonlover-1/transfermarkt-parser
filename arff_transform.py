import arff
import csv
from utils import *
from config import OUTPUT_DIR

# Dict with arff result
result = {
    'description': "Top 10_00 player by price",
    'relation': "players",
    'attributes': [
        ('age', 'INTEGER'),
        ('height,meters', 'REAL'),
        ('club_country',
         ['Turkiye', 'Italy', 'France', 'Spain', 'Netherlands', 'Germany', 'Portugal', 'Saudi_arabia', 'Brazil',
          'Ukraine', 'England']
         ),
        ('national_team',
         ['Hungary', 'France', 'Jamaica', 'Croatia', 'Sweden', 'Switzerland', 'Burkina_faso', 'England',
          'Morocco', 'Uruguay', 'Spain', 'Algeria', 'Guinea', 'Norway', 'Georgia', 'Ghana', 'Mali', 'Ukraine',
          'Slovakia', 'Slovenia', 'Senegal', 'Nigeria', 'Belgium', 'Argentina', 'Germany', 'Portugal', 'Brazil',
          'Denmark', 'Ivory_coast', 'South_korea', 'Usa', 'Colombia', 'Ecuador', 'Italy', 'Turkiye', 'Egypt', 'Mexico',
          "Cote_d_ivoire", 'Netherlands', 'Ireland', 'Cameroon', 'Japan', 'Wales', 'Canada', 'Serbia']
         ),
        ('position', ['second-striker', 'left-winger', 'centre-forward', 'centre-back', 'goalkeeper',
                      'defensive-midfield', 'right-back', 'right-midfield', 'left-back', 'central-midfield',
                      'attacking-midfield', 'right-winger']),
        ('captain', ['TRUE', 'FALSE']),
        ('cost,million_euros', 'REAL'),
        ('play_time,minutes', 'INTEGER'),
        ('games_amount', 'INTEGER'),
        ('goals_amount', 'INTEGER')
    ],
    'data': [
    ]
}

# Convert tsv to arff
with open(f"{OUTPUT_DIR}/out_en.tsv", "r") as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        age = extract_age(row["Age"])
        height = extract_height(row["Height"])
        club_country = extract_club_country(row["Club_country"])
        if club_country == 'Korea_south':
            club_country = "South_korea"
        national_team = extract_national_team(row["Nation_team"])
        if national_team == 'Korea_south':
            national_team = "South_korea"
        position = extract_position(row["Position"])
        captain = extract_captain(row["Captain"])
        cost = extract_cost(row["Cost"])
        play_time = extract_minutes(row["Minutes_in_game"])
        games_amount = extract_games_amount(row["Games_count"])
        goals_amount = extract_goals_amount(row["Goals_count"])
        result['data'].append(
            [age, height, club_country, national_team, position, captain, cost, play_time, games_amount, goals_amount]
        )

# Save result to arff
with open(f"{OUTPUT_DIR}/result_en.arff", "w") as file:
    arff.dump(result, file)
