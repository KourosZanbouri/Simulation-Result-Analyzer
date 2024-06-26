#### Dropped Error Rate with Distance, Huge Data, 3 UE

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Helper function to process data in chunks
def process_data_in_chunks(distance_file, dropped_file, chunk_size=10000):
    ue_data = {0: {'distance': [], 'dropped': []},
               1: {'distance': [], 'dropped': []},
               2: {'distance': [], 'dropped': []}}
    
    # Process distance data in chunks
    for chunk in pd.read_csv(distance_file, chunksize=chunk_size):
        for ue_id in range(3):
            ue_distance = chunk.loc[chunk['module'] == f'MainTest.ue[{ue_id}].cellularNic.nrChannelModel[0]', 'vecvalue']
            if not ue_distance.empty:
                ue_data[ue_id]['distance'].extend(np.fromstring(ue_distance.values[0].strip('[]'), sep=' '))
    
    # Process dropped data rate in chunks
    for chunk in pd.read_csv(dropped_file, chunksize=chunk_size):
        for ue_id in range(3):
            ue_dropped = chunk.loc[chunk['module'] == f'MainTest.ue[{ue_id}].app[{ue_id}].sink', 'vecvalue']
            if not ue_dropped.empty:
                ue_data[ue_id]['dropped'].extend(np.fromstring(ue_dropped.values[0].strip('[]'), sep=' '))

    # Convert lists to numpy arrays
    for ue_id in range(3):
        ue_data[ue_id]['distance'] = np.array(ue_data[ue_id]['distance'])
        ue_data[ue_id]['dropped'] = np.array(ue_data[ue_id]['dropped'])
    
    return ue_data

# Function to interpolate data
def interpolate_data(distance_series, dropped_series):
    if len(dropped_series) == len(distance_series):
        return dropped_series
    
    x_old = np.linspace(0, 1, len(dropped_series))
    x_new = np.linspace(0, 1, len(distance_series))
    interpolator = interp1d(x_old, dropped_series, kind='linear', fill_value="extrapolate")
    return interpolator(x_new)

# Function to aggregate data into bins
def aggregate_data(ue_data, bins):
    aggregated_data = {ue_id: np.zeros(len(bins)-1) for ue_id in range(3)}
    
    for ue_id in range(3):
        distance_series = ue_data[ue_id]['distance']
        dropped_series = interpolate_data(distance_series, ue_data[ue_id]['dropped'])
        
        bin_indices = np.digitize(distance_series, bins) - 1
        for i in range(len(bins) - 1):
            aggregated_data[ue_id][i] = np.sum(dropped_series[bin_indices == i])
    
    return aggregated_data

# Define the distance bins
bins = np.arange(0, 500, 0.5)  # Adjust the upper limit as needed

# Process the data in chunks
distance_file = 'distance.csv'
dropped_file = 'droppeddatarate.csv'
ue_data = process_data_in_chunks(distance_file, dropped_file)

# Aggregate the data
aggregated_data = aggregate_data(ue_data, bins)

# Plot the aggregated data
plt.figure(figsize=(10, 6))

for ue_id in range(3):
    plt.plot(bins[:-1] + 0.25, aggregated_data[ue_id], label=f'UE[{ue_id}]')

plt.xlabel('Distance (m)')
plt.ylabel('Dropped Data Rate')
plt.title('Dropped Data Rate vs. Distance')
plt.legend()
plt.grid(True)
plt.show()

