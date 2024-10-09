import os
import pandas as pd
import matplotlib.pyplot as plt

# Function to remove outliers using the IQR method
def remove_outliers_iqr(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data >= lower_bound) & (data <= upper_bound)]
    
    
# Define folder names for each profile-distance combination
profiles = ['InF-SL', 'InF-DL', 'InF-SH', 'InF-DH']
distances = ['d1', 'd2', 'd3']
streams = ['NC', 'Video', 'BE']

# Dictionary to map folder indices to profile-distance combinations
folder_map = {
    1: ('InF-SL', 'd1'), 2: ('InF-SL', 'd2'), 3: ('InF-SL', 'd3'),
    4: ('InF-DL', 'd1'), 5: ('InF-DL', 'd2'), 6: ('InF-DL', 'd3'),
    7: ('InF-SH', 'd1'), 8: ('InF-SH', 'd2'), 9: ('InF-SH', 'd3'),
    10: ('InF-DH', 'd1'), 11: ('InF-DH', 'd2'), 12: ('InF-DH', 'd3')
}

# Initialize a list to store the data
combined_data = []

# Loop through folder indices to load data
for folder_index in range(1, 13):
    profile, distance = folder_map[folder_index]

    # Load the CSV data from the folder (adjust the file path accordingly)
    file_path = f'/home/kouros/Desktop/Simulation result/5G-TSN Paper/BoxPlot/E2E-Distance/{folder_index}/e2e.csv'
    
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, skiprows=1)  # Skip first row if necessary
        cleaned_data = remove_outliers_iqr(data)
        
        # Extract the columns for Network Control (2nd), Video (4th), and Best Effort (6th)
        network_control = cleaned_data.iloc[:, 1]
        video = cleaned_data.iloc[:, 3]
        best_effort = cleaned_data.iloc[:, 5]

        # Append data with relevant labels
        for value in network_control:
            combined_data.append([value, profile, distance, 'NC'])
        for value in video:
            combined_data.append([value, profile, distance, 'Video'])
        for value in best_effort:
            combined_data.append([value, profile, distance, 'BE'])
    else:
        print(f"File not found: {file_path}")


# Convert the combined data into a DataFrame
df_combined = pd.DataFrame(combined_data, columns=['Value', 'Profile', 'Distance', 'Stream'])

# Create a new column combining Profile, Distance, and Stream for the X-axis labels
df_combined['Profile-Distance-Stream'] = df_combined['Profile'] + '-' + df_combined['Distance'] + '-' + df_combined['Stream']

# Define the correct order for the X-axis based on the desired pattern
profile_distance_stream_order = [
    f'{profile}-{distance}-{stream}' for profile in profiles for distance in distances for stream in streams
]

# Convert 'Profile-Distance-Stream' to categorical and enforce the order
df_combined['Profile-Distance-Stream'] = pd.Categorical(df_combined['Profile-Distance-Stream'], categories=profile_distance_stream_order, ordered=True)

# Plotting the boxplot with colors and legend
plt.figure(figsize=(14, 8))

# Customizing the colors for each stream
colors = {'NC': 'lightblue', 'Video': 'lightgreen', 'BE': 'lightcoral'}

# Create the boxplot using matplotlib directly
ax = df_combined.boxplot(column='Value', by='Profile-Distance-Stream', grid=False, showmeans=True, showfliers=False, patch_artist=True, figsize=(14,8))

# Iterate through the boxes and assign colors based on the stream type
for i, box in enumerate(ax.patches):  # Accessing boxes via 'patches'
    stream_type = profile_distance_stream_order[i].split('-')[-1]  # Extract stream type
    box.set_facecolor(colors[stream_type])  # Assign color based on the stream type

# Adding legend for the colors
handles = [plt.Rectangle((0, 0), 1, 1, color=colors[stream]) for stream in streams]
plt.legend(handles, streams)

# Labels and adjustments
plt.suptitle('')  # Remove the automatic title created by pandas boxplot
plt.title('')
plt.xlabel('Profile-Distance-Stream', fontsize=18)
plt.ylabel('End-to-End Delay (s)', fontsize=18)
plt.xticks(rotation=90, fontsize=18)  # Rotate x-axis labels for better readability
plt.yticks(fontsize=18)
plt.tight_layout()
plt.grid(True)

# Display the plot
plt.show()

