import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the uploaded CSV files
sinr_df = pd.read_csv('sinr.csv')
distance_df = pd.read_csv('distance.csv')

# Function to convert string of lists to list of floats
def convert_to_float_list(string):
    return list(map(float, string.strip('[]').split()))

# Convert the relevant columns to lists
sinr_timestamps = convert_to_float_list(sinr_df['vectime'].iloc[0])
sinr_values = convert_to_float_list(sinr_df['vecvalue'].iloc[0])
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

# Define distance intervals (10m each)
bins = list(range(0, int(max(merged_data['value_distance'])) + 50, 50))
merged_data['distance_bin'] = pd.cut(merged_data['value_distance'], bins)

# Group by distance intervals and calculate mean SINR
grouped_data = merged_data.groupby('distance_bin').agg({
    'value_sinr': 'mean'
}).reset_index()

# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(grouped_data['distance_bin'].astype(str), grouped_data['value_sinr'], marker='o', label='UE [0]')
plt.xlabel('Distance Interval (m)')
plt.ylabel('SINR (dB)')
plt.title('SINR vs Distance')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

