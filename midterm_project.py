import requests
import json
import html
import pandas as pd
import re
import numpy as np
from datetime import datetime

# Get earthquake data
url_1 = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_month.geojson"
url_2 = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson"
url_3 = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"

# Turn all data into dataframes
data_25 = requests.get(url_1)
json_data25 = data_25.json()
df_1 = pd.json_normalize(json_data25["features"])

# Second dataframe
data_45 = requests.get(url_2)
json_data45 = data_45.json()
df_2 = pd.json_normalize(json_data45["features"])

# Third dataframe
data_sig = requests.get(url_3)
json_data_sig = data_sig.json()
df_3 = pd.json_normalize(json_data_sig["features"])

# Now, it is time to combine all three dataframes into one
mega_frame = pd.concat([df_1, df_2, df_3], ignore_index = True, sort = False)
mega_frame.drop_duplicates(subset = ["id"]) # Drop duplicates

# Extract the geography information column. The numbers are between brackets and
# must be extracted
pattern = "-?\d+(?:\.\d+)?"
location_data = mega_frame["geometry.coordinates"]
longitude_ls = []
latitude_ls = []
depth_ls = []

# Iterate over the geography information and extract longitude/latitude/depth
for coord in location_data:
	listToStr = ' '.join(map(str, coord))
	extracted_values = re.findall(pattern, listToStr)
	longitude_ls.append(extracted_values[0])
	latitude_ls.append(extracted_values[1])
	depth_ls.append(extracted_values[2])

# In addition to reformatting the geography information, the times need to be converted to 
# a date and time. The current format measures milliseconds after epoch
# https://stackoverflow.com/questions/34883101/pandas-converting-row-with-unix-timestamp-in-milliseconds-to-datetime
time_ls = pd.to_datetime(mega_frame["properties.time"], unit = 'ms')
time_ls.dt.strftime("%Y-%m-%d %H:%M:%S.%f")

date = []
time = []

# Loop over the dataframe to extract the date and time 
for day in time_ls:
	date_str = str(day)
	date.append(date_str[0:10])
	time.append(date_str[11:])

# Now that the data has been cleaned and the columns are extracted (that will be used for analysis),
# it's time to put it all together into a final dataframe
final_df = pd.DataFrame() 
final_df["ID"] = mega_frame["id"]
final_df["Date"] = date
final_df["Time"] = time
final_df["Latitude"] = latitude_ls
final_df["Longitude"] = longitude_ls
final_df["Magnitude"] = mega_frame["properties.mag"]
final_df['Magnitude Quartile'] = pd.qcut(final_df['Magnitude'], 4, labels = False)
final_df["Intensity"] = mega_frame["properties.mmi"]
final_df["Depth"] = depth_ls

final_df.to_csv('final_df.csv')

