import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# List of folder names and profiles
folders = ['1', '2', '3', '4', '5', '6', '7']
profiles = ['TC1', 'TC2', 'TC3', 'TC4', 'TC5', 'TC6', 'TC7']

# Function to remove outliers using the IQR method
def remove_outliers(values):
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return values[(values >= lower_bound) & (values <= upper_bound)]

# Function to load data from a given folder and profile
def load_profile_data(folder, profile):
    file_path = os.path.join(folder, 'meanbitlife.csv')  # Assuming the file name is the same in each folder
    data = pd.read_csv(file_path)
    
    # Clean the string values in 'vecvalue' to be valid lists
    network_control_values_clean = np.fromstring(data.loc[1, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
    video_values_clean = np.fromstring(data.loc[2, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
    best_effort_values_clean = np.fromstring(data.loc[0, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
    
    # Remove outliers from the values
    network_control_values_clean = remove_outliers(network_control_values_clean)
    video_values_clean = remove_outliers(video_values_clean)
    best_effort_values_clean = remove_outliers(best_effort_values_clean)
    
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
    all_labels.append(f'{profile} (NC)')
    all_labels.append(f'{profile} (Video)')
    all_labels.append(f'{profile} (BE)')

# Create a boxplot for the combined values
plt.figure(figsize=(12, 8))

# Create the boxplot and capture the returned object
boxplot = plt.boxplot(all_values, labels=all_labels, patch_artist=True, showmeans=True, whis=1.5, showfliers=False)

# Define colors for each stream type
colors = ['skyblue', 'lightgreen', 'lightcoral']  # Example colors for Network Control, Video, Best Effort

# Color the boxes manually for each stream type
for i, box in enumerate(boxplot['boxes']):
    # Color each stream group based on its index (Network Control, Video, Best Effort)
    box.set_facecolor(colors[i % 3])

# Add a legend for the streams
legend_elements = [
    plt.Line2D([0], [0], color='skyblue', lw=4, label='NC'),
    plt.Line2D([0], [0], color='lightgreen', lw=4, label='Video'),
    plt.Line2D([0], [0], color='lightcoral', lw=4, label='BE')
]
plt.legend(handles=legend_elements, loc='upper left')

# Set the title and labels
plt.ylabel('End-to-End Delay (s)', fontsize=18)
plt.xticks(rotation=45, ha="right", fontsize=14)
plt.yticks(fontsize=14)

# Show the plot
plt.tight_layout()
plt.grid(True)
plt.show()

