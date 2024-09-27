import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the uploaded CSV files
sinr_df = pd.read_csv('sinr.csv')
distance_df = pd.read_csv('distance.csv')

# Extract relevant columns from the sinr data
sinr_timestamps = sinr_df.iloc[:, 0].tolist()
sinr_values = sinr_df.iloc[:, 1].tolist()

# Function to convert string of lists to list of floats for distance data
def convert_to_float_list(string):
    return list(map(float, string.strip('[]').split()))

# Convert the relevant columns to lists for distance data
distance_timestamps = convert_to_float_list(distance_df['vectime'].iloc[0])
distance_values = convert_to_float_list(distance_df['vecvalue'].iloc[0])

# Create dataframes in chunks to handle large data
chunk_size = 10000

def create_dataframe_in_chunks(timestamps, values):
    for start in range(0, len(timestamps), chunk_size):
        end = min(start + chunk_size, len(timestamps))
        yield pd.DataFrame({'timestamp': timestamps[start:end], 'value': values[start:end]})

# Combine the dataframes from chunks
sinr_data = pd.concat(create_dataframe_in_chunks(sinr_timestamps, sinr_values))
distance_data = pd.concat(create_dataframe_in_chunks(distance_timestamps, distance_values))

# Merge the dataframes on the timestamp column
merged_data = pd.merge_asof(sinr_data, distance_data, on='timestamp', suffixes=('_sinr', '_distance'))

# Filter the merged data to include only distances up to 260 meters
filtered_data = merged_data[merged_data['value_distance'] <= 250]

# Define distance intervals (50m each) up to 260m
bins = list(range(0, 261, 15))
filtered_data['distance_bin'] = pd.cut(filtered_data['value_distance'], bins)

# Group by distance intervals and calculate mean, min, and max SINR
grouped_data = filtered_data.groupby('distance_bin').agg({
    'value_sinr': ['mean', 'min', 'max']
}).reset_index()

# Flatten the multi-level columns
grouped_data.columns = ['distance_bin', 'mean_sinr', 'min_sinr', 'max_sinr']

# Calculate error bars
error_bars = [grouped_data['mean_sinr'] - grouped_data['min_sinr'], grouped_data['max_sinr'] - grouped_data['mean_sinr']]

# Plotting the results
plt.figure(figsize=(12, 6))
plt.errorbar(grouped_data['distance_bin'].astype(str), grouped_data['mean_sinr'], yerr=error_bars, fmt='-o', label='UE [0]', capsize=5)
plt.xlabel('Distance Interval (m)', fontsize=18)
plt.ylabel('SINR (dB)', fontsize=18)
plt.legend(fontsize=18)
plt.grid(True)
plt.xticks(rotation=45, fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
plt.show()

