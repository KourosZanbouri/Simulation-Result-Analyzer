import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import ast

# Function to parse the list strings directly with filtering for empty values
def parse_list_string(list_string):
    if isinstance(list_string, str):
        list_string = list_string.strip('[]')
        list_string = list_string.replace(' ', ',')
        return [float(x) for x in list_string.split(',') if x]
    return list_string

# Load the data
distance_df = pd.read_csv('distance.csv')
meanbitlife_df = pd.read_csv('meanbitlife.csv')

# Extract relevant columns
distance_df = distance_df[['vectime', 'vecvalue']]
meanbitlife_df = meanbitlife_df[['vectime', 'vecvalue']]

# Apply the function to the relevant columns
distance_df['vectime'] = distance_df['vectime'].apply(parse_list_string)
distance_df['vecvalue'] = distance_df['vecvalue'].apply(parse_list_string)
meanbitlife_df['vectime'] = meanbitlife_df['vectime'].apply(parse_list_string)
meanbitlife_df['vecvalue'] = meanbitlife_df['vecvalue'].apply(parse_list_string)

# Explode the lists into individual rows
distance_df = distance_df.explode(['vectime', 'vecvalue'])
meanbitlife_df = meanbitlife_df.explode(['vectime', 'vecvalue'])

# Convert columns to appropriate data types
distance_df['vectime'] = distance_df['vectime'].astype(float)
distance_df['vecvalue'] = distance_df['vecvalue'].astype(float)
meanbitlife_df['vectime'] = meanbitlife_df['vectime'].astype(float)
meanbitlife_df['vecvalue'] = meanbitlife_df['vecvalue'].astype(float)

# Renaming columns for clarity
distance_df.columns = ['timestamp', 'distance']
meanbitlife_df.columns = ['timestamp', 'meanbitlife']

# Merging dataframes with a tolerance for timestamp differences
merged_df = pd.merge_asof(distance_df.sort_values('timestamp'), meanbitlife_df.sort_values('timestamp'), on='timestamp', tolerance=0.001, direction='nearest')

# Remove rows with NaN values in the meanbitlife column
cleaned_df = merged_df.dropna(subset=['meanbitlife'])

# Group by distance intervals of 1 meter and calculate mean bit life time
distance_intervals = pd.cut(cleaned_df['distance'], bins=np.arange(135, cleaned_df['distance'].max() + 1, 1))
mean_bit_lifetime_per_interval = cleaned_df.groupby(distance_intervals)['meanbitlife'].mean()

# Plotting
plt.figure(figsize=(12, 6))
mean_bit_lifetime_per_interval.plot(kind='bar')
plt.xlabel('Distance (m)')
plt.ylabel('Mean Bit Lifetime per Packet (End-to-End Latency)')
plt.title('Mean Bit Lifetime per Packet vs Distance (1m Intervals)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Display the plot
plt.show()

