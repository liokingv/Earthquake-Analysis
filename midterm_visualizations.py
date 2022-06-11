import pandas as pd
import matplotlib.pyplot as plt
import folium
import numpy as np
import seaborn as sns
from sklearn import linear_model
from scipy import stats
import statsmodels.api as sm


# Question 1 visualization (map)
# I did a step by step tutorial from these pages:
# https://towardsdatascience.com/data-visualization-with-python-folium-maps-a74231de9ef7
# https://levelup.gitconnected.com/plotting-usgs-earthquake-data-with-folium-8f11ddc21950

# Load the cleaned up dataframe
earthquake_df = pd.read_csv ('final_df.csv')
#earthquake_df.info()

# Create blank map 
world_map = folium.Map(location = (0, 0), zoom_start = 2.1)

# Create a color dictionary for severity of earthquake magnitude 
colordict = {0: 'green', 1: 'yellow', 2: 'orange', 3: 'red'}
earthquake_df['Magnitude Quartile'] = pd.qcut(earthquake_df['Magnitude'], 4, labels = False) # quartiles of magnitude

# Title
title_map = 'Incidence of Seismic Events Over the Past 30 Days (1/13 - 2/11)'
title_html = '''
             <h3 align="center" style="font-size:16px"><b>{}</b></h3>
             '''.format(title_map)   

world_map.get_root().html.add_child(folium.Element(title_html))

# We iterate through the dataframe and plot the locations on the map
for i in range(len(earthquake_df)):
    folium.Circle(
        location = [earthquake_df.iloc[i]['Latitude'], earthquake_df.iloc[i]['Longitude']],
        radius = 60000,
        color = 'b',
        key_on = earthquake_df.iloc[i]['Magnitude Quartile'],
        threshold_scale = [0, 1, 2, 3],
        fill_color = colordict[earthquake_df.iloc[i]['Magnitude Quartile']],
        fill = True,
        fill_opacity = 0.7,
        zoom_control = False,
        scrollWheelZoom = False,
        dragging = False

    ).add_to(world_map)        

# Adding the tectonic plates over the map
url = 'https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_boundaries.json'

folium.GeoJson(
    url,
    name = 'geojson'
).add_to(world_map)

folium.LayerControl().add_to(world_map)

# Save to file
world_map.save('earthquakes.html')

# Question 2 visualization of the multilinear regression model
# Prepare the dataframe with only the variables that'll be used
# https://stackoverflow.com/questions/29314033/drop-rows-containing-empty-cells-from-a-pandas-dataframe
multi_df = earthquake_df[['Magnitude', 'Intensity', 'Depth']]
multi_df['Intensity'].replace('', np.nan, inplace = True)
multi_df = multi_df.dropna(subset=['Intensity'])
#print(multi_df)

# Visualize the data using scatter plot and histogram pairplots
sns.set_palette('colorblind')
pair_plots = sns.pairplot(data = multi_df, height = 2)
plt.subplots_adjust(top = 0.9)
plt.suptitle('Matrix Plots of Earthquake Magnitude, Intensity and Depth', fontsize = 10)
pair_plots.savefig('pair_plots.png', dpi = 200)

# Set independent and dependent variables
X = multi_df[['Intensity', 'Depth']]
y = multi_df['Magnitude']

# Initialize model and fit it to data
regr = linear_model.LinearRegression()
model = regr.fit(X, y)

# Set independent and dependent variables
X = multi_df[['Intensity', 'Depth']]
y = multi_df['Magnitude']

# Initialize model and fit it to data
regr = linear_model.LinearRegression()
model = regr.fit(X, y)


# y-hat = 4.401 + 0.125*X_1 + 0.003*X_2
print('Intercept:', model.intercept_)
print('Coefficients:', model.coef_)

# Validation of Model
#X = multi_df[['Intensity', 'Depth']]
X = sm.add_constant(X) # adding a constant
olsmod = sm.OLS(y, X).fit()
print(olsmod.summary())
print('R2 score:', olsmod.rsquared)
print(olsmod.pvalues)


# Question 3: Frequency of seismic occurrence
# Plotting hours and frequency of seismic events
sort_time = earthquake_df['Time']
times = []
bins_sort = np.arange(0, 24, 1)

# Extracting the hour 
for elem in sort_time:
    hour = int(elem[0:2])
    times.append(hour)

# Sorting times for histogram
times.sort()

# plotting times
plt.hist(times, bins = bins_sort, align='mid')
plt.xticks(np.arange(0, 24, 1))
plt.title("Number of Seismic Events by Hour")
plt.xlabel("Hour (UTC)")
plt.ylabel("Seismic Events")
plt.savefig('hoursplt.png')
plt.close()

# Plotting the past 30 days and seismic events
days = []
for elem in earthquake_df['Date']:  
    days.append(int(elem[-2:]))

# plotting times
plt.hist(days, bins = 30, align='mid')
plt.xticks(np.arange(0, 31, 2))
plt.title("Frequency of Seismic Events Over the Past Thirty Days (1/13 - 2/11)")
plt.xlabel("Day")
plt.ylabel("Seismic Events")
plt.savefig('times1.png')
plt.close()

    






