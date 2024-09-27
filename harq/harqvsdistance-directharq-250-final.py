import pandas as pd
import matplotlib.pyplot as plt

# Load the new harqerror data
harqerror_df = pd.read_csv('harqerror.csv', header=None, names=['vectime', 'vecvalue'])
distance_df = pd.read_csv('distance.csv')  # Assuming distance.csv remains unchanged

# Ensure the timestamp columns are numeric
harqerror_df['vectime'] = pd.to_numeric(harqerror_df['vectime'], errors='coerce')
harqerror_df['vecvalue'] = pd.to_numeric(harqerror_df['vecvalue'], errors='coerce')

# Convert the distance data from string format to list of floats
distance_timestamps = pd.to_numeric(distance_df['vectime'].iloc[0].strip('[]').split(), errors='coerce')
distance_values = pd.to_numeric(distance_df['vecvalue'].iloc[0].strip('[]').split(), errors='coerce')

# Remove null values from harqerror data
harqerror_df.dropna(subset=['vectime', 'vecvalue'], inplace=True)

# Create dataframes in chunks to handle large data
chunk_size = 10000

def create_dataframe_in_chunks(timestamps, values):
    for start in range(0, len(timestamps), chunk_size):
        end = min(start + chunk_size, len(timestamps))
        yield pd.DataFrame({'timestamp': timestamps[start:end], 'value': values[start:end]})

# Combine the dataframes from chunks
harqerror_data = pd.concat(create_dataframe_in_chunks(harqerror_df['vectime'], harqerror_df['vecvalue']))
distance_data = pd.concat(create_dataframe_in_chunks(distance_timestamps, distance_values))

# Remove null values from distance data
distance_data.dropna(subset=['timestamp', 'value'], inplace=True)

# Merge the dataframes on the timestamp column
merged_data = pd.merge_asof(harqerror_data, distance_data, on='timestamp', suffixes=('_harq', '_distance'))

# Filter for distances less than 250 meters
merged_data = merged_data[merged_data['value_distance'] < 250]

# Define distance intervals (50m each)
bins = list(range(0, 250 + 10, 10))  # 50m intervals up to 250 meters
merged_data['distance_bin'] = pd.cut(merged_data['value_distance'], bins)

# Group by distance intervals and calculate sum and count of HARQ errors
grouped_data = merged_data.groupby('distance_bin').agg({
    'value_harq': ['sum', 'count']
}).reset_index()

# Calculate the error rate
grouped_data.columns = ['distance_bin', 'error_sum', 'count']
grouped_data['error_rate'] = grouped_data['error_sum'] / grouped_data['count']

# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(grouped_data['distance_bin'].astype(str), grouped_data['error_rate'], marker='o', label='UE [0]')
plt.xlabel('Distance Interval (m)',fontsize=18)
plt.ylabel('HARQ Error Rate', fontsize=18)
plt.grid(True)
plt.legend(fontsize=18)
plt.xticks(rotation=45, fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
plt.show()

