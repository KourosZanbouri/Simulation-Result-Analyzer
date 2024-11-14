def generate_omnet_ini(num_ues, filename="omnet_config_dl.ini"):
    with open(filename, "w") as f:
        # General settings for numUe
#        f.write(f"*.numUe = {num_ues}\n\n")

        # Set the number of apps
        f.write(f"*.tsnDevice1.numApps = {num_ues * 3}\n\n")
        f.write(f"*.tsnDevice1.app[*].typename = UdpSourceApp\n\n")

        # Define apps and traffic settings dynamically
        app_count = 0
        for ue in range(num_ues):
            # For each UE, create 3 apps: network control, video, best effort
            for app_type in ["network control", "video", "best effort"]:
                # Write the display-name and other parameters for each app
                f.write(f"*.tsnDevice1.app[{app_count}].display-name = \"{app_type}\"\n")
                f.write(f"*.tsnDevice1.app[{app_count}].io.destAddress = \"ue[{ue}]\"\n")
                f.write(f"*.tsnDevice1.app[{app_count}].io.destPort = {1000 + app_count % 3}\n")
                f.write(f"*.tsnDevice1.app[{app_count}].source.packetLength = {'498B' if app_type == 'network control' else '1453B' if app_type == 'video' else '1429B'}\n")
                f.write(f"*.tsnDevice1.app[{app_count}].source.productionInterval = {'55ms' if app_type == 'network control' else 'uniform(60ms, 65ms)' if app_type == 'video' else 'exponential(600ms)'}\n")
                f.write("\n")
                
                # Increment app count
                app_count += 1

        print(f"Configuration file '{filename}' generated successfully!")

# Call the function to generate a configuration file for 5 UEs
generate_omnet_ini(10)

