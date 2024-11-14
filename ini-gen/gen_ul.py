def generate_omnet_ini(num_ues, filename="omnet_config_ul.ini"):
    with open(filename, "w") as f:
        # General settings for numUe
        #f.write("*.numUe = ${numUEs=" + str(num_ues) + "}\n\n")


        # Set the number of apps per UE
#        f.write(f"*.tsnDevice1.numApps = 0\n\n")  # No apps in tsnDevice1
        f.write(f"*.ue[*].numApps = 3\n\n\n")  # No apps in tsnDevice1

        # Define apps and traffic settings dynamically for each UE
        for ue in range(num_ues):
            # Each UE will have 3 apps: network control, video, best effort
            for app_index, app_type in enumerate(["network control", "video", "best effort"]):
                # Write the display-name and other parameters for each app in UE
                f.write(f"*.ue[{ue}].app[{app_index}].typename = \"UdpSourceApp\"\n")
                f.write(f"*.ue[{ue}].app[{app_index}].display-name = \"{app_type}\"\n")
                
                # Set destination address and port for tsnDevice1
                f.write(f"*.ue[{ue}].app[{app_index}].io.destAddress = \"tsnDevice1\"\n")
                f.write(f"*.ue[{ue}].app[{app_index}].io.destPort = {1000 + app_index}\n")
                
                # Packet length and production interval based on app type
                f.write(f"*.ue[{ue}].app[{app_index}].source.packetLength = "
                        f"{'498B' if app_type == 'network control' else '1453B' if app_type == 'video' else '1429B'}\n")
                f.write(f"*.ue[{ue}].app[{app_index}].source.productionInterval = "
                        f"{'55ms' if app_type == 'network control' else 'uniform(60ms, 65ms)' if app_type == 'video' else 'exponential(600ms)'}\n")
                f.write("\n")

        print(f"Configuration file '{filename}' generated successfully!")

# Call the function to generate a configuration file for 5 UEs
generate_omnet_ini(50)

