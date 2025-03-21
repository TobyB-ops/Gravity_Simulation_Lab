import csv, pandas as pd, numpy as np, matplotlib.pyplot as plt
data = pd.read_csv('Radii_HERMITE.csv')



earth_plt = data[data['Body']=='Earth']

#plt.errorbar(earth_plt['Time']/86400,earth_plt['Position']/1.496e+11)
#plt.xlabel = ('Time/Days')
#plt.ylabel = ('Orbital Radius/ AU')
#plt.show()



data.sort_values(by='Time', inplace=True)
planets = ['Mercury', 'Venus', 'Earth', ' Mars']
data = data[data['Body'].isin(planets)]



# Plotting each planet's orbital radius
plt.figure(figsize=(10, 6))

for body in data['Body'].unique():
    subset = data[data['Body'] == body]
    plt.plot(subset['Time'], subset['Position'], label=body)

plt.xlabel('Time (s)')
plt.ylabel('Orbital Radius (m)')
plt.title('Orbital Radii of Planetary Bodies Over Time')
plt.legend()
plt.grid(True)
plt.show()