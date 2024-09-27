import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# Function to parse the list strings directly with filtering for empty values
def parse_list_string(list_string):
    if isinstance(list_string, str):
        list_string = list_string.strip('[]')
        list_string = list_string.replace(' ', ',')
        return [float(x) for x in list_string.split(',') if x]
    return list_string

# Load the distance CSV file
distance_df = pd.read_csv('distance.csv')

# Load the new meanbitlife CSV file
meanbitlife_df_new = pd.read_csv('meanbitlife.csv')

# Parse and explode the distance data
distance_df['vectime'] = distance_df['vectime'].apply(parse_list_string)
distance_df['vecvalue'] = distance_df['vecvalue'].apply(parse_list_string)
distance_df = distance_df.explode(['vectime', 'vecvalue'])
distance_df['vectime'] = distance_df['vectime'].astype(float)
distance_df['vecvalue'] = distance_df['vecvalue'].astype(float)
distance_df_selected = distance_df[['vectime', 'vecvalue']]
distance_df_selected.columns = ['timestamp', 'distance']

# Parse and explode the meanbitlife data
meanbitlife_df_new['vectime'] = meanbitlife_df_new['vectime'].apply(parse_list_string)
meanbitlife_df_new['vecvalue'] = meanbitlife_df_new['vecvalue'].apply(parse_list_string)
meanbitlife_df_new = meanbitlife_df_new.explode(['vectime', 'vecvalue'])
meanbitlife_df_new['vectime'] = meanbitlife_df_new['vectime'].astype(float)
meanbitlife_df_new['vecvalue'] = meanbitlife_df_new['vecvalue'].astype(float)
meanbitlife_df_new_selected = meanbitlife_df_new[['vectime', 'vecvalue', 'module']]
meanbitlife_df_new_selected.columns = ['timestamp', 'meanbitlife', 'module']

# Extract app identifier from the module path to distinguish different apps
meanbitlife_df_new_selected['app'] = meanbitlife_df_new_selected['module'].apply(
    lambda x: re.search(r'app\[(\d+)\]', x).group(0) if re.search(r'app\[(\d+)\]', x) else 'app[0]'
)

# Map app identifiers to their respective names
app_name_mapping = {
    'app[0]': 'NC',
    'app[1]': 'Video',
    'app[2]': 'BE'
}
meanbitlife_df_new_selected['app'] = meanbitlife_df_new_selected['app'].map(app_name_mapping)

# Merging with distance data
merged_df_new = pd.merge_asof(
    distance_df_selected.sort_values('timestamp'), 
    meanbitlife_df_new_selected.sort_values('timestamp'), 
    on='timestamp', 
    tolerance=0.001, 
    direction='nearest'
)

# Remove rows with NaN values in the meanbitlife column
cleaned_df_new = merged_df_new.dropna(subset=['meanbitlife'])

# Multiply meanbitlife by 1,000,000 to convert to microseconds (μs)
cleaned_df_new['meanbitlife'] *= 1000000

# Recalculate min and max distances from the cleaned dataframe
min_distance_new = cleaned_df_new['distance'].min()
max_distance_new = cleaned_df_new['distance'].max()

# Group by distance intervals of 20 meters and calculate mean bit life time for each app
distance_intervals_new = pd.cut(cleaned_df_new['distance'], bins=np.arange(min_distance_new, 250 + 50, 50))
mean_bit_lifetime_per_interval_new = cleaned_df_new.groupby([distance_intervals_new, 'app'])['meanbitlife'].mean().unstack()

# Define colors for each app
color_mapping = {
    'NC': 'blue',
    'Video': 'green',
    'BE': 'red'
}

# Plotting the data for all apps with specified colors
plt.figure(figsize=(12, 6))
for app in mean_bit_lifetime_per_interval_new.columns:
    plt.plot(
        mean_bit_lifetime_per_interval_new.index.astype(str), 
        mean_bit_lifetime_per_interval_new[app], 
        marker='o', 
        label=app, 
        color=color_mapping[app]  # Specify the color for each app
    )
    
plt.xlabel('Distance (m)', fontsize=18)
plt.ylabel('End-to-End Delay - Mean (μs)', fontsize=18)
plt.xticks(rotation=45, fontsize=18)
plt.yticks(fontsize=18)
plt.grid(True)
plt.legend(fontsize=18)
plt.tight_layout()

# Display the plot
plt.show()

