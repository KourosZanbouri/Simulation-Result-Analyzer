import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'sinr.csv'  # Replace with the correct path if running locally
sinr_data = pd.read_csv(file_path)

# Extract SINR values from the second column (assuming the SINR values are in the second column)
sinr_values_corrected = sinr_data.iloc[:, 1].astype(float)

# Create the box plot with 'Profile=InF-SL' on the x-axis and SINR values on the y-axis
plt.figure(figsize=(8, 6))
plt.boxplot(sinr_values_corrected, patch_artist=True)
plt.title('SINR Box Plot with Profile=InF-SL')
plt.ylabel('SINR')
plt.xticks([1], ['Profile=InF-SL'])

# Display the plot
plt.show()

