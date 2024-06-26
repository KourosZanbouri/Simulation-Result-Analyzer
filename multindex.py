import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the uploaded CSV files
packetdrop_df = pd.read_csv('packetdrop-multi.csv')
distance_df = pd.read_csv('distance-multi.csv')

# Function to convert string of lists to list of floats
def convert_to_float_list(string):
    return list(map(float, string.strip('[]').split(',')))

# Helper function to create dataframes in chunks to handle large data
chunk_size = 10000

def create_dataframe_in_chunks(timestamps, values):
    for start in range(0, len(timestamps), chunk_size):
        end = min(start + chunk_size, len(timestamps))
        yield pd.DataFrame({'timestamp': timestamps[start:end], 'value': values[start:end]})

# Process data for each UE
UEs = ['ue[0]', 'ue[1]', 'ue[2]']
ue_data = {}

for ue in UEs:
    # Filter packet drop data for the specific UE
    ue_packetdrop_df = packetdrop_df[packetdrop_df['module'].str.contains(ue)]
    ue_distance_df = distance_df[distance_df['module'].str.contains(ue)]
    
    if not ue_packetdrop_df.empty and not ue_distance_df.empty:
        # Convert the relevant columns to lists
        packetdrop_timestamps = convert_to_float_list(ue_packetdrop_df['vectime'].iloc[0])
        packetdrop_values = convert_to_float_list(ue_packetdrop_df['vecvalue'].iloc[0])
        distance_timestamps = convert_to_float_list(ue_distance_df['vectime'].iloc[0])
        distance_values = convert_to_float_list(ue_distance_df['vecvalue'].iloc[0])

        # Create dataframes from chunks
        packetdrop_data = pd.concat(create_dataframe_in_chunks(packetdrop_timestamps, packetdrop_values))
        distance_data = pd.concat(create_dataframe_in_chunks(distance_timestamps, distance_values))
        
        # Merge the dataframes on the timestamp column
        merged_data = pd.merge_asof(packetdrop_data, distance_data, on='timestamp', suffixes=('_packetdrop', '_distance'))
        
        # Define distance intervals (10m each)
        bins = list(range(0, int(max(merged_data['value_distance'])) + 1, 1))
        merged_data['distance_bin'] = pd.cut(merged_data['value_distance'], bins)
        
        # Group by distance intervals and calculate sum and count of packet drops
        grouped_data = merged_data.groupby('distance_bin').agg({
            'value_packetdrop': ['sum', 'count']
        }).reset_index()
        
        # Calculate the drop rate
        grouped_data.columns = ['distance_bin', 'drop_sum', 'count']
        grouped_data['drop_rate'] = grouped_data['drop_sum'] / grouped_data['count']
        
        # Store the processed data for plotting
        ue_data[ue] = grouped_data

# Plotting the results for all UEs
plt.figure(figsize=(12, 6))

for ue, data in ue_data.items():
    plt.plot(data['distance_bin'].astype(str), data['drop_rate'], marker='o', label=ue)

plt.xlabel('Distance Interval (m)')
plt.ylabel('Packet Drop Rate')
plt.title('Packet Drop Rate vs Distance for Multiple UEs')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

