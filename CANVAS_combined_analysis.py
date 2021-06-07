# Combines analysis and produces charts across 10 mon of data

# Import packages required for program
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.ticker as mtick
import calendar
import seaborn as sns; sns.set()
import matplotlib.pylab as pylab

import util


# Inputs
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
INPUT_FILE_PATH = "F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/03_Polyfit_output/"
SUM_STATS_FILE_NAME = "_analysis_sum_stats_polyfit_v4.csv"
TS_FILE_NAME = "_analysis_profiles_polyfit_v4.csv"

OUTPUT_FILE_PATH = "F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/04_Findings/"
OUTPUT_VERSION = "_v1"

LINEAR_INPUT_FILE_PATH = "F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/02_Curtail_output/"
LINEAR_FILE_NAME = "_analysis_profiles_FULL_DETAIL_v4.csv"

CLEAR_SKY_DAYS_FILE_PATH = 'F:/CANVAS/clear_sky_days_01-2019_07-2020_manual.csv'

date_1 = "2019-07-02"

# data_date_list = ["2019-07-03","2019-07-04","2019-07-05"]
data_date_list = ["2019-07-03","2019-07-04","2019-07-05", #"2019-07-01",
                    "2019-07-06","2019-07-07","2019-07-08","2019-07-09","2019-07-10",
                    "2019-07-11","2019-07-12","2019-07-13","2019-07-14","2019-07-15",
                    "2019-07-16","2019-07-17","2019-07-18","2019-07-19","2019-07-20",
                    "2019-07-21","2019-07-22","2019-07-23","2019-07-24","2019-07-25",
                    "2019-07-26","2019-07-27","2019-07-28","2019-07-29","2019-07-30",
                    "2019-07-31","2019-08-02","2019-08-03","2019-08-04", #"2019-08-01",
                    "2019-08-05","2019-08-06","2019-08-07","2019-08-08","2019-08-09",
                    "2019-08-10","2019-08-11","2019-08-12","2019-08-13","2019-08-14",
                    "2019-08-15","2019-08-16","2019-08-17","2019-08-18","2019-08-19",
                    "2019-08-20","2019-08-21","2019-08-22","2019-08-23","2019-08-24",
                    "2019-08-25","2019-08-26","2019-08-27","2019-08-28","2019-08-29",#removed september!
                    "2019-08-30","2019-08-31",
                  "2019-09-01", "2019-09-02", "2019-09-03", "2019-09-04", "2019-09-05", "2019-09-06",
                  "2019-09-07", "2019-09-08", "2019-09-09", "2019-09-10", "2019-09-11", "2019-09-12",
                  "2019-09-13", "2019-09-14", "2019-09-15", "2019-09-16", "2019-09-17", "2019-09-18",
                  "2019-09-19", "2019-09-20", "2019-09-21", "2019-09-22", "2019-09-23", "2019-09-24",
                  "2019-09-25", "2019-09-26", "2019-09-27", "2019-09-28", "2019-09-29", "2019-09-30",
                    "2019-10-02","2019-10-03", #"2019-10-01",
                    "2019-10-04","2019-10-05","2019-10-06","2019-10-07","2019-10-08",
                    "2019-10-09","2019-10-10","2019-10-11","2019-10-12","2019-10-13",
                    "2019-10-14","2019-10-15","2019-10-16","2019-10-17","2019-10-18",
                    "2019-10-19","2019-10-20","2019-10-21","2019-10-22","2019-10-23",
                    "2019-10-24","2019-10-25","2019-10-26","2019-10-27","2019-10-28",
                    "2019-10-29","2019-10-30","2019-10-31","2019-11-02", #"2019-11-01",
                    "2019-11-03","2019-11-04","2019-11-05","2019-11-06","2019-11-07",
                    "2019-11-08","2019-11-09","2019-11-10","2019-11-11","2019-11-12",
                    "2019-11-13","2019-11-14","2019-11-15","2019-11-16","2019-11-17",
                    "2019-11-18","2019-11-19","2019-11-20","2019-11-21","2019-11-22",
                    "2019-11-23","2019-11-24","2019-11-25","2019-11-26","2019-11-27",
                    "2019-11-28","2019-11-29","2019-11-30","2019-12-02", #"2019-12-01",
                    "2019-12-03","2019-12-04","2019-12-05","2019-12-06","2019-12-07",
                    "2019-12-08","2019-12-09","2019-12-10","2019-12-11","2019-12-12",
                    "2019-12-13","2019-12-14","2019-12-15","2019-12-16","2019-12-17",
                    "2019-12-18","2019-12-19","2019-12-20","2019-12-21","2019-12-22",
                    "2019-12-23","2019-12-24","2019-12-25","2019-12-26","2019-12-27",
                    "2019-12-28","2019-12-29","2019-12-30","2019-12-31", #"2020-01-01",
                    "2020-01-02","2020-01-03","2020-01-04","2020-01-05","2020-01-06",
                    "2020-01-07","2020-01-08","2020-01-09","2020-01-10","2020-01-11",
                    "2020-01-12","2020-01-13","2020-01-14","2020-01-15","2020-01-16",
                    "2020-01-17","2020-01-18","2020-01-19","2020-01-20","2020-01-21",
                    "2020-01-22","2020-01-23","2020-01-24","2020-01-25","2020-01-26",
                    "2020-01-27","2020-01-28","2020-01-29","2020-01-30","2020-01-31",
                    "2020-02-02","2020-02-03","2020-02-04","2020-02-05", #"2020-02-01",
                    "2020-02-06","2020-02-07","2020-02-08","2020-02-09","2020-02-10",
                    "2020-02-11","2020-02-12","2020-02-13","2020-02-14","2020-02-15",
                    "2020-02-16","2020-02-17","2020-02-18","2020-02-19","2020-02-20",
                    "2020-02-21","2020-02-22","2020-02-23","2020-02-24","2020-02-25",
                    "2020-02-26","2020-02-27","2020-02-28","2020-02-29",# "2020-03-01",
                    "2020-03-02","2020-03-03","2020-03-04","2020-03-05","2020-03-06",
                    "2020-03-07","2020-03-08","2020-03-09","2020-03-10","2020-03-11",
                    "2020-03-12","2020-03-13","2020-03-14","2020-03-15","2020-03-16",
                    "2020-03-17","2020-03-18","2020-03-19","2020-03-20","2020-03-21",
                    "2020-03-22","2020-03-23","2020-03-24","2020-03-25","2020-03-26",
                    "2020-03-27","2020-03-28","2020-03-29","2020-03-30","2020-03-31",
                    "2020-04-02","2020-04-03","2020-04-04","2020-04-05", #"2020-04-01",
                    "2020-04-06","2020-04-07","2020-04-08","2020-04-09","2020-04-10",
                    "2020-04-11","2020-04-12","2020-04-13","2020-04-14","2020-04-15",
                    "2020-04-16","2020-04-17","2020-04-18","2020-04-19","2020-04-20",
                    "2020-04-21","2020-04-22","2020-04-23","2020-04-24","2020-04-25",
                    "2020-04-26","2020-04-27","2020-04-28","2020-04-29","2020-04-30"]

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#------------------------ Import all summary data and combine

