# Estimates volume of PV generation being curtailed due to over voltage
# TODO - as discussed, scripts currently don't do any filtering based on voltage

#------------------------ Step 0: Import required packages ------------------------
# Import packages required for program
import numpy as np
import pandas as pd

import util

# Inputs
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Pass a list of dates contained in the dataset
# # # TODO - Temporary for testing:
# data_date_list = ["2019-09-03"]
# DATA_DATE = data_date_list[0]
# data_date_list = ["2019-09-01", "2019-09-02", "2019-09-03", "2019-09-04", "2019-09-05", "2019-09-06",
#                   "2019-09-07", "2019-09-08", "2019-09-09", "2019-09-10", "2019-09-11", "2019-09-12",
#                   "2019-09-13", "2019-09-14", "2019-09-15", "2019-09-16", "2019-09-17", "2019-09-18",
#                   "2019-09-19", "2019-09-20", "2019-09-21", "2019-09-22", "2019-09-23", "2019-09-24",
#                   "2019-09-25", "2019-09-26", "2019-09-27", "2019-09-28", "2019-09-29", "2019-09-30"]
data_date_list = ["2019-07-02","2019-07-03","2019-07-04","2019-07-05", #"2019-07-01",
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
                    "2019-08-30","2019-08-31","2019-10-02","2019-10-03", #"2019-10-01",
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

# Input/output file locations
INPUT_DATA_FOLDER_PATH = 'F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/01_Cleaned_data/'
OUTPUT_DATA_FOLDER_PATH = 'F:/05_Solar_Analytics/2021-05-31_CANVAS_Solar_Analytics_data/02_Curtail_output/'

# CER and APVI data on PV penetration / installs
PC_INSTALLS_DATA_FILE_PATH = 'F:/CANVAS/Postcode_data_for_small-scale installations-SGU-Solar_approx_2019_20.csv'
DWELLINGS_DATA_FILE_PATH = 'F:/CANVAS/postcodes_4b8c.csv'

# Output file names
TS_DATA_FILE_NAME_FULL = "_analysis_profiles_FULL_DETAIL_v4.csv"
TS_DATA_FILE_NAME = "_analysis_profiles_v4.csv"
SUM_STATS_DATA_FILE_NAME = "_analysis_sum_stats_v4.csv"

# List of connection types for filtering
pv_list = ['pv_site_net', 'pv_site', 'pv_inverter_net']

# Approx capacity factor value considered to be 'zero', e.g. less than 1% CF is zero.
CF_ZERO_APPROX = 0.01
# Approx cf derivative at which considered to be 'ramp'. That is, for at least a 10% change in capacity factor (ABSOLUTE!) expect to be ramping up or down.
# Note, only applied 'next to' zeros. So should not capture shading effects.
FIRST_DERIV_FALL_LIMIT = -0.05
FIRST_DERIV_INCREASE_LIMIT = 0.05
# For missing data check
ALLOWED_MISSING_DATA_PERCENTAGE = 0.05
# Average percentage of capacity at which a system must operate over the course of the day in order to be included in analysis
VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY = 0.05

# Function for getting cumulative count of 0 with reset on 1
def rcount(a):
    without_reset = (a == 0).cumsum()
    reset_at = (a == 1)
    overcount = np.maximum.accumulate(without_reset * reset_at)
    result = without_reset - overcount
    return result
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ********************* Date loop  *********************
# Step through each date in turn
for DATA_DATE in data_date_list:

    # Get data file paths for this date
    cleaned_data_file_path = INPUT_DATA_FOLDER_PATH + DATA_DATE + '_cleaned.csv'
    circuit_details_file_path = INPUT_DATA_FOLDER_PATH + DATA_DATE + '_circuit_details_for_editing_cleaned.csv'

    # Get data
    unaltered_data = pd.read_csv(cleaned_data_file_path, index_col = 'ts', parse_dates=True )

    # rename energy column
    unaltered_data = unaltered_data.rename(columns = {'e' : 'energy', 'd':'duration', 'sum_ac':'ac'})
    # filter for clean
    unaltered_data = unaltered_data[unaltered_data['clean']=='cleaned']
    # Attempt to fix issues by sorting the index at the beginning
    unaltered_data = unaltered_data.sort_index()
    # Change name to t_stamp
    unaltered_data.index.name = 't_stamp'
    # Add time by seconds from start of the day
    unaltered_data['hrs'] = unaltered_data.index.hour
    unaltered_data['min'] = unaltered_data.index.minute
    unaltered_data['sec'] = unaltered_data.index.second
    unaltered_data['time_in_seconds'] = unaltered_data['hrs'] * 60 * 60 + unaltered_data['min'] * 60 + unaltered_data['sec']

    # Get list of time_intervals
    time_interval_list = unaltered_data['duration'].drop_duplicates().tolist()

    # ********************* Further data cleaning [START] *********************
    # Check for missing data issues
    # TODO - this may not longer work since the Solar Analytics data can contain a mix of 60s and 5s data
    # Flag sites with too much missing data (based on threshold), need to also keep the duration
    missing_data_df = pd.DataFrame({'num_data_pts': unaltered_data.groupby('c_id')['energy'].count(), 'duration': unaltered_data.groupby('c_id')['duration'].first()}).reset_index()
    # We now have two possible time intervals: 30s or 60s.
    # Therefore, we need to run twice?
    for time_interval in time_interval_list:
        # Expected number of time periods
        num_time_periods = 24 * 60 * (60 / time_interval)
        # Get the minimum number of data points required in order to have enough data (i.e. not lots of missing data)
        missing_data_threshold = num_time_periods * (1 - ALLOWED_MISSING_DATA_PERCENTAGE)
        missing_data_df['missing_data_flag'] = np.nan
        missing_data_df.loc[(missing_data_df['num_data_pts'] <= missing_data_threshold) & missing_data_df['duration']==time_interval , 'missing_data_flag'] = 1.0
    print("The number of c_ids with too much missing data is:")
    print(missing_data_df['missing_data_flag'].sum())
    print("The total number of c_ids is:")
    print(missing_data_df['num_data_pts'].count())
    # Merge information about missing data back onto time series df
    unaltered_data = unaltered_data.reset_index().merge(missing_data_df, on='c_id', how='left').set_index('t_stamp')
    # Filter unaltered data for only sites with sufficient data points
    unaltered_data = unaltered_data[unaltered_data['missing_data_flag'] != 1.0]

    # Filter for PV only
    unaltered_data = unaltered_data[unaltered_data['con_type'].isin(pv_list)]

    # First fix duratoin_x / duration_y problem. Not sure where it is coming from
    # I don't know why, but there is duration_x and duration_y. Drop one and rename the other
    unaltered_data = unaltered_data.drop(['duration_x'], axis=1)
    unaltered_data = unaltered_data.rename(columns={'duration_y': 'duration'})

    # Open _circuit_details_for_editing.csv file for sunrise/set times
    assist_df = pd.read_csv(circuit_details_file_path)

    # Check for PV sites with very low output and remove them
    get_site_ac_df = unaltered_data[['site_id', 'first_ac', 'ac']]
    get_site_ac_df = get_site_ac_df.drop_duplicates(subset='site_id')
    # merge keeping only the site_ids in the time series df.
    assist_df = assist_df.merge(get_site_ac_df, left_on='site_id', right_on='site_id', how='right')

    # Check whether c_ids operated at less than an average of 5% capacity
    # Compare using max power output compared with first_ac.
    max_p_df = pd.DataFrame({'max_p_kW': unaltered_data.groupby('c_id')['power_kW'].max(), 'first_ac' : unaltered_data.groupby('c_id')['first_ac'].first()})
    max_p_df['low_output_flag'] = np.nan
    max_p_df.loc[max_p_df['max_p_kW'] < VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY * max_p_df['first_ac'] , 'low_output_flag'] = 1
    # Copy c_ids to a column (from index)
    max_p_df['c_id'] = max_p_df.index
    # Get list of c_ids to be excluded
    c_ids_to_WITHOUT_low_output = max_p_df[max_p_df['low_output_flag'] != 1]
    c_ids_to_WITHOUT_low_output = c_ids_to_WITHOUT_low_output['c_id'].tolist()

    # Report the number of c_ids dropped.
    # TODO - would be better to report this in a csv for all sites for each data date
    print("The number of c_ids excluded due to max output < first_ac * " + str(VERY_LOW_OUTPUT_AVE_PERCENTAGE_CAPACITY)+ ":")
    print(len(max_p_df) - len(c_ids_to_WITHOUT_low_output))
    print("The total number of c_ids remaining is:")
    print(len(max_p_df))

    # Only keep sites that have enough output
    unaltered_data = unaltered_data[unaltered_data['c_id'].isin(c_ids_to_WITHOUT_low_output)]
    # ********************* Further data cleaning [END] *********************

    # Get assist_df with c_id as index
    assist_df_c_id = assist_df.set_index('c_id')

    # Get c_id list
    c_id_list = unaltered_data['c_id'].drop_duplicates().tolist()
    # Set up output_df
    output_df = pd.DataFrame()
    output_df.index.name = 't_stamp'

    # ********************* Circuit id loop  *********************
    # Loop through c_ids
    for c_id in c_id_list:

        # Get data for c_id
        data = unaltered_data[unaltered_data['c_id'] == c_id]

        # Filter for sunshine hours - NOTE must add an hour to sunrise / subtract and hour from sunset since Nick's code did the opposite, but I actually would like correct sunrise/set
        # Sunrise
        sun_rise = assist_df_c_id.loc[c_id,'sunrise']
        sun_rise = pd.to_datetime(sun_rise)
        sun_rise_hour = sun_rise.hour
        sun_rise_min = sun_rise.minute
        if sun_rise_min <10 :
            sun_rise_min = '0' + str(sun_rise_min)
        else:
            sun_rise_min = str(sun_rise_min)
        sun_rise_for_filter = str(sun_rise_hour + 1) + ':' + sun_rise_min + ':' + str(00)
        # Sunset
        sun_set = assist_df_c_id.loc[c_id,'sunset']
        sun_set = pd.to_datetime(sun_set)
        sun_set_hour = sun_set.hour
        sun_set_min = sun_set.minute
        if sun_set_min <10 :
            sun_set_min = '0' + str(sun_set_min)
        else:
            sun_set_min = str(sun_set_min)
        sun_set_for_filter = str(sun_set_hour - 1) + ':' + sun_set_min + ':' + str(00)

        data = data.between_time(sun_rise_for_filter, sun_set_for_filter)

        # Calc CF
        data['unaltered_cf'] = data['power_kW'] / data['ac']
        # Flag approximate zeroes (cf < CF_ZERO_APPROX)
        data['unaltered_zero_flag'] = 0
        data.loc[data['unaltered_cf'] <= CF_ZERO_APPROX, 'unaltered_zero_flag'] = 1
        data['non_zero_flag_count'] = data['unaltered_zero_flag']

        # Remove cases where 'blip' occurs. e.g. above zero but only for a max of 2 time intervals.
        # TODO - may be better to remove this step since we are also looking at non-clear sky days!
        # First, count the non zeros
        a = data['non_zero_flag_count']
        # Now remove from data
        data = data.drop(['non_zero_flag_count'], axis=1)
        # Count non zeros
        result = rcount(a)
        # Add onto data
        data = pd.concat([data,result], axis=1)

        # Copy the unaltered zero flag - we will then remove the 'blips' from it.
        data['zero_flag'] = data['unaltered_zero_flag']

        # Case where single point of 'non zero' before returning to zero
        data.loc[(data['non_zero_flag_count'].shift(-1) == 0) & (data['non_zero_flag_count'] == 1),'zero_flag'] = 1

        # If the non zero flag count in this row is 2 and in the next row is zero, then set zero_flag to 1 (i.e. remove 'blip')
        data.loc[(data['non_zero_flag_count'].shift(-1) == 0) & (data['non_zero_flag_count'] == 2),'zero_flag'] = 1
        data.loc[(data['non_zero_flag_count'].shift(-2) == 0) & (data['non_zero_flag_count'].shift(-1) == 2),'zero_flag'] = 1

        # Set CF to zero where zero flag occurs
        data['cf'] = data['unaltered_cf']
        data.loc[data['zero_flag'] == 1,'cf'] = 0

        # Get first derivative of cf
        data = util.calculate_first_derivative_of_variable(data, 'cf')

        # --------------------------------- Reductions immediately before zero
        # Falling dramatically before zeros
        data['start_deriv_flag'] = 0
        # Just get the first instance of ramp down
        # e.g. Times where zero flag (t+1) = 1, zero flag (t) <>1 and cf_first_deriv < limit
        data.loc[(data['zero_flag'].shift(-1) == 1) & (data['zero_flag'] == 0) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        # Dealing with 'soft' disconnect
        # Next interval is zero flagged, current value is greater than 'zero' limit
        data.loc[(data['zero_flag'].shift(-1) == 1) & (data['cf'] > CF_ZERO_APPROX),'start_deriv_flag'] = 1

        # Get the next instance of ramp down (well, previous) - repeat four times. Effectively means you can capture periods in which power falls over 5 time intervals (including initial one captured above)
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1
        data.loc[(data['start_deriv_flag'].shift(-1) == 1) & (data['cf_first_deriv'] < FIRST_DERIV_FALL_LIMIT),'start_deriv_flag'] = 1

        # --------------------------------- Increases immediately after zero
        # Increasing dramatically after zeros
        data['end_deriv_flag'] = 0
        # Just get the first instance of ramp up
        # e.g. Times where zero flag (t) = 1, zero flag (t+1) <>1 and cf_first_deriv > limit
        data.loc[(data['zero_flag'].shift(-1) == 0) & (data['zero_flag'] == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        # Dealing with 'soft' restarts.
        # Previous value was zero flagged, current value is greater than the 'zero' limit
        data.loc[(data['zero_flag'].shift(+1) == 1) & (data['cf'] > CF_ZERO_APPROX),'end_deriv_flag'] = 1

        # Get next instances (x8 as slower ramp up potentially)
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['cf_first_deriv'] > FIRST_DERIV_INCREASE_LIMIT),'end_deriv_flag'] = 1

        # --------------------------------- Get 'ramp' start and end points
        # Get start points
        data['start_pts'] = 0
        # Case where 'start_derive_flag' is zero in previous interval (t-1), and one in current interval (t)
        data.loc[(data['start_deriv_flag'].shift(+1) == 0) & (data['start_deriv_flag'] == 1),'start_pts'] = 1

        # Get end points
        data['end_pts'] = 0
        # Case where 'end_deriv_flag' is 1 in previous interval (t-1), and 0 in current interval (t)
        data.loc[(data['end_deriv_flag'].shift(+1) == 1) & (data['end_deriv_flag'] == 0),'end_pts'] = 1

        # --------------------------------- Add some things to data that we need
        # Check that the first 'start point' occurs before the first 'end point'. If not, then delete the first 'end point'
        # Else in the early hours of the day as the generation goes from zero to non zero it looks like 'soft start'
        # Check three times over (TODO would be better to do this as a while somehow... maybe so that it stops once the first_end_point stops changing?)
        try:
            for i in range(0,3):
                first_end_point = data[data['end_pts']==1]
                first_end_point = first_end_point['time_in_seconds'].iloc[0]
                # Find first start point
                first_start_point = data[data['start_pts']==1]
                first_start_point = first_start_point['time_in_seconds'].iloc[0]
                print(first_end_point)
                print(first_start_point)
                # Check that the first start point occurs after the first end point.
                if first_end_point < first_start_point:
                    data.loc[data['time_in_seconds']==first_end_point, 'end_pts'] = 0
        except:
            print('looks like no start of end points for this site')

        # Identify the start and end pt number (so they can be matched to each other)
        data['start_cumsum'] = data['start_pts'].cumsum()
        data['end_cumsum'] = data['end_pts'].cumsum()

        # Get cumulative zeros between 'start' and 'end' pts
        data['count_during_period'] = data['start_pts']
        data.loc[data['end_pts'] == 1,'count_during_period'] =1
        a = data['count_during_period']

        # Copy as a renamed column then remove ^ name from data
        data['start_end_combined'] = data['count_during_period']
        # NOTE - possible issue here? Dropped column but then used later. NO - all good, it's added back on a few
        # lines below using rcount function then merge.
        data = data.drop(['count_during_period'], axis=1)

        # Do count on df 'a' which contains the 'count_during_period' data from a few lines above.
        result = rcount(a)
        data = pd.concat([data,result], axis=1)

        # Flag 'estimate' period (i.e. between start and end pts)
        data['est_period'] = data['start_cumsum'] - data['end_cumsum']

        # --------------------------------- get start and end dfs, then get ramp df and merge onto data
        start_df = data[data['start_pts']==1]
        end_df = data[data['end_pts']==1]

        # In cases where there are no events, need to 'try'
        try:
            # Create new ramp_df.
            # NOTE use +2 in the range in order to capture additional end points if the first end point occurs before the first start point.
            # May make sense to even add a couple.. (i.e. +3 or +4) however this will do for now.
            count_start_pts = start_df['start_cumsum'].max()
            ramp_df = pd.DataFrame(data=list(range(1,int(count_start_pts+2))), columns=['event_num'])

            # Get data from dfs
            # Keep only cf, time_int and start_cumsum.
            start_df = start_df[['cf', 'time_in_seconds', 'start_cumsum']]
            # Then merge on start_cumsum
            ramp_df = ramp_df.merge(start_df, left_on='event_num', right_on='start_cumsum')
            # Rename columns
            ramp_df = ramp_df.rename(columns = {'cf' : 'start_cf'})
            ramp_df = ramp_df.rename(columns = {'time_in_seconds' : 'start_time_int'})

            # Keep only cf, time)nt and start_cumsum.
            end_df = end_df[['cf', 'time_in_seconds', 'end_cumsum']]
            # Then merge on start_cumsum
            ramp_df = ramp_df.merge(end_df, left_on='event_num', right_on='end_cumsum')
            # Rename columns
            ramp_df = ramp_df.rename(columns = {'cf' : 'end_cf'})
            ramp_df = ramp_df.rename(columns = {'time_in_seconds' : 'end_time_int'})

            # Check for cases where end time is BEFORE start time for an event.
            # If this is the case, then delete that end time and shift all end times up by one.
            # Check each event from top to bottom
            num_events = ramp_df['event_num'].max()
            for i in range(0, int(num_events)):
                if ramp_df.loc[i, 'end_time_int'] < ramp_df.loc[i, 'start_time_int']:
                    ramp_df['end_time_int'] = ramp_df['end_time_int'].shift(-1)

            # Calc the ramp rate
            ramp_df['m'] = (ramp_df['end_cf'] - ramp_df['start_cf']) / (ramp_df['end_time_int'] - ramp_df['start_time_int'])

            # Drop end and start cumsum, then merge onto data
            ramp_df = ramp_df.drop(['end_cumsum', 'start_cumsum'], axis=1)
            zero_row_for_ramp_df = pd.DataFrame(data=[0], columns=['event_num'])
            ramp_df = pd.concat([ramp_df, zero_row_for_ramp_df])

            data = data.reset_index().merge(ramp_df,  left_on='start_cumsum', right_on='event_num').set_index('t_stamp')
            # Calc estimated CF
            data['count_during_period_using_start_time'] = data['est_period'] * (data['time_in_seconds'] - data['start_time_int'])
            data['est_cf'] = data['est_period'] * (data['start_cf'] + data['count_during_period_using_start_time']*data['m'])
            # Add the 'end point'
            data.loc[data['end_pts']==1,'est_cf'] = data['cf']

            # Get est kW and est kWh
            data['est_kW'] = data['est_cf'] * data['ac']
            data['est_kWh'] = data['est_cf'] * data['ac'] * data['duration']/(60*60)

            # Get power lost estimate
            data['gen_loss_est_kWh'] = data['est_kWh'] - (data['power_kW']* data['duration']/(60*60))
            # Issue is that we don't want gen lost to be less than zero!
            data.loc[data['gen_loss_est_kWh'] <0,'gen_loss_est_kWh'] = 0
        except:
            data['no_PV_curtail'] = 1

        # --------------------------------- concat onto output_df
        output_df = pd.concat([output_df, data])

    # Calc gen_kWh for graphing and checking purposes
    output_df['gen_kWh'] = output_df['power_kW'] * output_df['duration']/(60*60)

    # Optional save data to csv
    output_df.to_csv(OUTPUT_DATA_FOLDER_PATH + DATA_DATE + TS_DATA_FILE_NAME_FULL)

    # Clean output_df before exporting to csv
    output_df_to_export = output_df[['ac','c_id','cf','clean','con_type','duration','energy','est_cf','est_kW',
                                     'est_kWh','reactive_power','first_ac','gen_kWh','gen_loss_est_kWh','Grouping','manufacturer',
                                     'model','power_kW','s_postcode','s_state','site_id','Standard_Version','v',
                                     'zero_flag', 'time_in_seconds']]
    # Optional save data to csv
    output_df_to_export.to_csv(OUTPUT_DATA_FOLDER_PATH + DATA_DATE + TS_DATA_FILE_NAME)

    # --------------------------------- Get summary stats
    # Get site_id list
    site_id_list = unaltered_data['site_id'].drop_duplicates().tolist()
    # Create df to store results
    sum_stats_df = pd.DataFrame(index=site_id_list)

    # Get data of relevance from output_df, summarised by site_id
    meta_df = pd.DataFrame({'power_kW': output_df.groupby('site_id')['power_kW'].sum(),
    'gen_loss_est_kWh': output_df.groupby('site_id')['gen_loss_est_kWh'].sum(),
    'event_num': output_df.groupby('site_id')['event_num'].max(),
    'duration': output_df.groupby('site_id')['duration'].first(),
    's_postcode': output_df.groupby('site_id')['s_postcode'].first(),
    'mean_v_all_daylight_hours': output_df.groupby('site_id')['v'].mean(),
    'first_ac': output_df.groupby('site_id')['first_ac'].first(),
    'ac': output_df.groupby('site_id')['ac'].first(),
    'Standard_Version': output_df.groupby('site_id')['Standard_Version'].first(),
    'Grouping': output_df.groupby('site_id')['Grouping'].first(),
    'model': output_df.groupby('site_id')['model'].first(),
    'manufacturer': output_df.groupby('site_id')['manufacturer'].first()
    })

    # Concat onto results df and name the index
    sum_stats_df = pd.concat([sum_stats_df, meta_df], axis=1)
    sum_stats_df.index.name = 'site_id'

    # Convert generation to kWh
    sum_stats_df['gen_kWh'] = sum_stats_df['power_kW'] * sum_stats_df['duration']/(60*60)
    # sum_stats_df = sum_stats_df.rename(columns = {'power_kW' : 'gen_kWh'})

    # Calc percentage of gen lost
    sum_stats_df['percentage_lost'] = sum_stats_df['gen_loss_est_kWh'].abs() / (sum_stats_df['gen_loss_est_kWh'].abs() + sum_stats_df['gen_kWh'].abs())

    # Get voltage box plot statistics for both curtail times and non curtail times
    curtail_v_df = output_df[output_df['est_period'] == 1]
    all_other_v_df = output_df[output_df['est_period'] != 1]
    # Filter for voltage and site it then get summary stats
    # Curtail times
    curtail_v_df = curtail_v_df[['v','site_id']]
    # rename 'v' to 'curtail_v' in order to see which is which when added to sum_stats_df
    curtail_v_df = curtail_v_df.rename(columns = {'v' : 'v_curtail'})
    curtail_v_box_plot_stats_df = curtail_v_df.groupby('site_id').describe()
    # Non curtail times
    all_other_v_df = all_other_v_df[['v','site_id']]
    # rename 'v' to 'other_v' in order to see which is which when added to sum_stats_df
    all_other_v_df = all_other_v_df.rename(columns = {'v' : 'v_all_other'})
    all_other_v_box_plot_stats_df = all_other_v_df.groupby('site_id').describe()

    # add box plot stats onto summary stats
    sum_stats_df = pd.concat([sum_stats_df, curtail_v_box_plot_stats_df, all_other_v_box_plot_stats_df], axis=1)

    # Get penetration by postcode
    # TODO - need to update the CER and APVI data files to match the Solar Analytics data set period being analysed!
    # TODO - could not locate the same type of APVI file (for dwellings) so may need to use the older data.
    # TODO - the CER data will require some attention and util will have to be updated to make it accept the updated CER data.
    sum_stats_df = util.get_penetration_by_postcode(PC_INSTALLS_DATA_FILE_PATH, DWELLINGS_DATA_FILE_PATH, sum_stats_df, output_df)

    # Sort and get % of systems
    sum_stats_df = sum_stats_df.sort_values('percentage_lost', ascending =False)

    # Get % of systems
    sum_stats_df['proportion_of_sites'] = range(len(sum_stats_df))
    sum_stats_df['proportion_of_sites'] = (sum_stats_df['proportion_of_sites'] + 1) / len(sum_stats_df)

    # Optional save data to csv
    sum_stats_df.to_csv(OUTPUT_DATA_FOLDER_PATH + DATA_DATE + SUM_STATS_DATA_FILE_NAME)





