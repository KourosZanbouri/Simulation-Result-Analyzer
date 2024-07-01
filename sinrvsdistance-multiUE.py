import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the uploaded CSV files
sinr_df = pd.read_csv('/mnt/data/sinr.csv')
distance_df = pd.read_csv('/mnt/data/distance.csv')

# Function to convert string of lists to list of floats
def convert_to_float_list(string):
    return list(map(float, string.strip('[]').split()))

# Initialize lists to store data for each UE
ue_sinr_data = []
ue_distance_data = []

# Extract data for each UE
for i in range(len(sinr_df)):
    sinr_timestamps = convert_to_float_list(sinr_df['vectime'].iloc[i])
    sinr_values = convert_to_float_list(sinr_df['vecvalue'].iloc[i])
    distance_timestamps = convert_to_float_list(distance_df['vectime'].iloc[i])
    distance_values = convert_to_float_list(distance_df['vecvalue'].iloc[i])
    
    # Create dataframes in chunks to handle large data
    sinr_data = pd.concat(create_dataframe_in_chunks(sinr_timestamps, sinr_values))
    distance_data = pd.concat(create_dataframe_in_chunks(distance_timestamps, distance_values))
    
    # Merge the dataframes on the timestamp column
    merged_data = pd.merge_asof(sinr_data, distance_data, on='timestamp', suffixes=('_sinr', '_distance'))
    
    # Store merged data for each UE
    ue_sinr_data.append(merged_data[['timestamp', 'value_sinr']])
    ue_distance_data.append(merged_data[['timestamp', 'value_distance']])

# Define distance intervals (10m each)
bins = list(range(0, int(max(distance_df['vecvalue'].apply(lambda x: max(convert_to_float_list(x))))) + 100, 100))

# Define markers and colors for each UE
markers = ['o', 's', '^', 'D', 'v', '*', 'P', 'X']
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange']

plt.figure(figsize=(12, 6))

# Plot data for each UE
for i, (sinr_data, distance_data) in enumerate(zip(ue_sinr_data, ue_distance_data)):
    sinr_data['distance_bin'] = pd.cut(distance_data['value_distance'], bins)
    grouped_data = sinr_data.groupby('distance_bin').agg({
        'value_sinr': 'mean'
    }).reset_index()
    
    plt.plot(grouped_data['distance_bin'].astype(str), grouped_data['value_sinr'], marker=markers[i % len(markers)], color=colors[i % len(colors)], label=f'UE [{i}]')

plt.xlabel('Distance Interval (m)')
plt.ylabel('SINR')
plt.title('SINR vs Distance')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