# First import the first data date so we've got something to join onto
sum_stats_df = pd.read_csv(INPUT_FILE_PATH + date_1 + SUM_STATS_FILE_NAME)
sum_stats_df = sum_stats_df.loc[:, ~sum_stats_df.columns.str.contains('^Unnamed')]
sum_stats_df['date'] = date_1

# Cycle through each date and append on the next df
for date_now in data_date_list:
    temp_df = pd.read_csv(INPUT_FILE_PATH + date_now + SUM_STATS_FILE_NAME)
    temp_df = temp_df.loc[:, ~temp_df.columns.str.contains('^Unnamed')]
    temp_df['date'] = date_now
    sum_stats_df = pd.concat([sum_stats_df, temp_df])

# Load clear sky days CSV and flag NON clear sky days in data_df
clear_sky_days_df = pd.read_csv(CLEAR_SKY_DAYS_FILE_PATH)
clear_sky_days_list = clear_sky_days_df['clear_sky_days'].astype(str).tolist()
sum_stats_df['clear_sky_day_flag'] = 0
sum_stats_df.loc[sum_stats_df['date'].isin(clear_sky_days_list), 'clear_sky_day_flag'] = 1

# Get month
sum_stats_df['month'] = sum_stats_df['date'].str[5:7]
sum_stats_df['month'] = sum_stats_df['month'].astype(int)
sum_stats_df['month_string'] = sum_stats_df['month'].apply(lambda x: calendar.month_abbr[x])

