import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# List of folder names and profiles
folders = ['1', '2', '3', '4', '5', '6', '7']
profiles = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5', 'TC6', 'T7']

# Function to load data from a given folder and profile
def load_profile_data(folder, profile):
    file_path = os.path.join(folder, 'meanbitlife.csv')  # Assuming the file name is the same in each folder
    data = pd.read_csv(file_path)
    
    # Clean the string values in 'vecvalue' to be valid lists
    network_control_values_clean = np.fromstring(data.loc[1, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
    video_values_clean = np.fromstring(data.loc[2, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
    best_effort_values_clean = np.fromstring(data.loc[0, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
    
    return network_control_values_clean, video_values_clean, best_effort_values_clean

# Store all values and labels for the boxplot
all_values = []
all_labels = []

# Iterate over each folder and profile, and collect the data
for folder, profile in zip(folders, profiles):
    network_control_values, video_values, best_effort_values = load_profile_data(folder, profile)
    
    # Append the values and labels
    all_values.append(network_control_values)
    all_values.append(video_values)
    all_values.append(best_effort_values)
    
    # Append corresponding labels for the boxplot
    all_labels.append(f'{profile} (Network Control)')
    all_labels.append(f'{profile} (Video)')
    all_labels.append(f'{profile} (Best Effort)')

# Create a boxplot for the combined values
plt.figure(figsize=(12, 8))
plt.boxplot(all_values, labels=all_labels, showmeans=True, whis=1.5, showfliers=False)

# Set the title and labels
plt.title('Box Plot of Streams for Different Profiles')
plt.ylabel('Value')
plt.xticks(rotation=45, ha="right")

# Show the plot
plt.tight_layout()
plt.show()

