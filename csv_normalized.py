from scipy.io import arff
import pandas as pd
import numpy as np
from config import OUTPUT_DIR


def normalize(frame: pd.DataFrame):
    """
    Normalize given DataFrame
    """
    return (frame - frame.min()) / (frame.max() - frame.min())


# Load arff file to pandas.Dataframe
arff_data, meta = arff.loadarff(f'{OUTPUT_DIR}/result_en.arff')
types_and_values = list(map(lambda x: meta[x][1], meta))
df = pd.DataFrame(arff_data)

# Decode strings from 'ascii'
df[["\"play_time,minutes\"", "games_amount", "goals_amount"]] = df[
    ["\"play_time,minutes\"", "games_amount", "goals_amount"]].fillna(0)
for column in ("club_country", "national_team", "captain", "position"):
    df[column] = df[column].str.decode("ascii")

# Make new column: minutes per game (play_time / games_amount)
df["minutes_per_game"] = df["\"play_time,minutes\""] / df["games_amount"]
df["minutes_per_game"] = df["minutes_per_game"].mask(df["games_amount"] == 0, 0)

# Normalize columns
for column in ("age", "\"height,meters\"", "\"cost,million_euros\"", "minutes_per_game", "goals_amount"):
    df[column] = normalize(df[column])

# Convert bool columns into columns with values {0, 1}
df["captain"] = (df["captain"] == "TRUE").astype(np.uint8)
for cl_country in types_and_values[2]:
    df[f"club_{cl_country}"] = (df["club_country"] == cl_country).astype(np.uint8)
for n_country in types_and_values[3]:
    df[f"national_{n_country}"] = (df["national_team"] == n_country).astype(np.uint8)

# Save result into csv
df["target"] = df["position"]
df.drop(["club_country", "national_team", "position", "games_amount", "\"play_time,minutes\""],
        axis=1, inplace=True)
df.rename(columns={"\"height,meters\"": 'height', "\"cost,million_euros\"": 'cost'}, inplace=True)
df.to_csv(f"{OUTPUT_DIR}/normalized_data.csv", index=False)