#------------------------ Import all timeseries data for a specific site and combine
site_list = [962508189, 1768287280, 878597128, 1081062438, 454204467]
site_list = [962508189]
# First import the first data date so we've got something to join onto
ts_df = pd.read_csv(INPUT_FILE_PATH + date_1 + TS_FILE_NAME, index_col = 't_stamp', parse_dates=True )
ts_df = ts_df.loc[:, ~ts_df.columns.str.contains('^Unnamed')]
ts_df = ts_df[ts_df['site_id'].isin(site_list)]
ts_df['t_stamp_copy'] = ts_df.index
# Get curtail period start time (for getting voltage)
start_times_df = pd.read_csv(LINEAR_INPUT_FILE_PATH + date_1 + LINEAR_FILE_NAME, index_col = 't_stamp', parse_dates=True)
start_times_df = start_times_df[start_times_df['site_id'].isin(site_list)]
start_times_df = start_times_df[['start_pts']]
# # Going to concat and assume the order is the same.
# test_df = pd.concat([ts_df, start_times_df], axis = 1)
# Merge the start_pts onto ts_df
ts_df = pd.merge(ts_df,start_times_df, right_index=True, left_index=True)
ts_df['date'] = date_1

# Cycle through each date and append on the next df
for date_now in data_date_list:
    temp_df = pd.read_csv(INPUT_FILE_PATH + date_now + TS_FILE_NAME, index_col = 't_stamp', parse_dates=True)
    temp_df = temp_df.loc[:, ~temp_df.columns.str.contains('^Unnamed')]
    temp_df = temp_df[temp_df['site_id'].isin(site_list)]
    # Get curtail period start time (for getting voltage)
    temp_start_times_df = pd.read_csv(LINEAR_INPUT_FILE_PATH + date_now + LINEAR_FILE_NAME, index_col='t_stamp',
                                 parse_dates=True)
    temp_start_times_df = temp_start_times_df[temp_start_times_df['site_id'].isin(site_list)]
    temp_start_times_df = temp_start_times_df[['start_pts']]
    # Merge the start_pts onto ts_df
    temp_df = pd.merge(temp_df, temp_start_times_df, right_index=True, left_index=True)
    temp_df['date'] = date_now
    # Add onto ts_df
    ts_df = pd.concat([ts_df, temp_df])

# Some of the start_pts are at the end of the day (must be filtered out later int he curtail scripts...)
# So, get start pts my own way - first get a copy of start_pts
ts_df['start_pts_check'] = ts_df['start_pts']
# Then check whether est_cf_preferred is nan and set these values of start_pts_check to zero
ts_df.loc[np.isnan(ts_df['est_cf_preferred']), 'start_pts_check'] = 0

# Plot voltage distribution
fig, ax = plt.subplots()
sns.boxplot(x='start_pts_check', y='v', data=ts_df, showmeans=True)
plt.show()

# Export data
ts_df.to_csv(OUTPUT_FILE_PATH + "100_full_10_months_ts_data_site_962508189_CHECK" + OUTPUT_VERSION + ".csv")

# Plot for single site
fig, ax = plt.subplots()
ax.plot(ts_df['cf'], c='purple', label='cf')
ax.plot(ts_df['est_cf_preferred'], c='blue', label='Estaimted cf (preferred)')
ax1 = ax.twinx()
ax1.plot(ts_df['v'])
ax1.plot(ts_df['v']*ts_df['start_pts'],  'o', c='red')
ax1.plot(ts_df['v']*ts_df['start_pts_check'],  'o', c='yellow')
ax1.grid(False)
ax.legend(loc='upper right')
plt.show()

# Purpose 2 - check voltages at 'start' time
ts_df_test = pd.read_csv("F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/02_Curtail_output/" + date_1 + "_analysis_profiles_FULL_DETAIL_v4.csv")

#------------------------ Check average curtailment for sites impacted
average_curtailment_impacted_sites = sum_stats_df['percentage_lost_preferred'].mean()
# Check average curtailment for ALL sites
sum_stats_df_TEST = sum_stats_df.copy()
sum_stats_df_TEST['percentage_lost_preferred'] = sum_stats_df_TEST['percentage_lost_preferred'].fillna(0)
average_curtailment_all_sites = sum_stats_df_TEST['percentage_lost_preferred'].mean()
# Check average curtailment for sites impacted on clear sky days
sum_stats_df_clear_sky_days = sum_stats_df[sum_stats_df['clear_sky_day_flag']==1]
average_curtailment_impacted_sites_clear_sky_days = sum_stats_df_clear_sky_days['percentage_lost_preferred'].mean()
# Check average curtailment for ALL sites on clear sky days
sum_stats_df_clear_sky_days_all_sites = sum_stats_df_TEST[sum_stats_df_TEST['clear_sky_day_flag']==1]
average_curtailment_all_sites_clear_sky_days = sum_stats_df_clear_sky_days_all_sites['percentage_lost_preferred'].mean()

