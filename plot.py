import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the uploaded CSV files
harqerror_df = pd.read_csv('harqerror.csv')
distance_df = pd.read_csv('distance.csv')

# Extracting the relevant columns for analysis
harqerror_values = harqerror_df['vecvalue'].iloc[0].strip('[]').split()
harqerror_values = list(map(float, harqerror_values))

distance_values = distance_df['vecvalue'].iloc[0].strip('[]').split()
distance_values = list(map(float, distance_values))

# Extracting the timestamp values from the datasets
harqerror_timestamps = harqerror_df['vectime'].iloc[0].strip('[]').split()
harqerror_timestamps = list(map(float, harqerror_timestamps))

distance_timestamps = distance_df['vectime'].iloc[0].strip('[]').split()
distance_timestamps = list(map(float, distance_timestamps))

# Combine the timestamps and values into dataframes
harqerror_data = pd.DataFrame({'timestamp': harqerror_timestamps, 'harqerror': harqerror_values})
distance_data = pd.DataFrame({'timestamp': distance_timestamps, 'distance': distance_values})

# Merge the dataframes on the timestamp column
merged_data = pd.merge_asof(harqerror_data, distance_data, on='timestamp')

# Define distance intervals (10m each)
bins = list(range(0, int(max(merged_data['distance'])) + 10, 10))
merged_data['distance_bin'] = pd.cut(merged_data['distance'], bins)

# Group by distance intervals and calculate sum and count of HARQ errors
grouped_data = merged_data.groupby('distance_bin').agg({
    'harqerror': ['sum', 'count']
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

