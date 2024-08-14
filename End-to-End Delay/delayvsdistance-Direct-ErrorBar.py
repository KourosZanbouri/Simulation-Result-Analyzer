import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to parse the list strings directly with filtering for empty values
def parse_list_string(list_string):
    if isinstance(list_string, str):
        list_string = list_string.strip('[]')
        list_string = list_string.replace(' ', ',')
        return [float(x) for x in list_string.split(',') if x]
    return list_string

# Function to process each chunk
def process_chunk(distance_chunk, meanbitlife_chunk):
    # Extract relevant columns
    distance_chunk = distance_chunk[['vectime', 'vecvalue']]
    meanbitlife_chunk.columns = ['vectime', 'vecvalue']

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

cleaned_chunks = []
for distance_chunk, meanbitlife_chunk in zip(distance_chunks, meanbitlife_chunks):
    cleaned_chunk = process_chunk(distance_chunk, meanbitlife_chunk)
    cleaned_chunks.append(cleaned_chunk)

# Combine all processed chunks
cleaned_df = pd.concat(cleaned_chunks)

# Debug: Check the range of distances
print("Distance range:", cleaned_df['distance'].min(), cleaned_df['distance'].max())

# Multiply meanbitlife by 1,000,000 to convert to microseconds (μs)
cleaned_df['meanbitlife'] *= 1000000

# Determine the min and max distances for the plot range
min_distance = cleaned_df['distance'].min()
max_distance = cleaned_df['distance'].max()

# Debug: Verify the min and max distances
print("Min distance:", min_distance)
print("Max distance:", max_distance)

# Group by distance intervals of 20 meters and calculate mean, min, and max bit life time
distance_intervals = pd.cut(cleaned_df['distance'], bins=np.arange(min_distance, max_distance + 20, 20))
mean_bit_lifetime_per_interval = cleaned_df.groupby(distance_intervals)['meanbitlife'].mean()
min_bit_lifetime_per_interval = cleaned_df.groupby(distance_intervals)['meanbitlife'].min()
max_bit_lifetime_per_interval = cleaned_df.groupby(distance_intervals)['meanbitlife'].max()

# Plotting with error bars
plt.figure(figsize=(12, 6))
plt.errorbar(mean_bit_lifetime_per_interval.index.astype(str), 
             mean_bit_lifetime_per_interval.values, 
             yerr=[mean_bit_lifetime_per_interval.values - min_bit_lifetime_per_interval.values,
                   max_bit_lifetime_per_interval.values - mean_bit_lifetime_per_interval.values],
             fmt='-o', capsize=5, label='UE[0]')
plt.xlabel('Distance (m)')
plt.ylabel('Mean Bit Lifetime per Packet (End-to-End Latency) (μs)')
plt.title('Mean Bit Lifetime per Packet vs Distance (20m Intervals)')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()

# Display the plot
plt.show()

