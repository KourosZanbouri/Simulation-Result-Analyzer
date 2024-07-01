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

# Function to process each chunk for a specific UE
def process_chunk(distance_chunk, meanbitlife_chunk, ue):
    # Filter data for the specific UE
    distance_chunk = distance_chunk[distance_chunk['module'].str.contains(f'ue\\[{ue}\\]')]
    meanbitlife_chunk = meanbitlife_chunk[meanbitlife_chunk['module'].str.contains(f'ue\\[{ue}\\]')]
    
    if distance_chunk.empty or meanbitlife_chunk.empty:
        print(f"No data for UE[{ue}] in this chunk.")
        return pd.DataFrame()
    
    # Extract relevant columns
    distance_chunk = distance_chunk[['vectime', 'vecvalue']]
    meanbitlife_chunk = meanbitlife_chunk[['vectime', 'vecvalue']]

    # Apply the function to the relevant columns
    distance_chunk['vectime'] = distance_chunk['vectime'].apply(parse_list_string)
    distance_chunk['vecvalue'] = distance_chunk['vecvalue'].apply(parse_list_string)
    meanbitlife_chunk['vectime'] = meanbitlife_chunk['vectime'].apply(parse_list_string)
    meanbitlife_chunk['vecvalue'] = meanbitlife_chunk['vecvalue'].apply(parse_list_string)

    # Explode the lists into individual rows
    distance_chunk = distance_chunk.explode(['vectime', 'vecvalue'])
    meanbitlife_chunk = meanbitlife_chunk.explode(['vectime', 'vecvalue'])

    # Convert columns to appropriate data types
    distance_chunk['vectime'] = distance_chunk['vectime'].astype(float)
    distance_chunk['vecvalue'] = distance_chunk['vecvalue'].astype(float)
    meanbitlife_chunk['vectime'] = meanbitlife_chunk['vectime'].astype(float)
    meanbitlife_chunk['vecvalue'] = meanbitlife_chunk['vecvalue'].astype(float)

    # Renaming columns for clarity
    distance_chunk.columns = ['timestamp', 'distance']
    meanbitlife_chunk.columns = ['timestamp', 'meanbitlife']

    # Merging dataframes with a tolerance for timestamp differences
    merged_chunk = pd.merge_asof(distance_chunk.sort_values('timestamp'), meanbitlife_chunk.sort_values('timestamp'), on='timestamp', tolerance=0.001, direction='nearest')

    # Remove rows with NaN values in the meanbitlife column
    cleaned_chunk = merged_chunk.dropna(subset=['meanbitlife'])
    
    return cleaned_chunk

# Read and process the data in chunks
chunk_size = 10000
distance_chunks = pd.read_csv('distance.csv', chunksize=chunk_size)
meanbitlife_chunks = pd.read_csv('meanbitlife.csv', chunksize=chunk_size)

cleaned_chunks_ue0 = []
cleaned_chunks_ue1 = []
cleaned_chunks_ue2 = []

for distance_chunk, meanbitlife_chunk in zip(distance_chunks, meanbitlife_chunks):
    cleaned_chunk_ue0 = process_chunk(distance_chunk, meanbitlife_chunk, 0)
    cleaned_chunk_ue1 = process_chunk(distance_chunk, meanbitlife_chunk, 1)
    cleaned_chunk_ue2 = process_chunk(distance_chunk, meanbitlife_chunk, 2)
    
    if not cleaned_chunk_ue0.empty:
        cleaned_chunks_ue0.append(cleaned_chunk_ue0)
    if not cleaned_chunk_ue1.empty:
        cleaned_chunks_ue1.append(cleaned_chunk_ue1)
    if not cleaned_chunk_ue2.empty:
        cleaned_chunks_ue2.append(cleaned_chunk_ue2)

# Combine all processed chunks for each UE
cleaned_df_ue0 = pd.concat(cleaned_chunks_ue0) if cleaned_chunks_ue0 else pd.DataFrame()
cleaned_df_ue1 = pd.concat(cleaned_chunks_ue1) if cleaned_chunks_ue1 else pd.DataFrame()
cleaned_df_ue2 = pd.concat(cleaned_chunks_ue2) if cleaned_chunks_ue2 else pd.DataFrame()

# Debugging: Check the number of rows for each UE
print(f'Number of rows for UE[0]: {len(cleaned_df_ue0)}')
print(f'Number of rows for UE[1]: {len(cleaned_df_ue1)}')
print(f'Number of rows for UE[2]: {len(cleaned_df_ue2)}')

# Function to plot the data for each UE on the same plot
def plot_data(cleaned_df_ue0, cleaned_df_ue1, cleaned_df_ue2):
    plt.figure(figsize=(12, 6))
    
    for ue, cleaned_df in enumerate([cleaned_df_ue0, cleaned_df_ue1, cleaned_df_ue2]):
        if not cleaned_df.empty and not pd.isna(cleaned_df['distance'].max()):
            min_distance = cleaned_df['distance'].min()
            max_distance = cleaned_df['distance'].max()
            print(f"UE[{ue}] - Min Distance: {min_distance}, Max Distance: {max_distance}")
            
            # Group by distance intervals of 50 meters and calculate mean bit life time
            distance_intervals = pd.cut(cleaned_df['distance'], bins=np.arange(min_distance, max_distance + 50, 50))
            mean_bit_lifetime_per_interval = cleaned_df.groupby(distance_intervals)['meanbitlife'].mean()
            
            # Plotting
            plt.plot(mean_bit_lifetime_per_interval.index.astype(str), mean_bit_lifetime_per_interval.values, marker='o', label=f'UE[{ue}]')
        else:
            print(f"No valid data for UE[{ue}] to plot.")
    
    plt.xlabel('Distance (m)')
    plt.ylabel('Mean Bit Lifetime per Packet (End-to-End Latency)')
    plt.title('Mean Bit Lifetime per Packet vs Distance (50m Intervals)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Display the plot
    plt.show()

# Plot data for all UEs on the same plot
plot_data(cleaned_df_ue0, cleaned_df_ue1, cleaned_df_ue2)

