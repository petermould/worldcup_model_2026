import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv('/Users/peter/Desktop/World Cup Predictor/Predictor/data/teams.csv')
df = df.set_index('team')

df['market_value_log'] = np.log(df['market_value'])

scaler = MinMaxScaler()
df[['xg_diff_norm', 'market_value_norm', 'form_norm']] = scaler.fit_transform(
    df[['xg_diff', 'market_value_log', 'form']]
)

df['rating'] = (0.40 * df['xg_diff_norm']) + (0.35 * df['market_value_norm']) + (0.25 * df['form_norm'])

if __name__ == "__main__":
    print(df[['rating']].sort_values('rating', ascending=False).to_string())