import pandas as pd
import matplotlib.pyplot as plt
import os

# Define profiles and distances
profiles = ['InF-SL', 'InF-DL', 'InF-SH', 'InF-DH']
distances = ['d1', 'd2', 'd3']

# Initialize lists to hold SINR values and labels for the x-axis
sinr_values_all = []
labels = []

# Loop through the folder structure (1 to 12) and process each .csv file
folder_base_path = ''  # Replace with the correct base path

# Define custom colors for each profile
colors = {
    'InF-SL': '#FF9999',  # Light red
    'InF-DL': '#99CCFF',  # Light blue
    'InF-SH': '#99FF99',  # Light green
    'InF-DH': '#FFCC99'   # Light orange
}

for i, profile in enumerate(profiles):
    for j, distance in enumerate(distances):
        folder_number = i * 3 + j + 1  # Folder number calculation (1 to 12)
        folder_path = os.path.join(folder_base_path, str(folder_number))
        file_path = os.path.join(folder_path, 'sinr.csv')  # Assuming the file name is the same in each folder
        
        # Read the CSV file from the folder
        try:
            sinr_data = pd.read_csv(file_path)
            
            # Extract SINR values from the second column
            sinr_values = sinr_data.iloc[:, 1].astype(float)
            
            # Add the SINR values to the list
            sinr_values_all.append(sinr_values)
            
            # Create a label for the x-axis based on the profile and distance
            labels.append(f'{profile} {distance}')
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

# Create a box plot with 12 data points (one for each profile and distance)
plt.figure(figsize=(12, 8))
box = plt.boxplot(sinr_values_all, patch_artist=True, showmeans=True, showfliers=False)

# Apply custom colors for each profile
for patch, label in zip(box['boxes'], labels):
    profile = label.split()[0]  # Extract profile name from the label
    patch.set_facecolor(colors.get(profile, '#FFFFFF'))  # Default to white if color not found
    
# Add legend based on profile colors
legend_labels = colors.keys()
legend_colors = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in legend_labels]
plt.legend(legend_colors, legend_labels, fontsize=16)    

plt.ylabel('SINR', fontsize=18)
plt.xticks(range(1, 13), labels, rotation=45, fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()
plt.grid()
# Display the plot
plt.show()