#------------------------ Export data to csv
sum_stats_df.to_csv(OUTPUT_FILE_PATH + "00_summary_stats" + OUTPUT_VERSION + ".csv")
sum_stats_df_TEST.to_csv(OUTPUT_FILE_PATH + "00_summary_stats_with_zeros" + OUTPUT_VERSION + ".csv")

#------------------------ Get the number of sites in the dataset for each date
plot_1_df = pd.DataFrame({'site_count' : sum_stats_df.groupby('date')['site_id'].count(),
                          'site_count_with_curtail' : sum_stats_df.groupby('date')['percentage_lost'].count(),
                          'date' : sum_stats_df.groupby('date')['date'].first(),
                          'sum_gen_kWh' : sum_stats_df.groupby('date')['gen_kWh'].sum(),
                          'sum_gen_loss_est_kWh_preferred' : sum_stats_df.groupby('date')['gen_loss_est_kWh_preferred'].sum(),
                          'clear_sky_day_flag' : sum_stats_df.groupby('date')['clear_sky_day_flag'].first()})
# Calculate percentage experiencing SOME curtailment (any at all!) and also the percentage of curtailment by date
plot_1_df['proportion_sites_experiencing_some_curtailment'] = plot_1_df['site_count_with_curtail'] / plot_1_df['site_count']
plot_1_df['percentage_gen_loss_est_kWh_preferred_across_all_sites'] = plot_1_df['sum_gen_loss_est_kWh_preferred'] / plot_1_df['sum_gen_kWh']
# Plot
fig, ax= plt.subplots()
ax = sns.barplot(x = 'date', y='site_count', data = plot_1_df, color='blue')
plt.show()
# Export data to csv
plot_1_df.to_csv(OUTPUT_FILE_PATH + "01_number_of_sites_by_date" + OUTPUT_VERSION + ".csv")

#------------------------ Get findings by site
plot_2_df = pd.DataFrame({'site_id' : sum_stats_df.groupby('site_id')['site_id'].first(),
                          'sum_gen_kWh' : sum_stats_df.groupby('site_id')['gen_kWh'].sum(),
                          'sum_gen_loss_est_kWh_preferred' : sum_stats_df.groupby('site_id')['gen_loss_est_kWh_preferred'].sum(),
                          'count_dates': sum_stats_df.groupby('site_id')['date'].count(),
                          'count_dates_with_curtail': sum_stats_df.groupby('site_id')['percentage_lost'].count(),
                          'Grouping' : sum_stats_df.groupby('site_id')['Grouping'].first(),
                          'Standard_Version' : sum_stats_df.groupby('site_id')['Standard_Version'].first(),
                          'ac' : sum_stats_df.groupby('site_id')['ac'].first(),
                          'manufacturer' : sum_stats_df.groupby('site_id')['manufacturer'].first(),
                          'model' : sum_stats_df.groupby('site_id')['model'].first(),
                          's_postcode' : sum_stats_df.groupby('site_id')['s_postcode'].first(),
                          'mean_percentage_lost' : sum_stats_df.groupby('site_id')['percentage_lost'].mean()})
# Calc percentage lost over the 10 month study period, proportion of dates experiencing curtailment etc.
plot_2_df['percentage_lost_over_10_mon'] = plot_2_df['sum_gen_loss_est_kWh_preferred'] / plot_2_df['sum_gen_kWh']
plot_2_df['percentage_dates_experiencing_curtailment'] = plot_2_df['count_dates_with_curtail'] / plot_2_df['count_dates']
plot_2_df = plot_2_df.sort_values('percentage_lost_over_10_mon', ascending=False)
plot_2_df = plot_2_df.sort_values('percentage_dates_experiencing_curtailment', ascending=False)

# Get proportion of sites for plotting
plot_2_df['proportion_of_sites_for_plotting'] = range(len(plot_2_df))
plot_2_df['proportion_of_sites_for_plotting'] = (plot_2_df['proportion_of_sites_for_plotting'] + 1) / len(plot_2_df)

# Plot percentage lost by site
fig, ax= plt.subplots()
ax = sns.lineplot(x = 'proportion_of_sites_for_plotting', y='percentage_lost_over_10_mon', data = plot_2_df, color='blue', marker='o')
ax = sns.scatterplot(x = 'proportion_of_sites_for_plotting', y = 'percentage_dates_experiencing_curtailment', data = plot_2_df)
plt.show()
# Export data to csv
plot_2_df.to_csv(OUTPUT_FILE_PATH + "02_findings_by_site" + OUTPUT_VERSION + ".csv")

