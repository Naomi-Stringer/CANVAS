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
# Also get mean for plotting
df['mean_1s_global_irr'] = pd.to_numeric(df["Mean global irradiance (over 1 minute) in W/sq m"], errors='coerce')
# df['mean_1s_global_irr'] = df['mean_1s_global_irr'].fillna(0)

# Get change in irradiance for "Minimum 1 second global irradiance (over 1 minute) in W/sq m"
df["min_1s_global_irr_SHIFTED"] = df["min_1s_global_irr"].shift(periods=-1)
# Set fill value to 0 (from nan) since fill_value arg is giving an error.
df["min_1s_global_irr_SHIFTED"] = df["min_1s_global_irr_SHIFTED"].fillna(0)
# Calculate change in irradiance
df['change_in_irr'] = (df['min_1s_global_irr'] - df["min_1s_global_irr_SHIFTED"])/df['min_1s_global_irr']
df['abs_change_in_irr'] = df['change_in_irr'].abs()

# Get times
df['year'] = pd.to_numeric(df["Year Month Day Hours Minutes in YYYY"], errors='coerce')
df['month'] = pd.to_numeric(df["MM"], errors='coerce')
df['day'] = pd.to_numeric(df["DD"], errors='coerce')
df['hour'] = pd.to_numeric(df["HH24"], errors='coerce')
df['minute'] = pd.to_numeric(df["MI format in Local standard time"], errors='coerce')
df['date'] = pd.to_datetime(df[["year","month","day"]])
df['date_time'] = pd.to_datetime(df[["year","month","day","hour","minute"]])

# Set index to date_time and filter VERY ROUGHLY for solar hours
# TODO would be great to instead find start and end pts for ecah day and filter for about an hour 'inside' this range,
#  see prevoius attempts on 23 March 2021
df = df.set_index('date_time')
df_approx_solar_hours = df.between_time('07:00', '17:00')

# ------------------------------------- Factor 1: max absolute variation in irradiance per day
# Get max absolute variation on each date.
df_max_abs_change_in_irr = pd.DataFrame(df_approx_solar_hours.groupby('date')['abs_change_in_irr'].max())

# Identify possible clear sky days
df_clear_sky_days = df_max_abs_change_in_irr[df_max_abs_change_in_irr['abs_change_in_irr']<=0.15]
print(len(df_clear_sky_days))
clear_sky_day_list = df_clear_sky_days.index.tolist()
df_clear_sky_days = df[df['date'].isin(clear_sky_day_list)]


# ------------------------------------- Factor 2: 95th and 99th percentile of change per day
# NOTE does NOT need to use the approx solar hours
df_temp_2 = df[['date','abs_change_in_irr']]
df_95th_percentile_abs_change_in_irr = pd.DataFrame(df_temp_2.groupby('date').quantile(0.95))
df_95th_percentile_abs_change_in_irr = df_95th_percentile_abs_change_in_irr.rename(columns={'abs_change_in_irr' : '95th percentile'})
df_99th_percentile_abs_change_in_irr = pd.DataFrame(df_temp_2.groupby('date').quantile(0.99))
df_99th_percentile_abs_change_in_irr = df_99th_percentile_abs_change_in_irr.rename(columns={'abs_change_in_irr' : '99th percentile'})

# Identify possible clear sky days
df_clear_sky_days_method_2 = df_95th_percentile_abs_change_in_irr[df_95th_percentile_abs_change_in_irr['95th percentile']<=0.1]
print(len(df_clear_sky_days_method_2))

# ------------------------------------- Factor 3: Total energy
# TODO access online at:

# ------------------------------------- Export by date
df_export = pd.concat([df_max_abs_change_in_irr, df_95th_percentile_abs_change_in_irr, df_99th_percentile_abs_change_in_irr], axis=1)
df_export.to_csv('F:/irradiance_data/1_min_solar/adelaide/2020_adelaide_irradiance_summary_statistics_for_clear_sky_day_analysis.csv')

# ------------------------------------- Plotting
# Plot the min irradiance
fig, ax = plt.subplots()
ax.plot(df['min_1s_global_irr'], c='purple')
ax.plot(df['mean_1s_global_irr'], c='blue')
ax1 = ax.twinx()
ax1.plot(df['change_in_irr'])
plt.show()

# Plot the min irradiance for approx solar hours
fig, ax = plt.subplots()
ax.plot(df_clear_sky_days['min_1s_global_irr'])
ax1 = ax.twinx()
ax1.plot(df_clear_sky_days['change_in_irr'])
plt.show()

# Plot the min irradiance for clear sky days
fig, ax = plt.subplots()
ax.plot(df_approx_solar_hours['min_1s_global_irr'])
ax1 = ax.twinx()
ax1.plot(df_approx_solar_hours['change_in_irr'])
plt.show()

