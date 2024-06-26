import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the uploaded CSV files
harqerror_df = pd.read_csv('harqerror.csv')
distance_df = pd.read_csv('distance.csv')

# Function to convert string of lists to list of floats
def convert_to_float_list(string):
    return list(map(float, string.strip('[]').split()))

# Convert the relevant columns to lists
harqerror_timestamps = convert_to_float_list(harqerror_df['vectime'].iloc[0])
harqerror_values = convert_to_float_list(harqerror_df['vecvalue'].iloc[0])
distance_timestamps = convert_to_float_list(distance_df['vectime'].iloc[0])
distance_values = convert_to_float_list(distance_df['vecvalue'].iloc[0])

# Create dataframes in chunks to handle large data
chunk_size = 10000

def create_dataframe_in_chunks(timestamps, values):
    for start in range(0, len(timestamps), chunk_size):
        end = min(start + chunk_size, len(timestamps))
        yield pd.DataFrame({'timestamp': timestamps[start:end], 'value': values[start:end]})

# Combine the dataframes from chunks
harqerror_data = pd.concat(create_dataframe_in_chunks(harqerror_timestamps, harqerror_values))
distance_data = pd.concat(create_dataframe_in_chunks(distance_timestamps, distance_values))

# Merge the dataframes on the timestamp column
merged_data = pd.merge_asof(harqerror_data, distance_data, on='timestamp', suffixes=('_harq', '_distance'))

# Define distance intervals (10m each)
bins = list(range(0, int(max(merged_data['value_distance'])) + 20, 20))
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
plt.plot(grouped_data['distance_bin'].astype(str), grouped_data['error_rate'], marker='o')
plt.xlabel('Distance Interval (m)')
plt.ylabel('HARQ Error Rate')
plt.title('HARQ Error Rate vs Distance')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Verify the calculation for the interval (400-410]
specific_interval_data = merged_data[(merged_data['value_distance'] > 400) & (merged_data['value_distance'] <= 410)]
error_sum = specific_interval_data['value_harq'].sum()
count = specific_interval_data['value_harq'].count()
error_rate = error_sum / count

error_sum, count, error_rate
