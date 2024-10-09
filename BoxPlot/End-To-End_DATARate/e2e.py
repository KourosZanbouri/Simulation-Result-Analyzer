import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'meanbitlife.csv'  # Update this path as needed
data = pd.read_csv(file_path)

# Clean the string values in 'vecvalue' to be valid lists
network_control_values_clean = np.fromstring(data.loc[1, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
video_values_clean = np.fromstring(data.loc[2, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')
best_effort_values_clean = np.fromstring(data.loc[0, 'vecvalue'].replace('[', '').replace(']', ''), sep=' ')

# Define labels for the streams
labels = ['InF-SL (Network Control)', 'InF-SL (Video)', 'InF-SL (Best Effort)']

# Create a boxplot for the cleaned values
values_clean = [network_control_values_clean, video_values_clean, best_effort_values_clean]

# Plot the cleaned values
plt.figure(figsize=(8, 6))
plt.boxplot(values_clean, labels=labels, showmeans=True, whis=[0, 100])

# Set the title and labels
plt.title('Box Plot of Streams with InF-SL Profile')
plt.ylabel('Value')
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()

