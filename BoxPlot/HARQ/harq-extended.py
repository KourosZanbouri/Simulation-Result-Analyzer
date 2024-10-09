import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the profiles, distances, colors, and patterns
profiles = ['InF-SL', 'InF-DL', 'InF-SH', 'InF-DH']
distances = ['d1', 'd2', 'd3']
profile_colors = {
    'InF-SL': '#FF9999',
    'InF-DL': '#99CCFF',
    'InF-SH': '#99FF99',
    'InF-DH': '#FFCC99'
}
distance_patterns = {
    'd1': '/',
    'd2': '\\',
    'd3': 'x'
}

# Create a mapping of folder numbers to profile-distance combinations
folder_mapping = {
    1: ('InF-SL', 'd1'),
    2: ('InF-SL', 'd2'),
    3: ('InF-SL', 'd3'),
    4: ('InF-DL', 'd1'),
    5: ('InF-DL', 'd2'),
    6: ('InF-DL', 'd3'),
    7: ('InF-SH', 'd1'),
    8: ('InF-SH', 'd2'),
    9: ('InF-SH', 'd3'),
    10: ('InF-DH', 'd1'),
    11: ('InF-DH', 'd2'),
    12: ('InF-DH', 'd3')
}

# Dictionary to store HARQ error rates
harq_error_rates = {}

# Loop through each folder
for folder_num, (profile, distance) in folder_mapping.items():
    # Construct the file path
    folder_path = f'{folder_num}/harq.csv'  # Replace with your actual path
    if os.path.exists(folder_path):
        # Read the CSV file
        harq_data = pd.read_csv(folder_path)
        
        # Clean and process the data as done previously
        harq_data_cleaned = harq_data.rename(columns={harq_data.columns[0]: 'Time', harq_data.columns[1]: 'State'})
        harq_data_cleaned = harq_data_cleaned.dropna()
        harq_data_cleaned['State'] = pd.to_numeric(harq_data_cleaned['State'], errors='coerce')

        # Calculate total transmissions and failed transmissions
        total_transmissions = len(harq_data_cleaned)
        failed_transmissions = harq_data_cleaned['State'].sum()

        # Calculate the HARQ error rate
        harq_error_rate = failed_transmissions / total_transmissions

        # Store the error rate in the dictionary
        harq_error_rates[(profile, distance)] = harq_error_rate

# Create a plot to visualize the error rates
plt.figure(figsize=(10, 6))
labels = [f'{profile}_{distance}' for profile, distance in harq_error_rates.keys()]
values = list(harq_error_rates.values())
colors = [profile_colors[profile] for profile, distance in harq_error_rates.keys()]
patterns = [distance_patterns[distance] for profile, distance in harq_error_rates.keys()]

bars = plt.bar(labels, values, color=colors)

# Apply different patterns to each bar based on the distance
for bar, pattern in zip(bars, patterns):
    bar.set_hatch(pattern)

# Add legend based on profile colors
legend_labels = profile_colors.keys()
legend_colors = [plt.Rectangle((0,0),1,1, color=profile_colors[label]) for label in legend_labels]
plt.legend(legend_colors, legend_labels, fontsize=16)

# Labeling the axes
plt.xlabel('Profile and Distance', fontsize=18)
plt.ylabel('HARQ Error Rate', fontsize=18)

# Rotate the x-axis labels for better readability
plt.xticks(rotation=90, ha='right', fontsize=18)
plt.yticks(fontsize=18)

# Add a grid
plt.grid()
plt.tight_layout()
# Display the plot
plt.show()

