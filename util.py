# Useful functions

# Import required things
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# Get clear sky days
# def get_clear_sky_days()

# Get first month of data
df = pd.read_csv('F:/irradiance_data/1_min_solar/adelaide/sl_023034_2020_01.txt')

# List rest of months
list=['02','03','04','05','06','07']
# Concat on rest of months
for i in list:
    df_temp = pd.read_csv('F:/irradiance_data/1_min_solar/adelaide/sl_023034_2020_'+i+'.txt')
    df = pd.concat([df, df_temp])

# Make sure numeric
df['min_1s_global_irr'] = pd.to_numeric(df["Minimum 1 second global irradiance (over 1 minute) in W/sq m"], errors='coerce')
df['min_1s_global_irr'] = df['min_1s_global_irr'].fillna(0)

# Get change in irradiance for "Minimum 1 second global irradiance (over 1 minute) in W/sq m"
df["min_1s_global_irr_SHIFTED"] = df["min_1s_global_irr"].shift(periods=-1)
# Set fill value to 0 (from nan) since fill_value arg is giving an error.
df["min_1s_global_irr_SHIFTED"] = df["min_1s_global_irr_SHIFTED"].fillna(0)
# Calculate change in irradiance
df['change_in_irr'] = (df['min_1s_global_irr'] - df["min_1s_global_irr_SHIFTED"])/df['min_1s_global_irr']

# Get times
df['year'] = pd.to_numeric(df["Year Month Day Hours Minutes in YYYY"], errors='coerce')
df['month'] = pd.to_numeric(df["MM"], errors='coerce')
df['day'] = pd.to_numeric(df["DD"], errors='coerce')
df['hour'] = pd.to_numeric(df["HH24"], errors='coerce')
df['minute'] = pd.to_numeric(df["MI format in Local standard time"], errors='coerce')
df['date_time'] = pd.to_datetime(df[["year","month","day","hour","minute"]])





# Plot the min irradiance
fig, ax = plt.subplots()
ax.plot(df['date_time'],df['min_1s_global_irr'])
ax1 = ax.twinx()
ax1.plot(df['date_time'],df['change_in_irr'])
plt.show()