#------------------------ Filter for clear sky days THEN get findings by site
sum_stats_df_clear_sky_days = sum_stats_df[sum_stats_df['clear_sky_day_flag'] == 1]
plot_3_df = pd.DataFrame({'site_id' : sum_stats_df_clear_sky_days.groupby('site_id')['site_id'].first(),
                          'sum_gen_kWh' : sum_stats_df_clear_sky_days.groupby('site_id')['gen_kWh'].sum(),
                          'sum_gen_loss_est_kWh_preferred' : sum_stats_df_clear_sky_days.groupby('site_id')['gen_loss_est_kWh_preferred'].sum(),
                          'count_dates': sum_stats_df_clear_sky_days.groupby('site_id')['date'].count(),
                          'count_dates_with_curtail': sum_stats_df_clear_sky_days.groupby('site_id')['percentage_lost'].count(),
                          'Grouping' : sum_stats_df_clear_sky_days.groupby('site_id')['Grouping'].first(),
                          'Standard_Version' : sum_stats_df_clear_sky_days.groupby('site_id')['Standard_Version'].first(),
                          'ac' : sum_stats_df_clear_sky_days.groupby('site_id')['ac'].first(),
                          'manufacturer' : sum_stats_df_clear_sky_days.groupby('site_id')['manufacturer'].first(),
                          'model' : sum_stats_df_clear_sky_days.groupby('site_id')['model'].first(),
                          's_postcode' : sum_stats_df_clear_sky_days.groupby('site_id')['s_postcode'].first(),
                          'mean_percentage_lost' : sum_stats_df_clear_sky_days.groupby('site_id')['percentage_lost'].mean()})
# Calc percentage lost over the 10 month study period, proportion of dates experiencing curtailment etc.
plot_3_df['percentage_lost_over_10_mon'] = plot_3_df['sum_gen_loss_est_kWh_preferred'] / plot_3_df['sum_gen_kWh']
plot_3_df['percentage_dates_experiencing_curtailment'] = plot_3_df['count_dates_with_curtail'] / plot_3_df['count_dates']
plot_3_df = plot_3_df.sort_values('percentage_lost_over_10_mon', ascending=False)
# plot_3_df = plot_3_df.sort_values('percentage_dates_experiencing_curtailment', ascending=False)

# Get proportion of sites for plotting
plot_3_df['proportion_of_sites_for_plotting'] = range(len(plot_3_df))
plot_3_df['proportion_of_sites_for_plotting'] = (plot_3_df['proportion_of_sites_for_plotting'] + 1) / len(plot_3_df)

# Plot percentage lost by site
fig, ax= plt.subplots()
ax = sns.lineplot(x = 'proportion_of_sites_for_plotting', y='percentage_lost_over_10_mon', data = plot_3_df, color='blue', marker='o')
ax = sns.scatterplot(x = 'proportion_of_sites_for_plotting', y = 'percentage_dates_experiencing_curtailment', data = plot_3_df)
plt.show()
# Export data to csv
plot_3_df.to_csv(OUTPUT_FILE_PATH + "03_findings_by_site_clear_sky_days" + OUTPUT_VERSION + ".csv")


#------------------------ Get curtailment over the year (by month)
# NOTE to self - boxplot automatically ignores empty rows, so the boxplot of sum_stats is actually only plotting the
# spread of curtailment at sites that experience curtailment, not across the whole dataset.
# Plot the spread of curtailment over each month FOR SITES EXPERIENCING CURTAILMENT
fig, ax= plt.subplots()
sns.boxplot(x='month_string', y='percentage_lost', data=sum_stats_df,
                 showmeans=True, meanprops={"marker":"o","markerfacecolor":"black"}, hue='clear_sky_day_flag')
# set y axis to percentage
vals = ax.get_yticks()
ax.set_yticklabels(['{:,.0%}'.format(x) for x in vals])
# Axis labels
plt.xlabel('Month')
plt.ylabel('Percentage generation lost')
# Save figure
# fig.savefig(SUM_STAT_DATA_PATH + 'Images/plot_6_spread_of_gen_lost_over_months_'+str(CURTAIL_METHOD)+ FIG_V_STRING + '.png', dpi=100,
#             bbox_inches = 'tight', pad_inches = 0)
plt.show()

